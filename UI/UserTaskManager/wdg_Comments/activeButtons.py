# from subprocess import Popen, PIPE
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt
from _lib.tactic_lib import tacticDataProcess
# from _lib import configUtils
from UI.UserTaskManager.utils import rvPlayerUtils


class ActiveButtons():

    def __init__(self, commentBlockWidget, taskManagerWdg,
                 textCommentDialog, tableCommentList):

        self.commentBlockWidget = commentBlockWidget
        self.taskManagerWdg = taskManagerWdg
        self.textCommentDialog = textCommentDialog
        # self.tableCommentList = tableCommentList

        self.lay_buttons = QHBoxLayout()

        self.addButton = QPushButton('Add')
        self.editButton = QPushButton('Edit')
        self.deleteButton = QPushButton('Delete')
        self.watchImageButton = QPushButton('IMGs')

        # self.textFiledWidget = TextCommentDialg(taskManagerWdg)

        # ======================= CONNECTS ===============================
        self.addButton.clicked.connect(self.newTextDialog)
        self.editButton.clicked.connect(self.updateTextDialog)
        self.deleteButton.clicked.connect(self.deleteNote)
        self.watchImageButton.clicked.connect(self.watchImage)

        self.lay_buttons.addWidget(self.addButton)
        self.lay_buttons.addWidget(self.editButton)
        self.lay_buttons.addWidget(self.deleteButton)
        self.lay_buttons.addWidget(self.watchImageButton)

    def newTextDialog(self):
        if len(self.taskManagerWdg.treeWidget.selectedItems()) == 0:
            return
        self.commentBlockWidget.callTextDialog("Add")

    def updateTextDialog(self):
        commentItem = self.commentBlockWidget.selectedCommentItem
        if commentItem is None:
            return
        if not self.commentBlockWidget.checkCommentOwner():
            print("You cannot change other people's comments.")
            return

        taskItem = self.getCommentTaskItem(commentItem)
        text = commentItem.data(Qt.UserRole).get('note')
        self.textCommentDialog.textField.setPlainText(text)
        self.commentBlockWidget.callTextDialog("Update", taskItem, False)

    def deleteNote(self):
        self.commentBlockWidget.deleteNote()

    def getCommentTaskItem(self, commentItem):
        process = commentItem.data(Qt.UserRole).get('process')
        parentSkey = commentItem.data(Qt.UserRole).get('parentSkey')

        if parentSkey.find('task') >= 0:
            shotSkey = tacticDataProcess.getTaskElementBySearchKey(self.taskManagerWdg.userServerCore.taskData, parentSkey).get('parent_search_key')
            shotName = shotSkey = tacticDataProcess.getTaskElementBySearchKey(self.taskManagerWdg.userServerCore.taskData, shotSkey).get('name')
        else:
            shotName = tacticDataProcess.getTaskElementBySearchKey(self.taskManagerWdg.userServerCore.taskData, parentSkey).get('name')

        shotItem = self.taskManagerWdg.treeWidget.findItems(shotName, Qt.MatchExactly | Qt.MatchRecursive)[0]
        shotChildren = [shotItem.child(idx) for idx in range(shotItem.childCount())]

        taskItem = list(filter(lambda x: x.text(0) == process, shotChildren))[0]
        return taskItem

    def watchImage(self):
        commentItem = self.commentBlockWidget.selectedCommentItem
        files = commentItem.data(Qt.UserRole).get('watchFiles')
        rvPlayerUtils.runRvPlayer(files)

