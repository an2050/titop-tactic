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

def getWatchFiles(__paths_dict__):
    watchFilePaths = [__paths_dict__[key][0] for key in list(__paths_dict__.keys()) if key not in ['web', 'icon']]
    return watchFilePaths

# print(__getTaskData())

# taskList = server.query("sthpw/note", [("project_code", project)], ["note", "process", "search_code"])
# print(taskList)
# snpshot = server.query("sthpw/snapshot", [("project_code", project), ("search_type", "sthpw/note"), ("context", "notes/attachment"), ("search_code", "NOTE00236")], ["snapshot", "__search_key__"])
snapshots = server.query_snapshots([("project_code", project), ("search_type", "sthpw/note"), ("context", "notes/attachment")], include_paths_dict=True)
columns = ["__search_key__", "__paths_dict__", "search_code"]

snapshots = [filterDictKeys(snap, columns) for snap in snapshots]
for i, snapshot in enumerate(snapshots):
    snapshot['watchFilePaths'] = getWatchFiles(snapshot.get('__paths_dict__'))
#     snpshots[i] = filterDictKeys(snapshot, columns)
    del snapshot['__paths_dict__']

# if "__paths_dict__" in snapshot:
#     rawPathDict = snapshot.get('__paths_dict__')
#     watchFilePaths = [rawPathDict[key][0] for key in list(rawPathDict.keys()) if key not in ['web', 'icon']]
#     # print(watchFilePaths)
    # snapshot['watcFiles'] = watchFilePaths
print(snapshots)
# paths = server.get_paths("sthpw/note?code=NOTE00236", context="notes/attachment", version=-1, file_type='f0', level_key=None, single=False, versionless=False)
# print(paths)