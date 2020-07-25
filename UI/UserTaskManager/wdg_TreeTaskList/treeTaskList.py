# import os
import re
from pathlib import Path
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor, QColor

from _lib import configUtils

from _lib.tactic_lib import tacticDataProcess

from . import itemUtils

taskManagerConfigFile = Path(__file__).parent.parent / "config.json"

class TreeTaskList(QTreeWidget):

    def __init__(self, taskManagerWdg):
        super(TreeTaskList, self).__init__(taskManagerWdg)

        self.taskManagerWdg = taskManagerWdg

        self.project = ""
        self.taskData = []
        self.allUsers = []
        self.pipelineData = []
        # taskManagerConfigFile = ""
        # self.styleCSS = ""
        self.treeIndexItem = []

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setColumnCount(3)
        self.setHeaderLabels(["Task", "Status", "User"])
        self.setColumnWidth(0, 200)
        self.setColumnWidth(1, 200)
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(1)

        # ======================= CONNECTS ===============================
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.callContextMenu)

        # ======================= UTILS ===============================
        self.itemUtils = itemUtils.ItemUtils(self)

    def completeTree(self, data, filterItems=False, filterElement=""):
        self.allUsers = self.taskManagerWdg.userServerCore.allUsers
        # self.createUsersComboBox(self.taskManagerWdg.userServerCore.allUsers)
        # print("TREE DATA = ", data)
        self.blockSignals(True)
        self.clear()
        if filterItems:
            self.addTreeItemFilter(data, filterElement)
            self.removeWaste()
        else:
            self.addTreeItem(data)
        self.sortItems(0, Qt.AscendingOrder)

        isExpanded = configUtils.loadConfigData(taskManagerConfigFile).get("treeExpand")
        if isExpanded:
            self.expandAllTree()
        else:
            self.collapseAllTree()

        self.setSelectedItem()
        self.blockSignals(False)

    def createUsersComboBox(self):
        usersData = self.allUsers
        users_combobox = QComboBox(self)
        [users_combobox.addItem(user.get('login'), user.get('function')) for user in usersData]
        return users_combobox

    def addTreeItem(self, data, parent=None):
        if parent is None:
            parent = self.invisibleRootItem()
        for dataItem in data:
            item = QTreeWidgetItem()

            if dataItem.get('children'):
                item.setText(0, dataItem['name'])
                item.setData(0, Qt.UserRole, dataItem.get('__search_key__'))
                self.addTreeItem(dataItem['children'], parent=item)
            else:
                item.setData(0, Qt.UserRole, dataItem.get('__search_key__'))
                item.setText(0, dataItem['process'])
                item.setText(1, dataItem['status'])
                # item.setText(2, dataItem['assigned'])


                statusColor = tacticDataProcess.getStatusColor(self.pipelineData, self.project,
                                                               dataItem['process'], dataItem['status'])
                if statusColor is not None:
                    item.setForeground(1, QColor(statusColor[0] + "DC" + statusColor[1:]))

            parent.addChild(item)
            self.setItemWidget(item, 2, self.createUsersComboBox())
            item.setExpanded(True)

    def addTreeItemFilter(self, data, filterElement, parent=None, haveParent=False):
        matchParent = True
        matchItem = True
        rootItem = self.invisibleRootItem()

        if parent is None:
            finalParent = rootItem
        elif haveParent:
            finalParent = parent
        else:
            matchParent = self.checkMatchPattern(parent.text(0), filterElement)
            finalParent = parent if matchParent else rootItem

        for dataItem in data:
            item = QTreeWidgetItem()

            if dataItem.get('children'):
                item.setText(0, dataItem['name'])
                matchItem = self.checkMatchPattern(item.text(0), filterElement)
                if matchItem:
                    finalParent = parent if parent is not None else finalParent
                else:
                    finalParent = rootItem
                    haveParent = False
                    matchParent = False

                if finalParent is not rootItem:
                    matchItem = True
                    haveParent = True

                item.setData(0, Qt.UserRole, dataItem.get('__search_key__'))
                self.addTreeItemFilter(dataItem['children'], filterElement, parent=item, haveParent=haveParent)
            elif matchParent:
                item.setData(0, Qt.UserRole, dataItem.get('__search_key__'))
                item.setText(0, dataItem['process'])
                item.setText(1, dataItem['status'])
                # item.setText(2, dataItem['assigned'])
                # self.setItemWidget(item, 1, self.createUsersComboBox())

                statusColor = tacticDataProcess.getStatusColor(self.pipelineData, self.project,
                                                               dataItem['process'], dataItem['status'])
                if statusColor is not None:
                    item.setForeground(1, QColor(statusColor[0] + "DC" + statusColor[1:]))

            finalParent.addChild(item)
            item.setExpanded(True)

    def checkMatchPattern(self, text, pattern):
        pattern = pattern.replace("*", ".*")
        pattern = r".*" + pattern + r".*"
        correctPattern = False
        while correctPattern is False:
            try:
                result = re.match(pattern, text, flags=re.IGNORECASE)
            except re.error as err:
                pattern = pattern[:err.pos] + "\\" + pattern[err.pos:]
            else:
                correctPattern = True

        return result

    def removeWaste(self):
        parent = self.invisibleRootItem()
        for idx in range(parent.childCount()):
            topItem = parent.child(idx)
            if topItem.childCount() == 0:
                parent.removeChild(topItem)
                self.removeWaste()
                break

    def expandAllTree(self, parent=None):
        if parent is None:
            parent = self.invisibleRootItem()

        childrenCount = parent.childCount()
        for idx in range(childrenCount):
            item = parent.child(idx)
            item.setExpanded(True)
            if item.childCount() > 0:
                self.expandAllTree(item)
        # self.setSelectedItem()

        configData = configUtils.loadConfigData(taskManagerConfigFile)
        configData["treeExpand"] = True
        configUtils.saveConfigData(taskManagerConfigFile, configData)

    def collapseAllTree(self, parent=None):
        if parent is None:
            parent = self.invisibleRootItem()

        childrenCount = parent.childCount()
        for idx in range(childrenCount):
            item = parent.child(idx)
            if item.parent() is None:
                item.setExpanded(True)
            else:
                item.setExpanded(False)
            if item.childCount() > 0:
                self.collapseAllTree(item)
        # self.setSelectedItem()

        configData = configUtils.loadConfigData(taskManagerConfigFile)
        configData["treeExpand"] = False
        configUtils.saveConfigData(taskManagerConfigFile, configData)

    def getTreeIndexItem(self, selectedItem):
        root = self.invisibleRootItem()
        parent = None

        treeIndxItem = []
        item = selectedItem
        while parent is not root:
            parent = item.parent()
            if parent is None:
                parent = root
            treeIndxItem.insert(0, parent.indexOfChild(item))
            item = parent
        return treeIndxItem

    def setSelectedItem(self):
        item = None
        treeIndexItem = self.treeIndexItem
        parent = self.invisibleRootItem()
        for i in treeIndexItem:
            if parent.childCount() < i + 1:
                return
            item = parent.child(i)
            parent = item

        if item is not None:
            self.setCurrentItem(item)

    def callContextMenu(self, pos):
        menu = QMenu(parent=self)
        # menu.addAction("run", self.runSoft)
        menu.addAction('expand All', self.expandAllTree)
        menu.addAction('collapse All', self.collapseAllTree)
        menu.exec_(QCursor.pos())
# ===========================================

# if __name__ == "__main__":
#     app = QApplication()
#     # app.setStyle(QStyleFactory.create("Fusion"))
#     window = TreeTaskList()
#     window.show()
#     app.exec_()
