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

# nukeConfigFile = configUtils.nukeConfigFile


def getNukeLocation(nukeDir, ver, afRender=False):

    nukeLocation = nukeDir.format(ver=ver)
    if afRender is False:
        expectedNKPath = nukeLocation
        while not os.path.exists(nukeLocation):
            dialog = simpleDialogs.PathFileDialog()
            text = 'Nuke not found!. \nRecomended path is: "{}". \nPlease select the Nuke folder'.format(expectedNKPath)
            nukeLocation = dialog.showDialog(text)
            if nukeLocation is None:
                return None, None

    pattern = r'^Nuke\d{1,2}(\.\d{1,2}(\.\d{1,2})?)?\.exe$'
    try:
        nukeExe = list(filter(lambda x: re.search(pattern, x), os.listdir(nukeLocation)))[0]
    except FileNotFoundError as err:
        print('===> Nuke location not found!')
        raise err

    return nukeLocation, nukeExe


# def getNukeLocation(afRender=False):

#     ver = configUtils.loadConfigData(nukeConfigFile).get('version')
#     nukeLocation = configUtils.loadConfigData(nukeConfigFile).get('location').format(ver=ver)

#     if afRender is False:
#         expectedNKPath = nukeLocation
#         while not os.path.exists(nukeLocation):
#             dialog = simpleDialogs.PathFileDialog()
#             text = 'Nuke not found!. \nRecomended path is: "{}". \nPlease select the Nuke folder'.format(expectedNKPath)
#             nukeLocation = dialog.showDialog(text)
#             if nukeLocation is None:
#                 return None, None

#     pattern = r'^Nuke\d{1,2}(\.\d{1,2}(\.\d{1,2})?)?\.exe$'
#     try:
#         nukeExe = list(filter(lambda x: re.search(pattern, x), os.listdir(nukeLocation)))[0]
#     except FileNotFoundError as err:
#         print('===> Nuke location not found!')
#         raise err

#     return nukeLocation, nukeExe


# def setEnvironmentVariables(nukeLocationExe=None, afRender=False):
#     cgHomePath = configUtils.cgHomePath

#     if nukeLocationExe is None:
#         nukeLocation, nukeExe = getNukeLocation(afRender)
#         if nukeLocation is None:
#             print('===> Nuke location not found!')
#             return
#         nukeLocationExe = "/".join([nukeLocation, nukeExe])

#     os.environ['NUKE_EXE'] = nukeLocationExe
#     os.environ["NUKE_PATH"] = '/'.join([cgHomePath, 'Nuke'])
#     # ======== CGRU SETUP ========
#     if os.environ.get('CGRU_LOCATION') is None:
#         os.environ["CGRU_LOCATION"] = '/'.join([cgHomePath, 'cgru.2.3.1'])

#     ptyhonAfPaths = ['afanasy/python', 'lib/python', 'plugins/nuke']
#     os.environ["PYTHONPATH"] = ";".join(["/".join([os.environ.get('CGRU_LOCATION'), path]) for path in ptyhonAfPaths])
#     os.environ["NUKE_CGRU_PATH"] = '/'.join([os.environ.get('CGRU_LOCATION'), 'plugins/nuke'])


def setEnvironmentVariables(nukeLocationExe=None, afRender=False):
    cgHomePath = configUtils.cgHomePath

    # if nukeLocationExe is None:
    #     nukeLocation, nukeExe = getNukeLocation(afRender)
    #     if nukeLocation is None:
    #         print('===> Nuke location not found!')
    #         return
    #     nukeLocationExe = "/".join([nukeLocation, nukeExe])

    os.environ['NUKE_EXE'] = nukeLocationExe
    os.environ["NUKE_PATH"] = '/'.join([cgHomePath, 'Nuke'])
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
    # mainNkData = getNukeConfigData(keyPrjPathsList)
    # print(mainNkData)


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

    # nkfile = ""
    # nukeLocation, nukeExe = getNukeLocation()

    # if nukeLocation:

        # nukeLocationExe = "/".join([nukeLocation, nukeExe])
        # setEnvironmentVariables(nukeLocationExe)

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

    nukeLocation = mainNkData.get('location')
    nukeVersion = mainNkData.get('version')

    nukeLocation, nukeExe = getNukeLocation(nukeLocation, nukeVersion)
    nukeLocationExe = "/".join([nukeLocation, nukeExe])

    setEnvironmentVariables(nukeLocationExe)

    nkfile = ""
    if keyPrjData and taskData:
        nkfile = getNKFile(keyPrjData, taskData, extraJobData, nukeLocation, mainNkData)
    # keyPrjPathsList = []
    # # ================ GET CONFIG PATHS ==========================
    # depth = keyDataProjectUtils.getDepth(keyPrjData)
    # for d in range(depth):
    #     config = keyDataProjectUtils.getKeyPrjPath(keyPrjData, d + 1, nameInclude=True)
    #     keyPrjPathsList.append(config)

    # mainNkData = getNukeConfigData(keyPrjPathsList)

    print(mainNkData)

    nukeCommand = [nukeLocationExe, "--nukex", nkfile]
    print("=> Starting NUKE process: ", nukeCommand)
    subprocess.Popen(nukeCommand)

    # if not sys.stdin.isatty():
    #     args = sys.stdin.readline().decode("utf-8")
    #     args = json.loads(args)

    #     keyPrjData = args.get('keyPrjData') if args.get('keyPrjData') else dict()
    #     keyPrjData = OrderedDict(sorted(keyPrjData.items(), key=lambda x: len(x[0]), reverse=True))
    #     taskData = args.get('taskData') if args.get('taskData') else dict()
    #     extraJobData = args.get('extraJobData') if args.get('extraJobData') else dict()

    #     if keyPrjData and taskData:
    #         nkfile = getNKFile(keyPrjData, taskData, extraJobData, nukeLocation)

    #     nukeCommand = [nukeLocationExe, "--nukex", nkfile]
    #     print("=> Starting NUKE process: ", nukeCommand)
    #     # subprocess.Popen(nukeCommand)
    # else:
    #     print('===> Nuke location not found!')

# =====================================================================
# if "starter.py" in sys.argv[0]:

#     nkfile = ""
#     nukeLocation, nukeExe = getNukeLocation()

#     if nukeLocation:

#         nukeLocationExe = "/".join([nukeLocation, nukeExe])
#         setEnvironmentVariables(nukeLocationExe)

#         if not sys.stdin.isatty():
#             args = sys.stdin.readline().decode("utf-8")
#             args = json.loads(args)

#             keyPrjData = args.get('keyPrjData') if args.get('keyPrjData') else dict()
#             keyPrjData = OrderedDict(sorted(keyPrjData.items(), key=lambda x: len(x[0]), reverse=True))
#             taskData = args.get('taskData') if args.get('taskData') else dict()
#             extraJobData = args.get('extraJobData') if args.get('extraJobData') else dict()

#             if keyPrjData and taskData:
#                 nkfile = getNKFile(keyPrjData, taskData, extraJobData, nukeLocation)

#         nukeCommand = [nukeLocationExe, "--nukex", nkfile]
#         print("=> Starting NUKE process: ", nukeCommand)
#         # subprocess.Popen(nukeCommand)
#     else:
#         print('===> Nuke location not found!')

