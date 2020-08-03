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
# class SheetDataWidget(QWidget):
#     def __init__(self, parent):
#         super(SheetDataWidget, self).__init__(parent)
#         # self.newProject = newProject

#         self.lay_main = QVBoxLayout()
#         self.setLayout(self.lay_main)

#         self.titleRowNumber = QSpinBox()
#         self.numberOfRows = QSpinBox()
#         self.excelDataList = QListWidget()

#         self.treeData = sheetRepresentationWidget.SheetRepresentationWidget(self)

#         # if parent.newProject:
#         self.addWidgtItem("Shot Name")

#         self.lay_main.addWidget(self.titleRowNumber)
#         self.lay_main.addWidget(self.numberOfRows)
#         self.lay_main.addWidget(self.excelDataList)
#         self.lay_main.addWidget(self.treeData)

#     def addWidgtItem(self, nameField=""):
#         item = QListWidgetItem()
#         self.excelDataList.addItem(item)
#         itemWdg = RowListWidget(self, nameField)
#         item.setSizeHint(itemWdg.sizeHint())
#         self.excelDataList.setItemWidget(item, itemWdg)


# class RowListWidget(QWidget):
#     def __init__(self, parent=None, nameField=""):
#         super(RowListWidget, self).__init__(parent)

#         self.lay_main = QHBoxLayout()
#         self.setLayout(self.lay_main)
#         # if parent.newProject
#         self.nameField = QLineEdit(nameField)
#         self.columnList_combobox = QComboBox()

#         self.lay_main.addWidget(self.nameField)
#         self.lay_main.addWidget(self.columnList_combobox)





if __name__ == "__main__":
    app = QApplication()
    wdg = sheetsDialog()
    wdg.show()
    app.exec_()
