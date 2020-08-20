import os
import sys
from subprocess import run, Popen
# import re
# import shutil
from PySide2.QtWidgets import *

sys.path = list(set(sys.path + [os.path.join(os.environ['CGPIPELINE'])]))

# from _lib.tactic_lib import tacticPostUtils

from _lib import configUtils
from UI.Dialogs import wdg_utils
# from UI.Dialogs.parserExcelDialog import ParserExcelDataWidget
# from . import headerProjectWidget

# synchScript = configUtils.synchScript


class UpdateDialog(QDialog):
    def __init__(self, parent=None):
        super(UpdateDialog, self).__init__(parent)

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
        serverPipelinePath = configUtils.serverPipelinePath  # storage/pipeline
        lcPipeline = os.path.abspath(configUtils.rootPath + "/..")  # local/pipeline

        srvNukeModule = os.path.abspath(os.path.join(serverPipelinePath, 'nuke'))
        srvhoudiniModule = os.path.abspath(os.path.join(serverPipelinePath, 'houdini'))
        srvPythonModule = os.path.abspath(os.path.join(serverPipelinePath, 'bin', 'python'))

        lcNukeModule = os.path.abspath(os.path.join(lcPipeline, 'nuke'))
        lcHouidniModule = os.path.abspath(os.path.join(lcPipeline, 'houdini'))
        lcPythonModule = os.path.abspath(os.path.join(lcPipeline, 'python'))

        if self.mainUpdateCheckBox.isChecked():
            run(["robocopy", serverPipelinePath, lcPipeline, '/MIR', '/XD', srvNukeModule, srvhoudiniModule, srvPythonModule])

        if self.nukeModuleUpdateCheckBox.isChecked():
            run(["robocopy", srvNukeModule, lcNukeModule, '/MIR'])

        if self.houdiniModueUpdateCheckBox.isChecked():
            run(["robocopy", srvhoudiniModule, lcHouidniModule, '/MIR'])

        if self.pythonModuleUpdateCheckBox.isChecked():
            run(["robocopy", srvPythonModule, lcPythonModule, '/MIR'])

        self.accept()

if __name__ == "__main__":
    app = QApplication()
    MainWindowWidget = UpdateDialog()
    MainWindowWidget.show()

    app.exec_()