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

def getUserData():

    grpList = []
    prj_code = "project_01"
    allGroupsData = server.query("sthpw/login_group", columns=["code", "access_rules"])
    print(allGroupsData)
    for grp in allGroupsData:
        rules = grp.get('access_rules')

        ruleList = list(ET.fromstring(rules))
        for rule in ruleList:
            d = rule.attrib
            if d.get('group') == 'project' and d.get('code') == prj_code and d.get('access') == 'allow':
                grpList += [grp.get('code')]
                break

    exp = getExpression_sObj('sthpw/login_in_group', 'login_group', grpList)
    userInGrp = server.eval(exp)
    userCodes = [user.get('login') for user in userInGrp]

    exp = getExpression_sObj('sthpw/login', 'login', userCodes)
    usersData = server.eval(exp)

    data = [] 
    for user in usersData:
        data.append(filterDictKeys(user, ["login", "function"]))
    # print(data)


def getExpression_sObj(sType, field, values):
    field = "'" + field + "'"
    values = "'" + "|".join(values) + "'"
    expElemets = ["@SOBJECT(", sType, "[", field, ", 'in', ", values, "])"]
    exp = "".join(expElemets)
    return(exp)


def filterDictKeys(d, keys):
    filteredDict = dict()
    for key in d:
        if key in keys:
            filteredDict[key] = d[key]
    return filteredDict

# print(getExpression_sObj('sthpw/login_in_group', 'login_group', ['admin', 'zaem0', 'art_comp']))
print(getUserData())
