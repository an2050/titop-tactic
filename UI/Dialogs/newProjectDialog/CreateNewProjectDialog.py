import os
import re
import shutil
from PySide2.QtWidgets import *

from _lib.tactic_lib import tacticPostUtils
from _lib import configUtils, pathUtils

from UI.Dialogs import wdg_utils, simpleDialogs, treeWdg_utils
from UI.Dialogs.parserExcelDialog import ParserExcelDataWidget
from . import headerProjectWidget


class NewProjectDialog(QDialog):
    def __init__(self, parent, userServerCore):
        super(NewProjectDialog, self).__init__(parent)

        self.userServerCore = userServerCore
        self.server = self.userServerCore.server

        self.prjCode = ""
        self.episodeSType = ""
        self.shotSType = ""
        self.processes = [configUtils.tacticProcessElements.get('comp')]

        self.setMinimumSize(720, 480)

        self.lay_main = QVBoxLayout()
        self.setLayout(self.lay_main)

# ====================== WIDGETS ===============================
        # - project name, etc
        self.headersFields = headerProjectWidget.HeaderProjectFields(self, self.userServerCore)
        # - PRM Path
        self.prmPathLable = QLabel('PRM folder')
        self.prmPathField = QLineEdit()
        self.prmPathButton = QPushButton("...")
        self.prmPathButton.setMaximumWidth(25)
        prmWidgetsList = [self.prmPathLable, self.prmPathField, self.prmPathButton]
        self.lay_prmPath = wdg_utils.arrangeHorizontalLayout(*prmWidgetsList)
        # - ecxel parser block
        self.parserExcelDataWidget = ParserExcelDataWidget.MainItnputDataWidget(self)
        self.createProjectButton = QPushButton('Create project')
        self.cancelButton = QPushButton('Cancel')
# ===================== CONNECTS ================================
        self.prmPathButton.clicked.connect(self.selectPrmFolder)
        self.createProjectButton.clicked.connect(self.projectCreatioinProcess)
        self.cancelButton.clicked.connect(self.reject)
# ==============================================================
        self.lay_main.addLayout(self.headersFields.lay_main)
        self.lay_main.addLayout(self.lay_prmPath)
        self.lay_main.addLayout(self.parserExcelDataWidget.lay_main)
        self.lay_main.addWidget(self.createProjectButton)
        self.lay_main.addWidget(self.cancelButton)
        # self.lay_main.addStretch()

    def selectPrmFolder(self):
        lastFolder = self.prmPathField.text()
        # self.prmPathField.setText("")
        path = wdg_utils.showQFolderDialog(self, "Select prm folder", lastFolder)
        if path:
            self.prmPathField.setText(path)

    def projectCreatioinProcess(self):
        prjTitle = self.headersFields.nameField.text()
        if not prjTitle:
            print("Enter prject title please.")
            return
        if re.search(r'^\d|[^\w^\ ]', prjTitle):
            print("Name cannot contain special characters or start with a number")
            return
        self.prjCode = re.sub(r'\W', '_', prjTitle).lower()
        prjTemplate = self.headersFields.templateList.currentText()

        treeData = self.parserExcelDataWidget.treeData
        if not treeData:
            text = "Shots not found."
            info = "Do you want to continue?"
            msg = simpleDialogs.MessageDialog(self)

            if msg.showDialog(text, info) is False:
                return

        elif not self.prmPathField.text():
            text = "The prm path is not specified."
            info = "Do you want to continue?"
            msg = simpleDialogs.MessageDialog(self)

            if msg.showDialog(text, info) is False:
                return
        else:
            wastePrmFiles, shotsNoPrm, prmPathData = self.checkPrmFiles(treeData)
            if wastePrmFiles or shotsNoPrm:
                text = "Detected inconsistencies prm files."
                info = "Do you want to continue creating the project?"
                detailed = "\nWASTE PRM FILES ARE: \n\t{} \nLOST PRM FILES FOR SHOTS:\n\t{}".format("\n".join(wastePrmFiles), "\n".join(shotsNoPrm))
                msg = simpleDialogs.MessageDialog(self)

                if msg.showDialog(text, info, detailed) is False:
                    return

            text = "Do you want to copy files to project directory?."
            msg = simpleDialogs.MessageDialog(self)
            if msg.showDialog(text):
                self.copyPrmFiles(prmPathData)

        prjSuccess = self.createProject(prjTemplate, prjTitle)
        if not prjSuccess:
            return
        self.createFolderSturcture(treeData)

        self.createTasks(treeData)

        print("Process finished!")
        self.accept()

    def createProject(self, prjTemplate, prjTitle):
        newProject = tacticPostUtils.createNewProject(self.server, self.prjCode, prjTemplate, prjTitle)
        if newProject is None:
            return
        print("Project '{}' has been created.".format(self.prjCode))
        return True

    def createFolderSturcture(self, treeData):
        prjStructureConfig = configUtils.projectStructureConfigFile
        treeFolderStructure = configUtils.loadConfigData(prjStructureConfig)
        paths = treeWdg_utils.getPathsData(treeFolderStructure)
        pathCollection = self.collectAllPaths(paths, self.prjCode, treeData)
        self.createFolders(pathCollection)

    def createFolders(self, pathCollection):
        for path in pathCollection:
            try:
                os.makedirs(path)
            except FileExistsError:
                continue

    def collectAllPaths(self, paths, prjCode, treeData):
        pathCollection = []
        for path in paths:
            path = re.sub(r'{projectName}', prjCode, "/".join(path))
            matchEpisod = re.search(r"{episodName}", path)
            if matchEpisod:
                for item in treeData:
                    newPath = re.sub(r'{episodName}', item.get('name'), path)
                    matchShot = re.search(r"{shotName}", path)
                    if not matchShot:
                        pathCollection.append(newPath)
                        continue
                    for child in item.get('children'):
                        pathCollection.append(re.sub(r'{shotName}', child.get('name'), newPath))
            else:
                pathCollection.append(path)
        return pathCollection

    def createTasks(self, treeData):
        self.server.set_project(self.prjCode)
        self.episodeSType, self.shotSType = self.getEpisodeShotSkey(self.prjCode)
        self.writeTaskData(treeData)
        self.server.set_project(self.userServerCore.activeProject)

    def checkPrmFiles(self, treeData):
        if not self.prmPathField.text():
            print("Prm path not found.")
            return

        prmDirs = []
        prmFiles = []
        for rootDir, folders, files in os.walk(self.prmPathField.text()):
            for file in files:
                if ".mov" in file or ".mp4" in file:
                    prmDirs.append(rootDir)
                    prmFiles.append(file)

        wastePrmFiles = list(prmFiles)
        shotsNoPrm = []
        prmPathData = []
        keyPrjData = {'project': self.prjCode, 'episod': None, 'shot': None}

        for episod in treeData:

            keyPrjData['episod'] = episod.get('name')
            for shot in episod.get('children'):

                found = False
                shotName = shot.get('name')
                for idx, file in enumerate(prmFiles):

                    if shotName in file:
                        wasteIdx = wastePrmFiles.index(file)
                        wastePrmFiles.pop(wasteIdx)

                        srcPath = "/".join([prmDirs[idx], prmFiles[idx]])
                        destPath = "/".join([pathUtils.getPRM_Path(keyPrjData), prmFiles[idx]])
                        prmPathData.append((srcPath, destPath))
                        found = True

                if found is False:
                    shotsNoPrm.append(shotName)

        return wastePrmFiles, shotsNoPrm, prmPathData

    def copyPrmFiles(self, prmPathData):
        amount = len(prmPathData)
        counter = 0
        for prmPath in prmPathData:
            counter += 1
            try:
                shutil.copyfile(prmPath[0], prmPath[1])
            except FileNotFoundError:
                os.makedirs(os.path.dirname(prmPath[1]))
                shutil.copyfile(prmPath[0], prmPath[1])
        print("File copyin gprocess...", str(counter / amount * 100), "%")

    def writeTaskData(self, treeData, episodeCode=""):
        for data in treeData:
            print("- Creating:", data.get('name'), "...")
            if "children" in list(data.keys()):
                episode = tacticPostUtils.createSObject(self.server, self.episodeSType, {"name": data.get('name')})
                episodeCode = episode.get('code')
                self.writeTaskData(data.get('children'), episodeCode)

            else:
                shotData = data.copy()
                shotData['episode_code'] = episodeCode
                shot = tacticPostUtils.createSObject(self.server, self.shotSType, shotData)
                task = tacticPostUtils.createTask(self.server, shot.get('__search_key__'), self.processes[0])
                try:
                    tacticPostUtils.updateSobject(self.server, task.get('__search_key__'),
                                                  {"status": configUtils.tacticStatusElements.get('Assignment')})
                except:
                    tacticPostUtils.updatePipelineDependencies(self.server, self.prjCode)
                    tacticPostUtils.updateSobject(self.server, task.get('__search_key__'),
                                                  {"status": configUtils.tacticStatusElements.get('Assignment')})

    def getEpisodeShotSkey(self, prjCode):
        episodeItem = configUtils.tacticKeyElements.get('episode')
        shotItem = configUtils.tacticKeyElements.get('shot')
        mainProject = self.userServerCore.mainProject
        episodSKey = self.userServerCore.getSearchType(episodeItem, prjCode, mainProject)
        shotSKey = self.userServerCore.getSearchType(shotItem, prjCode, mainProject)
        return episodSKey, shotSKey
