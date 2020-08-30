import os
import json
from subprocess import Popen, PIPE

from _lib import pathUtils, configUtils, sequenceUtils, exceptionUtils
from UI.Dialogs import simpleDialogs
from UI.UserTaskManager.utils import projectUtils


def raiseMessage(text):
    err = exceptionUtils.pathError()
    err.text = text
    err.displayMessageIcon()


def watchPrm(project, selectedItems):
    if len(selectedItems) == 0:
        return

    keyPrjData = projectUtils.getKeyPrjData(project, selectedItems[0])
    path = pathUtils.getPRM_Path(keyPrjData)
    try:
        catalogList = os.listdir(path)
    except FileNotFoundError:
        raiseMessage("Folder does not exists! : {}".format(path))
        return

    fileList = ["/".join([path, file]) for file in catalogList for item in selectedItems if file.lower().find(item.text(0).lower()) >= 0]

    if len(fileList) == 0:
        raiseMessage("prm not found!")
        return
    return runRvPlayer(fileList)


def watchDailies(project, selectedItems, annotate=False):
    func = pathUtils.getDailies_Path
    paths = getWatchPath(func, project, selectedItems)
    if paths is None:
        return

    filePaths = []
    for path in paths:
        try:
            filePaths += ["/".join([path, pathUtils.getVersioinFile(path, isFile=True, version=None)[0]])]
        except exceptionUtils.pathError as err:
            err.displayMessageIcon()
    if len(filePaths) > 0:
        return runRvPlayer(filePaths, annotate)


def watchHires(project, selectedItems, version=None, annotate=False):
    func = pathUtils.getHires_Path
    paths = getWatchPath(func, project, selectedItems, version)
    if paths is None:
        return
    seqPaths = collectSequencePath(paths)
    if len(seqPaths) > 0:
        return runRvPlayer(seqPaths, annotate)


def watchSRC(project, selectedItems):
    func = pathUtils.getSRC_Path
    paths = getWatchPath(func, project, selectedItems)
    if paths is None:
        return
    seqPaths = collectSequencePath(paths)
    if len(seqPaths) > 0:
        return runRvPlayer(seqPaths)


def watchPreview(project, selectedItem, annotate=False):
    if selectedItem is None:
        return

    keyPrjData = projectUtils.getKeyPrjData(project, selectedItem)
    keyTaskData = projectUtils.getItemTaskData(selectedItem, keyPrjData)

    filePath = None
    filePaths = []
    path = pathUtils.getJobOut_Path(keyPrjData, keyTaskData)
    try:
        filePath = "/".join([path, pathUtils.getVersioinFile(path, isFile=True, version=None)[0]])
        filePaths += [filePath] if filePath is not None else filePaths
    except exceptionUtils.pathError:
        pass
    try:
        folderPath = "/".join([path, pathUtils.getVersioinFile(path, isFile=False, version=None)[0]])
        seqList = list(sequenceUtils.getSequecneRepresentation(os.listdir(folderPath), countType='nuke').values())
        filePaths += ["/".join([folderPath, seq]) for seq in seqList] if len(seqList) > 0 else filePaths
    except exceptionUtils.pathError as err:
        err.displayMessageIcon()

    if len(filePaths) > 0:
        return runRvPlayer(filePaths, annotate)


def getWatchPath(func, project, selectedItems, version=None):
    if len(selectedItems) == 0:
        return []

    pathsList = []
    for item in selectedItems:
        keyPrjData = projectUtils.getKeyPrjData(project, item)
        if version is not None:
            path = func(keyPrjData, version)
        else:
            path = func(keyPrjData)
        pathsList += [path] if path else []

    return pathsList


def collectSequencePath(paths):
    seqPaths = []
    for path in paths:
        try:
            seqlist = list(sequenceUtils.getSequecneRepresentation(os.listdir(path), countType='nuke').values())
        except FileNotFoundError:
            seqlist = []
            exceptionUtils.pathError().displayMessageIcon("Folder does not exists! : {}".format(path))
        seqPaths += ["/".join([path, seq]) for seq in seqlist]
    return seqPaths


def runRvPlayer(paths, annotate=False):
    rvPlayerFolder = configUtils.rvPlayerPath

    expectedRVPath = rvPlayerFolder
    while not os.path.exists(rvPlayerFolder):
        dialog = simpleDialogs.PathFileDialog()
        text = f'RV Player not found!. \nRecomended path is: "{expectedRVPath}". \nPlease select the RV Player folder'
        rvPlayerFolder = dialog.showDialog(text)
        if rvPlayerFolder is None:
            return

    rvplayer = "/".join([rvPlayerFolder, "bin", "rvpush.exe"])
    rvplayer = '"'.join(["", rvplayer, ""])
    paths = ['"' + path + '"' for path in paths]
    command = " ".join([rvplayer] + [" -tag target merge"] + paths)
    rvProcess = Popen(command, stdout=PIPE, stderr=PIPE)

    print("Launching RV Player... ")
    # out = rvProcess.stdout.read()
    if annotate:
        out = rvProcess.stderr.read().decode('utf-8').strip().replace("\n", "")
        res = ""
        if "RESALT::" in out:
            start = out.find("::")
            end = out.find("}")
            res = out[start + 2: end + 1].strip()
            res = json.loads(res)
        return res
    # out, err = rvProcess.communicate()

    # print("OUT === ", out, "ERROR === ", err)
