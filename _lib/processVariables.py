import os
import json
from _lib import configUtils
from _lib.lib_widgets_ui import selectDialog


# def merge_two_dicts(d1, d2):
#     newDict = d1.copy()
#     newDict.update(d2)
#     return newDict


def merge_twoPathDict(d1, d2):
    for k in d1.keys():
        if k in list(d2.keys()):
            d2[k] = list(set(d1[k] + d2[k]))
    return configUtils.merge_two_dicts(d1, d2)


def updateInitSystemEnvs():
    if os.getenv("INITENVS") is None:
        os.environ["INITENVS"] = "true"
        initSystemEnvs = dict(os.environ.copy())
        userDir = os.path.join(os.getenv('APPDATA'), "cgpipeline",)
        sysEnvsFile = os.path.join(userDir, "initSystemEnvs.json")
        if os.path.exists(userDir) is False:
            os.mkdir(userDir)
        elif os.path.exists(sysEnvsFile):
            os.remove(sysEnvsFile)
        with open(sysEnvsFile, 'w') as f:
            json.dump(initSystemEnvs, f)


def getInitSystemEnvs():
    tempFile = os.path.join(os.getenv('APPDATA'), "cgpipeline", "initSystemEnvs.json")
    return configUtils.loadConfigData(tempFile)


# Return an element of config by key
def getVariabelElement(configData, element):
    try:
        element = list(list(filter(lambda x: element in x.keys(), configData))[0].values())[0]
        return element
    except IndexError:
        return None


# Collect all variables which may walk into deep. Collects it together
def collectPathEnvsVariables(configData, caseEnvsData):
    configData = getVariabelElement(configData, 'path_envs')
    if configData is None:
        return None
    caseEnvsData = collectDeepEnvsData(configData, caseEnvsData)


def collectRenderEnvsVariables(configList, caseEnvsData, render):

    if render == "Mantra":
        caseEnvsData['RENDER'] = ["Mantra"]
        return

    renderDataList = []
    for config in configList:
        configData = configUtils.loadConfigData(config)
        # configData = getJsonData(config)
        if configData is None:
            continue
        configData = getVariabelElement(configData, 'renders')
        if configData is None:
            continue
        renderDataList.append(configData)

    try:
        configData = renderDataList[-1]
    except IndexError:
        caseEnvsData['RENDER'] = ["Mantra"]
        # caseEnvsData = {}
        return None

    if render is None:
        renderItems = [list(x.keys())[0] for x in configData]
        if len(renderItems) > 1:
            selectedItems = selectDialog.executeDialog(renderItems)
        else:
            selectedItems = renderItems

    else:
        selectedItems = render.split(";")

    if len(selectedItems) == 0:
        caseEnvsData['RENDER'] = ["Mantra"]
        return None

    caseEnvsData['RENDER'] = selectedItems
    for data in configData:
        if list(data.keys())[0] in selectedItems:
            collectDeepEnvsData(list(data.values())[0], caseEnvsData)


def collectDeepEnvsData(configData, caseEnvsData):
    for var in configData:
        key = list(var.keys())[0]
        value = list(var.values())[0]
        if isinstance(value, list):
            collectDeepEnvsData(value, caseEnvsData)
        else:
            if key in caseEnvsData.keys():
                caseEnvsData[key].append(value)
            elif key in getInitSystemEnvs().keys():
                # caseEnvsData[key] = [getInitSystemEnvs()[key], value]
                InitSystemEnvs = getInitSystemEnvs()
                indx = len(InitSystemEnvs[key])
                caseEnvsData[key] = [InitSystemEnvs[key][:indx - 1] + InitSystemEnvs[key][indx - 1:].replace(";", ""), value]
            else:
                caseEnvsData[key] = [value]
    return caseEnvsData


# Collect variables at the top level. Overwrites value for identical keys.
def collectEnvsVariables(configData, caseEnvsData):
    for var in configData:
        if isinstance(list(var.values())[0], list) is False:
            caseEnvsData[list(var.keys())[0]] = list(var.values())[0]


def collectAssetPathsVariables(configFileList):
    configFileList = [f.replace("\\config.json", "") for f in configFileList[1:]]
    configData = dict()
    try:
        configData[r'{projectName}'] = configFileList[0]
    except IndexError:
        pass
    try:
        configData[r'{episodName}'] = configFileList[1]
    except IndexError:
        pass
    try:
        configData[r'{shotName}'] = configFileList[2]
    except IndexError:
        pass

    otlPaths = {"HOUDINI_OTLSCAN_PATH": []}

    templateConfigFilePath = configUtils.templateConfigFile
    templateData = configUtils.loadConfigData(templateConfigFilePath)['OTLPaths']
    # del templateData['projectTemplate']

    rawTemplates = [x for x in templateData.values()]

    for templ in rawTemplates:
        for k in configData.keys():
            if templ.find(k) >= 0:
                templ = templ.replace(k, configData[k])

                indx = templ.find(r"{assetName}")
                if indx == -1:
                    print("Wrong OTL Path template: Asset template must have '{assetName}' part")
                    continue
                pathToAssets = templ[:indx]
                if os.path.exists(pathToAssets):
                    for element in os.listdir(pathToAssets):
                        if os.path.isdir(os.path.join(pathToAssets, element)):
                            otlPath = templ.format(assetName=element)
                            if os.path.exists(otlPath):
                                otlPaths["HOUDINI_OTLSCAN_PATH"].append(otlPath)

    return otlPaths


def collectProjectVariables(configFileList):
    configFileList = [f.replace("\\config.json", "") for f in configFileList[1:]]
    projectVariables = dict()
    try:
        projectVariables['PRJ'] = configFileList[0]
    except IndexError:
        pass
    try:
        projectVariables['EPISOD'] = configFileList[1]
    except IndexError:
        pass
    try:
        projectVariables['SHOT'] = configFileList[2]
    except IndexError:
        pass
    return projectVariables


# leads collected path variales to right view
def completeAllPathEnvVariables(varsData):
    pathEnvsVariables = dict()
    for k, v in varsData.items():
        pathEnvsVariables[k] = "{lst_env};&;".format(lst_env=";".join(v))

    try:
        pathEnvsVariables['RENDER'] = pathEnvsVariables['RENDER'].replace(";&;", "")
    except KeyError:
        pass
    return pathEnvsVariables


# Main function
def projectSettingsProcess(configFileList, render):
    envsVariables = dict()
    projectVariables = collectProjectVariables(configFileList)
    pathEnvsVariables = dict()
    renderEnvsVariables = dict()
    assetPathsVariables = collectAssetPathsVariables(configFileList)

    collectRenderEnvsVariables(configFileList, renderEnvsVariables, render)

    for config in configFileList:
        configData = configUtils.loadConfigData(config)
        if configData is None:
            continue
        if isinstance(configData, list):
            collectEnvsVariables(configData, envsVariables)
            collectPathEnvsVariables(configData, pathEnvsVariables)
        else:
            print("Config file: {config} contains unexpected data".format(config=config))

    pathEnvsVariables = merge_twoPathDict(renderEnvsVariables, pathEnvsVariables)
    pathEnvsVariables = merge_twoPathDict(assetPathsVariables, pathEnvsVariables)
    envsVariables = configUtils.merge_two_dicts(projectVariables, envsVariables)

    pathEnvsVariables = completeAllPathEnvVariables(pathEnvsVariables)

    allEnvironmentVariables = configUtils.merge_two_dicts(pathEnvsVariables, envsVariables)
    allEnvironmentVariables['HOUDINI_DIR'] = allEnvironmentVariables['location'].format(ver=allEnvironmentVariables['version'])

    return allEnvironmentVariables
