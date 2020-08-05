
from PySide2.QtWidgets import *


class MessageDialog(QMessageBox):
    def __init__(self, parent=None):
        super(MessageDialog, self).__init__(parent)

    def showDialog(self, msgText, msgInfo="", msgDitails="", buttons=True):
        self.setText(msgText)
        self.setInformativeText(msgInfo)
        if buttons:
            self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.setDetailedText(msgDitails)
        return self.exec_() == QMessageBox.Ok

# class MessageDialog(QDialog):
#     def __init__(self, parent):
#         super(MessageDialog, self).__init__(parent)


# if __name__ == "__main__":
#     app = QApplication()
#     w = MessageDialog()
#     w.showDialog("")
#     # w.show()
#     app.exec_()