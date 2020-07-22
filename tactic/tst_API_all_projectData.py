import os
import sys

tacticAPI_path = os.path.join(os.path.abspath("."), "client", "tactic_client_lib")
sys.path += [tacticAPI_path]

import tactic_server_stub

serverIp = "192.168.88.200"
project = "main"
userName = "zaem0"
password = "123"

try:
    server = tactic_server_stub.TacticServerStub()
except:
    # tacticDataProcess.createSthpwUserFile(userName)
    server = tactic_server_stub.TacticServerStub()

server.set_server(serverIp)
server.set_project(project)

try:
    ticket = server.get_ticket(userName, password)
    server.set_ticket(ticket)
    print("Connect successful")
except (TimeoutError, ConnectionRefusedError):
    print("A connection attempt failed. Check IP adress.")
except:
    print("Login/Password combination incorrect")


columns = ["__search_key__", "search_code", "description"]
taskColums = ["assigned", "__search_key__", "search_code", "description", "status", "process"]

def getAllProjectData():
    episodes = server.query("main/episodes", columns=columns)
    assets = server.query("main/asset", columns=[])
    # print(episodes)
    for episod in episodes:
        episod['children'] = getEpisodChildren(episod.get('__search_key__'))
    episodes += [asset for asset in assets if not asset.get('episodes_code')]
    return episodes

def getEpisodChildren(sKey):
    assets = server.query("main/asset", parent_key=sKey, columns=columns)
    shots = server.query("default/shots", parent_key=sKey, columns=columns)

    episodChildren = assets + shots

    for child in episodChildren:
        child['children'] = getTaskData(child.get('__search_key__'))
    return episodChildren


def getTaskData(sKey):
    taskData = server.query("sthpw/task", parent_key=sKey, columns=taskColums)
    return taskData


    # print(" == ASSET == ", assets, " == ASSET == ")
# def __getTaskData():
#     userSearchKey = server.build_search_key("sthpw/login", userName)

#     taskList = server.query("sthpw/task", [("project_code", project)], columns=["__search_key__", "search_code__", "description", "status", "process"], parent_key=userSearchKey)
#     # print(taskList)
#     return __collectTaskData(taskList)


# def __collectTaskData(childrenList):
#     data = []
#     columns = ["__search_key__", "code", "name", "description"]
#     hasParent = False

#     for child in childrenList:
#         parent = server.get_parent(child.get('__search_key__'))

#         parent = filterDictKeys(parent, columns)

#         if parent == {}:
#             data.append(child)
#             continue
#         else:
#             hasParent = True

#         parentSKey = parent.get("__search_key__")
#         exists = False
#         idx = 0
#         for i, d in enumerate(data):
#             if d['__search_key__'] == parentSKey:
#                 idx = i
#                 exists = True
#                 break

#         if exists is False:
#             parent['children'] = [child]
#             data.append(parent)
#         else:
#             data[idx]['children'] += [child]

#     if hasParent:
#         return __collectTaskData(data)
#     else:
#         return(data)

def filterDictKeys(d, keys):
    filteredDict = dict()
    for key in d:
        if key in keys:
            filteredDict[key] = d[key]
    return filteredDict

# def getWatchFiles(__paths_dict__):
#     watchFilePaths = [__paths_dict__[key][0] for key in list(__paths_dict__.keys()) if key not in ['web', 'icon']]
#     return watchFilePaths

# # print(__getTaskData())

# def __getTaskData():
    # userSearchKey = server.build_search_key("sthpw/login", userName)

    # taskList = server.query("sthpw/task", [("project_code", project)], columns=["__search_key__", "search_code__", "description", "status", "process"], parent_key=userSearchKey)
    # print(taskList)
    # for i in range(20):
    #     # episodes2 = server.query("main/episodes")
    #     task = server.query("sthpw/task")
    #     print("=========")
    # shotes = server.query("default/shots", [('episodes_code', 'EPISODES00002')])
    # expressinResult = server.eval("@GET(main/episodes.default/shots.sthpw/task.process)")
    # expressinResult = server.eval("@SOBJECT(main/episodes.default/shots.sthpw/task)")
    # for i in range(20):
    #     task = server.eval("@SOBJECT(sthpw/task)", ['default/shots?project=main&code=SHOTS00002', 'default/shots?project=main&code=SHOTS00004'])
    #     print("=========")
    # return task


print(getAllProjectData())

