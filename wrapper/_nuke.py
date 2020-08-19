import os
import sys
import re
import json
import subprocess
from collections import OrderedDict

sys.path.append(os.environ['CGPIPELINE'])

from _lib import configUtils, pathUtils

from _lib.nk_lib import starter_nkython

nukeConfigFile = configUtils.nukeConfigFile


def getNukeLocation():
    ver = configUtils.loadConfigData(nukeConfigFile).get('version')
    nukeLocation = configUtils.loadConfigData(nukeConfigFile).get('location').format(ver=ver)
    if not os.path.exists(nukeLocation):
        print("=> Nuke location not found. Recomended path is: {}".format(nukeLocation))
        return ""
    else:
        pattern = r'^Nuke\d{1,2}(\.\d{1,2}(\.\d{1,2})?)?\.exe$'
        nukeExe = list(filter(lambda x: re.search(pattern, x), os.listdir(nukeLocation)))[0]

    return nukeLocation, nukeExe


def setEnvironmentVariables(nukeLocationExe=None):
    # nukeLocation = "C:\\Program Files\\Nuke10.5v5"
    # nukeExe = "Nuke10.5.exe"
    # nukeLocation = "C:\\Program Files\\Nuke11.3v5"
    # nukeExe = "Nuke11.3.exe"
    # nukeLocation = "C:\\Program Files\\Nuke12.0v5"
    # nukeExe = "Nuke12.0.exe"

    # os.environ['NUKE_EXE'] = os.path.join(nukeLocation, nukeExe)
    if nukeLocationExe is None:
        nukeLocation, nukeExe = getNukeLocation()
        nukeLocationExe = "/".join([nukeLocation, nukeExe])

    os.environ['NUKE_EXE'] = nukeLocationExe
    os.environ["NUKE_PATH"] = 'C:/pipeline/Nuke'
    # ======== CGRU SETUP ========
    os.environ["PYTHONPATH"] = 'C:/pipeline/cgru.2.3.1/afanasy/python;C:/pipeline/cgru.2.3.1/lib/python;c:/pipeline/cgru.2.3.1/plugins/nuke'
    os.environ["CGRU_LOCATION"] = 'C:/pipeline/cgru.2.3.1'
    os.environ["NUKE_CGRU_PATH"] = 'C:/pipeline/cgru.2.3.1/plugins/nuke'


def getNKFile(keyPrjData, taskData, extraJobData, nukeLocation):

    workPath = pathUtils.getWork_Path(keyPrjData, taskData)
    fileName = pathUtils.createFileName(keyPrjData, taskData, ext="nk")
    nkfile = "/".join([workPath, fileName])

    if os.path.exists(nkfile):
        fileName = pathUtils.getVersioinFile(nkfile, isFile=True, ext="nk", version=None)[0]
        nkfile = "/".join([workPath, fileName])
        return nkfile
    else:
        print("=> Creating nuke script...: '{}'".format(nkfile))
        starter_nkython.initNKScene(nkfile, keyPrjData, extraJobData, nukeLocation)
        return nkfile


if "starter.py" in sys.argv[0]:

    nkfile = ""
    nukeLocation, nukeExe = getNukeLocation()
    nukeLocationExe = "/".join([nukeLocation, nukeExe])

    setEnvironmentVariables(nukeLocationExe)

    if not sys.stdin.isatty():
        args = sys.stdin.readline().decode("utf-8")
        args = json.loads(args)

        keyPrjData = args.get('keyPrjData') if args.get('keyPrjData') else dict()
        keyPrjData = OrderedDict(sorted(keyPrjData.items(), key=lambda x: len(x[0]), reverse=True))
        taskData = args.get('taskData') if args.get('taskData') else dict()
        extraJobData = args.get('extraJobData') if args.get('extraJobData') else dict()

        if keyPrjData and taskData:
            nkfile = getNKFile(keyPrjData, taskData, extraJobData, nukeLocation)

    nukeCommand = [nukeLocationExe, "--nukex", nkfile]
    print("=> Starting NUKE process: ", nukeCommand)
    subprocess.Popen(nukeCommand)

