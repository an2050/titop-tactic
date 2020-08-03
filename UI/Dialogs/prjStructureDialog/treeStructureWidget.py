import os
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor

from UI.Dialogs import treeWdg_utils
from _lib import configUtils


class TreeStructureWidget(QTreeWidget):

    def __init__(self, parent):
        super(TreeStructureWidget, self).__init__(parent)

        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.SortOrder(0))
        self.headerItem().setHidden(True)
        self.setAlternatingRowColors(1)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.callContextMenu)

    def addNewItem(self):
        if not self.selectedItems():
            parent = self.invisibleRootItem()
        else:
            parent = self.selectedItems()[0]

        item = QTreeWidgetItem()
        item.setText(0, r"{folderName}")
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
        parent.addChild(item)
        item.setExpanded(True)

    def removeItem(self):
        for item in self.selectedItems():
            parent = item.parent()
            parent = self.invisibleRootItem() if parent is None else parent
            parent.removeChild(item)

    def completTreeData(self):
        path = "/".join([os.path.dirname(__file__), "treeData.json"])
        treeData = configUtils.loadConfigData(path)
        if treeData:
            treeWdg_utils.completeTree(self, treeData, editable=True)
            treeWdg_utils.expandAllTree(self)

    def saveTreeData(self):
        treeData = treeWdg_utils.collectTreeData(self)
        path = "/".join([os.path.dirname(__file__), "treeData.json"])
        configUtils.saveConfigData(path, treeData)

    def saveProjectStructureConfigData(self):
        structData = treeWdg_utils.getSimpleStructureData(self)
        configPath = configUtils.projectStructureConfigFile
        configUtils.saveConfigData(configPath, structData)

    def callContextMenu(self, pos):
        menu = QMenu(parent=self)
        menu.addAction('Add Folder', self.addNewItem)
        menu.addAction('Remove Folder', self.removeItem)
        menu.exec_(QCursor.pos())
