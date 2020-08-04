from PySide2.QtWidgets import *
from PySide2.QtCore import Qt
# from widgets_ui import template_form_ui
import re
import os

if __name__ == "__main__":
    import sys
    libPath = os.path.join(os.environ['CGPIPELINE'], "_lib")
    sys.path.append(libPath)

from _lib import configUtils


templateConfigFile = configUtils.templateConfigFile


class template_form(QDialog):
    """docstring for template_form"""

    def __init__(self, arg=None):
        super(template_form, self).__init__(arg)
        # self.setupUi(self)
        self.setWindowModality(Qt.WindowModal)
        self.resize(500, 100)

        # Layouts
        self.lay_main = QVBoxLayout(self)
        self.setLayout(self.lay_main)
        self.lay_templ_horizontal = QHBoxLayout()
        self.lay_btn_horizontal = QHBoxLayout()
        self.lay_otlPathTab_vertical = QGridLayout()
        self.lay_workPathTab_vertical = QGridLayout()

        # Widgets--------------
        self.lableStructureProject = QLabel("Project Structure Template:")
        self.templateStructureProject = QLineEdit(self)

        self.tabWidget = QTabWidget(self)
        #================ Tabs ==============

        self.workPathTab = QWidget(self.tabWidget)
        self.workPathTab.setLayout(self.lay_workPathTab_vertical)
        self.tabWidget.addTab(self.workPathTab, "Work Paths for Project")

        self.otlPathsTab = QWidget(self.tabWidget)
        self.otlPathsTab.setLayout(self.lay_otlPathTab_vertical)
        self.tabWidget.addTab(self.otlPathsTab, "OTL Paths for Project")
        
        # ============ OTL Path Templates ============
        self.lableOtlPath_prj = QLabel("Project:")
        self.templateOtlPath_prj = QLineEdit(self)
        self.lableOtlPath_epi = QLabel("Episod:")
        self.templateOtlPath_epi = QLineEdit(self)
        self.lableOtlPath_shot = QLabel("Shot:")
        self.templateOtlPath_shot = QLineEdit(self)

        # ============ Work Path Templates ============
        self.lableWorkPath_prj = QLabel("Project:")
        self.templateWorkPath_prj = QLineEdit(self)
        self.lableWorkPath_epi = QLabel("Episod:")
        self.templateWorkPath_epi = QLineEdit(self)
        self.lableWorkPath_shot = QLabel("Shot:")
        self.templateWorkPath_shot = QLineEdit(self)
        
        # buttons widget
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        # Connects
        self.save_button.clicked.connect(self.saveSettings)
        self.cancel_button.clicked.connect(self.close)

        self.layoutSetup()

        self.updateTemplate()

    def layoutSetup(self):

        # Layouts Setup
        # buttons
        self.lay_btn_horizontal.addStretch(0)
        self.lay_btn_horizontal.addWidget(self.save_button)
        self.lay_btn_horizontal.addWidget(self.cancel_button)
        # project template
        self.lay_main.addWidget(self.lableStructureProject)
        self.lay_main.addWidget(self.templateStructureProject)

        self.lay_main.addWidget(self.tabWidget)
        # OTL Paths Templates
        self.lay_otlPathTab_vertical.addWidget(self.lableOtlPath_prj, 0, 0)
        self.lay_otlPathTab_vertical.addWidget(self.templateOtlPath_prj, 0, 1)
        self.lay_otlPathTab_vertical.addWidget(self.lableOtlPath_epi)
        self.lay_otlPathTab_vertical.addWidget(self.templateOtlPath_epi)
        self.lay_otlPathTab_vertical.addWidget(self.lableOtlPath_shot)
        self.lay_otlPathTab_vertical.addWidget(self.templateOtlPath_shot)
        # Work Path Templates
        self.lay_workPathTab_vertical.addWidget(self.lableWorkPath_prj, 0, 0)
        self.lay_workPathTab_vertical.addWidget(self.templateWorkPath_prj, 0, 1)
        self.lay_workPathTab_vertical.addWidget(self.lableWorkPath_epi)
        self.lay_workPathTab_vertical.addWidget(self.templateWorkPath_epi)
        self.lay_workPathTab_vertical.addWidget(self.lableWorkPath_shot)
        self.lay_workPathTab_vertical.addWidget(self.templateWorkPath_shot)

        self.lay_main.addLayout(self.lay_btn_horizontal)
        self.lay_main.addStretch(0)

    def updateTemplate(self):
        templatesData = configUtils.loadConfigData(templateConfigFile)
        if templatesData is None:
            return None
        self.templateStructureProject.setText(templatesData['projectTemplate'])

        print(templatesData)
        otlPathData = templatesData['OTLPaths']
        self.templateOtlPath_prj.setText(otlPathData['OTLPath_prj'])
        self.templateOtlPath_epi.setText(otlPathData['OTLPath_epi'])
        self.templateOtlPath_shot.setText(otlPathData['OTLPath_shot'])

        workPathData = templatesData['Work_Paths']
        self.templateWorkPath_prj.setText(workPathData['workPath_prj'])
        self.templateWorkPath_epi.setText(workPathData['workPath_epi'])
        self.templateWorkPath_shot.setText(workPathData['workPath_shot'])

    def saveSettings(self):
        prjTemplate = self.templateStructureProject.text()

        OTLPaths_prj = self.templateOtlPath_prj.text()
        OTLPath_epi = self.templateOtlPath_epi.text()
        OTLPath_shot = self.templateOtlPath_shot.text()

        workPath_prj = self.templateWorkPath_prj.text()
        workPath_epi = self.templateWorkPath_epi.text()
        workPath_shot = self.templateWorkPath_shot.text()

        templatesData = {"projectTemplate": prjTemplate,
                        "OTLPaths": {"OTLPath_prj": OTLPaths_prj,
                                    "OTLPath_epi": OTLPath_epi,
                                    "OTLPath_shot": OTLPath_shot},
                        "Work_Paths":{"workPath_prj": workPath_prj,
                                    "workPath_epi": workPath_epi,
                                    "workPath_shot": workPath_shot}}

        path = self.getProjectsFolder(prjTemplate)
        if os.path.exists(path):
            configUtils.saveConfigData(templateConfigFile, templatesData)
            self.close()
        else:
            msg = QMessageBox()
            msg.setText("'{dir}' directory is not exists".format(dir=path))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def getProjectsFolder(self, template):
        return template[:template.find("{projectName}")]


if __name__ == "__main__":
    app = QApplication()
    w = template_form()
    w.show()
    app.exec_()
# import configUtils
