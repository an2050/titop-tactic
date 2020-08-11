# import os
from pathlib import Path

from PySide2.QtWidgets import *
from PySide2.QtCore import Qt

from UI.UserTaskManager.wdg_TreeTaskList import treeTaskList, treeTaskList_admins
from UI.UserTaskManager.wdg_Comments.CommentBlockWidget import CommentBlockWidget
from UI.UserTaskManager.wdg_Filters import FiltersBlockWidget, filtersBlockWidget_admin
from UI.UserTaskManager.utils import treeDataUtils

from _lib import configUtils
from _lib.tactic_lib import tacticServerData, tacticDataProcess

from . import rvButtons
from . import activeButtons

taskManagerConfigFile = Path(__file__).parent / "config.json"
# styleCSS = Path(__file__).parent.parent.parent / "css" / "style.css"
# tacticConfigFile = configUtils.tacticConfigFile

# pythonExe = os.path.join(configUtils.pythonDir, "python27", "python.exe")
# starterPath = [pythonExe, configUtils.starterPath]


class UserTaskWidget(QWidget):

    def __init__(self, mainWindow, userServerCore):
        super(UserTaskWidget, self).__init__(mainWindow)

        self.mainWindow = mainWindow

        self.userServerCore = userServerCore
        self.userPosition = "no position"
        self.currentProject = {}

        # self.setStyleSheet(open(styleCSS).read())

        # Layouts
        self.lay_main = QHBoxLayout(self)
        self.setLayout(self.lay_main)

        self.leftMainWidget = QWidget(self)
        self.leftMainWidget.setMinimumSize(440, 520)
        self.leftMainWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.lay_leftVertical = QVBoxLayout()
        self.leftMainWidget.setLayout(self.lay_leftVertical)

        self.rightMainWidget = QWidget(self)
        self.rightMainWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.rightMainWidget.setMinimumSize(440, 520)
        self.lay_rightVertical = QVBoxLayout()
        self.rightMainWidget.setLayout(self.lay_rightVertical)

        # ======================= WIDGETS ===============================
        self.setUserPositionWidgets()
        self.rvButtons = rvButtons.rvButtonsTM(self, self.treeWidget)
        self.commentBlock = CommentBlockWidget(self, self.treeWidget)

        # ======================= CONNECTS ===============================
        self.treeWidget.currentItemChanged.connect(self.treeItemChanged)

        # ======================= LAYOUT SETUP ===============================
        self.lay_leftVertical.addLayout(self.filtersBlock.lay_main)
        self.lay_leftVertical.addWidget(self.treeWidget)

        self.lay_rightVertical.addLayout(self.activeButtons.lay_activeButtons)
        self.lay_rightVertical.addLayout(self.rvButtons.lay_rvButtons)
        self.lay_rightVertical.insertLayout(3, self.commentBlock.lay_main)

        self.lay_main.addWidget(self.leftMainWidget)
        self.lay_main.addWidget(self.rightMainWidget)
# ====================================================
        configUtils.checkAndCreateConfigFile(taskManagerConfigFile)
        self.treeWidget.taskManagerConfigFile = taskManagerConfigFile
# ========================================================================================
        self.initializeWidgetData()
# ========================================================================================

    def setUserPositionWidgets(self):
        self.setUserPosition()

        if self.userPosition == 'Supervisor':
            self.filtersBlock = FiltersBlockWidget.FiltersBlockWidget(self)
            self.treeWidget = treeTaskList_admins.TreeTaskList_supervisor(self)
            self.activeButtons = activeButtons.activeButtons_supervisor(self, self.treeWidget)

        elif self.userPosition == 'Coordinator':
            self.filtersBlock = FiltersBlockWidget.FiltersBlockWidget(self)
            self.treeWidget = treeTaskList_admins.TreeTaskList_coordinator(self)
            self.activeButtons = activeButtons.activeButtons_coordinator(self, self.treeWidget)

        else:
            self.filtersBlock = filtersBlockWidget_admin.FiltersBlockWidget_admin(self)
            self.treeWidget = treeTaskList.TreeTaskList(self)
            self.activeButtons = activeButtons.activeButtons_artist(self, self.treeWidget)

            self.mainWindow.menuBar.setVisible(False)

    def initializeWidgetData(self):
        self.treeWidget.clear()
        self.filtersBlock.setUserButtonText(self.userServerCore.userName + " (" + self.userPosition + ")")
        self.filtersBlock.settProjectList_comboBox()

# ===========Fill Project & Status drop down lists =======================================
    def getServerObj(self):
        return self.userServerCore.server

    def getProjectsData(self):
        return self.userServerCore.getProjectsData()

    def getUserProjects(self):
        return self.userServerCore.getUserProjects()

    def getAllPrjUsers(self):
        return self.userServerCore.allUsers

    def getProcessList(self):
        return self.userServerCore.activeProcessesList

    def getProcessesData(self):
        return self.userServerCore.processesData

    def getActiveProject(self):
        return self.userServerCore.activeProject.get('code')

    def setUserPosition(self):
        userPosition = self.userServerCore.userData[0].get('user_position')
        self.userPosition = userPosition if userPosition else 'no position'

    def setServerProject(self, project):
        self.userServerCore.setServerProject(project)

    def saveActiveProject(self, project):
        configData = configUtils.loadConfigData(taskManagerConfigFile)
        configData["activeProject"] = project
        configUtils.saveConfigData(taskManagerConfigFile, configData)

    def loadActiveProject(self):
        activeProject = configUtils.loadConfigData(taskManagerConfigFile).get("activeProject")
        return activeProject

# ===================== Connects ==========================
    def clearCombobBoxWidgetList(self, comboBoxWidget):
        comboBoxWidget.blockSignals(True)
        prjCount = comboBoxWidget.count()
        while prjCount > 0:
            comboBoxWidget.removeItem(0)
            prjCount -= 1
        comboBoxWidget.blockSignals(False)

    def treeItemChanged(self, current, previous):
        if current is None:
            return None
        elementData = tacticDataProcess.getTaskElementBySearchField(self.userServerCore.taskData, "__search_key__", current.data(0, Qt.UserRole))
        # elementData = tacticDataProcess.getTaskElementBySearchKey(self.userServerCore.taskData, current.data(0, Qt.UserRole))
        description_lable = tacticDataProcess.filterElementsData([elementData], fields=["description"])
        # self.description_lable.setText(description_lable[0]['description'])

        self.completeNoteList(current)
        self.commentBlock.setDescriptionText(description_lable[0]['description'])
        # note = tacticDataProcess.getNotesElement(current.data(0, Qt.UserRole), self.userServerCore.taskData, self.userServerCore.notesData)
        # self.commentBlock.completeTableList(note)
        # self.refreshCommentData()
        # self.commentBlock.clearTextDialogField()
        self.treeWidget.treeIndexItem = self.treeWidget.getTreeIndexItem(current)

# ===========================================================
    def completeNoteList(self, selectedItem):
        itemSkey = selectedItem.data(0, Qt.UserRole)
        note = tacticDataProcess.getNotesElement(itemSkey, self.userServerCore.taskData, self.userServerCore.notesData)
        self.commentBlock.completeTableList(note, itemSkey)

    def refreshCommentData(self):
        self.userServerCore.refreshNotesData()
        try:
            selectedItem = self.treeWidget.selectedItems()[0]
        except IndexError:
            print("Comment data cannot updates, no selected items.")
            return
        self.completeNoteList(selectedItem)

    def refreshTaskData(self, resetFilter=False):
        isAllData = self.userPosition in ["Coordinator", "Supervisor"]
        self.userServerCore.resetProjectData(isAllData)
        userTaskData = self.userServerCore.taskData

        self.treeWidget.pipelineData = self.userServerCore.pipelineData

        if userTaskData is not None:
            if resetFilter:
                self.treeWidget.treeIndexItem = []
                self.filtersBlock.filterShotField.setText("")
                self.treeWidget.shotFilter = ""

            self.completeTree()
            self.filtersBlock.setStatusList_comboBox()
            self.filtersBlock.setUserList_comboBox()
            self.filtersBlock.setProcessList_comboBox()

        else:
            self.treeWidget.clear()

    def completeTree(self):
        treeData = self.userServerCore.taskData

        status = self.filtersBlock.filterStatus_comboBox.currentText()
        if status != "--no filter" and status != "":
            treeData = treeDataUtils.filterTreeData(treeData, "status", status)

        user = self.filtersBlock.filterUser_comboBox.currentText()
        if user != "--no filter" and user != "":
            treeData = treeDataUtils.filterTreeData(treeData, "assigned", user)

        process = self.filtersBlock.filterProcess_comboBox.currentText()
        if process != "--no filter" and process != "":
            treeData = treeDataUtils.filterTreeData(treeData, "process", process)
        self.treeWidget.completeTree(treeData)

    def collectExtraJobData(self, selectedItem):
        extraDataDict = {}
        extraDataDict['frames'] = self.getFramesCount(selectedItem)
        return extraDataDict

    def getFramesCount(self, selectedItem):
        searchKey = selectedItem.parent().data(0, Qt.UserRole)
        currentElementData = tacticDataProcess.getTaskElementBySearchField(self.userServerCore.taskData, "__search_key__", searchKey)
        framesCount = currentElementData.get('frames_count')
        if not framesCount:
            return 100
        else:
            return framesCount


if __name__ == "__main__":
    app = QApplication()
    app.setStyle(QStyleFactory.create("Fusion"))

    userServerCore = tacticServerData.userServerCore()
    if userServerCore.connectToServer():
        taskManager = UserTaskWidget(userServerCore)
        taskManager.show()
    app.exec_()


def userTaskWindow(parent=None):
    window = UserTaskWidget(parent)
    return window
