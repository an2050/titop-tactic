import os
import sys
from PySide2.QtWidgets import *

sys.path = list(set(sys.path + [os.environ.get('CGPIPELINE')]))

from UI.Dialogs.newProjectDialog import CreateNewProjectDialog
from UI.Dialogs.prjStructureDialog import PrjSturctureDialog
from UI.Dialogs.updateDialog import UpdateDialog

from UI.UserTaskManager.wdg_TaskManager.UserTaskManager import UserTaskWidget

from _lib.tactic_lib import tacticServerData

from _lib import configUtils
styleCSS = "/".join([configUtils.rootPath, "UI", "css", "style.css"])


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
        self.act_udate = self.settingsMenu.addAction("Udate", self.openUpdateDialog)
        self.setMenuBar(self.menuBar)

        # ============ CENTRAL WIDGET ====================
        self.centralTaskManager = UserTaskWidget(self, self.userServerCore)
        self.setCentralWidget(self.centralTaskManager)

    def createNewProject(self):
        admin = self.userServerCore.isAdmin
        if not admin:
            return

        createProjectDialog = CreateNewProjectDialog.NewProjectDialog(self, self.userServerCore)
        createProjectDialog.exec_()

    def openProjectStructure(self):
        prjSturctureDialog = PrjSturctureDialog.ProjectStructureDialog(self)
        prjSturctureDialog.exec_()

    def openUpdateDialog(self):
        updateDialogWidget = UpdateDialog.UpdateDialog(self)
        updateDialogWidget.exec_()
        pass


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
