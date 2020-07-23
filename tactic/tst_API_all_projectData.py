import os
import sys

tacticAPI_path = os.path.join(os.path.abspath("."), "client", "tactic_client_lib")
sys.path += [tacticAPI_path]

import tactic_server_stub
from xmlrpc.client import Fault
from socket import gaierror


# def main():
#     server = tactic_server_stub.TacticServerStub()
#     server.start("Ping Test")
#     try:
#         print(server.ping())
#     except:
#         server.abort()
#         raise
#     else:
#         server.finish()
#     return server

# server = main()

# serverIp = "192.168.88.197"
# # project = "main"
# userName = "zaem0"
# password = "123"


mainProject = "titop"
tacticTicket = os.path.join(os.path.expanduser("~"), ".tactic", "etc", os.getlogin() + ".tacticrc")
import re
def storeUserTicket(Ip, userName, ticket, mainProject):
    file = open(tacticTicket, "w")
    file.write("login=" + userName + "\n")
    file.write("server=" + Ip + "\n")
    file.write("ticket=" + ticket + "\n")
    file.write("project=" + mainProject)
    file.close()

def getUserTicket():
    file = open(tacticTicket, "r")
    text = file.read()
    file.close()
    try:
        ticket = re.search(r'ticket=(.*)$', text).group(1)
    except AttributeError:
        print("Wrong user ticket file. Ticket not found!")
        return
    return ticket



server = tactic_server_stub.TacticServerStub()
try:
    server.ping()
    # print(server.query('sthpw/project'))
except (AttributeError, Fault):
    serverIp = "192.168.88.197"
    userName = "zaem0"
    password = "123"
    # server.set_server(serverIp)

    try:
        newTicket = server.get_ticket(userName, password)
        server.set_login_ticket(newTicket)
        storeUserTicket(serverIp, userName, newTicket, mainProject)
        # print("NEW TICKET ==== ", server.query('sthpw/project', columns=["code"]))
    except Fault:
        print("Login/Password combination incorrect")
    except (gaierror):
        print("soket problem")

# print(server.get_parent("titop/asset?project=titop&code=ASSET00002"))
# print(server.query("titop/asset"))
    # print(newTicket)
# print(newTicket)
    # ticketData = {"login": "art_comp", "server": "192.168.88.197", "ticket": ticket}

# print(server, "=========")

# # except:
#     # tacticDataProcess.createSthpwUserFile(userName)
#     server = tactic_server_stub.TacticServerStub()

# server.set_server(serverIp)
# # server.set_project(project)

# try:
#     ticket = server.get_ticket(userName, password)
#     # ticket = server.generate_ticket()
#     print(ticket)
#     server.set_login_ticket(ticket)
#     print("Connect successful")
# except (TimeoutError, ConnectionRefusedError):
#     print("A connection attempt failed. Check IP adress.")
# except (Fault):
#     print("Login/Password combination incorrect")
# except (gaierror):
#     print("soket problem")

projects = server.query('sthpw/project')
projects = filter(lambda x: x.get('code') not in ["sthpw", "admin"], projects)
print(list(projects))

# taskList = server.query('sthpw/task')
# print(taskList)










# columns = ["__search_key__", "search_code", "description"]
# taskColums = ["assigned", "__search_key__", "search_code", "description", "status", "process"]

# def getAllProjectData():
#     return server.query("sthpw/project")
#     # episodes = server.query("main/episodes", columns=columns)
#     # assets = server.query("main/asset", columns=[])
#     # # print(episodes)
#     # for episod in episodes:
#     #     episod['children'] = getEpisodChildren(episod.get('__search_key__'))
#     # episodes += [asset for asset in assets if not asset.get('episodes_code')]
#     # return episodes

# def getEpisodChildren(sKey):
#     assets = server.query("main/asset", parent_key=sKey, columns=columns)
#     shots = server.query("default/shots", parent_key=sKey, columns=columns)

#     episodChildren = assets + shots

#     for child in episodChildren:
#         child['children'] = getTaskData(child.get('__search_key__'))
#     return episodChildren


# def getTaskData(sKey):
#     taskData = server.query("sthpw/task", parent_key=sKey, columns=taskColums)
#     return taskData

#     # print(" == ASSET == ", assets, " == ASSET == ")


# def filterDictKeys(d, keys):
#     filteredDict = dict()
#     for key in d:
#         if key in keys:
#             filteredDict[key] = d[key]
#     return filteredDict

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


# print(getAllProjectData())

