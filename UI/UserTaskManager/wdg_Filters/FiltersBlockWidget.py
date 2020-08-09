from PySide2.QtWidgets import *
from PySide2.QtCore import Qt

from UI.Dialogs import wdg_utils

class FiltersBlockWidget(QWidget):

    def __init__(self, taskManagerWdg):
        super(FiltersBlockWidget, self).__init__(taskManagerWdg)

        self.taskManagerWdg = taskManagerWdg

        self.lay_main = QVBoxLayout()

        # - main layout levels
        self.lay_filters_horizontal_l0 = QHBoxLayout()
        self.lay_filters_horizontal_l1 = QHBoxLayout()
        # ===================== WIDGETS =================================
        # - filter prject
        self.filterProject_comboBox = QComboBox(self)
        self.filterProject_comboBox.setMinimumSize(150, 20)

        # - filter shot field -
        self.filterShot_Lable = QLabel(self)
        self.filterShot_Lable.setText("     Shot:")
        self.filterShotField = QLineEdit(self)
        self.filterShotField.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.filterShot_blockLayout = wdg_utils.getHorizontalBlockLayout(self.filterShot_Lable, self.filterShotField)

        # - filter process -
        self.filterProcess_Lable = QLabel(self)
        self.filterProcess_Lable.setText("Process:")
        self.filterProcess_comboBox = QComboBox(self)
        self.filterProcess_comboBox.setMinimumSize(150, 25)
        self.filterProcess_blockLayout = wdg_utils.getHorizontalBlockLayout(self.filterProcess_Lable, self.filterProcess_comboBox)

        # - filter status -
        self.filterStatus_Lable = QLabel(self)
        self.filterStatus_Lable.setText("Status:")
        self.filterStatus_comboBox = QComboBox(self)
        self.filterStatus_comboBox.setMinimumSize(150, 25)
        self.filterStatus_blockLayout = wdg_utils.getHorizontalBlockLayout(self.filterStatus_Lable, self.filterStatus_comboBox)
        # - filter user -
        self.filterUser_Lable = QLabel(self)
        self.filterUser_Lable.setText("User:")
        self.filterUser_comboBox = QComboBox(self)
        self.filterUser_comboBox.setMinimumSize(150, 25)
        self.filterUser_blockWidget = wdg_utils.getHorizontalBlockWidget(self.filterUser_Lable, self.filterUser_comboBox)

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
        self.filterProject_blockLayout = wdg_utils.getHorizontalBlockLayout(self.filterProject_comboBox, self.refreshButton)

        self.lay_filters_horizontal_l0.addLayout(self.filterShot_blockLayout)
        self.lay_filters_horizontal_l0.addLayout(self.filterProject_blockLayout)
        self.lay_filters_horizontal_l0.addWidget(self.userButton)
        # self.lay_filters_horizontal_l0.addStretch()

        self.lay_filters_horizontal_l1.addLayout(self.filterProcess_blockLayout)
        self.lay_filters_horizontal_l1.addLayout(self.filterStatus_blockLayout)
        self.lay_filters_horizontal_l1.addWidget(self.filterUser_blockWidget)
        # self.lay_filters_horizontal_l1.addStretch()

        self.lay_main.addLayout(self.lay_filters_horizontal_l0)
        self.lay_main.addLayout(self.lay_filters_horizontal_l1)

    def setUserButtonText(self, text):
        self.userButton.setText(text)

# ======================== connects =================================
    def changeUserButton(self):
        if not self.taskManagerWdg.userServerCore.connectToServer(resetTicket=True):
            return
        self.taskManagerWdg.setUserPosition()
        self.taskManagerWdg.initializeWidgetData()

    def refreshTaskDataButton(self):
        self.settProjectList_comboBox()
        self.taskManagerWdg.refreshTaskData(True)

    def filter_ShotProcess(self, text):
        self.taskManagerWdg.treeWidget.shotFilter = text
        self.taskManagerWdg.completeTree()

    def filter_ProjectProcess(self):
        currCode = self.filterProject_comboBox.currentData()
        if not currCode:
            return
        self.taskManagerWdg.saveActiveProject(currCode)
        self.taskManagerWdg.setServerProject(currCode)
        self.taskManagerWdg.refreshTaskData()

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
        self.filterProcess_comboBox.addItems(processList)

    def settProjectList_comboBox(self):
        userProjectsList = set(self.taskManagerWdg.getUserProjects())
        if not userProjectsList:
            return
        allProjects = self.taskManagerWdg.getProjectsData()
        if "*" not in userProjectsList:
            allProjects = filter(lambda x: x.get('code') in userProjectsList, allProjects)

        self.taskManagerWdg.clearCombobBoxWidgetList(self.filterProject_comboBox)

        activeProject = self.taskManagerWdg.loadActiveProject()
        prjList = sorted(allProjects, key=lambda x: x.get('code') != activeProject)

        self.filterProject_comboBox.blockSignals(True)
        for prjItem in prjList:
            self.filterProject_comboBox.addItem(prjItem.get('title'), prjItem.get('code'))
        self.filterProject_comboBox.blockSignals(False)

        currCode = self.filterProject_comboBox.currentData()
        self.taskManagerWdg.setServerProject(currCode)

