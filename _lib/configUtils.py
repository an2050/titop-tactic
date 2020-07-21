import os
import sys
import json


tacticAssetsPath = "//fed_TACTIC"

rootPath = os.environ['CGPIPELINE']

pythonDir = os.path.join(rootPath, "python")
py2exe = os.path.join(pythonDir, "python27", "python.exe")

starterPath = os.path.join(rootPath, "starter.py")
starter_hythonPath = os.path.join(rootPath, "_lib", "hou_lib", "starter_hython.cmd")

mainProjectConfigFile = os.path.join(rootPath, "config_main.json")
templateConfigFile = os.path.join(rootPath, "config_template.json")
activeProjectsFile = os.path.join(rootPath, "activeProjects.json")

rvPlayerPath = 'C:/Program Files/Shotgun/RV-7.8.0/bin'

tacticConfigFile = os.path.join(rootPath, "tactic", "tacticConfig.json")

tacticKeyElements = {"episodes": "episod", "shots": "shot"}  # Items that match the names in TACTIC
tacticProcessElements = {"comp": "comp"}
tacticStatusElements = {"Assignment": "Assignment", "Complete": "Complete"}


def loadConfigData(filePath):
    if os.path.exists(filePath) is False:
        print("File {filePath} is not exists".format(filePath=filePath))
        return None
    with open(filePath) as f:
        try:
            return json.load(f)
        except json.decoder.JSONDecodeError:
            print("Config {config} is incorrect".format(config=filePath))


def saveConfigData(filePath, data):
    with open(filePath, "w") as f:
        json.dump(data, f, indent=4)


def checkAndCreateConfigFile(filePath):
    if os.path.exists(filePath):
        return True

    dirName = os.path.dirname(filePath)
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    with open(filePath, "w") as f:
        json.dump(dict(), f, indent=4)


def merge_two_dicts(d1, d2):
    newDict = d1.copy()
    newDict.update(d2)
    return newDict


def filterDictKeys(d, keys):
    filteredDict = dict()
    for key in d:
        if key in keys:
            filteredDict[key] = d[key]
    return filteredDict


def decodeDict(data):
    decodeDict = {}
    if sys.version_info[0] >= 3:
        for k, v in data.items():
            if isinstance(k, str) is False:
                k = k.decode('utf-8')
            if isinstance(v, str) is False:
                v = v.decode('utf-8')
            decodeDict[k] = v
    else:
        for k, v in data.items():
            if isinstance(k, unicode):
                k = str(k)
            if isinstance(v, unicode):
                v = str(v)
            decodeDict[k] = v
    return decodeDict
