import os
import sys
import json

sys.path.append(os.path.join(os.environ['CGPIPELINE'], "wrapper"))
sys.path.append(os.path.join(os.environ['CGPIPELINE']))

import houdini


def cacheSystemEnvironmentVariables():
    initSystemEnvs = dict(os.environ.copy())
    userDir = os.path.join(os.getenv('APPDATA'), "cgpipeline",)
    sysEnvsFile = os.path.join(userDir, "initSystemEnvs.json")
    if os.path.exists(userDir) is False:
        os.mkdir(userDir)
    elif os.path.exists(sysEnvsFile):
        os.remove(sysEnvsFile)
    with open(sysEnvsFile, 'w') as f:
        json.dump(initSystemEnvs, f)


def setupHouodiniVariables():
    configArgs = sys.argv[-1].replace("'", "\"")
    configArgs = configArgs.replace("None", "null")
    configArgs = json.loads(configArgs)

    configFileList = configArgs[:-1]
    configFileList = [f for f in configFileList if f is not None]

    renderEngine = configArgs[-1]
    allVariables = houdini.getAllEnvironmentVariables(configFileList, False, renderEngine)
    # print("Render Engine == ", renderEngine)

    for k, v in allVariables.items():
        os.environ[k] = v


cacheSystemEnvironmentVariables()
setupHouodiniVariables()

mainCommandArgs = sys.argv[1:-1]
mainCommandArgs = mainCommandArgs[:-2] + ['"{}"'.format(x) for x in mainCommandArgs[-2:]]

cgru_hrender = os.path.join(os.environ['CGRU_LOCATION'], "software_setup", "bin", "hrender_af.cmd")
mainCommandList = [cgru_hrender] + mainCommandArgs
mainCommand = " ".join(mainCommandList)
# print("AF HOU COMMAND IS =", mainCommand)
os.system(mainCommand)
