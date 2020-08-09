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
        return self.taskManager.getActiveProject()

    def updateStatus(self, status, items=[], refresh=True, multipleItems=False):
        if not items:
            items = self.itemUtils.getSelected_ProcessItems(multipleItems)
            if not items:
                return

        items = items if isinstance(items, list) else [items]
        data = {}
        for item in items:
            data[item.data(0, Qt.UserRole)] = {"status": status}
        tacticPostUtils.updateMultipleSobjects(self.taskManager.userServerCore.server, data)
        if refresh:
            self.taskManager.refreshTaskData()

    def autoInProgressStatus(self, selectedItem):
        itemStatus = selectedItem.text(1)
        if itemStatus in ["Ready to start"]:
            messageDialog = QMessageBox(text='Do you want to get start?', parent=self.taskManager)
            messageDialog.setStyleSheet("QPushButton{ width:60px; font-size: 15px; }")
            messageDialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            confirm = messageDialog.exec_()
            if confirm == QMessageBox.Yes:
                self.updateStatus('In Progress', [selectedItem])
        else:
            self.taskManager.refreshTaskData()

    def runSoft(self):
        selectedItem = self.itemUtils.getSelected_ProcessItems()
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

        # ======================= CONNECTS ===============================
        self.completeButton.clicked.connect(lambda: self.updateStatus('Revise'))
        self.openButton.clicked.connect(self.runSoft)

        # ======================= LAYOUT SETUP ===============================
        self.lay_activeButtons.addWidget(self.openButton)
        self.lay_activeButtons.addWidget(self.completeButton)


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

        # ======================= CONNECTS ===============================
        self.rejectButton.clicked.connect(lambda: self.updateStatus('Pending'))
        self.acceptButton.clicked.connect(lambda: self.updateStatus('Review'))
        self.openButton.clicked.connect(self.runSoft)

        # ======================= LAYOUT SETUP ===============================
        self.lay_activeButtons.addWidget(self.rejectButton)
        self.lay_activeButtons.addWidget(self.acceptButton)
        self.lay_activeButtons.addWidget(self.openButton)


class activeButtons_coordinator(activeButtonsTM):

    def __init__(self, taskManager, treeWidget):
        super(activeButtons_coordinator, self).__init__(taskManager, treeWidget)

        self.lay_activeButtons = QHBoxLayout()

        # ======================= BUTTONS ===============================
        # self.openButton = QPushButton("Open")
        # self.openButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        self.rejectButton = QPushButton('Reject')
        self.rejectButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.rejectButton.setMinimumSize(50, 50)
        # self.completeButton.setStyleSheet("QPushButton {background-color:#525353;}")

        self.acceptButton = QPushButton('Approved :-)')
        self.acceptButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.acceptButton.setMinimumSize(50, 50)

        # ======================= CONNECTS ===============================
        self.rejectButton.clicked.connect(lambda: self.updateStatus('Pending', multipleItems=True))
        self.acceptButton.clicked.connect(lambda: self.updateStatus('Approved :-)', multipleItems=True))
        # self.openButton.clicked.connect(self.runSoft)

        # ======================= LAYOUT SETUP ===============================
        self.lay_activeButtons.addWidget(self.rejectButton)
        self.lay_activeButtons.addWidget(self.acceptButton)
        # self.lay_activeButtons.addWidget(self.openButton)
