import os
import sys
# import time
import xml.etree.ElementTree as ET

from . import tacticDataProcess, tacticPostUtils

from xmlrpc.client import Fault, ProtocolError
from socket import gaierror

tacticApi = os.path.join(os.environ.get('CGPIPELINE'), "tactic", "client")
_lib = os.path.join(os.environ.get('CGPIPELINE'), "_lib")
sys.path += [tacticApi, _lib]

from tactic_client_lib import TacticServerStub
from tactic_client_lib.tactic_server_stub import TacticApiException
from _lib import configUtils

tacticKeyElements = configUtils.tacticKeyElements
tacticAssetElement = configUtils.tacticAssetElement

projectColumns = ["code", "title", "description", "status", "__search_key__"]
episodColumns = ["code", "__search_key__", "search_code", "description", "name"]
shotColumns = ["code", "__search_key__", "search_code", "description", "name", "episodes_code"]
assetColumns = ["code", "__search_key__", "search_code", "description", "name", "episodes_code"]
taskColums = ["code", "__search_key__", "search_code", "assigned", "description", "status", "process"]
userColumns = ["code", "__search_key__", "login", "department", "user_position", "login_groups"]


class userServerCore:
    def __init__(self):
        self.server = None
        self.connected = False
        self.IpAdress = ""
        self.userName = ""
        self.activeProject = {"code": "", "type": ""}
        self.userData = []
        self.isAdmin = False
        self.allUsers = []
        self.taskData = []
        self.userProjects = []
        self.processList = []
        self.pipelineData = []
        self.notesData = []
        self.snapshotNotesData = []

    def connectToServer(self, resetTicket=False):
        try:
            server = TacticServerStub()
        except TacticApiException:
            tacticDataProcess.createSthpwUserFile(os.getlogin())
            server = TacticServerStub()

        print("Connecting to server...")

        if resetTicket:
            if not self.setTicket(server):
                print("Connecting interrupted.")
                return

        try:
            server.ping()
        except Exception as err:
            print(err)
            if not self.setTicket(server):
                print("Connecting interrupted.")
                return

        print("Connection successful.")

        self.connected = True
        self.server = server
        ticketData = tacticDataProcess.getTicketData()
        self.userName = ticketData.get('login')
        self.IpAdress = ticketData.get('IpAdress')
        self.ticket = ticketData.get('ticket')
        self.userData = self.__getUserData(self.userName)
        self.userProjects = self.__getAllUserProjects(self.userName)
        self.isAdmin = tacticPostUtils.checkAdminPremition(server, self.userName)
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
            except ProtocolError as err:
                textErr = 'A protocol error occurred. {} {}'.format(err.errmsg, err.errcode)
                print("URL: %s" % err.url)
                print("Error code: %d" % err.errcode)
                print("Error message: %s" % err.errmsg)
        return True

    def resetProjectData(self, isAllData):
        if not self.userProjects:
            return

        prj_code = self.activeProject.get('code')
        try:
            if isAllData:
                self.taskData = self.__getAllProjectData(prj_code, False)
                self.allUsers = self.__getAllProjecUsers(prj_code)
            else:
                self.taskData = self.__getTaskData(prj_code, False)

            self.pipelineData = self.__getPipelineData(prj_code)
            self.notesData = self.__getNotesData(prj_code)
            self.snapshotNotesData = self.__getSnapshotNotesData(prj_code)
            self.processList = tacticDataProcess.getProcessList(self.taskData)
        except Fault as err:
            print("Premission error: ", err)
            self.cleanServerData()

    def cleanServerData(self):
        self.taskData = []
        self.pipelineData = []
        self.notesData = []
        self.snapshotNotesData = []

    def refreshNotesData(self):
        prj_code = self.activeProject.get('code')
        self.server.set_project(prj_code)
        self.notesData = self.__getNotesData(prj_code)
        self.snapshotNotesData = self.__getSnapshotNotesData(prj_code)

    def getProjectsData(self, readCache=False):
        projectData = self.server.query("sthpw/project", columns=projectColumns)
        projectData = filter(lambda x: x.get('code') not in ["sthpw", "admin"], projectData)
        return list(projectData)

    def getUserProjects(self):
        return self.__getAllUserProjects(self.userName)

    def setServerProject(self, prj_code):
        # if prj_code == self.activeProject['code']:
        #     return
        prj_type = self.server.query("sthpw/project", [("code", prj_code)], columns=["type"])[0].get('type')
        self.server.set_project(prj_code)
        self.activeProject['code'] = prj_code
        self.activeProject['type'] = prj_type

    def getTemplateProjectList(self):
        templates = self.server.query("sthpw/project", [("is_template", "True")], columns=["code"])
        templates = [template.get('code') for template in templates]
        return templates

    def __getUserData(self, userName):
        return self.server.query("sthpw/login", [('code', userName)], columns=userColumns)

    def __getAllProjecUsers(self, prj_code=None):
        allGroups = self.server.query("sthpw/login_group", columns=["code", "access_rules"])

        # Getting groups that are available for current project
        prjGrps = []
        for grp in allGroups:
            rules_xml = grp.get('access_rules')

            ruleList = list(ET.fromstring(rules_xml))
            for rule in ruleList:
                d = rule.attrib
                if d.get('group') == 'project' and (d.get('code') == prj_code or d.get('code') == "*") and d.get('access') == 'allow':
                    prjGrps += [grp.get('code')]
                    break

        # Getting users in this groups 
        exp_userInGrp = tacticDataProcess.getExpression_sObj('sthpw/login_in_group', 'login_group', prjGrps)
        userInGrp = self.server.eval(exp_userInGrp)
        # List of user's codes
        userCodes = [user.get('login') for user in userInGrp]

        # Getting data for this users
        exp_rawUserData = tacticDataProcess.getExpression_sObj('sthpw/login', 'login', userCodes)
        rawUserData = self.server.eval(exp_rawUserData)

        userData = []
        for user in rawUserData:
            userData.append(configUtils.filterDictKeys(user, userColumns))
        return userData

    def __getAllUserProjects(self, user):
        usersGroupData = self.server.query("sthpw/login_in_group", [('login', user)], columns=['login_group'])
        usersGroupList = [grp.get('login_group') for grp in usersGroupData]

        exp = tacticDataProcess.getExpression_sObj('sthpw/login_group', 'code', usersGroupList)
        groupsData = self.server.eval(exp)

        prjList = []
        for grp in groupsData:
            rules_xml = grp.get('access_rules')

            ruleList = list(ET.fromstring(rules_xml))
            for rule in ruleList:
                d = rule.attrib
                if d.get('group') == 'project' and d.get('access') == 'allow':
                    availablePrj = d.get('code')
                    prjList += [(availablePrj)]

        return list(set(prjList))

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
# ============================= GET ALL DATA ==============================================
    def __getAllProjectData(self, prj_code, readCache=False):
        epiSkey = self.getSearchType(tacticKeyElements.get('episode'), prj_code, self.activeProject['type'])
        episodes = self.server.query(epiSkey, columns=episodColumns)

        assetSkey = self.getSearchType(tacticAssetElement.get('asset'), prj_code, self.activeProject['type'])
        assets = self.server.query(assetSkey)

        episodeCode = tacticKeyElements.get('episode') + "_code"
        mainAsstes = [asset for asset in assets if not asset.get(episodeCode)]

        for episod in episodes:
            episod['children'] = self.__getEpisodChildren(prj_code, episod.get('__search_key__'))
        for asset in mainAsstes:
            asset['children'] = self.__getProcessData(asset.get('__search_key__'))
        episodes += mainAsstes
        return episodes

    def __getEpisodChildren(self, prj_code, episodSkey):
        assetSkey = self.getSearchType(tacticAssetElement.get('asset'), prj_code, self.activeProject['type'])
        assets = self.server.query(assetSkey, parent_key=episodSkey, columns=shotColumns)

        shotSkey = self.getSearchType(tacticKeyElements.get('shot'), prj_code, self.activeProject['type'])
        shots = self.server.query(shotSkey, parent_key=episodSkey, columns=shotColumns)
        episodChildren = assets + shots

        for child in episodChildren:
            child['children'] = self.__getProcessData(child.get('__search_key__'))
        return episodChildren

    def __getProcessData(self, itemSkey):
        processData = self.server.query("sthpw/task", parent_key=itemSkey, columns=taskColums)
        return processData

# ============================= GET TASK DATA ==============================================
    def __getTaskData(self, prj_code, readCache=False):
        if readCache:
            return tacticDataProcess.readDiskCache(tacticDataProcess.tacticTaskFileCache)
        else:
            userSearchKey = self.server.build_search_key("sthpw/login", self.userName)
            taskList = self.server.query("sthpw/task", [("project_code", prj_code)], columns=taskColums, parent_key=userSearchKey)
            return self.__collectTaskData(taskList)

    def __collectTaskData(self, childrenList):
        data = []
        hasParent = False
        columns = ["__search_key__", "code", "name", "description", "frames_count"]

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

    def getSearchType(self, itemName, prj_code, dataBase="sthpw"):
        serachType = self.server.build_search_type("/".join([dataBase, itemName]), prj_code)
        return serachType
