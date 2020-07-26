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
from UI.UserTaskManager.utils import treeDataUtils

# from UI.UserTaskManager.utils import itemsUtils

from _lib import configUtils
from _lib.tactic_lib import tacticServerData, tacticDataProcess

import activeButtons
import rvButtons

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

        self.userLable = QLabel(self)
        self.userLable.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        self.userLable.setText("User:")
        self.userButton = QPushButton("user")
        # self.userNameField = QLineEdit(self)
        # self.userNameField.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # - filters
        self.filterShotField = QLineEdit(self)
        self.filterShotField.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.filterStatus_comboBox = QComboBox(self)
        self.filterStatus_comboBox.setMinimumSize(150, 25)
        # self.filterStatus_comboBox.setFocusPolicy(Qt.StrongFocus)
        # -
        self.filterShot_Lable = QLabel(self)
        self.filterShot_Lable.setText("Shot:")
        self.filterShot_Lable.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.filterStatus_Lable = QLabel(self)
        self.filterStatus_Lable.setText("    Status:")
        self.filterStatus_Lable.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.project_comboBox = QComboBox(self)
        self.project_comboBox.setMinimumSize(150, 20)
        self.project_comboBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # ======================= BUTTONS ===============================
        self.refreshButton = QPushButton('Refresh')
        self.refreshButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # ======================= UTILS ===============================
        # self.itemsUtils = itemsUtils.ItemsUtils(self)

        # ======================= CONNECTS ===============================
        self.userButton.clicked.connect(self.changeUser)
        self.treeWidget.currentItemChanged.connect(self.treeItemChanged)

        # self.userNameField.editingFinished.connect(self.changedUser_lineEdit)
        self.refreshButton.clicked.connect(self.refreshTaskDataButton)
        self.project_comboBox.currentIndexChanged.connect(self.changedProject_dorpList)

        self.filterShotField.textChanged.connect(self.filterShot)
        self.filterStatus_comboBox.currentTextChanged.connect(self.filterStatusProcess)

        # ======================= LAYOUT SETUP ===============================
        self.lay_main.addLayout(self.lay_leftVertical)
        self.lay_main.addLayout(self.lay_rightVertical)

        self.lay_leftVertical.addLayout(self.lay_upLeftHorizontal)
        self.lay_leftVertical.addLayout(self.lay_upLeftHorizontal_2)
        self.lay_leftVertical.addWidget(self.treeWidget)

        self.lay_upLeftHorizontal.addWidget(self.project_comboBox)
        self.lay_upLeftHorizontal.addWidget(self.refreshButton)
        self.lay_upLeftHorizontal.addWidget(self.userLable)
        self.lay_upLeftHorizontal.addWidget(self.userButton)
        # self.lay_upLeftHorizontal.addWidget(self.userNameField)

        self.lay_upLeftHorizontal_2.addWidget(self.filterShot_Lable)
        self.lay_upLeftHorizontal_2.addWidget(self.filterShotField)
        self.lay_upLeftHorizontal_2.addWidget(self.filterStatus_Lable)
        self.lay_upLeftHorizontal_2.addWidget(self.filterStatus_comboBox)
        self.lay_upLeftHorizontal_2.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))

# ====================================================
# ====================================================
        self.activeButtons = activeButtons.activeButtonsTM(self, self.treeWidget)
        self.lay_rightVertical.addLayout(self.activeButtons.lay_activeButtons)

        self.rvButtons = rvButtons.rvButtonsTM(self, self.treeWidget)
        self.lay_rightVertical.addLayout(self.rvButtons.lay_rvButtons)

        self.commentBlock = CommentBlockWidget(self, self.treeWidget)
        self.lay_rightVertical.addLayout(self.commentBlock.lay_main)

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

    def initializeWidgetData(self):
        self.userButton.setText(self.userServerCore.userName + " (" + self.userFunction + ")")
        self.settProjectList_comboBox()
        self.refreshUserTaskData()
        self.setStatusList_comboBox()
        self.commentBlock.server = self.userServerCore.server

# ===========Fill Project & Status drop down lists =======================================
    def settProjectList_comboBox(self):
        self.project_comboBox.blockSignals(True)
        projectsData = self.userServerCore.getProjecstData()
        self.clearCombobBoxWidgetList(self.project_comboBox)
        activeProject = configUtils.loadConfigData(taskManagerConfigFile).get("activeProject")
        prjList = sorted(projectsData, key=lambda x: x.get('code') != activeProject)
        [self.project_comboBox.addItem(prjItem.get('title'), prjItem.get('code')) for prjItem in prjList]
        self.currentProject = {"title": self.project_comboBox.currentText(), "code": self.project_comboBox.currentData()}
        self.userServerCore.server.set_project(self.currentProject.get('code'))
        self.project_comboBox.blockSignals(False)

    def setStatusList_comboBox(self):
        self.filterStatus_comboBox.blockSignals(True)
        self.clearCombobBoxWidgetList(self.filterStatus_comboBox)
        statusList = list()
        self.filterStatus_comboBox.addItems(["--no filter"] + self.getStatusList(self.userServerCore.taskData, statusList))
        self.filterStatus_comboBox.blockSignals(False)

    def getStatusList(self, data, statusList=[]):
        for element in data:
            if element.get('children') is not None:
                self.getStatusList(element['children'], statusList)
            elif element.get("status") is not None:
                statusList += [element['status']]
        return list(set(statusList))

# ===================== Connects ==========================
    def clearCombobBoxWidgetList(self, comboBoxWidget):
        prjCount = comboBoxWidget.count()
        while prjCount > 0:
            comboBoxWidget.removeItem(0)
            prjCount -= 1

    def changeUser(self):
        self.userServerCore.connectToServer(resetTicket=True)
        self.userFunction = userServerCore.userData[0].get('function')
        self.initializeWidgetData()

    def changedProject_dorpList(self):
        self.currentProject = {"title": self.project_comboBox.currentText(), "code": self.project_comboBox.currentData()}
        self.refreshUserTaskData()
        configData = configUtils.loadConfigData(taskManagerConfigFile)
        configData["activeProject"] = self.currentProject.get('code')
        configUtils.saveConfigData(taskManagerConfigFile, configData)

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
        # self.userServerCore.refreshNotesData()
        try:
            selectedItem = self.treeWidget.selectedItems()[0]
        except IndexError:
            return
        self.completeNoteList(selectedItem)

    def refreshTaskDataButton(self):
        self.setStatusList_comboBox()
        self.refreshUserTaskData(True)

    def refreshUserTaskData(self, resetFilter=False):
        isTaskData = self.userFunction == "Artist"
        # print("CURRETN PROJECT = ", self.currentProject.get('code'))
        self.userServerCore.resetProjectData(self.currentProject.get('code'), isTaskData)
        userTaskData = self.userServerCore.taskData

        self.treeWidget.pipelineData = self.userServerCore.pipelineData
        self.treeWidget.project = self.currentProject.get('code')

        if userTaskData is not None:
            if resetFilter:
                self.treeWidget.treeIndexItem = []
                self.filterShotField.setText("")
                self.treeWidget.shotFilter = ""
                # self.treeWidget.completeTree(userTaskData)
            # else:
                # self.filterTreeByStatus()
            self.completeTree()
        else:
            self.treeWidget.clear()

# =============== Filters =============================
    # def filterShot(self, text):
    #     self.treeWidget.blockSignals(True)
    #     # self.treeWidget.treeIndexItem = []
    #     self.filterTreeByStatus()
    #     self.treeWidget.blockSignals(False)

    # def filterStatusProcess(self):
    #     self.treeWidget.treeIndexItem = []
    #     self.filterTreeByStatus()

    # def filterTreeByStatus(self):
    #     data = self.userServerCore.taskData
    #     if self.filterStatus_comboBox.currentText() == "--no filter" or self.filterStatus_comboBox.currentText() == "":
    #         filteredData = data
    #     else:
    #         # filteredData = self.filteredByStatusData(data)
    #         filteredData = self.filterTreeData(data, "status", self.filterStatus_comboBox.currentText())
    #         treeData = treeDataUtils.filterTreeData(data, "status", self.filterStatus_comboBox.currentText()) 
    #     self.treeWidget.completeTree(filteredData, filterItems=True, filterElement=self.filterShotField.text())

    def filterShot(self, text):
        # self.treeWidget.blockSignals(True)
        self.treeWidget.shotFilter = text
        self.completeTree()
        # self.treeWidget.blockSignals(False)

    def filterStatusProcess(self):
        self.completeTree()

    def completeTree(self, text=""):
        treeData = self.userServerCore.taskData
        status = self.filterStatus_comboBox.currentText()
        if status != "--no filter" and status != "":
            treeData = treeDataUtils.filterTreeData(treeData, "status", status)
        self.treeWidget.completeTree(treeData)


    # def filterTreeData(self, data, field, value):
    #     filteredData = []

    #     for element in data:
    #         element = dict(element)
    #         if element.get('children'):
    #             children = self.filterTreeData(element['children'], field, value)
    #             element['children'] = children
    #             filteredData.append(element)

    #         elif element.get(field) == value:
    #             filteredData.append(element)

    #         if element.get('children') is not None:
    #             if len(element['children']) == 0:
    #                 idx = filteredData.index(element)
    #                 filteredData.pop(idx)
    #     return filteredData
    # def filteredByStatusData(self, data):
    #     filteredData = []

    #     for element in data:
    #         element = dict(element)
    #         if element.get('children'):
    #             children = self.filteredByStatusData(element['children'])
    #             element['children'] = children
    #             filteredData.append(element)

    #         elif element.get('status') == self.filterStatus_comboBox.currentText():
    #             filteredData.append(element)

    #         if element.get('children') is not None:
    #             if len(element['children']) == 0:
    #                 idx = filteredData.index(element)
    #                 filteredData.pop(idx)
    #     return filteredData

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
