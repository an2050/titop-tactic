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

projects = server.query('sthpw/project')
projects = filter(lambda x: x.get('code') not in ["sthpw", "admin"], projects)
# print(list(projects))

epiColumns = ["__search_key__", "search_code", "description", "name"]
shotColumns = ["__search_key__", "search_code", "episodes_code", "description", "name"]
assetColumns = ["__search_key__", "search_code", "episodes_code", "description", "name"]
taskColums = ["assigned", "__search_key__", "search_code", "description", "status", "process"]

currentProject = "project_01"
tacticKeyElements = {"episode": "episode", "shot": "shot"}
tacticAssetElement = {"asset": "asset"}

def getSearchType(templateProject, itemName, project):
    serachType = server.build_search_type("/".join([templateProject, itemName]), project)
    return serachType


def __getTaskData(readCache=False):
    epiSkey = getSearchType(mainProject, tacticKeyElements.get('episode'), currentProject)
    print(epiSkey)
    episodes = server.query(epiSkey, columns=epiColumns)
    # print(episodes)

    assetSkey = getSearchType(mainProject, tacticAssetElement.get('asset'), currentProject)
    assets = server.query(assetSkey)
    # print(assets)

    episodeCode = tacticKeyElements.get('episode') + "_code"
    mainAsstes = [asset for asset in assets if not asset.get(episodeCode)]
    # print('+++++++++', mainAsstes)

#     # episodes += [asset for asset in assets if not asset.get('episodes_code')]
    for episod in episodes:
        episod['children'] = getEpisodChildren(episod.get('__search_key__'))
    for asset in mainAsstes:
        asset['children'] = getTaskData(asset.get('__search_key__'))
    episodes += mainAsstes
    return episodes


def getEpisodChildren(sKey):
    assetSkey = getSearchType(mainProject, tacticAssetElement.get('asset'), currentProject)
    assets = server.query(assetSkey, parent_key=sKey, columns=shotColumns)

    shotSkey = getSearchType(mainProject, tacticKeyElements.get('shot'), currentProject)
    shots = server.query(shotSkey, parent_key=sKey, columns=shotColumns)
    episodChildren = assets + shots

    for child in episodChildren:
        child['children'] = getTaskData(child.get('__search_key__'))
    return episodChildren


def getTaskData( sKey):
    taskData = server.query("sthpw/task", parent_key=sKey, columns=taskColums)
    return taskData

print(__getTaskData())


