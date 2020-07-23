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

class userServerCore:
    def __init__(self):
        self.serverIp = ""
        self.userName = ""
        self.password = ""
        self.connected = False
        self.server = None
        # self.project = ""
        self.taskData = []
        self.pipelineData = []
        self.notesData = []
        self.snapshotNotesData = []

        self.projectClms = ["code", "title", "description", "status", "__search_key__"]

        # self.epiColumns = ["__search_key__", "search_code", "description", "name"]
        # self.shotColumns = ["__search_key__", "search_code", "episodes_code", "description", "name"]
        # self.assetColumns = ["__search_key__", "search_code", "episodes_code", "description", "name"]
        # self.taskColums = ["assigned", "__search_key__", "search_code", "description", "status", "process"]

    def connectToServer(self):
        try:
            server = TacticServerStub()
        except TacticApiException:
            tacticDataProcess.createSthpwUserFile(os.getlogin())
            server = TacticServerStub()

        print("Connecting to server...")
        try:
            server.ping()
        except (AttributeError, Fault):

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

        self.connected = True
        self.server = server
        self.userName = tacticDataProcess.getTicketData().get('login')
        self.IpAdress = tacticDataProcess.getTicketData().get('IpAdress')
        self.ticket = tacticDataProcess.getTicketData().get('ticket')
        # return server

    # def setCredential(sefl):
    #     credential = tacticDataProcess.getCredentialDialog()
    #     if credential is None:
    #         return
    #     print("Input new credential")
    #     serverIp = "192.168.88.197"
    #     userName = credential.get('userName')
    #     password = credential.get('password')

        # server.set_server(self.serverIp)
        # server.set_project(self.project)
        # # print("IP: ", self.serverIp, "User :", self.userName, "Password ", self.password)
        # print("Connecting to tactic server...")
        # try:
        #     ticket = server.get_ticket(self.userName, self.password)
        #     server.set_ticket(ticket)
        #     self.connected = True
        #     self.server = server
        #     print("Connect successful")
        #     return server
        # except (TimeoutError, ConnectionRefusedError):
        #     print("A connection attempt failed. Check IP adress.")
        # except:
        #     print("Login/Password combination incorrect")

        # self.connected = False
        # self.taskData = []
        # return None

    def refreshTaskData(self, prj_code):
        if self.connected:
            self.taskData = self.__getTaskData(prj_code, False)
            self.pipelineData = self.__getPipelineData()
            self.notesData = self.__getNotesData()
            self.snapshotNotesData = self.__getSnapshotNotesData()
            # print(self.pipelineData)

    def refreshNotesData(self):
        self.notesData = self.__getNotesData()
        self.snapshotNotesData = self.__getSnapshotNotesData()

    def getProjecstData(self, readCache=False):
        # if self.connected:
        # print(server.query('sthpw/project', columns=["code"]))
        projectData = self.server.query("sthpw/project", columns=self.projectClms)
        projectData = filter(lambda x: x.get('code') not in ["sthpw", "admin"], projectData)
            # tacticDataProcess.saveDiskCache(projectData, tacticDataProcess.tacticProjectFileCache)
        # else:
        #     projectData = ['no connection to server']
        return projectData

    def __getPipelineData(self, filters=[], readCache=False):
        filters = [("project_code", self.project), ("search_type", "sthpw/task")]
        pipelineData = self.server.query("sthpw/pipeline", filters)
        return pipelineData

    def __getNotesData(self):
        filters = [("project_code", self.project)]
        fields = ["search_code", "code", "process", "note", "login", "timestamp"]
        notesData = self.server.query("sthpw/note", filters, fields)
        return notesData

    def __getSnapshotNotesData(self):
        snapshots = self.server.query_snapshots([("project_code", self.project), ("search_type", "sthpw/note"), ("context", "notes/attachment")], include_paths_dict=True)
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


    # def __getTaskData(self, readCache=False):
    #     episodes = self.server.query("main/episodes", columns=self.epiColumns)
    #     assets = self.server.query("main/asset", columns=self.assetColumns)
    #     mainAsstes = [asset for asset in assets if not asset.get('episodes_code')] 
    #     print('+++++++++', mainAsstes)

    #     # episodes += [asset for asset in assets if not asset.get('episodes_code')]
    #     for episod in episodes:
    #         episod['children'] = self.getEpisodChildren(episod.get('__search_key__'))
    #     for asset in mainAsstes:
    #         asset['children'] = self.getTaskData(asset.get('__search_key__'))
    #     episodes += mainAsstes
    #     return episodes

    # def getEpisodChildren(self, sKey):
    #     assets = self.server.query("main/asset", parent_key=sKey, columns=self.shotColumns)
    #     shots = self.server.query("default/shots", parent_key=sKey, columns=self.shotColumns)
    #     episodChildren = assets + shots

    #     for child in episodChildren:
    #         child['children'] = self.getTaskData(child.get('__search_key__'))
    #     return episodChildren


    # def getTaskData(self, sKey):
    #     taskData = self.server.query("sthpw/task", parent_key=sKey, columns=self.taskColums)
    #     return taskData






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