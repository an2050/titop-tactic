import json
import subprocess
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt
from _lib import configUtils
from UI.UserTaskManager.utils import projectUtils
from UI.Dialogs import simpleDialogs
from _lib.tactic_lib import tacticPostUtils

from configUtils import tctProcessElements, tctStatusElements


class activeButtonsTM():
    def __init__(self, taskManager, treeWidget):
        self.taskManager = taskManager
        self.treeWidget = treeWidget
        self.itemUtils = self.treeWidget.itemUtils

    def changeStatus(self, prevStatuses, newStatus, multipleItems=False):
        selectedItems = self.itemUtils.getSelected_ProcessItems(multipleItems)
        if selectedItems is None:
            return

        if isinstance(selectedItems, list):
            itemStatus = selectedItems[0].text(1)
        else:
            itemStatus = selectedItems.text(1)
        if itemStatus in prevStatuses:
            self.updateStatus(newStatus, selectedItems)
        else:
            if self.statusConfirmDialog(itemStatus, newStatus):
                self.updateStatus(newStatus, selectedItems)

    def statusConfirmDialog(self, status, newStatus):
        msg = simpleDialogs.MessageDialog(self.taskManager)
        # textMsg = "Procedure not followed. Continue?"
        textInfo = "You change the status '{status}' to new status '{newStatus}'. Continue?".format(status=status, newStatus=newStatus)
        return msg.showDialog(textInfo, buttons=True)

    def updateStatus(self, status, items=[], refresh=None, multipleItems=False):
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
        elif refresh is None:
            msg = simpleDialogs.MessageDialog(self.taskManager)
            textMsg = "Do you want to refresh view?"
            if msg.showDialog(textMsg, buttons=True):
                self.taskManager.refreshTaskData()
        else:
            pass

    def autoInProgressStatus(self, selectedItem):
        itemStatus = selectedItem.text(1)
        if itemStatus in [tctStatusElements['readyToStart'],
                          tctStatusElements['pending']]:

            messageDialog = QMessageBox(text='Do you want to get start?', parent=self.taskManager)
            messageDialog.setStyleSheet("QPushButton{ width:60px; font-size: 15px; }")
            messageDialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            confirm = messageDialog.exec_()
            if confirm == QMessageBox.Cancel:
                return False
            elif confirm == QMessageBox.Yes:
                self.updateStatus(tctStatusElements['inProgress'], [selectedItem], refresh=False)
        return True

    def runSoft(self):
        selectedItem = self.itemUtils.getSelected_ProcessItems()
        if selectedItem is None:
            return

        currProject = self.taskManager.getActiveProject()
        keyPrjData = projectUtils.getKeyPrjData(currProject, selectedItem)
        taskData = projectUtils.getItemTaskData(selectedItem, keyPrjData)
        extraJobData = self.taskManager.collectExtraJobData(selectedItem)

        inputData = {}
        inputData['keyPrjData'] = keyPrjData
        inputData['taskData'] = taskData
        inputData['extraJobData'] = extraJobData
        inputData = json.dumps(inputData).encode()

        soft = '_nuke' if taskData.get("task") == tctProcessElements['comp'] else 'houdini'
        runArgs = [configUtils.py2exe, configUtils.starterPath] + [soft]
        if self.autoInProgressStatus(selectedItem):
            subprocess.run(runArgs, input=inputData)
            self.taskManager.refreshTaskData()


class activeButtons_coordinator(activeButtonsTM):
    def __init__(self, taskManager, treeWidget):
        super(activeButtons_coordinator, self).__init__(taskManager, treeWidget)

        self.lay_activeButtons = QHBoxLayout()
        # ======================= BUTTONS ===============================
        self.rejectButton = QPushButton('Reject')
        self.rejectButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.rejectButton.setMinimumSize(50, 50)

        self.acceptButton = QPushButton('Approved :-)')
        self.acceptButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.acceptButton.setMinimumSize(50, 50)

        # ======================= CONNECTS ===============================
        self.rejectButton.clicked.connect(self.rejectTaskButton)
        self.acceptButton.clicked.connect(self.approvedTaskButton)

        # ======================= LAYOUT SETUP ===============================
        self.lay_activeButtons.addWidget(self.rejectButton)
        self.lay_activeButtons.addWidget(self.acceptButton)

    def rejectTaskButton(self):
        prevStatuses = [tctStatusElements['review']]
        newStatus = tctStatusElements['pending']
        self.changeStatus(prevStatuses, newStatus, multipleItems=True)

    def approvedTaskButton(self):
        prevStatuses = [tctStatusElements['review']]
        newStatus = tctStatusElements['approved']
        self.changeStatus(prevStatuses, newStatus, multipleItems=True)


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
        self.rejectButton.clicked.connect(self.rejectTaskButton)
        self.acceptButton.clicked.connect(self.acceptTaskButton)
        self.openButton.clicked.connect(self.runSoft)

        # ======================= LAYOUT SETUP ===============================
        self.lay_activeButtons.addWidget(self.rejectButton)
        self.lay_activeButtons.addWidget(self.acceptButton)
        self.lay_activeButtons.addWidget(self.openButton)

    def rejectTaskButton(self):
        prevStatuses = [tctStatusElements['revise']]
        newStatus = tctStatusElements['pending']
        self.changeStatus(prevStatuses, newStatus, multipleItems=True)

    def acceptTaskButton(self):
        prevStatuses = [tctStatusElements['revise']]
        newStatus = tctStatusElements['review']
        self.changeStatus(prevStatuses, newStatus, multipleItems=True)


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
        self.completeButton.clicked.connect(self.completeTaskButton)
        self.openButton.clicked.connect(self.runSoft)

        # ======================= LAYOUT SETUP ===============================
        self.lay_activeButtons.addWidget(self.openButton)
        self.lay_activeButtons.addWidget(self.completeButton)

    def completeTaskButton(self):
        selectedItem = self.itemUtils.getSelected_ProcessItems()
        itemStatus = selectedItem.text(1)
        if itemStatus in [tctStatusElements['inProgress']]:
            self.updateStatus(tctStatusElements['revise'])
        else:
            msg = simpleDialogs.MessageDialog(self.taskManager)
            textMsg = "To complete this task the status must be '{inProgress}'".format(inProgress=tctStatusElements['inProgress'])
            msg.showDialog(textMsg, buttons=False)

