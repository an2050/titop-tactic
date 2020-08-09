try:
    from PySide2.QtWidgets import QMessageBox  # , QWidget
    from PySide2.QtCore import QCoreApplication
except ImportError:
    from PySide.QtCore import QCoreApplication
    from PySide.QtGui import QMessageBox


class pathError(Exception):
    def __init__(self, text=""):
        super(pathError, self).__init__()
        self.text = text

    def displayMessageIcon(self, text="", widget=None):
        text = self.text if text == "" else text
        if widget is None:
            app = QCoreApplication.instance()
            widget = app.activeWindow()
        dialog = QMessageBox(widget, text=text)
        dialog.show()
