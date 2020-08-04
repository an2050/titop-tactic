import sys
import os

# libPath = os.path.join(os.environ['CGPIPELINE'], "_lib")
libPath = os.path.join(os.environ['CGPIPELINE'])
sys.path.append(libPath)

from PySide2.QtWidgets import *
from PySide2.QtCore import Qt

import central_widget
import dock_widget
import template_form

from _lib import configUtils, keyDataProjectUtils

styleCSS = os.path.join(os.path.dirname(__file__), "style.css")


class projectManagerWindow(QMainWindow):
    """docstring for projectManagerWindow"""

    def __init__(self):
        super(projectManagerWindow, self).__init__()

        # self.setStyleSheet(open(styleCSS).read())

        self.resize(1280, 720)

        # Main central Project Manager.
        self.centralProjetWidget = central_widget.centralWidget(self)
        self.setCentralWidget(self.centralProjetWidget)

        # Dock Widgets
        self.dockVarsManager = dock_widget.dockWidget(self, "Variables Manger")
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockVarsManager, Qt.Horizontal)

        # Widgets
        self.projectList = self.centralProjetWidget.projectListWidget
        self.tabWidget = self.dockVarsManager.tabWidget
        self.varsTreeWidgetTab0 = self.dockVarsManager.tabWidget.widget(0)
        self.varsTreeWidgetTab1 = self.dockVarsManager.tabWidget.widget(1)

        # Connects
        self.tabWidget.currentChanged.connect(self.completeTree)
        # self.tabWidget.currentChanged.connect(self.completeTree)
        self.projectList.itemClicked.connect(self.completeTree)

        self.varsTreeWidgetTab0.treeWidget.itemChanged.connect(self.changedItem)
        self.varsTreeWidgetTab1.treeWidget.itemChanged.connect(self.changedItem)
        self.varsTreeWidgetTab0.treeWidget.customContextMenuRequested.connect(self.callTreeContextMenu)
        self.varsTreeWidgetTab1.treeWidget.customContextMenuRequested.connect(self.callTreeContextMenu)

        # Extra Dialogs
        self.templateDialog = template_form.template_form(self)

        # Init functions
        self.completeTree()

        # Tool Bar
        self.toolBarSetup()

        self.centralProjetWidget.admin = True

    # TOOLBAR SETUP
    def toolBarSetup(self):
        self.toolBar = QToolBar(self)
        self.addToolBar(Qt.LeftToolBarArea, self.toolBar)

        dockEnvsAtcion = self.dockVarsManager.toggleViewAction()
        dockEnvsAtcion.setText("ENVS")
        self.toolBar.addAction(dockEnvsAtcion)

        self.toolBar.addAction("TMPL", self.openTemplateDialog)

    def callTreeContextMenu(self):
        index = self.tabWidget.currentIndex()
        varsTreeWidget = self.tabWidget.widget(index)
        varsTreeWidget.callContextMenu(self.getCurrentConfigPath())

    def changedItem(self, item):
        self.saveVariableConfig()

    def saveVariableConfig(self):
        configPath = self.getCurrentConfigPath()
        if configPath is None:
            return None
        currTreeData = self.getTreeData()
        configUtils.saveConfigData(configPath, currTreeData)

    def completeTree(self):
        configData = self.getCurrentConfigData()
        if configData is None:
            return None
        currTreeWidget = self.tabWidget.widget(self.tabWidget.currentIndex())
        currTreeWidget.completeTree(configData)

    def getCurrentConfigPath(self, index=None):
        index = self.tabWidget.currentIndex() if index is None else index
        if index == 1:
            selectedItemData = self.projectList.getSelectedItemData()
            if selectedItemData is False:
                return None
            configPath = keyDataProjectUtils.getKeyPrjPath(selectedItemData, nameInclude=True) + "/config.json"
        else:
            configPath = configUtils.mainProjectConfigFile
        return configPath

    def getCurrentConfigData(self, index=None):
        index = self.tabWidget.currentIndex() if index is None else index
        configPath = self.getCurrentConfigPath(index)
        if configPath is None:
            return None
        if os.path.exists(configPath):
            configData = configUtils.loadConfigData(configPath)
        else:
            configData = [{"Config file is not exists": ""}]
        return configData

    def getTreeData(self, index=None):
        index = self.tabWidget.currentIndex() if index is None else index
        currTreeWidget = self.tabWidget.widget(index)
        return currTreeWidget.getVarsTreeData()

    def openTemplateDialog(self):
        self.templateDialog.show()


if __name__ == "__main__":
    app = QApplication()
    window = projectManagerWindow()
    window.show()
    app.exec_()


# Function for CG Application
def getCentralWidget():
    w = central_widget.centralWidget()
    return w
