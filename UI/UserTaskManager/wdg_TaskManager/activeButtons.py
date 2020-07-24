import json
import subprocess
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt
from _lib import configUtils
from UI.UserTaskManager.wdg_TreeTaskList.itemUtils import ItemUtils

compProcess = configUtils.tacticProcessElements['comp']

class activeButtonsTM():

    def __init__(self, taskManager, treeWidget):
        self.taskManager = taskManager
        self.treeWidget = treeWidget
        self.itemUtils = self.treeWidget.itemUtils

        self.lay_activeButtons = QVBoxLayout()

        # ======================= WIDGETS ===============================
        self.inProgressButton = QPushButton('In Progress')
        self.openButton = QPushButton("Let's go")
        self.openButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.openButton.setMinimumSize(5, 40)
        self.pendingButton = QPushButton('Pending')

        # ======================= CONNECTS ===============================
        self.openButton.clicked.connect(self.runSoft)
        self.pendingButton.clicked.connect(self.setPending)
        self.inProgressButton.clicked.connect(self.setInProgress)

        # ======================= LAYOUT SETUP ===============================
        self.lay_activeButtons.addWidget(self.inProgressButton)
        self.lay_activeButtons.addWidget(self.openButton)
        self.lay_activeButtons.addWidget(self.pendingButton)

    def getProjectName(self):
        return self.taskManager.currentProject.get('code')

    def setPending(self, item=None):
        self.updateStatus("Pending", item)

    def setInProgress(self, item=None):
        self.updateStatus("In Progress", item)

    def updateStatus(self, status, item=None):
        if item is None or item is False:
            item = self.itemUtils.getSelected_ProcessItem()
        if not item:
            return
        searchKey = item.data(0, Qt.UserRole)
        data = {"status": status}
        self.taskManager.userServerCore.updateTaskData(searchKey, data)
        self.taskManager.refreshUserTaskData()

    def autoInProgressStatus(self, selectedItem):
        itemStatus = selectedItem.text(1)
        if itemStatus in ["Ready to Start", "Assignment", "Rework"]:
            messageDialog = QMessageBox(text='Update to "In Progress" status?', parent=self.taskManager)
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

        keyPrjData = itemUtils.getKeyPrjData(self.getProjectName(), selectedItem)
        keyTaskData = itemUtils.getItemTaskData(selectedItem, keyPrjData)
        keyPrjData = json.dumps(keyPrjData)
        taskData = json.dumps(keyTaskData)
        extraJobData = json.dumps(self.taskManager.collectExtraJobData(selectedItem))

        # soft = '_nuke' if keyTaskData.get("task") == "comp" else 'houdini'
        soft = '_nuke' if keyTaskData.get("task") == compProcess else 'houdini'

        runArgs = [configUtils.py2exe, configUtils.starterPath] + [soft] + [keyPrjData] + [taskData] + [extraJobData]

        subprocess.Popen(runArgs, shell=True)  # , stdout=True,)

        self.autoInProgressStatus(selectedItem)
