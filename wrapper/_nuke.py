import os
import sys
import re
import json
import subprocess
from collections import OrderedDict

sys.path.append(os.environ['CGPIPELINE'])

from _lib import keyDataProjectUtils

from _lib import configUtils, pathUtils

from _lib.nk_lib import starter_nkython
from UI.Dialogs import simpleDialogs


def getLocalNukeLocation(ver):

    configFile = configUtils.configLocal
    if not os.path.exists(configFile):
        configUtils.saveConfigData(configFile, dict())

    localNukeLocation = configUtils.loadConfigData(configUtils.configLocal).get('NUKE_location')
    nukeLocation = ""
    if localNukeLocation:
        rootDir, nukeDir = os.path.split(localNukeLocation)
        nukeDir = "/".join([rootDir, r"Nuke{ver}"])
        nukeLocation = nukeDir.format(ver=ver)
    return nukeLocation


def getNukeLocation(ver, afRender=False):
    from platform import system
    nukeDir = ""
    if system() is 'Windows':
        nukeDir = "/".join(['C:', 'Program Files', r'Nuke{ver}'])
    elif system() is 'Linux':
        nukeDir = ''
    elif system() == 'Darwin':
        nukeDir = ''

    nukeLocation = nukeDir.format(ver=ver)
    if not os.path.exists(nukeLocation):
        nukeLocation = getLocalNukeLocation(ver)

    if not os.path.exists(nukeLocation):
        if afRender:
            print('===> Nuke location not found!')
            raise FileNotFoundError
        else:
            while not os.path.exists(nukeLocation):
                dialog = simpleDialogs.PathFileDialog()
                text = 'Specify the nuke folder please. \nRecomended verison is: Nuke"{}"'.format(ver)
                nukeLocation = dialog.showDialog(text)
                if nukeLocation is None:
                    return None, None

                localData = configUtils.loadConfigData(configUtils.configLocal)
                localData['NUKE_location'] = nukeLocation
                configUtils.saveConfigData(configUtils.configLocal, localData)

    pattern = r'^Nuke\d{1,2}(\.\d{1,2}(\.\d{1,2})?)?\.exe$'
    try:
        nukeExe = list(filter(lambda x: re.search(pattern, x), os.listdir(nukeLocation)))[0]
    except FileNotFoundError as err:
        print('===> Nuke location not found!')
        raise err

    return nukeLocation, nukeExe


def setEnvironmentVariables(nukeLocationExe, keyPrjData):
    cgHomePath = configUtils.cgHomePath

    os.environ['NUKE_EXE'] = nukeLocationExe
    os.environ["NUKE_PATH"] = '/'.join([cgHomePath, 'Nuke'])
    if keyPrjData:
        os.environ["PROJECT_ROOT"] = keyDataProjectUtils.getProjectFolder(keyPrjData)
    # ======== CGRU SETUP ========
    # if os.environ.get('CGRU_LOCATION') is None:
    #     os.environ["CGRU_LOCATION"] = '/'.join([cgHomePath, 'cgru.2.3.1'])

    ptyhonAfPaths = ['afanasy/python', 'lib/python', 'plugins/nuke']
    os.environ["PYTHONPATH"] = ";".join(["/".join([os.environ.get('CGRU_LOCATION'), path]) for path in ptyhonAfPaths])
    os.environ["NUKE_CGRU_PATH"] = '/'.join([os.environ.get('CGRU_LOCATION'), 'plugins/nuke'])


def getNKFile(keyPrjData, taskData, extraJobData, nukeLocation, mainNkData):

    workPath = pathUtils.getWork_Path(keyPrjData, taskData)
    fileName = pathUtils.createFileName(keyPrjData, taskData, ext="nk")
    nkfile = "/".join([workPath, fileName])

    if os.path.exists(nkfile):
        fileName = pathUtils.getVersioinFile(nkfile, isFile=True, ext="nk", version=None)[0]
        nkfile = "/".join([workPath, fileName])
        return nkfile
    else:
        print("=> Creating nuke script...: '{}'".format(nkfile))
        starter_nkython.initNKScene(nkfile, keyPrjData, extraJobData, nukeLocation, mainNkData)
        return nkfile


def getConfigList(keyPrjData):

    keyPrjPathsList = []
    depth = keyDataProjectUtils.getDepth(keyPrjData)
    for d in range(depth):
        config = keyDataProjectUtils.getKeyPrjPath(keyPrjData, d + 1, nameInclude=True)
        keyPrjPathsList.append(config)

    return keyPrjPathsList


def getNukeConfigData(keyPrjPathsList):
    configPathsList = []
    configPathsList = [os.path.join(x, "config.json") for x in keyPrjPathsList]
    configPathsList.insert(0, configUtils.mainProjectConfigFile)

    mainNkData = dict()
    for config in configPathsList:
        configData = configUtils.loadConfigData(config)

        if configData is None:
            continue
        try:
            nkConfigData = [data for data in configData if data.get('NUKE')][0].get('NUKE')
            [mainNkData.update(data) for data in nkConfigData]
        except IndexError:
            continue
    return mainNkData


if "starter.py" in sys.argv[0]:

    keyPrjData = dict()
    taskData = None
    extraJobData = None

    if not sys.stdin.isatty():
        args = sys.stdin.readline().decode("utf-8")
        args = json.loads(args)

        keyPrjData = args.get('keyPrjData') if args.get('keyPrjData') else dict()
        keyPrjData = OrderedDict(sorted(keyPrjData.items(), key=lambda x: len(x[0]), reverse=True))
        taskData = args.get('taskData') if args.get('taskData') else None
        extraJobData = args.get('extraJobData') if args.get('extraJobData') else None

    keyPrjPathsList = getConfigList(keyPrjData)
    mainNkData = getNukeConfigData(keyPrjPathsList)

    nukeLocation, nukeExe = getNukeLocation(mainNkData.get('version'))
    nukeLocationExe = "/".join([nukeLocation, nukeExe])

    setEnvironmentVariables(nukeLocationExe, keyPrjData)

    nkfile = ""
    if keyPrjData and taskData:
        nkfile = getNKFile(keyPrjData, taskData, extraJobData, nukeLocation, mainNkData)

    nukeCommand = [nukeLocationExe, "--nukex", nkfile]
    print("=> Starting NUKE process: ", nukeCommand)
    subprocess.Popen(nukeCommand)
