# import sys
# import os
# sys.path = list(set(sys.path + [os.path.join(os.environ['CGPIPELINE'])]))

from openpyxl import load_workbook
from PySide2.QtWidgets import *
# from PySide2.QtCore import QSize
from UI.Dialogs import wdg_utils
from . import allSheetsDataDialog
from . import treeExcelDataWidget


class MainItnputDataWidget(QWidget):
    def __init__(self, parent=None):
        super(MainItnputDataWidget, self).__init__(parent)

        self.workBook = None
        self.treeData = []

        self.lay_main = QVBoxLayout()
        # self.setLayout(self.lay_main)

        # self.mainTabsWidget = sheetDataWidget.MainTabsWidget(self)
# ==================== Path block ==================================
        # - lable
        self.pathLable = QLabel("Excel file")
        # - field
        self.pathField = QLineEdit()
        self.pathField.setMinimumSize(300, 0)
        # - button
        self.pathButton = QPushButton("...")
        self.pathButton.setMaximumWidth(25)
        # - layout
        pathWidgets_list = [self.pathLable, self.pathField, self.pathButton]
        self.lay_pathWidgets = wdg_utils.arrangeHorizontalLayout(*pathWidgets_list)

# ==================== Sheets block ==================================
        # - lable
        self.sheetLable = QLabel("Available sheets:")
        self.sheetLable.setFixedSize(100, 50)
        # - list
        self.availableSheetsList = QListWidget()
        self.availableSheetsList.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.availableSheetsList.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        # - button
        self.sheetsDialogButton = QPushButton("Setup")
        self.sheetsDialogButton.setFixedWidth(50)
        # - layout
        self.lay_sheetsBlock = wdg_utils.arrangeHorizontalLayout(self.sheetLable, self.availableSheetsList, self.sheetsDialogButton)

# ==================== Tree widget ==================================
        self.treeDataWidget = treeExcelDataWidget.TreeDataWidget(self)

# =================== CONNECTS ==============================
        self.pathButton.clicked.connect(self.defineExcelFile)
        self.sheetsDialogButton.clicked.connect(self.openSheetsDialog)
        # self.availableSheetsList.currentItemChanged.connect(self.test)

# =================== LAYOUTS ==============================
        self.lay_main.addLayout(self.lay_pathWidgets)
        # self.lay_main.addWidget(self.sheetsGroupbox)
        self.lay_main.addLayout(self.lay_sheetsBlock)
        self.lay_main.addWidget(self.treeDataWidget)
        # self.lay_main.addStretch()

    def defineExcelFile(self):
        # self.pathField.setText("")

        filters = [('Excel file', '*.xl*'), ('All', '*.*')]
        excelFile, filter_ = wdg_utils.showQFileDialog(self, "Select excel file", self.pathField.text(), filters, True)
        if not excelFile:
            return

        self.pathField.setText(excelFile)
        self.workBook = load_workbook(excelFile)
        self.completeSheetList()

    def completeSheetList(self):
        self.availableSheetsList.clear()
        if self.workBook is None:
            print("No excel files available.")
            return
        sheets = [sheet.title for sheet in self.workBook]
        for sheetName in sheets:
            listItem = QListWidgetItem()
            self.availableSheetsList.addItem(listItem)

            checkBoxWdg = self.createCheckBoxSet(sheetName)
            listItem.setSizeHint(checkBoxWdg.sizeHint())
            self.availableSheetsList.setItemWidget(listItem, checkBoxWdg)

    def openSheetsDialog(self):
        if self.workBook is None:
            print("No excel files available.")
            return
        selectedSheets = []
        for i in range(self.availableSheetsList.count()):
            item = self.availableSheetsList.item(i)
            chekcBoxWdg = self.availableSheetsList.itemWidget(item)
            if chekcBoxWdg.checkBox.isChecked():
                selectedSheets.append(self.workBook[chekcBoxWdg.checkBoxLable.text()])

        sheetsDialog = allSheetsDataDialog.AllSheetsDialog(self)
        sheetsDialog.selectedSheets = selectedSheets
        sheetsDialog.getSheetTabs()
        result = sheetsDialog.exec_()
        if result:
            self.treeData = sheetsDialog.collectAllTreeData()
            self.treeDataWidget.completeTree(self.treeData)
        # print(result)

    def createCheckBoxSet(self, name):
        wdg = QWidget(self)
        lay_main = QHBoxLayout()
        wdg.setLayout(lay_main)

        wdg.checkBoxLable = QLabel(name)
        wdg.checkBoxLable.setMinimumWidth(80)
        wdg.checkBox = QCheckBox(self)

        lay_main.addWidget(wdg.checkBoxLable)
        lay_main.addWidget(wdg.checkBox)
        lay_main.addStretch()
        return wdg

# if __name__ == "__main__":
#     app =QApplication()
#     wdg = MainItnputDataWidget()
#     wdg.show()
#     app.exec_()