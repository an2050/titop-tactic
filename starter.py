import sys
import os
import tempfile

os.chdir(tempfile.gettempdir())

# sys.path.append(os.path.join(os.environ['CGPIPELINE'], "python", "python27", "lib", "site-packages"))
from _lib import processVariables

soft = sys.argv[1]

# Cahce system environments
if soft == "houdini":
    processVariables.updateInitSystemEnvs()

print("starting " + soft + "...")

__import__("wrapper." + soft)
