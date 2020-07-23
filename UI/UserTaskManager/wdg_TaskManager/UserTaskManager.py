import os
import sys

sys.path = list(set(sys.path + [os.path.join(os.environ['CGPIPELINE'])]))

from pathlib import Path
import getpass

from PySide2.QtWidgets import *
from PySide2.QtCore import Qt

from UI.UserTaskManager.wdg_TreeTaskList.treeWidgetTaskList import TreeTaskList
# from UI.UserTaskManager.wdg_Comments.tableCommentList import TableCommentList
from UI.UserTaskManager.wdg_Comments.CommentBlockWidget import CommentBlockWidget
from UI.CredentialWindow import CredentialtWindow

from UI.UserTaskManager.utils import itemsUtils

from _lib import configUtils
from _lib.tactic_lib import tacticServerData, tacticDataProcess

import activeButtons
import rvButtons

taskManagerConfigFile = Path(__file__).parent / "config.json"
styleCSS = Path(__file__).parent.parent.parent / "css" / "style.css"
tacticConfigFile = configUtils.tacticConfigFile

pythonExe = os.path.join(configUtils.pythonDir, "python27", "python.exe")
starterPath = [pythonExe, configUtils.starterPath]

# sysUserName = getpass.getuser()
# password = "123"




class UserTaskWidget(QWidget):

    def __init__(self, parent=None):
        super(UserTaskWidget, self).__init__(parent)

        self.project = ""
        self.currentProject = {}

        self.resize(1280, 720)

        self.setStyleSheet(open(styleCSS).read())

        # Layouts
        lay_main = QHBoxLayout(self)
        self.setLayout(lay_main)
        self.lay_leftVertical = QVBoxLayout()
        self.lay_rightVertical = QVBoxLayout()
        self.lay_upLeftHorizontal = QHBoxLayout()
        self.lay_upLeftHorizontal_2 = QHBoxLayout()
        self.lay_grpBoxVertical = QVBoxLayout()

        # ======================= WIDGETS ===============================
        # - tree task widget
        self.treeWidget = TreeTaskList(self)

        self.userLable = QLabel(self)
        self.userLable.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        self.userLable.setText("User:")
        self.userNameField = QLineEdit(self)
        self.userNameField.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        # self.userNameField.setText(sysUserName)
        # - filters
        self.filterShotField = QLineEdit(self)
        self.filterShotField.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.filterStatus_comboBox = QComboBox(self)
        self.filterStatus_comboBox.setMinimumSize(150, 25)
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
        self.itemsUtils = itemsUtils.ItemsUtils(self)

        # ======================= CONNECTS ===============================
        self.treeWidget.currentItemChanged.connect(self.treeItemChanged)

        self.userNameField.editingFinished.connect(self.changedUser_lineEdit)
        self.refreshButton.clicked.connect(self.refreshTaskDataButton)
        self.project_comboBox.currentIndexChanged.connect(self.changedProject_dorpList)

        self.filterShotField.textChanged.connect(self.filterShot)
        self.filterStatus_comboBox.currentTextChanged.connect(self.filterStatusProcess)

        # ======================= LAYOUT SETUP ===============================
        lay_main.addLayout(self.lay_leftVertical)
        lay_main.addLayout(self.lay_rightVertical)

        self.lay_leftVertical.addLayout(self.lay_upLeftHorizontal)
        self.lay_leftVertical.addLayout(self.lay_upLeftHorizontal_2)
        self.lay_leftVertical.addWidget(self.treeWidget)

        self.lay_upLeftHorizontal.addWidget(self.project_comboBox)
        self.lay_upLeftHorizontal.addWidget(self.refreshButton)
        self.lay_upLeftHorizontal.addWidget(self.userLable)
        self.lay_upLeftHorizontal.addWidget(self.userNameField)

        self.lay_upLeftHorizontal_2.addWidget(self.filterShot_Lable)
        self.lay_upLeftHorizontal_2.addWidget(self.filterShotField)
        self.lay_upLeftHorizontal_2.addWidget(self.filterStatus_Lable)
        self.lay_upLeftHorizontal_2.addWidget(self.filterStatus_comboBox)
        self.lay_upLeftHorizontal_2.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))

# ====================================================
# ====================================================
        self.activeButtons = activeButtons.activeButtonsTM(self)
        self.lay_rightVertical.addLayout(self.activeButtons.lay_activeButtons)

        self.rvButtons = rvButtons.rvButtonsTM(self)
        self.lay_rightVertical.addLayout(self.rvButtons.lay_rvButtons)

        self.commentBlock = CommentBlockWidget(self)
        self.lay_rightVertical.addLayout(self.commentBlock.lay_main)

# ====================================================
# ====================================================

        configUtils.checkAndCreateConfigFile(taskManagerConfigFile)
        self.treeWidget.taskManagerConfigFile = taskManagerConfigFile
        # self.treeWidget.styleCSS = styleCSS

        # self.setConnection()

    def setConnection(self):
        self.userServerCore = tacticServerData.userServerCore()
        self.userServerCore.connectToServer()

    def initializeWidgetData(self):
        # if self.userServerCore.server:
        self.userNameField.setText(self.userServerCore.userName)

        self.settProjectList_comboBox()
        # self.refreshUserTaskData()
        self.setStatusList_comboBox()
        self.commentBlock.server = self.userServerCore.server
            # return True
        # else:
            # self.project_comboBox.addItems(["no connection to server"])
            # return False

# ========================================================================================
    # def getCredentialData(self):
    #     credentialData = {}
    #     credential = CredentialtWindow.CredentialDialog(self)
    #     accepted = credential.exec_()
    #     if accepted:
    #         credentialData = credential.getData()
    #         return credentialData


    def getServerIp(self):
        configData = configUtils.loadConfigData(tacticConfigFile)
        if configData is None:
            return ""
        return configUtils.loadConfigData(tacticConfigFile).get("serverIp")

# ===========Fill Project & Status drop down lists =======================================
    def settProjectList_comboBox(self):
        self.project_comboBox.blockSignals(True)
        projectsData = self.userServerCore.getProjecstData()
        self.clearCombobBoxWidgetList(self.project_comboBox)

        prjList = tacticDataProcess.filterElementsData(projectsData, [("status", None)], fields=["title", "code"])
        activeProject = configUtils.loadConfigData(taskManagerConfigFile).get("activeProject")
        prjList = sorted(prjList, key=lambda x: x.get('code') != activeProject)
        [self.project_comboBox.addItem(prjItem.get('title'), prjItem.get('code')) for prjItem in prjList]

        self.currentProject = {"title": self.project_comboBox.currentText(), "code": self.project_comboBox.currentData()}
        # print(self.currentProject)
        # print(self.project_comboBox.currentData())
        self.project_comboBox.blockSignals(False)
        #     self.project_comboBox.addItems(["no connection to server"])
        # else:
        # prjList = [(prj.get('title'), prj.get('__search_key__')) for prj in prjList]
        # print(prjList)
        # self.project_comboBox.addItems(prjList)
        # self.project = self.project_comboBox.currentText()


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
# ==============================================================

# ===================== Connects ==========================
    def changedUser_lineEdit(self):
        self.project_comboBox.blockSignals(True)
        self.clearCombobBoxWidgetList(self.project_comboBox)
        self.treeWidget.clear()

        typedName = self.userNameField.text()
        if typedName != sysUserName:
            self.userNameField.blockSignals(True)
            typedPassword, ok = QInputDialog().getText(self, "", "Password:", QLineEdit.Password)
            self.userNameField.blockSignals(False)

            if ok:
                self.userServerCore.userName = typedName
                self.userServerCore.password = typedPassword
                self.userServerCore.project = None
                self.userServerCore.connectToServer()
                if self.userServerCore.connected is False:
                    print("Login/Password incorrect")
                    return None
            else:
                return None
        else:
            self.userServerCore.password = password
            self.userServerCore.userName = sysUserName
            self.userServerCore.connectToServer()
        self.settProjectList_comboBox()
        self.refreshUserTaskData()
        self.project_comboBox.blockSignals(False)

    def changedProject_dorpList(self):
        # self.userServerCore.project = self.project_comboBox.currentText()
        self.refreshUserTaskData()

        configData = configUtils.loadConfigData(taskManagerConfigFile)
        configData["activeProject"] = self.project_comboBox.currentData()
        configUtils.saveConfigData(taskManagerConfigFile, configData)

    def treeItemChanged(self, current, previous):
        if current is None:
            return None
        elementData = tacticDataProcess.getTaskElementBySearchKey(self.userServerCore.taskData, current.data(0, Qt.UserRole))
        description_lable = tacticDataProcess.filterElementsData([elementData], fields=["description"])
        # self.description_lable.setText(description_lable[0]['description'])

        self.completeNoteList(current)
        self.commentBlock.setDescriptionText(description_lable[0]['description'])
        # note = tacticDataProcess.getNotesElement(current.data(0, Qt.UserRole), self.userServerCore.taskData, self.userServerCore.notesData)
        # self.commentBlock.completeTableList(note)
        # self.refreshCommentData()
        # self.commentBlock.clearTextDialogField()
        self.treeWidget.treeIndexItem = self.treeWidget.getTreeIndexItem(current)
# ==============================================================

    def completeNoteList(self, selectedItem):
        itemSkey = selectedItem.data(0, Qt.UserRole)
        note = tacticDataProcess.getNotesElement(itemSkey, self.userServerCore.taskData, self.userServerCore.notesData)
        self.commentBlock.completeTableList(note, itemSkey)

    def clearCombobBoxWidgetList(self, comboBoxWidget):
        prjCount = comboBoxWidget.count()
        while prjCount > 0:
            comboBoxWidget.removeItem(0)
            prjCount -= 1

    # def completeTaskTree():
    #     self.treeWidget.completeTree(self.userServerCore.taskData)

    # def refreshPipelineData(self):
    #     self.filterTreeByStatus()

    def refreshCommentData(self):
        self.userServerCore.refreshNotesData()
        # self.userServerCore.refreshNotesData()
        try:
            selectedItem = self.treeWidget.selectedItems()[0]
        except IndexError:
            return
        self.completeNoteList(selectedItem)

    def refreshTaskDataButton(self):
        self.refreshUserTaskData(True)
        self.setStatusList_comboBox()

    def refreshUserTaskData(self, resetFilter=False):
        self.userServerCore.serverIp = self.getServerIp()
        self.userServerCore.userName = self.userNameField.text()

        if self.project_comboBox.currentText() == "no connection to server":
            self.clearCombobBoxWidgetList(self.project_comboBox)
            self.userServerCore.project = None
            self.userServerCore.connectToServer()
            self.settProjectList_comboBox()

        self.userServerCore.project = self.project_comboBox.currentText()
        # self.userServerCore.connectToServer()
        if self.userServerCore.connected:
            self.userServerCore.refreshTaskData(self.project_comboBox.currentData())

            userTaskData = self.userServerCore.taskData
            print(userTaskData, "========================================")

            # self.treeWidget.taskData = userTaskData
            self.treeWidget.pipelineData = self.userServerCore.pipelineData
            self.treeWidget.project = self.userServerCore.project

            if userTaskData is not None:
                if resetFilter:
                    self.treeWidget.treeIndexItem = []
                    self.filterShotField.setText("")
                    self.treeWidget.completeTree(userTaskData)
                else:
                    self.filterTreeByStatus()
            else:
                self.treeWidget.clear()

# =============== Filters =============================
    def filterShot(self, text):
        self.treeWidget.blockSignals(True)
        self.treeWidget.treeIndexItem = []
        self.filterTreeByStatus()
        self.treeWidget.blockSignals(False)

    def filterStatusProcess(self):
        self.treeWidget.treeIndexItem = []
        self.filterTreeByStatus()

    def filterTreeByStatus(self):
        data = self.userServerCore.taskData
        if self.filterStatus_comboBox.currentText() == "--no filter" or self.filterStatus_comboBox.currentText() == "":
            filtratedData = data
        else:
            filtratedData = self.filteredByStatusData(data)
        self.treeWidget.completeTree(filtratedData, filterItems=True, filterElement=self.filterShotField.text())

    def filteredByStatusData(self, data):
        filtratedData = []

        for element in data:
            element = dict(element)
            if element.get('children'):
                children = self.filteredByStatusData(element['children'])
                element['children'] = children
                filtratedData.append(element)

            elif element.get('status') == self.filterStatus_comboBox.currentText():
                filtratedData.append(element)

            if element.get('children') is not None:
                if len(element['children']) == 0:
                    idx = filtratedData.index(element)
                    filtratedData.pop(idx)
        return filtratedData

    def collectExtraJobData(self, selectedItem):
        extraDataDict = {}
        extraDataDict['frames'] = self.getFramesCount(selectedItem)
        return extraDataDict

    def getFramesCount(self, selectedItem):
        # selectedItem = itemsUtils.getSelected_ProcessItem(self)
        searchKey = selectedItem.parent().data(0, Qt.UserRole)
        currentElementData = tacticDataProcess.getTaskElementBySearchKey(self.userServerCore.taskData, searchKey)
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

    taskManager = UserTaskWidget()
    taskManager.setConnection()
    if taskManager.userServerCore.connected:
        taskManager.initializeWidgetData()
        taskManager.show()

    app.exec_()


def userTaskWindow(parent=None):
    window = UserTaskWidget(parent)
    return window
