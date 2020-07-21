

def createNote(server, sObj, noteText="", process=None, subcontext=None, user=None):
    return server.create_note(sObj, noteText, process=process)


def udateNote(server, sKey, text):
    return server.update(sKey, {"note": text})


def deleteNote(server, sKey, dependece):
    server.delete_sobject(sKey, dependece)

# def simpleCheckin(sObj, context, filePath, description, mode, create_icon=True, checkin_type="strict", process=process)
#   pass

def checkinNote(server, noteSobj, files):
    noteSKey = noteSobj.get('__search_key__')
    process = noteSobj.get('process')
    context = "notes/attachment"
    description = "note snapshot"
    # print(noteSKey, "==================")
    snapshot = createSnapshot(server, noteSKey, context, description=description, process=process)
    snapshot_code = snapshot.get('code')

    server.add_file(snapshot_code, files.pop(), mode='upload', create_icon=True)

    fileTypes = ["f" + str(idx) for idx in range(len(files))]
    server.add_file(snapshot_code, files, file_type=fileTypes, mode='upload', create_icon=False)


def createSnapshot(server, search_key, context, snapshot_type="file", description="No description", process="", is_current=True, level_key=None, is_revision=False, triggers=True):

    return server.create_snapshot(search_key, context, snapshot_type=snapshot_type, description=description,
                                  is_current=is_current, level_key=level_key, is_revision=is_revision, triggers=triggers)

def checkinIcon(server, sKey, context, filePath, description):
    server.simple_checkin(note, context, file_path, description=snapshotDesctription,
                                mode="upload", create_icon=True, checkin_type="strict", process=process)