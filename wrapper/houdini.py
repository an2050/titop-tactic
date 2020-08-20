import os
import sys
import re
import json
import subprocess
import configUtils
import keyDataProjectUtils
from _lib import pathUtils
from hou_lib import transferToHython


def processUserVariables(allEnvironmentVariables):
    for k, v in allEnvironmentVariables.items():
        pattern = r'%(.*?)%'
        if re.findall(pattern, v):
            allEnvironmentVariables[k] = re.sub(pattern, lambda x: getUserPatternValue(x, allEnvironmentVariables), v)


def getUserPatternValue(match, allEnvironmentVariables):
    match = match.groups()[0]
    if match in allEnvironmentVariables.keys():
        pattern = r'%(.*?)%'
        if re.findall(pattern, allEnvironmentVariables[match]):
            allEnvironmentVariables[match] = re.sub(pattern, lambda x: getUserPatternValue(x, allEnvironmentVariables), allEnvironmentVariables[match])
        return allEnvironmentVariables[match].replace(";&;", "")


def getAllEnvironmentVariables(keyPrjPathsList, systemVars=True, renderEngine=None):
    import processVariables

    keyPrjPathsList = [os.path.join(x, "config.json") for x in keyPrjPathsList]
    keyPrjPathsList.insert(0, configUtils.mainProjectConfigFile)

    allEnvironmentVariables = processVariables.projectSettingsProcess(keyPrjPathsList, renderEngine)

    if systemVars:
        initSystemEnvs = processVariables.getInitSystemEnvs()
        allEnvironmentVariables = configUtils.merge_two_dicts(initSystemEnvs, allEnvironmentVariables)

    if allEnvironmentVariables.get('CGHOME') == 'local' or allEnvironmentVariables.get('CGHOME') is None:
        allEnvironmentVariables['CGHOME'] = configUtils.cgHomePath

    allEnvironmentVariables = configUtils.decodeDict(allEnvironmentVariables)
    processUserVariables(allEnvironmentVariables)

    # for e in sorted(allEnvironmentVariables.keys()):
    #     print(e, " = ", allEnvironmentVariables[e])
    # print(allEnvironmentVariables['HOUDINI_OTLSCAN_PATH'].replace(";", "\n"))
    # print(allEnvironmentVariables['HOUDINI_DIR'].replace(";", "\n"))

    return allEnvironmentVariables


# ================= START SCRIPT =============================

if "starter.py" in sys.argv[0]:

    hipFile = ""

    keyPrjData = dict()
    taskData = None
    extraJobData = None

    if not sys.stdin.isatty():
        args = sys.stdin.readline().decode("utf-8")
        args = json.loads(args)

        keyPrjData = args.get('keyPrjData') if args.get('keyPrjData') else dict()
        taskData = args.get('taskData') if args.get('taskData') else None
        extraJobData = args.get('extraJobData') if args.get('extraJobData') else None

    # try:
    #     keyPrjData = json.loads(sys.argv[2])
    #     keyPrjData = OrderedDict(sorted(keyPrjData.items(), key=lambda x: len(x[0]), reverse=True))
    # except IndexError:
    #     keyPrjData = {}
    # try:
    #     taskData = json.loads(sys.argv[3])
    # except IndexError:
    #     taskData = None
    # try:
    #     extraJobData = json.loads(sys.argv[4])
    # except IndexError:
    #     extraJobData = None

    keyPrjPathsList = []
    # ================ GET CONFIG PATHS ==========================
    depth = keyDataProjectUtils.getDepth(keyPrjData)
    for d in range(depth):
        config = keyDataProjectUtils.getKeyPrjPath(keyPrjData, d + 1, nameInclude=True)
        keyPrjPathsList.append(config)

    # ================  GET VARIABLES ==========================
    allEnvironmentVariables = getAllEnvironmentVariables(keyPrjPathsList)
    houdiniLocation = allEnvironmentVariables['location'].format(ver=allEnvironmentVariables['version'])

    # ================ BUILD HIP SCENE ===========================
    if taskData is not None:
        workPath = pathUtils.getWork_Path(keyPrjData, taskData, create=True)
        hipName = pathUtils.createFileName(keyPrjData, taskData, ext="hip")
        hipFile = "/".join([workPath, hipName])

        if os.path.exists(hipFile) is False:
            varsToPassList = ['HOUDINI_DIR', 'PRJ', 'EPISOD', 'SHOT', 'RENDER', 'RESX', "RESY", "FPS"]
            varsToPass = dict([(k, allEnvironmentVariables.get(k)) for k in varsToPassList if allEnvironmentVariables.get(k) is not None])
            transferToHython.buildHoudiniScene(hipFile, varsToPass, keyPrjPathsList, keyPrjData, taskData, extraJobData)
        else:
            hipName = pathUtils.getVersioinFile(hipFile, isFile=True, ext="hip", version=None)[0]
            hipFile = "/".join([workPath, hipName])

    # print(allEnvironmentVariables['HOUDINI_PATH'].replace(";", "\n"))

    # ================  RUN HOUDINI ==========================
    if houdiniLocation is not None and os.path.exists(houdiniLocation):
        hipFile = [] if hipFile == "" else [hipFile]
        houdiniCommand = [os.path.join(houdiniLocation, "bin", "houdini.exe")] + hipFile
        subprocess.Popen(houdiniCommand, env=allEnvironmentVariables, shell=True)
    else:
        print("Wrong Houdini location path:", houdiniLocation)
