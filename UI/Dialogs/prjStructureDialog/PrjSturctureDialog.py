from PySide2.QtWidgets import *

from . import treeStructureWidget
from UI.Dialogs import wdg_utils

from _lib import configUtils

class ProjectStructureDialog(QDialog):

    def __init__(self, parent=None):
        super(ProjectStructureDialog, self).__init__(parent)

        self.resize(500, 500)

        self.lay_main = QVBoxLayout()
        self.setLayout(self.lay_main)

        self.treeStructureWdg = treeStructureWidget.TreeStructureWidget(self)

        self.saveButton = QPushButton("Save")
        self.acceptButton = QPushButton("Accept")
        self.discardButton = QPushButton("Discard")
        self.lay_buttons = wdg_utils.arrangeHorizontalLayout(self.saveButton, self.acceptButton, self.discardButton)

        self.saveButton.clicked.connect(self.saveProjectStructure)
        self.acceptButton.clicked.connect(self.saveAndAccept)
        self.discardButton.clicked.connect(self.reject)

        self.lay_main.addWidget(self.treeStructureWdg)
        self.lay_main.addLayout(self.lay_buttons)

        self.initialize()

    def initialize(self):
        self.treeStructureWdg.completTreeData()

    def saveAndAccept(self):
        self.treeStructureWdg.saveTreeData()
        self.treeStructureWdg.saveProjectStructureConfigData()
        self.accept()

    def saveProjectStructure(self):
        self.treeStructureWdg.saveTreeData()
        self.treeStructureWdg.saveProjectStructureConfigData()

