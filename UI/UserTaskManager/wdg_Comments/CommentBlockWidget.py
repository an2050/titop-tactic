# import os
# import shutil
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt

from _lib.tactic_lib import tacticPostUtils

from .tableCommentList import TableCommentList
from .descriptionField import DescriptionFieldWidget
from .activeButtons import ActiveButtons
from .textCommentDialog import TextCommentDialg

class CommentBlockWidget(QWidget):

    def __init__(self, taskManagerWdg, treeWidget):
        self.taskManagerWdg = taskManagerWdg
        self.treeWidget = treeWidget
        self.server = None
        self.selectedCommentItem = None
        # self.selectedTaskItem = None

        self.lay_main = QVBoxLayout()

        # ======================= WIDGETS ===============================
        self.tableCommentList = TableCommentList(self, self.taskManagerWdg)
        self.descriptionField = DescriptionFieldWidget(self.taskManagerWdg)
        self.textCommentDialog = TextCommentDialg(self, taskManagerWdg, treeWidget)
        self.activeButtons = ActiveButtons(self, self.taskManagerWdg, self.textCommentDialog, self.tableCommentList)

        # ======================= CONNECTS ===============================
        # self.tableCommentList.currentItemChanged.connect(self.commentItemChanged)

        # ======================= LAYOUTS ===============================
        self.lay_main.addWidget(self.tableCommentList)
        self.lay_main.addLayout(self.activeButtons.lay_buttons)
        self.lay_main.addWidget(self.descriptionField.groupBoxDescription)

    def completeTableList(self, noteData, parentSkey=""):
        self.tableCommentList.completeTable(noteData, parentSkey)

    def setDescriptionText(self, text):
        self.descriptionField.setDescriptionText(text)

    def clearTextDialogField(self):
        self.textCommentDialog.clearTextDialogField()

    def callTextDialog(self, action, taskItem=None, clear=True):
        if clear:
            self.clearTextDialogField()
        self.textCommentDialog.action = action
        self.textCommentDialog.acceptButton.setText(action)
        self.textCommentDialog.taskItem = taskItem
        self.textCommentDialog.exec_()
        self.taskManagerWdg.refreshCommentData()
        
        self.textCommentDialog.noteData = None
        self.textCommentDialog.taskItem = None
        self.textCommentDialog.rvSTDOUT = None

    def getSelectedCommentItem(self, column=0):
        selectModel = self.tableCommentList.selectionModel()
        if not selectModel.hasSelection():
            print("Error: none selected comment items!")
            return
        selectedRow = selectModel.selectedRows()[0].row()
        item = self.tableCommentList.item(selectedRow, column)
        return item

    def getCommentOwner(self):
        item = self.getSelectedCommentItem(0)
        if item is not None:
            return item.text()

    def checkCommentOwner(self):
        userName = self.taskManagerWdg.userServerCore.userName
        owner = self.getCommentOwner()
        return userName == owner

    def createNote(self, sObject, text, process=""):
        noteData = tacticPostUtils.createNote(self.server, sObject, text, process=process)
        # self.taskManagerWdg.refreshCommentData()
        return noteData

    def updateNote(self, text, noteSkey=None):
        if not self.checkCommentOwner():
            print("You cannot delete other people's comments.")
            return
        noteSkey = self.selectedCommentItem.data(Qt.UserRole).get('sKey') if noteSkey is None else noteSkey
        noteData = tacticPostUtils.udateNote(self.server, noteSkey, text)
        # self.taskManagerWdg.refreshCommentData()
        return noteData

    def deleteNote(self, commentItem=None):
        commentItem = self.selectedCommentItem if commentItem is None else commentItem

        if commentItem is None:
            return
        if not self.checkCommentOwner():
            print("You cannot delete other people's comments.")
            return
        sKey = commentItem.data(Qt.UserRole).get('sKey')
        tacticPostUtils.deleteNote(self.taskManagerWdg.userServerCore.server, sKey, True)
        self.taskManagerWdg.refreshCommentData()

    def checkinNote(self, noteSkey, files):
        server = self.taskManagerWdg.userServerCore.server
        tacticPostUtils. checkinNote(server, noteSkey, files)


