import os
import sys

tacticAPI_path = os.path.join(os.path.abspath("."), "client", "tactic_client_lib")
sys.path += [tacticAPI_path]

import tactic_server_stub

serverIp = "192.168.88.197"
project = "titop"
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


def __getTaskData():
    userSearchKey = server.build_search_key("sthpw/login", userName)

    taskList = server.query("sthpw/task", [("project_code", project)], columns=["__search_key__", "search_code", "description", "status", "process"], parent_key=userSearchKey)
    # print(taskList)
    return __collectTaskData(taskList)


def __collectTaskData(childrenList):
    data = []
    columns = ["__search_key__", "code", "name", "description"]
    hasParent = False

    for child in childrenList:
        parent = server.get_parent(child.get('__search_key__'))

        parent = filterDictKeys(parent, columns)

        if parent == {}:
            data.append(child)
            continue
        else:
            hasParent = True

        parentSKey = parent.get("__search_key__")
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
        return __collectTaskData(data)
    else:
        return(data)

def filterDictKeys(d, keys):
    filteredDict = dict()
    for key in d:
        if key in keys:
            filteredDict[key] = d[key]
    return filteredDict

print(__getTaskData())

# taskList = server.query("sthpw/note", [("project_code", project)], ["note", "process", "search_code"])
# print(taskList)
