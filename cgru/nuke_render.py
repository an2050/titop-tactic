import os
import sys
import json

sys.path.append(os.path.join(os.environ['CGPIPELINE'], "wrapper"))
sys.path.append(os.path.join(os.environ['CGPIPELINE'], "_lib"))

import _nuke

keyPrjData = json.loads(sys.argv[-1].replace("\'", "\""))

keyPrjPathsList = _nuke.getConfigList(keyPrjData)
mainNkData = _nuke.getNukeConfigData(keyPrjPathsList)
nukeLocation, nukeExe = _nuke.getNukeLocation(mainNkData.get('version'), afRender=True)
nukeLocationExe = "/".join([nukeLocation, nukeExe])

_nuke.setEnvironmentVariables(nukeLocationExe)

cgru_nuke_render = os.path.join(os.environ['CGRU_LOCATION'], "software_setup", "bin", "NUKE.cmd")
mainCommand = [cgru_nuke_render] + ['"' + arg + '"' for arg in sys.argv[1:-1]]
mainCommand = " ".join(mainCommand)
# print("MAIN COMMAND IS ====", mainCommand)

os.system(mainCommand)
