from PySide2.QtWidgets import *


class MessageDialog(QMessageBox):
    def __init__(self, parent=None):
        super(MessageDialog, self).__init__(parent)
        self.setStyleSheet("QPushButton{ width:60px; font-size: 15px; }")

    def showDialog(self, msgText, msgInfo="", msgDitails="", buttons=True):
        self.setText(msgText)
        self.setInformativeText(msgInfo)
        if buttons:
            self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.setDetailedText(msgDitails)
        return self.exec_() == QMessageBox.Ok


def showQFileDialog(parent, title, defaultDir="", filters=[("All", "*.*")], singleFile=False):
    filters = ";;".join(["{d}({p})".format(d=f[0], p=f[1]) for f in filters])
    if singleFile:
        return QFileDialog.getOpenFileName(parent, title, defaultDir, filters)
    else:
        return QFileDialog.getOpenFileNames(parent, title, defaultDir, filters)
        return


def showQFolderDialog(parent, title, defaultDir=""):
    return QFileDialog.getExistingDirectory(parent, title, defaultDir)
