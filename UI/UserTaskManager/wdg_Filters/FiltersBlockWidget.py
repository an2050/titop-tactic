from PySide2.QtWidgets import *
from PySide2.QtCore import Qt

class FiltersBlockWidget(QWidget):

    def __init__(self, taskManagerWdg):
        super(FiltersBlockWidget, self).__init__(taskManagerWdg)

        self.taskManagerWdg = taskManagerWdg

        self.lay_main = QVBoxLayout()
        # self.setLayout(self.lay_main)

        # - main layout levels 
        self.lay_filters_horizontal_l0 = QHBoxLayout()
        self.lay_filters_horizontal_l1 = QHBoxLayout()

        # - shot, project, user widhets
        self.lay_filterShotFiled = QHBoxLayout()
        self.lay_filterProject = QHBoxLayout()
        self.lay_changeUser = QHBoxLayout()

        # - drop-down filter layouts
        self.lay_filterProcess = QHBoxLayout()
        self.lay_filterStatus = QHBoxLayout()
        self.lay_filterUser = QHBoxLayout()

        # ===================== WIDGETS =================================
        # - filter prject
        self.filterProject_comboBox = QComboBox(self)
        self.filterProject_comboBox.setMinimumSize(150, 20)

        # - filter shot field -
        self.filterShot_Lable = QLabel(self)
        self.filterShot_Lable.setText("     Shot:")
        self.filterShotField = QLineEdit(self)

        # - filter process -
        self.filterProcess_Lable = QLabel(self)
        self.filterProcess_Lable.setText("Process:")
        self.filterProcess_comboBox = QComboBox(self)
        self.filterProcess_comboBox.setMinimumSize(150, 25)
        # - filter status -
        self.filterStatus_Lable = QLabel(self)
        self.filterStatus_Lable.setText("Status:")
        self.filterStatus_comboBox = QComboBox(self)
        self.filterStatus_comboBox.setMinimumSize(150, 25)
        # - filter user -
        self.filterUser_Lable = QLabel(self)
        self.filterUser_Lable.setText("User:")
        self.filterUser_comboBox = QComboBox(self)
        self.filterUser_comboBox.setMinimumSize(150, 25)

        # ======================= BUTTONS ===============================
        self.userButton = QPushButton("user")
        self.refreshButton = QPushButton('Refresh')

        # ======================= CONNECTS ===============================
        self.userButton.clicked.connect(self.changeUserButton)
        self.refreshButton.clicked.connect(self.refreshTaskDataButton)
        self.filterProject_comboBox.currentIndexChanged.connect(self.filter_ProjectProcess)
        self.filterStatus_comboBox.currentTextChanged.connect(self.filter_StatusProcess)
        self.filterShotField.textChanged.connect(self.filter_ShotProcess)
        self.filterUser_comboBox.currentTextChanged.connect(self.filter_UserProcess)
        self.filterProcess_comboBox.currentTextChanged.connect(self.filter_ProcessCallback)

        # ===================== LAYOUTS =================================
        # - filter shot layout -
        self.lay_filterShotFiled.addWidget(self.filterShot_Lable)
        self.lay_filterShotFiled.addWidget(self.filterShotField)
        self.lay_filterShotFiled.addStretch()
        # - filter project layout
        self.lay_filterProject.addWidget(self.filterProject_comboBox)
        self.lay_filterProject.addWidget(self.refreshButton)
        self.lay_filterProject.addStretch()
        # - change user block
        self.lay_changeUser.addWidget(self.userButton)

        # - filter process layout -
        self.lay_filterProcess.addWidget(self.filterProcess_Lable)
        self.lay_filterProcess.addWidget(self.filterProcess_comboBox)
        self.lay_filterProcess.addStretch()
        self.lay_filters_horizontal_l1.addLayout(self.lay_filterProcess)
        # - filter status layout -
        self.lay_filterStatus.addWidget(self.filterStatus_Lable)
        self.lay_filterStatus.addWidget(self.filterStatus_comboBox)
        self.lay_filterStatus.addStretch()
        self.lay_filters_horizontal_l1.addLayout(self.lay_filterStatus)
        self.lay_filters_horizontal_l1.addLayout(self.lay_filterStatus)
        # - filter user layout -
        self.lay_filterUser.addWidget(self.filterUser_Lable)
        self.lay_filterUser.addWidget(self.filterUser_comboBox)
        self.lay_filters_horizontal_l1.addLayout(self.lay_filterUser)
        self.lay_filters_horizontal_l1.addLayout(self.lay_filterUser)

        self.lay_filters_horizontal_l0.addLayout(self.lay_filterShotFiled)
        self.lay_filters_horizontal_l0.addLayout(self.lay_filterProject)
        self.lay_filters_horizontal_l0.addLayout(self.lay_changeUser)

        self.lay_main.addLayout(self.lay_filters_horizontal_l0)
        self.lay_main.addLayout(self.lay_filters_horizontal_l1)

    def setUserButtonText(self, text):
        self.userButton.setText(text)

# ======================== connects =================================
    def changeUserButton(self):
        self.taskManagerWdg.userServerCore.connectToServer(resetTicket=True)
        self.taskManagerWdg.setUserFunction()
        self.taskManagerWdg.initializeWidgetData()

    def refreshTaskDataButton(self):
        self.setStatusList_comboBox()
        self.taskManagerWdg.refreshTaskData(True)

    def filter_ShotProcess(self, text):
        self.taskManagerWdg.treeWidget.shotFilter = text
        self.taskManagerWdg.completeTree()

    def filter_ProjectProcess(self):
        currCode = self.filterProject_comboBox.currentData()
        currTitle = self.filterProject_comboBox.currentText()
        self.taskManagerWdg.setCurrentProject(currCode, currTitle)
        self.taskManagerWdg.refreshTaskData()
        self.taskManagerWdg.saveActiveProject(currCode)

    def filter_StatusProcess(self):
        self.taskManagerWdg.completeTree()

    def filter_UserProcess(self):
        self.taskManagerWdg.completeTree()

    def filter_ProcessCallback(self):
        self.taskManagerWdg.completeTree()

# ========================= drop list setup =================================
    def setStatusList_comboBox(self):
        self.filterStatus_comboBox.blockSignals(True)
        self.taskManagerWdg.clearCombobBoxWidgetList(self.filterStatus_comboBox)
        statusList = list()
        self.filterStatus_comboBox.addItems(["--no filter"] + self.getStatusList(self.taskManagerWdg.userServerCore.taskData, statusList))
        self.filterStatus_comboBox.blockSignals(False)

    def getStatusList(self, data, statusList=[]):
        for element in data:
            if element.get('children') is not None:
                self.getStatusList(element['children'], statusList)
            elif element.get("status") is not None:
                statusList += [element['status']]
        return list(set(statusList))

    def setUserList_comboBox(self):
        allUsers = self.taskManagerWdg.getAllPrjUsers()
        userList = ["--no filter"] + [user.get('login') for user in allUsers]
        self.taskManagerWdg.clearCombobBoxWidgetList(self.filterUser_comboBox)
        self.filterUser_comboBox.addItems(userList)

    def setProcessList_comboBox(self):
        processList = ["--no filter"] + self.taskManagerWdg.getProcessList()
        self.taskManagerWdg.clearCombobBoxWidgetList(self.filterProcess_comboBox)
        # print(processList)
        self.filterProcess_comboBox.addItems(processList)

    def settProjectList_comboBox(self):
        self.filterProject_comboBox.blockSignals(True)
        projectsData = self.taskManagerWdg.getProjectsData()
        self.taskManagerWdg.clearCombobBoxWidgetList(self.filterProject_comboBox)
        activeProject = self.taskManagerWdg.loadActiveProject()
        prjList = sorted(projectsData, key=lambda x: x.get('code') != activeProject)

        for prjItem in prjList:
            self.filterProject_comboBox.addItem(prjItem.get('title'), prjItem.get('code'))
        currCode = self.filterProject_comboBox.currentData()
        currTitle = self.filterProject_comboBox.currentText()
        self.taskManagerWdg.setCurrentProject(currCode, currTitle)
        self.taskManagerWdg.setServerProject(currCode)
        self.filterProject_comboBox.blockSignals(False)


# if __name__ == "__main__":
#     app = QApplication()
#     app.setStyle(QStyleFactory.create("Fusion"))
#     wdg = FiltersBlockWidget()
#     wdg.show()

#     app.exec_()