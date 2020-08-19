from PySide2.QtWidgets import*
from PySide2.QtCore import*
from PySide2.QtGui import*

app = QCoreApplication.instance()

class MouseDetector(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            print("start")

mouseFilter = MouseDetector()
app.installEventFilter(mouseFilter)