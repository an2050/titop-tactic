from PySide2.QtWidgets import *
from UI.UserTaskManager.utils import rvPlayerUtils

class rvButtonsTM():

    def __init__(self, taskManagerWdg):
        self.taskManagerWdg = taskManagerWdg
        self.project = self.taskManagerWdg.project

        self.itemsUtils = self.taskManagerWdg.itemsUtils

        self.lay_rvButtons = QVBoxLayout()

        self.watchPrmButton = QPushButton('watchPrm')
        self.watchDailiesButton = QPushButton('watchDailies')
        self.watchHiResButton = QPushButton('watchHires')
        self.watchSRCButton = QPushButton('watchSRC')
        self.watchPreviewButton = QPushButton('watchPreview')

        self.watchPrmButton.clicked.connect(self.watchPrm)
        self.watchDailiesButton.clicked.connect(self.watchDailies)
        self.watchHiResButton.clicked.connect(self.watchHires)
        self.watchSRCButton.clicked.connect(self.watchSRC)
        self.watchPreviewButton.clicked.connect(self.watchPreview)

        # ======================= LAYOUT SETUP ===============================
        self.lay_rvButtons.addWidget(self.watchPrmButton)
        self.lay_rvButtons.addWidget(self.watchDailiesButton)
        self.lay_rvButtons.addWidget(self.watchHiResButton)
        self.lay_rvButtons.addWidget(self.watchSRCButton)
        self.lay_rvButtons.addWidget(self.watchPreviewButton)

    def getProject(self):
        project = self.taskManagerWdg.project
        return project

    def watchPrm(self):
        selectectedItems = self.itemsUtils.getSelected_shotItems()
        rvPlayerUtils.watchPrm(self.getProject(), selectectedItems)

    def watchDailies(self):
        selectectedItems = self.itemsUtils.getSelected_shotItems()
        rvPlayerUtils.watchDailies(self.getProject(), selectectedItems)

    def watchHires(self):
        selectectedItems = self.itemsUtils.getSelected_shotItems()
        rvPlayerUtils.watchHires(self.getProject(), selectectedItems)

    def watchSRC(self):
        selectectedItems = self.itemsUtils.getSelected_shotItems()
        rvPlayerUtils.watchSRC(self.getProject(), selectectedItems)

    def watchPreview(self):
        selectectedItem = self.itemsUtils.getSelected_ProcessItem()
        rvPlayerUtils.watchPreview(self.getProject(), selectectedItem)
