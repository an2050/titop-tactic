import json
import subprocess
import configUtils

def buildHoudiniScene(hipFile, envVars, keyPrjPathsList, keyPrjData, taskData, extraJobData):
    dataArgs = {'envVars': envVars, 'hipFile': hipFile, 'keyPrjPathsList': keyPrjPathsList, "keyPrjData": keyPrjData, "taskData": taskData, "extraJobData": extraJobData}
    dataArgs = json.dumps(dataArgs)
    function = "buildHoudiniScene(data)"

    houdiniDir = envVars['HOUDINI_DIR']
    hython_starter = configUtils.starter_hythonPath
    runArgs = [hython_starter, houdiniDir, dataArgs, function]
    subprocess.call(runArgs)
