import os
import shutil
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon

from UI.Dialogs import simpleDialogs

availableExt = [".jpg", ".jpeg", ".png", ".tif", ".tiff", ".tga", ".bmp", ".gif", ".exr", ".dpx", ".raw", ".mov", ".mp4"]


class IconListWidget(QListWidget):
    def __init__(self, parent):
        super(IconListWidget, self).__init__(parent)

        self.pathFileDialog = os.path.expanduser("~")
        self.tempCatalogs = []

        self.setViewMode(QListView.IconMode)
        self.setIconSize(QSize(128, 128))
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setDragDropMode(QAbstractItemView.DropOnly)

    def setIconList(self, files, isTemp=False):
        currList = [self.item(idx).data(Qt.UserRole) for idx in range(self.count())]

        tempCatalogs = []
        for file in files:
            if file in currList:
                continue
            item = QListWidgetItem(self)
            item.setText(os.path.basename(file))
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

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasUrls() and mimeData.urls()[0].isLocalFile():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        mimeData = event.mimeData()
        paths = [url.toLocalFile() for url in mimeData.urls()]
        files = []
        for path in paths:
            files += self.collectImageFiles(path)

        self.setIconList(files)

    def mouseDoubleClickEvent(self, event):
        filters = [("All", "*.*")] + [("", "*" + _filter) for _filter in availableExt]

        imgFiles, filter_ = simpleDialogs.showQFileDialog(self, "Select img files", self.pathFileDialog, filters)
        if not imgFiles:
            return
        self.pathFileDialog = os.path.dirname(imgFiles[0])

        files = []
        for path in imgFiles:
            files += self.collectImageFiles(path)
        self.setIconList(files)

    def collectImageFiles(self, path):
        files = []
        if os.path.isdir(path):
            for root, dirs, _files in os.walk(path):
                _files = ["/".join([root, file]) for file in _files]
                files += _files
        else:
            files.append(path)

        return filter(lambda x: os.path.splitext(x)[1] in availableExt, files)
