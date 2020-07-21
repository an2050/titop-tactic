import os
import sys
# import time
from . import tacticDataProcess

tacticApi = os.path.join(os.environ.get('CGPIPELINE'), "tactic", "client")
_lib = os.path.join(os.environ.get('CGPIPELINE'), "_lib")
sys.path += [tacticApi, _lib]

from tactic_client_lib import TacticServerStub
from _lib import configUtils

class userServerCore:
    def __init__(self):
        self.serverIp = ""
        self.userName = ""
        self.password = ""
        self.connected = False
        self.server = None
        self.project = ""
        self.TaskData = []
        self.pipelineData = []
        self.notesData = []
        self.snapshotNotesData = []

    def connectToServer(self):
        try:
            server = TacticServerStub()
        except:
            tacticDataProcess.createSthpwUserFile(self.userName)
            server = TacticServerStub()

        server.set_server(self.serverIp)
        server.set_project(self.project)
        # print("IP: ", self.serverIp, "User :", self.userName, "Password ", self.password)
        print("Connecting to tactic server...")
        try:
            ticket = server.get_ticket(self.userName, self.password)
            server.set_ticket(ticket)
            self.connected = True
            self.server = server
            print("Connect successful")
            return server
        except (TimeoutError, ConnectionRefusedError):
            print("A connection attempt failed. Check IP adress.")
        except:
            print("Login/Password combination incorrect")

        self.connected = False
        self.taskData = []
        return None

    def refreshTaskData(self):
        if self.connected:
            self.taskData = self.__getTaskData(False)
            self.pipelineData = self.__getPipelineData()
            self.notesData = self.__getNotesData()
            self.snapshotNotesData = self.__getSnapshotNotesData()
            # print(self.pipelineData)

    def refreshNotesData(self):
        self.notesData = self.__getNotesData()
        self.snapshotNotesData = self.__getSnapshotNotesData()

    def getProjecstData(self, readCache=False):
        if self.connected:
            projectData = self.server.query("sthpw/project")
            # tacticDataProcess.saveDiskCache(projectData, tacticDataProcess.tacticProjectFileCache)
        else:
            projectData = ['no connection to server']
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

    def __getTaskData(self, readCache=False):
        if readCache:
            return tacticDataProcess.readDiskCache(tacticDataProcess.tacticTaskFileCache)
        else:
            userSearchKey = self.server.build_search_key("sthpw/login", self.userName)
            try:
                taskList = self.server.query("sthpw/task", [("project_code", self.project)], parent_key=userSearchKey)
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