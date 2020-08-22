import os
import sys

sys.path.append(os.path.join(os.environ['CGPIPELINE'], "wrapper"))
sys.path.append(os.path.join(os.environ['CGPIPELINE'], "_lib"))

import _nuke


_nuke.setEnvironmentVariables(afRender=True)

cgru_nuke_render = os.path.join(os.environ['CGRU_LOCATION'], "software_setup", "bin", "NUKE.cmd")
mainCommand = [cgru_nuke_render] + ['"' + arg + '"' for arg in sys.argv[1:]]
mainCommand = " ".join(mainCommand)
# print("MAIN COMMAND IS ====", mainCommand)

os.system(mainCommand)
