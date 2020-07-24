import os
import sys
# import time
from . import tacticDataProcess

from xmlrpc.client import Fault
from socket import gaierror

tacticApi = os.path.join(os.environ.get('CGPIPELINE'), "tactic", "client")
_lib = os.path.join(os.environ.get('CGPIPELINE'), "_lib")
sys.path += [tacticApi, _lib]

from tactic_client_lib import TacticServerStub
from tactic_client_lib.tactic_server_stub import TacticApiException
from _lib import configUtils

tacticKeyElements = configUtils.tacticKeyElements
tacticAssetElement = configUtils.tacticAssetElement

episodColumns = ["__search_key__", "search_code", "description", "name"]
shotColumns = ["__search_key__", "search_code", "episodes_code", "description", "name"]
assetColumns = ["__search_key__", "search_code", "episodes_code", "description", "name"]
taskColums = ["assigned", "__search_key__", "search_code", "description", "status", "process"]
userColumns = ["code", "login", "department", "function", "login_groups", "__search_key__"]

class userServerCore:
    def __init__(self):
        self.server = None
        self.connected = False
        self.IpAdress = ""
        self.userName = ""
        self.mainProject = ""

        self.userData = []
        self.taskData = []
        self.pipelineData = []
        self.notesData = []
        self.snapshotNotesData = []

        self.projectClms = ["code", "title", "description", "status", "__search_key__"]

    def connectToServer(self, resetTicket=False):
        try:
            server = TacticServerStub()
        except TacticApiException:
            tacticDataProcess.createSthpwUserFile(os.getlogin())
            server = TacticServerStub()

        print("Connecting to server...")

        if resetTicket:
            self.setTicket(server)

        try:
            server.ping()
        except (AttributeError, Fault):
            if self.setTicket(server) is None:
                return

        print("Connection successful.")

        self.connected = True
        self.server = server
        ticketData = tacticDataProcess.getTicketData()
        self.userName = ticketData.get('login')
        self.IpAdress = ticketData.get('IpAdress')
        self.ticket = ticketData.get('ticket')
        self.mainProject = ticketData.get('project')
        self.userData = self.__getUserData(self.userName)
        return True

    def setTicket(self, server):
        _input = False
        textErr = ""
        while _input is False:
            userInput = tacticDataProcess.getCredentialDialog(textErr)
            if userInput is None:
                return

            userName, password, serverIp = [userInput.get('userName'), userInput.get('password'), userInput.get('IpAdress')]
            server.set_server(serverIp)

            try:
                newTicket = server.get_ticket(userName, password)
                server.set_login_ticket(newTicket)
                tacticDataProcess.storeUserTicket(serverIp, userName, newTicket)
                _input = True
            except Fault:
                textErr = "Login/Password combination incorrect"
                print(textErr)
            except (gaierror):
                textErr = "Socket problem"
                print(textErr)
            except (TimeoutError, ConnectionRefusedError):
                textErr = "A connection attempt failed. Check IP adress."
                print(textErr)
        return True

    def resetProjectData(self, prj_code, isTaskData):
        if isTaskData:
            self.taskData = self.__getTaskData(prj_code, False)
        else:
            self.taskData = self.__getAllProjectData(prj_code, False)

        self.pipelineData = self.__getPipelineData(prj_code)
        self.notesData = self.__getNotesData(prj_code)
        self.snapshotNotesData = self.__getSnapshotNotesData(prj_code)
        # print(self.pipelineData)

    def refreshNotesData(self, prj_code):
        self.notesData = self.__getNotesData(prj_code)
        self.snapshotNotesData = self.__getSnapshotNotesData(prj_code)

    def getProjecstData(self, readCache=False):
        # if self.connected:
        # print(server.query('sthpw/project', columns=["code"]))
        projectData = self.server.query("sthpw/project", columns=self.projectClms)
        projectData = filter(lambda x: x.get('code') not in ["sthpw", "admin"], projectData)
            # tacticDataProcess.saveDiskCache(projectData, tacticDataProcess.tacticProjectFileCache)
        # else:
        #     projectData = ['no connection to server']
        return projectData

    def __getUserData(self, userName):
        return self.server.query("sthpw/login", [('code', userName)], columns=userColumns)

    def __getPipelineData(self, prj_code, filters=[], readCache=False):
        filters = [("project_code", prj_code), ("search_type", "sthpw/task")]
        pipelineData = self.server.query("sthpw/pipeline", filters)
        return pipelineData

    def __getNotesData(self, prj_code):
        filters = [("project_code", prj_code)]
        fields = ["search_code", "code", "process", "note", "login", "timestamp"]
        notesData = self.server.query("sthpw/note", filters, fields)
        return notesData

    def __getSnapshotNotesData(self, prj_code):
        snapshots = self.server.query_snapshots([("project_code", prj_code), ("search_type", "sthpw/note"), ("context", "notes/attachment")], include_paths_dict=True)
        columns = ["__search_key__", "__paths_dict__", "search_code"]
        snapshots = [configUtils.filterDictKeys(snap, columns) for snap in snapshots]
        for i, snapshot in enumerate(snapshots):
            snapshot['watchFilePaths'] = self.__getWatchFiles(snapshot.get('__paths_dict__'))
            del snapshot['__paths_dict__']
        return snapshots

    def __getWatchFiles(self, __paths_dict__):
        watchFilePaths = [__paths_dict__[key][0] for key in list(__paths_dict__.keys()) if key not in ['web', 'icon']]
        return watchFilePaths

# =================== read server data ======================================
    def __getAllProjectData(self, prj_code, readCache=False):
        print("mainProject === ", self.mainProject)
        print("prj_code = ", prj_code)
        print("itemName === ", tacticKeyElements.get('episode'))
        epiSkey = self.getSearchType(self.mainProject, tacticKeyElements.get('episode'), prj_code)
        print(epiSkey)
        episodes = self.server.query(epiSkey, columns=episodColumns)
        # print(episodes)

        assetSkey = self.getSearchType(self.mainProject, tacticAssetElement.get('asset'), prj_code)
        assets = self.server.query(assetSkey)
        # print(assets)

        episodeCode = tacticKeyElements.get('episode') + "_code"
        mainAsstes = [asset for asset in assets if not asset.get(episodeCode)]
        # print('+++++++++', mainAsstes)

    #     # episodes += [asset for asset in assets if not asset.get('episodes_code')]
        for episod in episodes:
            episod['children'] = self.__getEpisodChildren(prj_code, episod.get('__search_key__'))
        for asset in mainAsstes:
            asset['children'] = self.__getProcessData(asset.get('__search_key__'))
        episodes += mainAsstes
        return episodes

    def __getEpisodChildren(self, prj_code, episodSkey):
        assetSkey = self.getSearchType(self.mainProject, tacticAssetElement.get('asset'), prj_code)
        assets = self.server.query(assetSkey, parent_key=episodSkey, columns=shotColumns)

        shotSkey = self.getSearchType(self.mainProject, tacticKeyElements.get('shot'), prj_code)
        shots = self.server.query(shotSkey, parent_key=episodSkey, columns=shotColumns)
        episodChildren = assets + shots

        for child in episodChildren:
            child['children'] = self.__getProcessData(child.get('__search_key__'))
        return episodChildren

    def __getProcessData(self, itemSkey):
        processData = self.server.query("sthpw/task", parent_key=itemSkey, columns=taskColums)
        return processData






    def __getTaskData(self, prj_code, readCache=False):
        if readCache:
            return tacticDataProcess.readDiskCache(tacticDataProcess.tacticTaskFileCache)
        else:
            userSearchKey = self.server.build_search_key("sthpw/login", self.userName)
            try:
                taskList = self.server.query("sthpw/task", [("project_code", prj_code)], parent_key=userSearchKey)
            except:
                print("No have premission for prject '{}'".format(self.project))
                return None

            return self.__collectTaskData(taskList)

    def __collectTaskData(self, childrenList):
        data = []
        hasParent = False
        columns = ["__search_key__", "code", "name", "description"]

        for child in childrenList:
            parent = self.server.get_parent(child.get('__search_key__'))

            parent = configUtils.filterDictKeys(parent, columns)

            if parent == {}:
                data.append(child)
                continue
            else:
                hasParent = True

            parentSKey = parent.get("__search_key__")
            child["parent_search_key"] = parentSKey

            exists = False
            idx = 0
            for i, d in enumerate(data):
                if d['__search_key__'] == parentSKey:
                    idx = i
                    exists = True
                    break

            if exists is False:
                parent['children'] = [child]
                data.append(parent)
            else:
                data[idx]['children'] += [child]

        if hasParent:
            return self.__collectTaskData(data)
        else:
            tacticDataProcess.saveDiskCache(data, tacticDataProcess.tacticTaskFileCache)
            return(data)
# ======================================================================

    def getSearchType(self, itemName, prj_code, mainPrj="sthpw"):
        serachType = self.server.build_search_type("/".join([mainPrj, itemName]), prj_code)
        return serachType

    def updateTaskData(self, searchKey, data):
        if self.connected:
            self.server.update(searchKey, data)


if __name__ == "__main__":
    serverIp = "192.168.1.249:9000"
    project = "avanpost"
    userName = ""
    password = "123"

    userServerCore = userServerCore()
    # projectsData = userServerCore.projecsData
    # data = userServerCore.filterElementsData(userServerCore.projectsData, [("code", "t34")], ["type", "id", "title"])
    # print(data)