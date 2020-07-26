import json
import subprocess
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt
from _lib import configUtils
# from UI.UserTaskManager.wdg_TreeTaskList.itemUtils import ItemUtils
from UI.UserTaskManager.utils import projectUtils
from _lib.tactic_lib import tacticPostUtils

compProcess = configUtils.tacticProcessElements['comp']


class activeButtonsTM():

    def __init__(self, taskManager, treeWidget):
        self.taskManager = taskManager
        self.treeWidget = treeWidget
        self.itemUtils = self.treeWidget.itemUtils

    def getProjectName(self):
        return self.taskManager.currentProject.get('code')

    def updateStatus(self, status, item=None, refresh=True):
        if item is None or item is False:
            item = self.itemUtils.getSelected_ProcessItem()
        if not item:
            return
        searchKey = item.data(0, Qt.UserRole)
        data = {"status": status}

        # self.taskManager.userServerCore.updateTaskData(searchKey, data)
        tacticPostUtils.updateSobject(self.taskManager.userServerCore.server, searchKey, data)
        if refresh:
            self.taskManager.refreshUserTaskData()

    def autoInProgressStatus(self, selectedItem):
        itemStatus = selectedItem.text(1)
        # if itemStatus in ["Ready to Start", "Assignment", "Rework"]:
        if itemStatus in ["Assigned", "Pending"]:
            # messageDialog = QMessageBox(text='Update to "In Progress" status?', parent=self.taskManager)
            messageDialog = QMessageBox(text='Start work process?', parent=self.taskManager)
            messageDialog.setStyleSheet("QPushButton{ width:60px; font-size: 15px; }")
            messageDialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            confirm = messageDialog.exec_()
            if confirm == QMessageBox.Yes:
                self.setInProgress(selectedItem)
        else:
            self.taskManager.refreshUserTaskData()

    def runSoft(self):
        selectedItem = self.itemUtils.getSelected_ProcessItem()
        if selectedItem is None:
            return

        keyPrjData = projectUtils.getKeyPrjData(self.getProjectName(), selectedItem)
        keyTaskData = projectUtils.getItemTaskData(selectedItem, keyPrjData)
        keyPrjData = json.dumps(keyPrjData)
        taskData = json.dumps(keyTaskData)
        extraJobData = json.dumps(self.taskManager.collectExtraJobData(selectedItem))

        # soft = '_nuke' if keyTaskData.get("task") == "comp" else 'houdini'
        soft = '_nuke' if keyTaskData.get("task") == compProcess else 'houdini'
        runArgs = [configUtils.py2exe, configUtils.starterPath] + [soft] + [keyPrjData] + [taskData] + [extraJobData]
        subprocess.Popen(runArgs, shell=True)  # , stdout=True,)
        self.autoInProgressStatus(selectedItem)


class activeButtons_artist(activeButtonsTM):

    def __init__(self, taskManager, treeWidget):
        super(activeButtons_artist, self).__init__(taskManager, treeWidget)

        self.lay_activeButtons = QHBoxLayout()

        # ======================= BUTTONS ===============================
        self.openButton = QPushButton("Let's go")
        self.openButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.openButton.setMinimumSize(50, 50)

        self.completeButton = QPushButton('Complete')
        self.completeButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.completeButton.setMinimumSize(50, 50)
        # self.completeButton.setStyleSheet("QPushButton {background-color:#525353;}")

        # ======================= CONNECTS ===============================
        self.completeButton.clicked.connect(self.setComplete)
        # self.inProgressButton.clicked.connect(self.setInProgress)
        self.openButton.clicked.connect(self.runSoft)

        # ======================= LAYOUT SETUP ===============================
        # self.lay_activeButtons.addWidget(self.inProgressButton)
        self.lay_activeButtons.addWidget(self.openButton)
        self.lay_activeButtons.addWidget(self.completeButton)

    def setComplete(self, item=None):
        self.updateStatus("Revise", item)

    def setInProgress(self, item=None):
        self.updateStatus("In Progress", item)


class activeButtons_supervisor(activeButtonsTM):

    def __init__(self, taskManager, treeWidget):
        super(activeButtons_supervisor, self).__init__(taskManager, treeWidget)

        self.lay_activeButtons = QHBoxLayout()

        # ======================= BUTTONS ===============================
        self.openButton = QPushButton("Open")
        self.openButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        self.rejectButton = QPushButton('Reject')
        self.rejectButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.rejectButton.setMinimumSize(50, 50)
        # self.completeButton.setStyleSheet("QPushButton {background-color:#525353;}")

        self.acceptButton = QPushButton('Accept')
        self.acceptButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.acceptButton.setMinimumSize(50, 50)

        # self.unassignButton = QPushButton('Unassign')
        # self.unassignButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        # self.acceptButton.setMinimumSize(50, 50)

        # ======================= CONNECTS ===============================
        self.rejectButton.clicked.connect(self.setReject)
        self.acceptButton.clicked.connect(self.setAccept)
        # self.unassignButton.clicked.connect(self.setUnassign)
        self.openButton.clicked.connect(self.runSoft)

        # ======================= LAYOUT SETUP ===============================
        self.lay_activeButtons.addWidget(self.rejectButton)
        # self.lay_activeButtons.addWidget(self.unassignButton)
        self.lay_activeButtons.addWidget(self.acceptButton)
        self.lay_activeButtons.addWidget(self.openButton)

    def setReject(self):
        self.updateStatus("Pending")

    def setAccept(self):
        self.updateStatus("Review")
