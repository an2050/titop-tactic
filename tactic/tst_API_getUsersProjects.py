import os
import sys

tacticAPI_path = os.path.join(os.path.abspath("."), "client", "tactic_client_lib")
sys.path += [tacticAPI_path]

import tactic_server_stub
from xmlrpc.client import Fault
from socket import gaierror

import xml.etree.ElementTree as ET


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

userColumns = ["code", "login", "department", "function", "login_groups", "__search_key__"]

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




def filterDictKeys(d, keys):
    filteredDict = dict()
    for key in d:
        if key in keys:
            filteredDict[key] = d[key]
    return filteredDict


def __getAllUsersProjects():
    user = "art_comp"
    usersGroupsData = server.query("sthpw/login_in_group", [('login', user)], columns=['login_group'])
    usersGroupsList = [grp.get('login_group') for grp in usersGroupsData]

    exp = getExpression_sObj('sthpw/login_group', 'code', usersGroupsList)
    groupsData = server.eval(exp)

    prjList = []
    # print(groupsData)
    for grp in groupsData:
        rules_xml = grp.get('access_rules')

        ruleList = list(ET.fromstring(rules_xml))
        for rule in ruleList:
            d = rule.attrib
            if d.get('group') == 'project' and d.get('access') == 'allow':
                availablePrj = d.get('code')
                prjList += [(availablePrj)]

    return list(set(prjList))
    # groupsData = server.query("sthpw/login_group", [('code', user)], columns=['login_group'])


def getAllProjects():
    prjData = server.query("sthpw/project")
    projects = [prj.get('code') for prj in prjData]
    return projects


def getExpression_sObj(sType, field, values):
    field = "'" + field + "'"
    values = "'" + "|".join(values) + "'"
    expElemets = ["@SOBJECT(", sType, "[", field, ", 'in', ", values, "])"]
    exp = "".join(expElemets)
    return(exp)


usersPrjcts = __getAllUsersProjects()
allPrjts = getAllProjects()
print("All = ", allPrjts)
print("Users = ", usersPrjcts)

print("*" in usersPrjcts)
print(set(usersPrjcts).intersection(set(allPrjts)))




# print(getUserData())
