from openpyxl import load_workbook

from PySide2.QtWidgets import *

from . import specialSheetDataWidget


class AllSheetsDialog(QDialog):

    def __init__(self, ecxelBlockWidget=None):
        super(AllSheetsDialog, self).__init__(ecxelBlockWidget)

        self.selectedSheets = []
        self.allTreeData = []

        self.lay_main = QVBoxLayout()
        self.setLayout(self.lay_main)
# ======================== WIDGETS =============================
        self.tabWidget = QTabWidget(self)
        self.acceptButton = QPushButton("Accept")
        self.cancelButton = QPushButton("Cancel")
# ======================== CONNECTS =============================
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

# ======================== LAYOUTS =============================
        self.lay_main.addWidget(self.tabWidget)
        self.lay_main.addWidget(self.acceptButton)
        self.lay_main.addWidget(self.cancelButton)

    def getSheetTabs(self):
        self.tabWidget.clear()
        if not self.selectedSheets:
            print("No sheets available.")
            return

        for sheet in self.selectedSheets:
            self.addNewSheetTab(sheet.title, sheet)

    def addNewSheetTab(self, name, sheet):
        sheetTabWidget = specialSheetDataWidget.SheetDataWidget(self, sheet)
        self.tabWidget.addTab(sheetTabWidget, name)

    def collectAllTreeData(self):
        allTreeData = []
        for idx in range(self.tabWidget.count()):
            wdg = self.tabWidget.widget(idx)
            allTreeData += wdg.treeData
        # print(allTreeData)
        # self.allTreeData = allTreeData
        return allTreeData
