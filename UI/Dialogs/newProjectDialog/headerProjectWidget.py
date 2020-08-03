from PySide2.QtWidgets import *
from UI.Dialogs import wdg_utils


class HeaderProjectFields(QWidget):

    def __init__(self, parent, userServerCore):
        super(HeaderProjectFields, self).__init__(parent)

        self.userServerCore = userServerCore

# ====================== WIDGETS ===============================
        self.lay_main = QVBoxLayout()

        self.nameLable = QLabel("Project name")
        self.nameField = QLineEdit(self)

        self.templateLable = QLabel("Template")
        self.templateList = QComboBox(self)

        self.esеimateLable = QLabel("Estimate")
        self.estimateChackbox = QCheckBox(self)
        horizontalWidgets_list = [self.nameLable, self.nameField, self.templateLable, self.templateList, self.esеimateLable, self.estimateChackbox]
        self.lay_header_01 = wdg_utils.arrangeHorizontalLayout(*horizontalWidgets_list)

        self.lay_header_01.addStretch(1000)
        self.lay_main.addLayout(self.lay_header_01)

        self.setTemplateList_comboBox()

    def setTemplateList_comboBox(self):
        # self.userServerCore.server.set_project("admin")
        templateProjectList = self.userServerCore.getTemplateProjectList()
        # self.userServerCore.server.set_project(self.userServerCore.activeProject)
        self.templateList.addItems(templateProjectList)
