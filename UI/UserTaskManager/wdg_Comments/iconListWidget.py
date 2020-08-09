import os
import shutil
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon


class IconListWidget(QListWidget):
    def __init__(self, parent):
        super(IconListWidget, self).__init__(parent)

        self.tempCatalogs = []

        self.setViewMode(QListView.IconMode)
        self.setIconSize(QSize(128, 128))
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setDragDropMode(QAbstractItemView.NoDragDrop)

    def setIconList(self, files, isTemp=False):
        tempCatalogs = []
        for file in files:
            item = QListWidgetItem(self)
            item.setIcon(QIcon(file))
            item.setData(Qt.UserRole, file)
            tempCatalogs += [os.path.dirname(file)] if isTemp else []
        self.tempCatalogs = list(set(self.tempCatalogs + tempCatalogs))

    def getImageFiles(self):
        files = []
        for idx in range(self.count()):
            files.append(self.item(idx).data(Qt.UserRole))
        return files

    def clearIconList(self):
        self.clear()
        for catalog in self.tempCatalogs:
            try:
                shutil.rmtree(catalog)
            except OSError:
                pass
        self.tempCatalogs = []
