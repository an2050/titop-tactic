import os
import sys

if sys.version_info[0] >= 3:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import Qt
else:
    from PySide.QtGui import *
    from PySide.QtCore import Qt

sys.path = list(set(sys.path + [os.environ.get('CGPIPELINE')]))
from _lib import configUtils
styleCSS = "/".join([configUtils.rootPath, "UI", "css", "style.css"])


class MessageDialog(QMessageBox):

    def __init__(self, parent=None):
        if QApplication.instance() is None:
            QApplication(sys.argv)

        super(MessageDialog, self).__init__(parent)
        if parent is None:
            self.setStyleSheet(open(styleCSS).read())
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


def showQFolderDialog(parent, title, defaultDir=""):
    return QFileDialog.getExistingDirectory(parent, title, defaultDir)


class PathFileDialog(QDialog):

    def __init__(self, parent=None):
        if QApplication.instance() is None:
            QApplication(sys.argv)

        super(PathFileDialog, self).__init__(parent)
        if parent is None:
            self.setStyleSheet(open(styleCSS).read())

        self.fileChoiseText = ""
        self.defaultDir = ""

        self.setMinimumWidth(300)

        lay = QVBoxLayout()
        self.setLayout(lay)

        self.msgLable = QLabel()
        self.msgLable.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.msgLable.setAlignment(Qt.AlignCenter)

        self.pathField = QLineEdit()
        self.fileButton = QPushButton('...')
        self.fileButton.setFixedWidth(25)
        self.fileButton.clicked.connect(self.fileChoiceButton)
        lay_02 = QHBoxLayout()
        lay_02.addWidget(self.pathField)
        lay_02.addWidget(self.fileButton)

        self.okBtn = QPushButton('OK')
        self.cancelBtn = QPushButton('Cancel')
        lay_03 = QHBoxLayout()
        lay_03.addWidget(self.okBtn)
        lay_03.addWidget(self.cancelBtn)
        lay_03.insertStretch(0)

        self.okBtn.clicked.connect(self.accept)
        self.cancelBtn.clicked.connect(self.reject)

        lay.addWidget(self.msgLable)
        lay.addLayout(lay_02)
        lay.addLayout(lay_03)

    def fileChoiceButton(self):
        path = showQFolderDialog(self, title=self.fileChoiseText, defaultDir=self.defaultDir)
        if path:
            self.pathField.setText(path)

    def showDialog(self, msg):
        self.msgLable.setText(msg)
        if self.exec_():
            return self.pathField.text()

