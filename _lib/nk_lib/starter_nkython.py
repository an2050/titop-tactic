import os
from subprocess import Popen, PIPE
import json


def initNKScene(nkfile, keyPrjData, extraJobData, nukeLocation, mainNkData):
    data = {"nkFile": nkfile, "keyPrjData": keyPrjData, "extraJobData": extraJobData, "mainNkData": mainNkData}
    data = json.dumps(data).encode()

    initScenePy = "/".join([os.path.dirname(__file__), "initNKScene.py"])

    nkython = "/".join([nukeLocation, "python.exe"])

    command = " ".join([nkython, initScenePy])

    process = Popen(command, stdin=PIPE)
    print("=> nkython bridge process...")
    process.communicate(input=data)

