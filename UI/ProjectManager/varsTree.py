from PySide2.QtWidgets import *
from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor
from _lib import configUtils


class varsTreeWidget(QWidget):
    """docstring for varsTreeWidget"""

    def __init__(self, arg):
        super(varsTreeWidget, self).__init__(arg)

        # self.setMinimumSize(500,0)

        # Lyaouts
        lay_main = QVBoxLayout(self)
        self.setLayout(lay_main)
        lay_horizontal = QHBoxLayout()
        lay_horizontal.setAlignment(Qt.AlignLeft)

        # Tree Widget
        self.treeWidget = QTreeWidget(self)
        self.treeWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)  #.AdjustToContents)  # 

        self.treeWidget.setColumnCount(2)
        self.treeWidget.setHeaderLabels(["Key", "Value"])
        self.treeWidget.setColumnWidth(0, 300)
        self.treeWidget.setColumnWidth(1, 300)
        self.treeWidget.setDragDropMode(QAbstractItemView.InternalMove)
        self.treeWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)

        # Buttons
        self.buttonAdd = QPushButton("Add")
        self.buttonAdd.setMaximumSize(70, 40)
        # self.buttonRemove = QPushButton("Remove")
        # self.buttonRemove.setMaximumSize(70, 40)
        # self.buttonSave = QPushButton("Save")
        # self.buttonSave.setMaximumSize(70, 40)

        # Connects
        # self.treeWidget.customContextMenuRequested.connect(self.callContextMenu)
        self.buttonAdd.clicked.connect(self.addUserItem)
        # self.buttonRemove.clicked.connect(self.removeUserItem)

        # Layouts Setup
        lay_main.addWidget(self.treeWidget)
        # lay_horizontal.addWidget(self.buttonSave)
        lay_horizontal.addWidget(self.buttonAdd)
        # lay_horizontal.addWidget(self.buttonRemove)
        lay_main.addLayout(lay_horizontal)


    def completeTree(self, data):
        if isinstance(data, list) is False:
            data = [{"Config file contains the wrong data": ""}]

        self.treeWidget.clear()
        self.addTreeItem(data)
        # self.expandAllItems() === EXPAND TREE ===


    def addTreeItem(self, data, parent=None):
        if parent is None:
            parent = self.treeWidget.invisibleRootItem()

        for keyValItem in data:
            for k, v in keyValItem.items():
                item = QTreeWidgetItem()
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled )

                item.setText(0, k)
                if isinstance(v, list):
                    self.addTreeItem(v, item)
                else:
                    item.setText(1, v)
                parent.addChild(item)
                item.setExpanded(True)

    def expandAllItems(self, parent=None):
        parent = self.treeWidget.invisibleRootItem() if parent is None else parent
        childrenCount = parent.childCount()
        for childIndx in range(childrenCount):
            item = parent.child(childIndx)
            item.setExpanded(True)
            self.expandAllItems(item)

    def getVarsTreeData(self):
        return self.collectTreeData()

    def collectTreeData(self, parent=None):
        parent = self.treeWidget.invisibleRootItem() if parent is None else parent
        childrenCount = parent.childCount()
        collectData = []

        for childIndx in range(childrenCount):
            item = parent.child(childIndx)
            if item.childCount() > 0:
                collectData.append({item.text(0): self.collectTreeData(item)})  # [item.text(0)] = self.collectTreeData(item)
            else:
                collectData.append({item.text(0): item.text(1)})  # [item.text(0)] = item.text(1)
        return collectData

    def callContextMenu(self, configPath=None):
        menu = QMenu()

        menu.addAction("Add", self.addUserItem)
        menu.addAction("Remove", lambda : self.removeUserItem(configPath))
        menu.exec_(QCursor.pos())

    def addUserItem(self):
        parent = None
        try:
            parent = self.treeWidget.selectedItems()[0]
        except IndexError:
            pass

        dictData = [{"NEW_KEY": ""}]
        self.addTreeItem(dictData, parent)

    def removeUserItem(self, configPath):
        for item in self.treeWidget.selectedItems():
            parent = item.parent()
            parent = self.treeWidget.invisibleRootItem() if parent is None else parent
            parent.removeChild(item)

        if configPath is not None:
            self.saveConfigData(configPath)

    def saveConfigData(self, configPath):
        currTreeData = self.getVarsTreeData()
        configUtils.saveConfigData(configPath, currTreeData)