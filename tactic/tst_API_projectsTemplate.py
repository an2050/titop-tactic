import os
import sys

tacticAPI_path = os.path.join(os.path.abspath("."), "client", "tactic_client_lib")
sys.path += [tacticAPI_path]

import tactic_server_stub

serverIp = "192.168.88.197"
project = "admin"
userName = "super"
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
    projectData = server.query("sthpw/project", [("is_template", "True")])
    return projectData


# def filterDictKeys(d, keys):
#     filteredDict = dict()
#     for key in d:
#         if key in keys:
#             filteredDict[key] = d[key]
#     return filteredDict

print(__getTaskData())

# taskList = server.query("sthpw/note", [("project_code", project)], ["note", "process", "search_code"])
# print(taskList)
