from PySide2.QtWidgets import *
from PySide2.QtCore import (Qt, QItemSelectionModel)
from PySide2.QtGui import QFont
import os

from _lib import configUtils, keyDataProjectUtils
class projectListWidget(QListWidget):
    """docstring for projectListWidget"""

    def __init__(self, arg):

        super(projectListWidget, self).__init__(arg)
        self.depthData = {"project": None, "episod": None, "shot": None}
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Widgets
        self.chkBox_showInactive = False
        self.chkBox_showAllFolder = False

        # Connects
        self.itemDoubleClicked.connect(self.changeDepth)
        self.updateList(self.depthData)

        self.inactiveFont = QFont()
        self.inactiveFont.setUnderline(True)
        self.inactiveFont.setPointSize(8)

    def updateList(self, depthData, depthIndx=0):
        newDepthData = dict(depthData)
        path = keyDataProjectUtils.getKeyPrjPath(newDepthData, depthIndx)
        if os.path.exists(path) is False:
            return None

        depthLevel = list(newDepthData.keys())[depthIndx]
        self.depthData = dict(newDepthData)
        self.clear()

        rootItem = QListWidgetItem("...")
        rootItem.setData(Qt.UserRole, "ROOT")
        self.addItem(rootItem)

        if depthIndx == 0:
            activeProjectsFilePath = configUtils.activeProjectsFile
            activeProjectsList = configUtils.loadConfigData(activeProjectsFilePath)
            if activeProjectsList is not None:
                self.fillProjectsView(path, newDepthData, depthLevel, activeProjectsList)
            else:
                self.fillOtherView(path, newDepthData, depthLevel)
        else:
            self.fillOtherView(path, newDepthData, depthLevel)

    def fillProjectsView(self, path, data, depthLevel, activeProjectsList):
        for element in os.listdir(path):
            data[depthLevel] = element
            item = QListWidgetItem(element)

            if (element in activeProjectsList) is False:
                if self.chkBox_showInactive is False:
                    continue
                else:
                    item.setFont(self.inactiveFont)

            item.setData(Qt.UserRole, data)
            self.addItem(item)

    def fillOtherView(self, path, data, depthLevel):
        for element in os.listdir(path):
            item = QListWidgetItem(element)

            if os.path.isfile(os.path.join(path, element)):
                continue
            if ("config.json" in os.listdir(os.path.join(path, element))) is False:
                if self.chkBox_showAllFolder is False:
                    continue
                else:
                    item.setFont(self.inactiveFont)

            data[depthLevel] = element
            item.setData(Qt.UserRole, data)
            self.addItem(item)

    def changeDepth(self, item):
        if(item.text() == "..."):
            self.upDir()
        else:
            self.diveIn(item)

    def diveIn(self, item):
        itemData = item.data(Qt.UserRole)
        itemData = dict(sorted(itemData.items(), key=lambda x: len(x[0]), reverse=True))  # Sort dict
        depthIndx = keyDataProjectUtils.getDepth(itemData)
        self.updateList(itemData, min(depthIndx, 2))

    def upDir(self):
        depth = keyDataProjectUtils.getDepth(self.depthData)
        depth = max(depth - 1, 0)
        keys = list(self.depthData.keys())[depth:]

        for k in keys:
            self.depthData[k] = None

        self.updateList(self.depthData, depth)

    def getSelectedItemData(self):
        try:
            itemDepthData = self.selectedItems()[0].data(Qt.UserRole)

            if(itemDepthData == "ROOT"):
                return False

            itemDepthData = sorted(itemDepthData.items(), key=lambda x: len(x[0]), reverse=True)
            return dict(itemDepthData)

        except IndexError:
            print("no selected items")
            return False

   
    def getItemConfig(self, item):
        itemDepthData = item.data(Qt.UserRole)
        if itemDepthData == "ROOT":
            return None
        itemDepthData = dict(sorted(itemDepthData.items(), key=lambda x: len(x[0]), reverse=True))
        path = keyDataProjectUtils.getKeyPrjPath(itemDepthData, nameInclude=True)
        return os.path.join(path, "config.json")

    def removeConfigFile(self):
        for item in self.selectedItems():
            filePath = self.getItemConfig(item)
            try:
                os.remove(filePath)
            except FileNotFoundError:
                pass

    def addConfiFile(self):
        for item in self.selectedItems():
            filePath = self.getItemConfig(item)
            if os.path.exists(filePath) is False:
                configUtils.saveConfigData(filePath, [])

    # def selectItem(self, item):
    #     self.updateDataInfo(item.data(Qt.UserRole))

 #    def updateDataInfo(self, data):
 #        info = """Project: {}
 # Episod: {}
 #   Shot: {}""".format(data['project'], data['episod'], data['shot'])
 #        self.info_label.setText(info)