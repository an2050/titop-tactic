import os
import sys
from PySide2.QtWidgets import *

sys.path = list(set(sys.path + [os.path.join(os.environ['CGPIPELINE'])]))

from pathlib import Path
from _lib import configUtils

tacticConfigFile = configUtils.tacticConfigFile

styleCSS = "/".join([configUtils.rootPath, "UI", "css", "style.css"])
crPath = Path(__file__).parent / "cr.json"


class CredentialDialog(QDialog):
    def __init__(self, parent=None):
        super(CredentialDialog, self).__init__(parent)
        self.setStyleSheet(open(styleCSS).read())

        self.setMinimumSize(360, 240)

        # ======================= INITIAL LAYOUTS ===============================
        self.lay_main = QVBoxLayout(self)
        self.setLayout(self.lay_main)
        self.stack_lay = QVBoxLayout()
        self.rowIp_lay = QHBoxLayout()
        self.rowName_lay = QHBoxLayout()
        self.rowPass_lay = QHBoxLayout()
        self.btn_lay = QHBoxLayout()
        # ======================= WIDGETS ===============================
        self.inputGroupBox = QGroupBox()
        self.inputGroupBox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.infoLable = QLabel(self)

        self.userIpAdressLable = QLabel(self)
        self.userIpAdressLable.setText("IP:          ")
        self.userIpAdressField = QLineEdit(self)

        self.userNameLabel = QLabel(self)
        self.userNameLabel.setText("User:      ")
        self.userNameField = QLineEdit(self)

        self.userPasswordLable = QLabel(self)
        self.userPasswordLable.setText("Password")
        self.userPasswordField = QLineEdit(self)
        self.userPasswordField.setEchoMode(QLineEdit.Password)

        self.btnOK = QPushButton("OK")
        self.btnClose = QPushButton("Close")

        self.btnOK.clicked.connect(self.accept)
        self.btnClose.clicked.connect(self.reject)
        # ======================= LAYOUTS ===============================
        self.rowIp_lay.addWidget(self.userIpAdressLable)
        self.rowIp_lay.addWidget(self.userIpAdressField)

        self.rowName_lay.addWidget(self.userNameLabel)
        self.rowName_lay.addWidget(self.userNameField)

        self.rowPass_lay.addWidget(self.userPasswordLable)
        self.rowPass_lay.addWidget(self.userPasswordField)

        self.stack_lay.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.stack_lay.addWidget(self.infoLable)
        self.stack_lay.addLayout(self.rowIp_lay)
        self.stack_lay.addLayout(self.rowName_lay)
        self.stack_lay.addLayout(self.rowPass_lay)
        self.stack_lay.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.inputGroupBox.setLayout(self.stack_lay)

        self.btn_lay.addWidget(self.btnOK)
        self.btn_lay.addWidget(self.btnClose)

        self.lay_main.addWidget(self.inputGroupBox)
        self.lay_main.addLayout(self.btn_lay)

        self.initialzePreData()

    def initialzePreData(self):
        credData = configUtils.loadConfigData(crPath)
        try:
            self.userIpAdressField.setText(credData.get('IpAdress'))
            self.userNameField.setText(credData.get('userName'))
            self.userPasswordField.setText(credData.get('password'))
        except Exception:
            pass

    def getData(self):
        data = dict()
        data = {"userName": self.userNameField.text(), "password": self.userPasswordField.text(), "IpAdress": self.userIpAdressField.text()}
        self.saveCredentialData(data)
        return data

    def saveCredentialData(self, data):
        configUtils.checkAndCreateConfigFile(crPath)
        configUtils.saveConfigData(crPath, data)


# if __name__ == "__main__":
#     app = QApplication()
#     window = CredentialDialog()
#     window.show()
#     app.exec_()

