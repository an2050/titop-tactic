import os
import sys

sys.path = list(set(sys.path + [os.path.join(os.environ['CGPIPELINE'])]))

from pathlib import Path
# import getpass

from PySide2.QtWidgets import *
from PySide2.QtCore import Qt

from UI.UserTaskManager.wdg_TreeTaskList import treeTaskList, treeTaskList_supervisor
# from UI.UserTaskManager.wdg_TreeTaskList.treeWidgetTaskList import TreeTaskList
# from UI.UserTaskManager.wdg_Comments.tableCommentList import TableCommentList
from UI.UserTaskManager.wdg_Comments.CommentBlockWidget import CommentBlockWidget
from UI.UserTaskManager.wdg_Filters import FiltersBlockWidget
from UI.UserTaskManager.utils import treeDataUtils

# from UI.UserTaskManager.utils import itemsUtils

from _lib import configUtils
from _lib.tactic_lib import tacticServerData, tacticDataProcess

from . import rvButtons
from . import activeButtons
# import rvButtons

taskManagerConfigFile = Path(__file__).parent / "config.json"
styleCSS = Path(__file__).parent.parent.parent / "css" / "style.css"
tacticConfigFile = configUtils.tacticConfigFile

pythonExe = os.path.join(configUtils.pythonDir, "python27", "python.exe")
starterPath = [pythonExe, configUtils.starterPath]


class UserTaskWidget(QWidget):

    def __init__(self, userServerCore, parent=None):
        super(UserTaskWidget, self).__init__(parent)

        self.userServerCore = userServerCore
        self.userFunction = userServerCore.userData[0].get('function')
        self.currentProject = {}

        self.resize(1280, 720)
        self.setStyleSheet(open(styleCSS).read())

        # Layouts
        self.lay_main = QHBoxLayout(self)
        self.setLayout(self.lay_main)
        self.lay_leftVertical = QVBoxLayout()
        self.lay_rightVertical = QVBoxLayout()
        self.lay_upLeftHorizontal = QHBoxLayout()
        self.lay_upLeftHorizontal_2 = QHBoxLayout()
        self.lay_grpBoxVertical = QVBoxLayout()

        # ======================= WIDGETS ===============================
        self.setTreeTaskWidget()

        # ======================= BUTTONS ===============================
        # ======================= UTILS ===============================

        # ======================= CONNECTS ===============================
        self.treeWidget.currentItemChanged.connect(self.treeItemChanged)

        # ======================= LAYOUT SETUP ===============================
        self.lay_main.addLayout(self.lay_leftVertical)
        self.lay_main.addLayout(self.lay_rightVertical)

        self.lay_leftVertical.addLayout(self.lay_upLeftHorizontal)
        self.lay_leftVertical.addLayout(self.lay_upLeftHorizontal_2)
        self.lay_leftVertical.addWidget(self.treeWidget)

        self.filtersBlock = FiltersBlockWidget.FiltersBlockWidget(self)
        self.lay_leftVertical.insertLayout(1, self.filtersBlock.lay_main)
# ====================================================
# ====================================================
        self.activeButtons = self.setActiveButtons()
        self.lay_rightVertical.addLayout(self.activeButtons.lay_activeButtons)

        self.rvButtons = rvButtons.rvButtonsTM(self, self.treeWidget)
        self.lay_rightVertical.addLayout(self.rvButtons.lay_rvButtons)

        self.commentBlock = CommentBlockWidget(self, self.treeWidget)
        self.lay_rightVertical.insertLayout(3, self.commentBlock.lay_main)

# ====================================================
# ====================================================

        configUtils.checkAndCreateConfigFile(taskManagerConfigFile)
        self.treeWidget.taskManagerConfigFile = taskManagerConfigFile

# ========================================================================================
        self.initializeWidgetData()

# ========================================================================================

    def setTreeTaskWidget(self):
        if self.userFunction == 'Artist':
            self.treeWidget = treeTaskList.TreeTaskList(self)
        else:
            self.treeWidget = treeTaskList_supervisor.TreeTaskList_supervisor(self)

    def setActiveButtons(self):
        if self.userFunction == 'Artist':
            return activeButtons.activeButtons_artist(self, self.treeWidget)
        else:
            return activeButtons.activeButtons_supervisor(self, self.treeWidget)

    def initializeWidgetData(self):
        self.filtersBlock.setUserButtonText(self.userServerCore.userName + " (" + self.userFunction + ")")
        self.filtersBlock.settProjectList_comboBox()
        self.refreshTaskData()
        self.filtersBlock.setStatusList_comboBox()
        self.filtersBlock.setUserList_comboBox()
        self.filtersBlock.setProcessList_comboBox()
        self.commentBlock.server = self.userServerCore.server

# ===========Fill Project & Status drop down lists =======================================
    def getProjectsData(self):
        return self.userServerCore.getProjectsData()

    def getAllPrjUsers(self):
        return self.userServerCore.allUsers

    def getProcessList(self):
        return self.userServerCore.processList

    def setUserFunction(self):
        self.userFunction = self.userServerCore.userData[0].get('function')

    def setCurrentProject(self, code, title):
        self.currentProject = {"code": code, "title": title}

    def setServerProject(self, project):
        self.userServerCore.server.set_project(project)
        self.userServerCore.activeProject = project

    def saveActiveProject(self, project):
        configData = configUtils.loadConfigData(taskManagerConfigFile)
        configData["activeProject"] = project
        configUtils.saveConfigData(taskManagerConfigFile, configData)

    def loadActiveProject(self):
        activeProject = configUtils.loadConfigData(taskManagerConfigFile).get("activeProject")
        return activeProject

# ===================== Connects ==========================
    def clearCombobBoxWidgetList(self, comboBoxWidget):
        prjCount = comboBoxWidget.count()
        while prjCount > 0:
            comboBoxWidget.removeItem(0)
            prjCount -= 1

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
        self.userServerCore.refreshNotesData(self.currentProject.get('code'))
        try:
            selectedItem = self.treeWidget.selectedItems()[0]
        except IndexError:
            return
        self.completeNoteList(selectedItem)

    def refreshTaskData(self, resetFilter=False):
        isTaskData = self.userFunction == "Artist"
        # print("CURRETN PROJECT = ", self.currentProject.get('code'))
        self.userServerCore.resetProjectData(self.currentProject.get('code'), isTaskData)
        userTaskData = self.userServerCore.taskData

        self.treeWidget.pipelineData = self.userServerCore.pipelineData
        self.treeWidget.project = self.currentProject.get('code')

        if userTaskData is not None:
            if resetFilter:
                self.treeWidget.treeIndexItem = []
                self.filtersBlock.filterShotField.setText("")
                self.treeWidget.shotFilter = ""
                # self.treeWidget.completeTree(userTaskData)
            # else:
                # self.filterTreeByStatus()
            # self.filtersBlock.settProjectList_comboBox()
            self.completeTree()
            self.filtersBlock.setStatusList_comboBox()
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
        # self.treeWidget.completeTree(treeData)

        process = self.filtersBlock.filterProcess_comboBox.currentText()
        if process != "--no filter" and process != "":
            treeData = treeDataUtils.filterTreeData(treeData, "process", process)
        self.treeWidget.completeTree(treeData)


    def collectExtraJobData(self, selectedItem):
        extraDataDict = {}
        extraDataDict['frames'] = self.getFramesCount(selectedItem)
        return extraDataDict

    def getFramesCount(self, selectedItem):
        # selectedItem = itemsUtils.getSelected_ProcessItem(self)
        searchKey = selectedItem.parent().data(0, Qt.UserRole)
        currentElementData = tacticDataProcess.getTaskElementBySearchField(self.userServerCore.taskData, "__search_key__", searchKey)
        # frame_in = currentElementData.get("frame_in")
        # frame_out = currentElementData.get("frame_out")
        frame_in = currentElementData.get("tc_frame_start")
        frame_out = currentElementData.get("tc_frame_end")
        if frame_in is not None and frame_out is not None:
            return frame_out - frame_in + 1
        else:
            return 0


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
