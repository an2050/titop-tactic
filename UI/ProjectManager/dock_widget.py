from PySide2.QtWidgets import *
from PySide2.QtCore import Qt, QSize

from varsTree import varsTreeWidget


class dockWidget(QDockWidget):
    """docstring for dockWidget"""

    def __init__(self, parent=None, title="TEMP"):
        super(dockWidget, self).__init__(title, parent)
        self.setTitleBarWidget(QWidget())

        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)

        # Main Widget
        self.mainWidget = QWidget(self)
        self.mainWidget.setMinimumSize(345, 0)
        self.lay_main = QVBoxLayout(self.mainWidget)
        self.mainWidget.setLayout(self.lay_main)

        # Widgets
        self.tabWidget = QTabWidget(self)
        self.tabWidget.addTab(varsTreeWidget(self), "Main Variables")
        self.tabWidget.addTab(varsTreeWidget(self), "Task Variables")

        # Set Layouts
        self.lay_main.addWidget(self.tabWidget)

        # Dock Out
        self.setWidget(self.mainWidget)

        # self.close()