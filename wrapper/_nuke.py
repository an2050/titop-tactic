import os
import sys


def setEnvironmentVariables():

    # nukeLocation = "C:\\Program Files\\Nuke10.5v5"
    # nukeExe = "Nuke10.5.exe"
    nukeLocation = "C:\\Program Files\\Nuke11.3v5"
    nukeExe = "Nuke11.3.exe"
    # nukeLocation = "C:\\Program Files\\Nuke12.0v5"
    # nukeExe = "Nuke12.0.exe"

    os.environ['NUKE_EXE'] = os.path.join(nukeLocation, nukeExe)
    os.environ["NUKE_PATH"] = 'C:/pipeline/Nuke'
    # ======== CGRU SETUP ========
    os.environ["PYTHONPATH"] = 'C:/pipeline/cgru.2.3.1/afanasy/python;C:/pipeline/cgru.2.3.1/lib/python;c:/pipeline/cgru.2.3.1/plugins/nuke'
    os.environ["CGRU_LOCATION"] = 'C:/pipeline/cgru.2.3.1'
    os.environ["NUKE_CGRU_PATH"] = 'C:/pipeline/cgru.2.3.1/plugins/nuke'


def getNKFile():
    import re
    import configUtils
    import pathUtils

    try:
        taskData = json.loads(sys.argv[3])
    except IndexError:
        return ""

    try:
        if dict(keyPrjData).keys()[-1] == "shot":
            workPath = pathUtils.getWork_Path(keyPrjData, taskData)
            fileName = pathUtils.createFileName(keyPrjData, taskData, ext="nk")
            nkfile = os.path.join(workPath, fileName)

            if os.path.exists(nkfile):
                fileName = pathUtils.getVersioinFile(nkfile, isFile=True, ext="nk", version=None)[0]
                nkfile = os.path.join(workPath, fileName)
                return nkfile
            else:
                print("'{}' does not exists".format(nkfile))
                return nkfile
        else:
            return ""
    except IndexError:
        return ""


if "starter.py" in sys.argv[0]:
    from collections import OrderedDict
    import json
    import subprocess

    try:
        keyPrjData = json.loads(sys.argv[2])
        keyPrjData = OrderedDict(sorted(keyPrjData.items(), key=lambda x: len(x[0]), reverse=True))
    except IndexError:
        keyPrjData = {}

    nkfile = ""
    if len(keyPrjData) > 0:
        nkfile = getNKFile()
        print(nkfile)

    setEnvironmentVariables()
    nukeLocation = os.environ['NUKE_EXE']
    nukeCommand = [nukeLocation, "--nukex", nkfile]
    subprocess.Popen(nukeCommand, shell=True)
