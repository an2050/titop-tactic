from PySide2.QtWidgets import *


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
    lay_horizontal = QHBoxLayout()
    wdg.setLayout(lay_horizontal)

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

