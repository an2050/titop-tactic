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


file_path = "d:/other/refs/particles/DSC_5030.JPG"

episod = server.build_search_key('main/episodes', 'EPISODES00002')
shot = server.build_search_key('default/shots', 'SHOTS00002')

sObj = shot
# noteText = "This note has been created by API This note has been created by API This note has been created by tacticAPI_pathThis note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by tacticAPI_pathThis note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by tacticAPI_pathThis note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by tacticAPI_pathThis note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by tacticAPI_pathThis note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API This note has been created by API"
noteText = "This note has been created by API This note has been created by API."

# context = "publish"
context = "notes/attachment"
process = "animation"
note = server.create_note(sObj, noteText, process=process, subcontext=None, user=None)

snapshotDesctription = "Description for snapshot"

note = note.get('__search_key__')

checkin = server.simple_checkin(note, context, file_path, description=snapshotDesctription,
                                mode="upload", create_icon=True, checkin_type="strict", process=process)

snapshot = server.get_snapshot(note, context)
snapshot_code = snapshot.get('code')

file_path2 = "d:/other/refs/particles/32b8ce610116c605bd3b4532192a690d.jpg"
file_path3 = "d:/other/refs/particles/moshki.jpg"
files = [file_path2, file_path3]
file_types = ["f1", "f2"]
server.add_file(snapshot_code, files, file_type=file_types, mode='upload', create_icon=False)

print(server.get_client_dir(snapshot_code))
print(server.get_all_paths_from_snapshot(snapshot_code))
# server.connect_sobjects(note, snapshot, "attachment")

