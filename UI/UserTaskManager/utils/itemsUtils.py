from PySide2.QtWidgets import QInputDialog
from PySide2.QtCore import Qt

from _lib import configUtils


class ItemsUtils(object):

    def __init__(self, userTaskWidget):
        self.userTaskWidget = userTaskWidget
        self.tacticElements = configUtils.tacticKeyElements
        self.treeWidget = self.userTaskWidget.treeWidget

    def getSelected_ProcessItem(self):
        try:
            selectedItem = self.treeWidget.selectedItems()[0]
        except IndexError:
            print("Error: none selected items!")
            return
        if selectedItem.parent() is None:
            print("Select a more specific item please!")
            return

        if selectedItem.childCount() > 1:
            lst = [selectedItem.child(x).text(0) for x in range(selectedItem.childCount())]
            i, ok = QInputDialog().getItem(self.userTaskWidget, "Dialog Title", "Lable:", lst, 0, False)
            if not ok:
                return None
            idx = lst.index(i)
            return selectedItem.child(idx)
        elif selectedItem.childCount() == 1:
            return selectedItem.child(0)
        else:
            return selectedItem

    def getSelected_shotItems(self):

        selectedItems = self.treeWidget.selectedItems()
        print(type(self.treeWidget))
        try:
            if len(selectedItems) == 1 and selectedItems[0].parent().data(0, Qt.UserRole).find(self.tacticElements['shots']) >= 0:
                return [selectedItems[0].parent()]
        except AttributeError:
            pass

        episodes = list(filter(lambda x: x.data(0, Qt.UserRole).find(self.tacticElements['episodes']) >= 0, selectedItems))
        if len(episodes) > 0:
            # Getting shots for all selected episodes
            items = []
            for episod in episodes:
                items += [episod.child(x) for x in range(episod.childCount()) if episod.child(x).data(0, Qt.UserRole).find(self.tacticElements['shots']) >= 0]
            # Gettin all selected shot items
            allSelectedShots = list(filter(lambda x: x.data(0, Qt.UserRole).find(self.tacticElements['shots']) >= 0, selectedItems))
            return list(set(items + allSelectedShots))

        else:
            return list(filter(lambda x: x.data(0, Qt.UserRole).find(self.tacticElements['shots']) >= 0, selectedItems))


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
