import os
import shutil
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt
# from _lib.tactic_lib import tacticPostUtils
from _lib.configUtils import tacticProcessElements
# from _lib.tactic_lib import tacticDataProcess
from UI.UserTaskManager.utils import rvPlayerUtils
# from _lib import exceptionUtils

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
        self.rvSTDOUT = None

        self.lay_main = QVBoxLayout(self)
        self.lay_bottom = QHBoxLayout(self)

        # ======================= WIDGETS ===============================
        self.textField = QPlainTextEdit(self)
        self.textField.setMinimumSize(500, 200)

        # self.saveButton = QPushButton("Save")
        self.acceptButton = QPushButton("Accept")
        self.rvButton = QPushButton("rvButton")

        # ======================= CONNECTS ===============================
        # self.saveButton.clicked.connect(self.saveComment)
        self.acceptButton.clicked.connect(self.acceptComment)
        self.rvButton.clicked.connect(self.runRvPlayer)

        # ======================= LAYOUTS ===============================
        self.lay_main.addWidget(self.textField)

        self.lay_bottom.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
        self.lay_bottom.addWidget(self.rvButton)
        # self.lay_bottom.addWidget(self.saveButton)
        self.lay_bottom.addWidget(self.acceptButton)

        self.lay_main.addLayout(self.lay_bottom)

    def clearTextDialogField(self):
        self.textField.document().setPlainText("")

    def saveComment(self):
        text = self.textField.toPlainText()

        if self.action == "Add":

            if self.taskItem is None:            
                self.taskItem = self.itemUtils.getSelected_ProcessItem()
                # self.taskItem = taskItem
                if self.taskItem is None:
                    return
            # else:
            #     taskItem - self.taskItem

            shotSkey = self.taskItem.parent().data(0, Qt.UserRole)
            process = self.taskItem.text(0)
            # self.taskItem = taskItem
            self.process = process
            self.noteData = self.commentBlockWidget.createNote(shotSkey, text, process)


        elif self.action == "Update":
            self.noteData = self.commentBlockWidget.updateNote(text)
        else:
            print("Action error: uexpected comment action!")

    def acceptComment(self):
        if self.noteData is None:
            self.saveComment()
        self.checkinNote(self.noteData)
        self.accept()

    def checkinNote(self, noteData):
        if self.rvSTDOUT is not None:
            catalog = os.path.dirname(list(self.rvSTDOUT.values())[0])
            if not os.path.exists(catalog):
                return

            files = ["/".join([catalog, file]) for file in os.listdir(catalog)]
            self.commentBlockWidget.checkinNote(noteData, files)

            try:
                shutil.rmtree(catalog)
            except OSError:
                pass

    def runRvPlayer(self):
        # if self.noteData is None:
        #     self.saveComment()

        # if self.taskItem is None:
        #     print("no task item")
        #     return
        if self.taskItem is None:
            self.taskItem = self.itemUtils.getSelected_ProcessItem()
            if self.taskItem is None:
                print("no task item")
                return

        if self.taskItem.text(0) == compProcess:
            stdout = rvPlayerUtils.watchDailies(self.getProject(), [self.taskItem], annotate=True)
        else:
            stdout = rvPlayerUtils.watchPreview(self.getProject(), self.taskItem, annotate=True)
        self.rvSTDOUT = stdout

    def getProject(self):
        project = self.taskManagerWdg.currentProject.get('code')
        return project

