from PySide2.QtWidgets import *
# from PySide2.QtCore import Qt


def getHorizontalBlockLayout(*widgets, lay=False):
    lay_horizontal = QHBoxLayout()
    for widget in widgets:
        if lay:
            lay_horizontal.addLayout(widget)
        else:
            lay_horizontal.addWidget(widget)
    lay_horizontal.addStretch()
    return lay_horizontal


def getHorizontalBlockWidget(*widgets, lay=False):
    wdg = QWidget()
    # wdg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
    lay_horizontal = QHBoxLayout()
    wdg.setLayout(lay_horizontal)
    # lay = QHBoxLayout()

    for widget in widgets:
        if lay:
            lay_horizontal.addLayout(widget)
        else:
            lay_horizontal.addWidget(widget)
    lay_horizontal.addStretch()
    return wdg


def arrangeVerticalLayout(*widgets):
    lay_horizontal = QHBoxLayout()
    for widget in widgets:
        lay_horizontal.addWidget(widget)
    return lay_horizontal


def showQFileDialog(parent, title, defaultDir="", filters=[("All", "*.*")], singleFile=False):
    filters = ";;".join(["{d}({p})".format(d=f[0], p=f[1]) for f in filters])
    if singleFile:
        return QFileDialog.getOpenFileName(parent, title, defaultDir, filters)
    else:
        return QFileDialog.getOpenFileNames(parent, title, defaultDir, filters)

def showQFolderDialog(parent, title, defaultDir=""):
    return QFileDialog.getExistingDirectory(parent, title, defaultDir)
