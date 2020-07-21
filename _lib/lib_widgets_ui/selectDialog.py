try:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import QCoreApplication
    title = []
except:
    from PySide.QtGui import *
    from PySide.QtCore import QCoreApplication
    title = "Dialog"


class selectDialog(QDialog):
    """docstring for selectDialog"""

    def __init__(self, itemList, parent=None):
        super(selectDialog, self).__init__(parent)

        lay = QVBoxLayout(self)
        self.setLayout(lay)
        self.selectList = []
        for b in itemList:
            b = QCheckBox(b)
            b.stateChanged.connect(lambda x, t=b.text(): self.setData(x, t))
            lay.addWidget(b)

    def setData(self, state, t):
        if state > 0:
            self.selectList.append(t)
        else:
            indx = self.selectList.index(t)
            self.selectList.pop(indx)


def executeDialog(itemList):
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(title)
    w = selectDialog(itemList)
    w.exec_()

    return w.selectList
