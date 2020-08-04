import os
import json
import subprocess
from pathlib import Path
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor

if __name__ == "__main__":
    import sys
    libPath = os.path.join(os.environ['CGPIPELINE'], "_lib")
    sys.path.append(libPath)

import projectList
from _lib import configUtils, keyDataProjectUtils

activeProjectsFile = Path(__file__).parent / "activeProjects.json"
print(activeProjectsFile)

pythonExe = os.path.join(configUtils.pythonDir, "python27", "python.exe")
starterPath = [pythonExe, configUtils.starterPath]
styleCSS = os.path.join(os.path.dirname(__file__), "style.css")


class centralWidget(QWidget):
    """docstring for centralWidget"""

    def __init__(self, arg=None):
        super(centralWidget, self).__init__(arg)

        # self.setStyleSheet(open(styleCSS).read())

        self.resize(720, 480)

        self.admin = False

        # Layouts
        self.lay_main = QVBoxLayout(self)
        self.lay_upBar = QHBoxLayout()

        # Widgets
        self.projectListWidget = projectList.projectListWidget(self)
        self.depthLabe = QLabel(self)
        self.chkBox_showInactive = QCheckBox("Show inactive projects", self)
        self.chkBox_showAllFolder = QCheckBox("Show all folders")

        # Connects
        self.projectListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.projectListWidget.customContextMenuRequested.connect(self.callContextMenu)
        self.projectListWidget.itemClicked.connect(self.setDepthLable)
        self.chkBox_showInactive.stateChanged.connect(self.updateActiveProjectList)
        self.chkBox_showAllFolder.stateChanged.connect(self.udpateAllProjectList)

        # Layout setup
        # self.lay_main.addWidget(self.btn_setActiveProjects)
        self.lay_upBar.addWidget(self.depthLabe)
        self.lay_upBar.addWidget(self.chkBox_showInactive)
        self.lay_upBar.addWidget(self.chkBox_showAllFolder)
        self.lay_main.addLayout(self.lay_upBar)
        self.lay_main.addWidget(self.projectListWidget)

    def updateActiveProjectList(self):
        chkBox_showInactive = self.chkBox_showInactive.isChecked()
        depthData = self.projectListWidget.depthData
        depthIndx = keyDataProjectUtils.getDepth(depthData)
        self.projectListWidget.chkBox_showInactive = chkBox_showInactive

        if depthIndx == 0:
            self.projectListWidget.updateList(depthData)

    def udpateAllProjectList(self):
        chkBox_showAllFolder = self.chkBox_showAllFolder.isChecked()
        depthData = self.projectListWidget.depthData
        depthIndx = keyDataProjectUtils.getDepth(depthData)
        self.projectListWidget.chkBox_showAllFolder = chkBox_showAllFolder
        self.projectListWidget.updateList(depthData, depthIndx)

    def setDepthLable(self, item):
        depthData = self.projectListWidget.depthData
        data = dict(depthData)

        depthIndx = keyDataProjectUtils.getDepth(data)
        k = list(data.keys())[depthIndx]
        data[k] = item.text()
        data = dict([k for k in data.items() if k[1] is not None])
        text = ""
        for k in data.keys():
            text += "/{}".format(data[k])
        self.depthLabe.setText(text)

    def callContextMenu(self, pos):
        menu = QMenu()

        # Actions
        menu.addAction("run", self.runSoft)

        if self.admin:
            menu.addSeparator()
            menu.addAction("addConfig", self.addConfigFile)
            menu.addAction("removeConfig", self.removeConfigFile)

            depthData = self.projectListWidget.depthData
            depth = keyDataProjectUtils.getDepth(depthData)
            if depth == 0:
                menu.addAction("Activate/Deactivate", self.setActive)

        menu.exec_(QCursor.pos())

    def addConfigFile(self):
        self.projectListWidget.addConfiFile()

    def removeConfigFile(self):
        dialog = QMessageBox()
        dialog.exec_()
        self.projectListWidget.removeConfigFile()

    def setActive(self):
        projectNameList = self.projectListWidget.selectedItems()

        filePath = activeProjectsFile
        data = configUtils.loadConfigData(filePath)
        data = [] if data is None else data

        for projectName in projectNameList:
            if projectName.text() in data:
                data.pop(data.index(projectName.text()))
            else:
                data.append(projectName.text())

            configUtils.saveConfigData(filePath, data)
            self.updateActiveProjectList()

    def runSoft(self):
        itemDepthData = self.projectListWidget.getSelectedItemData()
        # taskData = {"assetName": "asset1", "task": "lighting"}
        itemDepthData = json.dumps(itemDepthData)
        # taskData = json.dumps(taskData)
        runArgs = starterPath + ['houdini'] + [itemDepthData] # + [taskData]

        subprocess.Popen(runArgs, shell=True, stdout=True)

if __name__ == "__main__":
    app = QApplication()
    window = centralWidget()
    window.show()
    app.exec_()

