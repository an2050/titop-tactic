from PySide2.QtCore import Qt


def getKeyPrjData(projectName, selectedItem):
    keyPrjData = {'project': None, 'episod': None, 'shot': None}
    keyPrjData["project"] = projectName

    if selectedItem.data(0, Qt.UserRole).find('task') >= 0:
        selectedItem = selectedItem.parent()

    if selectedItem.parent() is not None:
        keyPrjData['episod'] = selectedItem.parent().text(0)
        keyPrjData['shot'] = selectedItem.text(0)
    else:
        keyPrjData['episod'] = selectedItem.text(0)

    return keyPrjData


def getItemTaskData(selectedItem, keyPrjData):
    depth = len([x for x in keyPrjData.values() if x is not None])
    if depth == 3:
        keyTaskData = {"assetName": selectedItem.text(0), "task": selectedItem.text(0)}
    else:
        keyTaskData = {"assetName": selectedItem.parent().text(0), "task": selectedItem.text(0)}
    return keyTaskData
