import hou
import os
import sys
# import re
import json

sys.path.append(os.environ['CGPIPELINE'])
from _lib import configUtils, pathUtils



# def getAssetFolder(keyPrjPathsList):
#     depth = len(keyPrjPathsList) - 1
#     if depth == -1:
#         return ""

#     configData = keyPrjPathsList[-1]
#     templateConfigPath = configUtils.templateConfigFile
#     templateData = configUtils.loadConfigData(templateConfigPath)['Work_Paths']
#     orderConfigKeys = [r'{projectName}', r'{episodName}', r'{shotName}']
#     orderTemplKeys = ['workPath_prj', 'workPath_epi', 'workPath_shot']

#     templ = templateData[orderTemplKeys[depth]]
#     print("***", templ)
#     assetTemplate = templ.replace(orderConfigKeys[depth], configData)
#     pattern = r"({assetName}|shotName})"

#     print("===", assetTemplate)
#     assetsFolder = re.sub(pattern, "", assetTemplate)
#     print("+++", assetsFolder)

#     return assetsFolder

def getAssetFolder(keyPrjPathsList):
    depth = len(keyPrjPathsList) - 1
    if depth == -1:
        return ""

    configData = keyPrjPathsList[-1]
    templateConfigPath = configUtils.templateConfigFile
    templateData = configUtils.loadConfigData(templateConfigPath)['OTLPaths']
    orderConfigKeys = [r'{projectName}', r'{episodName}', r'{shotName}']
    orderTemplKeys = ['OTLPath_prj', 'OTLPath_epi', 'OTLPath_shot']

    templ = templateData[orderTemplKeys[depth]]
    assetTemplate = templ.replace(orderConfigKeys[depth], configData)

    assetRoot = assetTemplate.find(r"{assetName}")
    assetsFolder = assetTemplate[:assetRoot]

    return assetsFolder

def setPlaybackSettings(startFrame=1001, frames=100, fps=24):
    hou.setFps(float(fps))
    startF = startFrame
    endF = startFrame + frames - 1
    hou.playbar.setFrameRange(startF, endF)
    hou.playbar.setPlaybackRange(startF, endF)
    hou.setFrame(startF)
    hou.hscript('fplayback -r on')


def buildHoudiniScene(data):

    hipFile = data['hipFile']
    envVars = data['envVars']
    keyPrjPathsList = data['keyPrjPathsList']
    keyPrjData = data['keyPrjData']
    taskData = data['taskData']
    extraJobData = data['extraJobData']

    # keyPrjPathsList, hipFile, keyPrjData, taskData, envVars

    assetsFolder = getAssetFolder(keyPrjPathsList)
    jobFolder = os.path.dirname(hipFile)

    hipVer = "0".zfill(pathUtils.padding)
    hou.hscript('setenv HIPVER = ' + "{}".format(hipVer))
    hou.hscript('setenv ASSETS = ' + assetsFolder.replace("\\", "/"))
    hou.hscript('setenv JOB = ' + jobFolder.replace("\\", "/"))
    try:
        hou.hscript('setenv -l _PRJ = ' + keyPrjData['project'])
    except TypeError:
        pass
    try:
        hou.hscript('setenv -l _EPISOD = ' + keyPrjData['episod'])
    except TypeError:
        pass
    try:
        hou.hscript('setenv -l _SHOT = ' + keyPrjData['shot'])
    except TypeError:
        pass
    hou.hscript('setenv -l _ASSET = ' + taskData['assetName'])
    hou.hscript('setenv -l _TASK = ' + taskData['task'])
    hou.hscript('setenv -l _PADDING = ' + str(pathUtils.padding))

    for k, v in envVars.items():
        hou.hscript('setenv -l ' + k + ' = "' + v.replace("\\", "/") + '"')
        print(k, v)

    fps = envVars.get('FPS')
    startFrame = envVars.get('STARTFRAME')
    frames = extraJobData.get('frames')
    if fps is None:
        fps = 24
    if startFrame is None:
        startFrame = 1001
    if frames is None:
        frames = 100

    setPlaybackSettings(startFrame, frames, fps)

    hou.hipFile.save(hipFile)
    hou.exit()


# def setLocalVariablesForHip(data):
#     hipFile = data['hipFile']
#     localVars = data['localVars']

#     # hou.exit()
#     hou.hipFile.load(hipFile, True)
#     print("after loading", hou.hipFile.path())
#     print("JOB", hou.hscript('echo $JOB')[0].strip())

#     hou.hipFile.clearEventCallbacks()
#     for k, v in localVars.items():
#         hou.hscript('setenv -l ' + k + ' = "' + v.replace("\\", "/") + '"')

#     hou.hipFile.save(hipFile)
#     hou.exit()


func = sys.argv[-1]
data = json.loads(sys.argv[-2])
print("start hython process: ", func)
exec(func)
