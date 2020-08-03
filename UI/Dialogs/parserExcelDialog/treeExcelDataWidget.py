from PySide2.QtWidgets import *
from PySide2.QtCore import Qt
# import json


class TreeDataWidget(QWidget):

    def __init__(self, parent=None):
        super(TreeDataWidget, self).__init__(parent)

        self.lay_main = QHBoxLayout()
        self.setLayout(self.lay_main)
# ======================== WIDGETS =============================
        self.treeDataWidget = QTreeWidget()
        self.treeDataWidget.setColumnCount(2)
        header = self.treeDataWidget.header()
        header.setDefaultAlignment(Qt.AlignHCenter)
        header.setDefaultSectionSize(125)
        self.treeDataWidget.setHeaderLabels(["Episod/Shot", "Shots count"])

        self.description = DescriptionFieldWidget(self)
        self.description.setDescriptionText("")
# ======================== CONNECTS =============================
        self.treeDataWidget.currentItemChanged.connect(self.treeItemChanged)
# ======================== LAYOUTS =============================
        self.lay_main.addWidget(self.treeDataWidget)
        self.lay_main.addWidget(self.description.groupBoxDescription)

    def treeItemChanged(self, currentItem):
        itemData = currentItem.data(0, Qt.UserRole)
        descrition = self.convertDictToText(itemData)
        self.description.setDescriptionText(descrition)

    def completeTree(self, treeData):
        self.treeDataWidget.clear()
        self.addTreeItem(treeData)

    def addTreeItem(self, data, parent=None):
        if parent is None:
            parent = self.treeDataWidget.invisibleRootItem()
        for dataItem in data:
            item = QTreeWidgetItem()
            item.setTextAlignment(0, Qt.AlignCenter)
            item.setTextAlignment(1, Qt.AlignCenter)

            if dataItem.get('children'):
                item.setText(0, dataItem['name'])
                item.setText(1, str(len(dataItem.get('children'))))
                item.setData(0, Qt.UserRole, {"name": dataItem['name']})
                item.setTextAlignment(0, Qt.AlignLeft)
                self.addTreeItem(dataItem['children'], parent=item)
            else:
                item.setData(0, Qt.UserRole, dataItem)
                item.setText(0, dataItem['name'])
                # item.setTextAlignment(0, 1)

            parent.addChild(item)

    def convertDictToText(self, d):
        text = ""
        for k, v in d.items():
            text += "{k}:\n\t{v}\n".format(k=k.upper(), v=v)
        return text


class DescriptionFieldWidget():
    def __init__(self, parent):
        # super(DescriptionFieldWidget, self).__init__(parent)

        self.lay_grpBoxVertical = QVBoxLayout()

        self.groupBoxDescription = QGroupBox("Prview Info")
        self.groupBoxDescription.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.description_lable = QLabel()
        self.description_lable.setMinimumSize(300, 200)
        self.description_lable.setWordWrap(True)
        self.description_lable.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.description_lable.setStyleSheet("QLabel {font: 15px;}")
        self.description_lable.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.lay_grpBoxVertical.addSpacerItem(QSpacerItem(0, 8))
        self.lay_grpBoxVertical.addWidget(self.description_lable)
        self.groupBoxDescription.setLayout(self.lay_grpBoxVertical)

    def setDescriptionText(self, text):
        self.description_lable.setText(text)


if __name__ == "__main__":
    app = QApplication()
    wdg = SheetRepresentationWidget()
    wdg.show()
    app.exec_()
