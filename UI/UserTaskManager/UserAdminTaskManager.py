import os
import sys
from PySide2.QtWidgets import *
lib = os.path.join(os.environ['CGPIPELINE'], "_lib")
sys.path += [lib]

from pathlib import Path

import configUtils
from UserTaskManager import userTaskWidget

styleCSS = Path(__file__).parent.parent / "css" / "style.css"

tacticConfigFile = configUtils.tacticConfigFile

class mainWindow(QWidget):
    """docstring for mainWindow"""

    def __init__(self):
        super(mainWindow, self).__init__()

        self.setStyleSheet(open(styleCSS).read())

        self.resize(720, 480)
        # Layouts
        lay_main = QVBoxLayout(self)
        self.setLayout(lay_main)
        lay_upHorizontal = QHBoxLayout()

        # Widgets
        self.userTaskWidget = userTaskWidget(self)
        self.serverIp_lable = QLabel(self)
        self.serverIp_lable.setText("Server IP: ")
        self.serverIp_filed = QLineEdit(self)

        # Connects
        self.serverIp_filed.editingFinished.connect(self.saveServerIp)

        # Layout setup
        lay_main.addLayout(lay_upHorizontal)
        lay_main.addWidget(self.userTaskWidget)

        lay_upHorizontal.addWidget(self.serverIp_lable)
        lay_upHorizontal.addWidget(self.serverIp_filed)

        self.loadServerIp()

    def loadServerIp(self):
        data = configUtils.loadConfigData(tacticConfigFile)
        if data is not None:
            self.serverIp_filed.setText(data.get("serverIp"))

    def saveServerIp(self):
        data = configUtils.loadConfigData(tacticConfigFile)
        if data is None:
            data = {'serverIp': self.serverIp_filed.text()}
        else:
            data['serverIp'] = self.serverIp_filed.text()
        configUtils.saveConfigData(tacticConfigFile, data)


if __name__ == "__main__":
    app = QApplication()
    window = mainWindow()
    window.show()
    app.exec_()

