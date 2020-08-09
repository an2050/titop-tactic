import os
import sys

from PySide2.QtWidgets import QApplication, QWidget

from xmlrpc.client import Fault, ProtocolError
from socket import gaierror

tacticApi = os.path.join(os.environ.get('CGPIPELINE'), "tactic", "client")
modules = os.path.join(os.environ.get('CGPIPELINE'))
sys.path += [tacticApi, modules]

from _lib.tactic_lib import tacticDataProcess  # , tacticPostUtils
from tactic_client_lib import TacticServerStub
from tactic_client_lib.tactic_server_stub import TacticApiException


server = None
def connectToServer(resetTicket=False):
    global server
    try:
        server = TacticServerStub()
    except TacticApiException:
        tacticDataProcess.createSthpwUserFile(os.getlogin())
        server = TacticServerStub()

    print("Connecting to server...")

    if resetTicket:
        setTicket(server)

    print("server", server)

    try:
        server.ping()
    except Exception as err:
        print(err)
        if setTicket(server) is None:
            return

    print("Connection successful.")

    # connected = True
    # server = server
    # ticketData = tacticDataProcess.getTicketData()
    # userName = ticketData.get('login')
    # IpAdress = ticketData.get('IpAdress')
    # ticket = ticketData.get('ticket')
    # mainProject = ticketData.get('project')
    # userData = __getUserData(userName)
    # isAdmin = tacticPostUtils.checkAdminPremition(server, userName)
    return True


def setTicket(server):

    _input = False
    textErr = ""
    while _input is False:
        userInput = tacticDataProcess.getCredentialDialog(textErr)
        if userInput is None:
            return

        userName, password, serverIp = [userInput.get('userName'), userInput.get('password'), userInput.get('IpAdress')]
        server.set_server(serverIp)

        try:
            newTicket = server.get_ticket(userName, password)
            server.set_login_ticket(newTicket)
            tacticDataProcess.storeUserTicket(serverIp, userName, newTicket)
            _input = True
        except Fault:
            textErr = "Login/Password combination incorrect"
            print(textErr)
        except gaierror:
            textErr = "Socket problem"
            print(textErr)
        except (TimeoutError, ConnectionRefusedError):
            textErr = "A connection attempt failed. Check IP adress."
            print(textErr)
        except ProtocolError as err:
            textErr = 'A protocol error occurred. {} {}'.format(err.errmsg, err.errcode)
            # print(textErr)
            print("URL: %s" % err.url)
            print("Error code: %d" % err.errcode)
            print("Error message: %s" % err.errmsg)
    return True

def getProjectData():
    projectData = server.query("sthpw/project")
    return projectData



if __name__ == "__main__":
    app = QApplication()
    wdg = QWidget()
    print("CONNECT IS = ", connectToServer())


    print(getProjectData())


    wdg.show()

    app.exec_()
