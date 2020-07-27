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



def main(args):

    # USAGE: create_project.py <project_code> <project_title> <project_type> 
    project_code = args[0]
    project_title = args[1]
    project_type = args[2]

    # assert project_type in ['prod', 'flash', 'simple', 'unittest', 'titop']
    # assert project_title

    regexs = r'^\d|\W'
    m = re.search(r'%s' % regexs, project_code) 

    if m:
        raise TacticApiException('<project_code> cannot contain special characters or start with a number.')

    # server = TacticServerStub.get();
    # do the actual work
    server.start("Create Project", "Project creation for [%s] of type [%s]" % (project_code, project_type))

    try:

        args = {
        'project_code': project_code,
        'template_code': project_title,
        'project_title': project_type}

        # class_name = "tactic.command.CreateProjectCmd"
        class_name = "tactic.command.create_project_cmd.CopyProjectFromTemplateCmd"

        ret_val = server.execute_cmd(class_name, args=args)

        print(ret_val)

    except:

        server.abort()

        raise

    else:

        server.finish()

if __name__ == '__main__':
    executable = sys.argv[0]
    args = sys.argv[1:]
    args = ["api_project", "titop", "API Project"]
    if len(args) != 3:
        print("python create_project.py <project_code> <project_title> <project_type>")
        sys.exit(0)
    main(args)

# print(getUserData())


