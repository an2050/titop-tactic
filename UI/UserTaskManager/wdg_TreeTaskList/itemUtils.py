from PySide2.QtWidgets import QInputDialog
from PySide2.QtCore import Qt

from _lib import configUtils


class ItemUtils(object):

    def __init__(self, treeWidget):
        self.treeWidget = treeWidget
        self.tacticElements = configUtils.tacticKeyElements
        self.tacticAssetElement = configUtils.tacticAssetElement

    def getSelected_ProcessItems(self, getMultiple=False):
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
            if getMultiple:
                lst.insert(0, 'all')

            i, ok = QInputDialog().getItem(self.treeWidget, "Dialog Title", "Lable:", lst, 0, False)

            if not ok:
                return
            elif i == 'all':
                return [selectedItem.child(idx) for idx in range(selectedItem.childCount())]
            else:
                idx = lst.index(i)
                return selectedItem.child(idx)

        elif selectedItem.childCount() == 1:
            return selectedItem.child(0)
        else:
            return selectedItem

    def getSelected_shotItems(self):

        def compareShotAssetType(item):
            shotType = self.tacticElements['shot']
            assetType = self.tacticAssetElement['asset']
            itemSKey = item.data(0, Qt.UserRole)
            return itemSKey.find(shotType) >= 0 or itemSKey.find(assetType) >= 0

        selectedItems = self.treeWidget.selectedItems()
        try:
            if len(selectedItems) == 1 and compareShotAssetType(selectedItems[0].parent()):
                return [selectedItems[0].parent()]
        except AttributeError:
            pass

        episodes = list(filter(lambda x: x.data(0, Qt.UserRole).find(self.tacticElements['episode']) >= 0, selectedItems))
        if len(episodes) > 0:
            items = []
            for episod in episodes:
                items += [episod.child(x) for x in range(episod.childCount()) if compareShotAssetType(episod.child(x))]

            allSelectedShots = list(filter(lambda x: compareShotAssetType(x), selectedItems))
            return list(set(items + allSelectedShots))
        else:
            return list(filter(lambda x: compareShotAssetType(x), selectedItems))
