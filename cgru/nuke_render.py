import os
import sys

sys.path.append(os.path.join(os.environ['CGPIPELINE'], "wrapper"))
import _nuke


_nuke.setEnvironmentVariables()

cgru_nuke_render = os.path.join(os.environ['CGRU_LOCATION'], "software_setup", "bin", "NUKE.cmd")
mainCommand = [cgru_nuke_render] + sys.argv[1:]
mainCommand = " ".join(mainCommand)

os.system(mainCommand)
