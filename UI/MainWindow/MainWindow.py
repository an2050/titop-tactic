import os
import sys
from pathlib import Path
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt

sys.path = list(set(sys.path + [os.path.join(os.environ['CGPIPELINE'])]))

from UI.Dialogs.newProjectDialog import CreateNewProjectDialog
from UI.Dialogs.prjStructureDialog import PrjSturctureDialog

from UI.UserTaskManager.wdg_TaskManager.UserTaskManager import UserTaskWidget

from _lib.tactic_lib import tacticServerData  # , tacticPostUtils, tacticDataProcess

styleCSS = Path(__file__).parent.parent / "css" / "style.css"


class MainWindowWidget(QMainWindow):
    def __init__(self, userServerCore):
        super(MainWindowWidget, self).__init__()

        self.setStyleSheet(open(styleCSS).read())
        self.userServerCore = userServerCore

        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # Menu bar
        self.menuBar = QMenuBar()
        self.fileMenu = self.menuBar.addMenu('File')
        self.settingsMenu = self.menuBar.addMenu('Settings')
        # Action NewProject
        self.act_newProject = self.fileMenu.addAction("New Project", self.createNewProject)
        self.act_projectStruct = self.settingsMenu.addAction("Project structure", self.openProjectStructure)
        self.setMenuBar(self.menuBar)

        # ============ CENTRAL WIDGET ====================
        self.centralTaskManager = UserTaskWidget(self, self.userServerCore)
        self.setCentralWidget(self.centralTaskManager)

    def createNewProject(self):
        # login = self.userServerCore.userData[0].get("login")
        admin = self.userServerCore.isAdmin
        if not admin:
            return
        # templateProjectList = self.userServerCore.getTemplateProjectList()
        createProjectDialog = CreateNewProjectDialog.NewProjectDialog(self, self.userServerCore)
        createProjectDialog.exec_()

    def openProjectStructure(self):
        prjSturctureDialog = PrjSturctureDialog.ProjectStructureDialog(self)
        prjSturctureDialog.exec_()


if __name__ == "__main__":
    app = QApplication()
    app.setStyle(QStyleFactory.create("Fusion"))

    userServerCore = tacticServerData.userServerCore()
    if userServerCore.connectToServer():
        MainWindowWidget = MainWindowWidget(userServerCore)
        MainWindowWidget.show()

    app.exec_()


# def userTaskWindow(parent=None):
#     window = UserTaskWidget(parent)
#     return window
