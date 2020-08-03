import os
import sys
from pathlib import Path
from PySide2.QtWidgets import *

sys.path = list(set(sys.path + [os.path.join(os.environ['CGPIPELINE'])]))

from UI.Dialogs.newProjectDialog import CreateNewProjectDialog
from UI.Dialogs.prjStructureDialog import PrjSturctureDialog

from UI.UserTaskManager.wdg_TaskManager.UserTaskManager import UserTaskWidget

from _lib.tactic_lib import tacticServerData  # , tacticPostUtils, tacticDataProcess

styleCSS = Path(__file__).parent.parent / "css" / "style.css"


class MainWindowWidget(QMainWindow):
    """docstring for MainWindowWidget"""

    def __init__(self, userServerCore):
        super(MainWindowWidget, self).__init__()

        self.setStyleSheet(open(styleCSS).read())
        self.userServerCore = userServerCore

        self.centralTaskManager = UserTaskWidget(self.userServerCore, parent=self)
        self.setCentralWidget(self.centralTaskManager)

        # Menu bar
        self.menuBar = QMenuBar()
        self.fileMenu = self.menuBar.addMenu('File')
        self.settingsMenu = self.menuBar.addMenu('Settings')
        # Action NewProject
        self.act_newProject = self.fileMenu.addAction("New Project", self.createNewProject)
        self.act_projectStruct = self.settingsMenu.addAction("Project structure", self.openProjectStructure)
        self.setMenuBar(self.menuBar)

    def createNewProject(self):
        login = self.userServerCore.userData[0].get("login")
        admin = self.userServerCore.isAdmin
        if not admin:
            return
        # templateProjectList = self.userServerCore.getTemplateProjectList()
        createProjectDialog = CreateNewProjectDialog.NewProjectDialog(self, self.userServerCore)
        result = createProjectDialog.exec_()

        # print(result)

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
