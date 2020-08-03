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

userColumns = ["code", "login", "department", "function", "login_groups", "__search_key__"]

server = tactic_server_stub.TacticServerStub()
try:
    server.ping()
    # print(server.query('sthpw/project'))
except (AttributeError, Fault):
    serverIp = "192.168.88.197"
    userName = "super"
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




def createNewProject(prj_code, template_code, title):
    server.start("Create Project", "Project creation for {} of type {}".format(prj_code, template_code))
    try:
        args = {'project_code': prj_code,
                'template_code': template_code,
                'project_title': title}

        class_name = "tactic.command.create_project_cmd.CopyProjectFromTemplateCmd"

        ret_val = server.execute_cmd(class_name, args=args)
        return ret_val
    except Fault as err:
        print(err)
        print("Creating project error: {}".format(err))
        server.abort()
    else:
        server.finish()

createNewProject("koxoball", "titop", "Koxoball")
