import os
import sys
# import re
# import shutil
from PySide2.QtWidgets import *

sys.path = list(set(sys.path + [os.path.join(os.environ['CGPIPELINE'])]))

# from _lib.tactic_lib import tacticPostUtils

from _lib import configUtils
from UI.Dialogs import wdg_utils
# from UI.Dialogs.parserExcelDialog import ParserExcelDataWidget
# from . import headerProjectWidget

serverPipelinePath = configUtils.serverPipelinePath
synchScript = configUtils.synchScript


class UdateDialog(QDialog):
    def __init__(self, parent=None):
        super(UdateDialog, self).__init__(parent)

        # self.setMinimumSize(360, 240)

        self.lay_main = QVBoxLayout()
        self.setLayout(self.lay_main)

        self.groupBox = QGroupBox()
        self.lay_groupBox = QVBoxLayout()
        self.groupBox.setLayout(self.lay_groupBox)


# ====================== WIDGETS ===============================
        self.mainUpdateLable = QLabel("    Main Update")
        self.mainUpdateCheckBox = QCheckBox()
        self.mainUpdateCheckBox.setChecked(True)
        self.lay_mainUpdate = wdg_utils.getHorizontalBlockLayout(self.mainUpdateLable, self.mainUpdateCheckBox)
        self.lay_groupBox.addLayout(self.lay_mainUpdate)

        self.nukeModuleUpdateLable = QLabel("    Nuke Module")
        self.nukeModuleUpdateCheckBox = QCheckBox()
        self.lay_nukeModuleUpdate = wdg_utils.getHorizontalBlockLayout(self.nukeModuleUpdateLable, self.nukeModuleUpdateCheckBox)
        self.lay_groupBox.addLayout(self.lay_nukeModuleUpdate)

        self.houdiniModueUpdateLable = QLabel("Houdini Module")
        self.houdiniModueUpdateCheckBox = QCheckBox()
        self.lay_houdiniModueUpdate = wdg_utils.getHorizontalBlockLayout(self.houdiniModueUpdateLable, self.houdiniModueUpdateCheckBox)
        self.lay_groupBox.addLayout(self.lay_houdiniModueUpdate)

        self.pythonModuleUpdateLable = QLabel("Python Module")
        self.pythonModuleUpdateCheckBox = QCheckBox()
        self.lay_pythonModuleUpdate = wdg_utils.getHorizontalBlockLayout(self.pythonModuleUpdateLable, self.pythonModuleUpdateCheckBox)
        self.lay_groupBox.addLayout(self.lay_pythonModuleUpdate)

# ====================== BUTTONS ===============================
        self.btnUdate = QPushButton("Udate")
        self.btnCancel = QPushButton("Cancel")
        self.lay_btns = wdg_utils.getHorizontalBlockLayout(self.btnUdate, self.btnCancel)
        self.btnUdate.clicked.connect(self.update)
        self.btnCancel.clicked.connect(self.reject)


        self.lay_main.addWidget(self.groupBox)
        self.lay_main.addLayout(self.lay_btns)

    def update(self):
        print("Update")
        self.accept()

        if self.mainUpdateCheckBox.isChecked():
            src = serverPipelinePath
            dst = 
            pass
        if self.nukeModuleUpdateCheckBox.isChecked():
            pass
        if self.houdiniModueUpdateLable.isChecked():
            pass
        if self.pythonModuleUpdateLable.isChecked():
            pass



if __name__ == "__main__":
    app = QApplication()
    MainWindowWidget = UdateDialog()
    MainWindowWidget.show()

    app.exec_()