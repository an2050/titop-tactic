import re
from . import configUtils


def getRootFolder():
    keyPrjData = {"project": None, "episod": None, "shot": None}
    return getKeyPrjPath(keyPrjData)


def getProjectFolder(keyPrjData):
    return getKeyPrjPath(keyPrjData, depthIndex=1, nameInclude=True)


def getDepth(keyPrjData):
    depth = filter(lambda x: x is not None, keyPrjData.values())
    depth = len(list(depth))
    return depth

def getKeyPrjPath(keyPrjData, depthIndex=None, nameInclude=False):

    if nameInclude:
        pattern = r"((((.*){projectName}).*{episodName}).*{shotName})"
    else:
        pattern = r"((((.*){projectName}.*){episodName}.*){shotName}.*)"

    depthIndex = getDepth(keyPrjData) if depthIndex is None else depthIndex

    template = configUtils.loadConfigData(configUtils.templateConfigFile)['projectTemplate']
    template = list(re.findall(pattern, template)[0])

    template = template[::-1][depthIndex]

    path = template.format(projectName=keyPrjData['project'], episodName=keyPrjData['episod'], shotName=keyPrjData['shot'])
    return path.strip("/")


def collapseToKeyPrjData(path):
    from collections import OrderedDict

    templateConfigPath = configUtils.templateConfigFile
    mainTemplate = configUtils.loadConfigData(templateConfigPath)['projectTemplate']
    configKeys = [r'{projectName}', r'{episodName}', r'{shotName}']

    keyPrjData = {"project": None, "episod": None, "shot": None}
    keyPrjData = OrderedDict(sorted(keyPrjData.items(), key=lambda x: len(x[0]), reverse=True))
    for d in configKeys:
        idx = mainTemplate.find(d)
        depthTemplate = mainTemplate[:idx]

        pattern = re.escape(depthTemplate)
        pattern = re.sub(r"\\\\", r"[\\\\|\/]", pattern, flags=re.IGNORECASE)
        pattern += r"(.+?)(\\|\/|\b)"
        matchPath = re.match(pattern, path, flags=re.IGNORECASE)
        if matchPath:
            depthName = matchPath.group(1)

            key = d.replace("Name", "")
            key = key.replace("{", "")
            key = key.replace("}", "")
            keyPrjData[key] = depthName
            mainTemplate = mainTemplate.replace(d, depthName)

    return dict(keyPrjData)