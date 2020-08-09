import os
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt

from .iconListWidget import IconListWidget

from _lib.configUtils import tacticProcessElements
from UI.UserTaskManager.utils import rvPlayerUtils

compProcess = tacticProcessElements['comp']


class TextCommentDialg(QDialog):
    def __init__(self, commentBlockWidget, taskManagerWdg, treeWidget):
        super(TextCommentDialg, self).__init__(taskManagerWdg)
        self.commentBlockWidget = commentBlockWidget
        self.taskManagerWdg = taskManagerWdg
        self.treeWidget = treeWidget
        self.itemUtils = self.treeWidget.itemUtils

        self.action = ""
        self.taskItem = None
        self.noteData = None

        self.lay_main = QVBoxLayout(self)
        self.lay_bottom = QHBoxLayout()

        # ======================= WIDGETS ===============================
        self.textField = QPlainTextEdit(self)
        self.textField.setMinimumSize(500, 200)

        self.iconListWidget = IconListWidget(self)

        self.acceptButton = QPushButton("Accept")
        self.rvButton = QPushButton("rvButton")

        # ======================= CONNECTS ===============================
        self.acceptButton.clicked.connect(self.acceptComment)
        self.rvButton.clicked.connect(self.runRvPlayer)

        # ======================= LAYOUTS ===============================
        self.lay_main.addWidget(self.textField)
        self.lay_main.addWidget(self.iconListWidget)

        self.lay_bottom.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
        self.lay_bottom.addWidget(self.rvButton)
        self.lay_bottom.addWidget(self.acceptButton)

        self.lay_main.addLayout(self.lay_bottom)

    def acceptComment(self):
        if self.noteData is None:
            self.saveComment()
        self.checkinNote(self.noteData)
        self.accept()

    def clearTextDialogField(self):
        self.textField.document().setPlainText("")

    def clearIconList(self):
        self.iconListWidget.clearIconList()

    def saveComment(self):
        text = self.textField.toPlainText()

        if self.action == "Add":
            if self.taskItem is None:
                self.taskItem = self.itemUtils.getSelected_ProcessItems()
                if self.taskItem is None:
                    return
            shotSkey = self.taskItem.parent().data(0, Qt.UserRole)
            process = self.taskItem.text(0)
            self.process = process
            self.noteData = self.commentBlockWidget.createNote(shotSkey, text, process)

        elif self.action == "Update":
            self.noteData = self.commentBlockWidget.updateNote(text)
        else:
            print("Action error: unexpected comment action!")

    def checkinNote(self, noteData):
        files = self.iconListWidget.getImageFiles()
        if not files:
            return
        self.commentBlockWidget.checkinNote(noteData, files)

    def runRvPlayer(self):
        if self.taskItem is None:
            self.taskItem = self.itemUtils.getSelected_ProcessItems()
            if self.taskItem is None:
                print("no task item")
                return

        if self.taskItem.text(0) == compProcess:
            stdout = rvPlayerUtils.watchDailies(self.getProject(), [self.taskItem], annotate=True)
        else:
            stdout = rvPlayerUtils.watchPreview(self.getProject(), self.taskItem, annotate=True)

        if stdout is not None:
            catalog = os.path.dirname(list(stdout.values())[0])
            if not os.path.exists(catalog):
                return

        files = ["/".join([catalog, file]) for file in os.listdir(catalog)]
        self.iconListWidget.setIconList(files, isTemp=True)

    def getProject(self):
        project = self.taskManagerWdg.getActiveProject()
        return project

