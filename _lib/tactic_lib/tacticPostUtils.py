from _lib import exceptionUtils
from xmlrpc.client import Fault


def createNewProject(server, prj_code, template_code, title):
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
    server.finish()


def checkAdminPremition(server, login):
    adminGroupCode = "admin"
    logInGroup = server.query("sthpw/login_in_group", [("login_group", adminGroupCode), ("login", login)])
    if logInGroup:
        return True
    else:
        return False


def createSObject(server, sType, data):
    return server.insert(sType, data)


def createTask(server, sKey, process, assigned=None):
    return server.create_task(sKey, process, assigned=assigned)


def createNote(server, sObj, noteText="", process=None, subcontext=None, user=None):
    return server.create_note(sObj, noteText, process=process)


def udateNote(server, sKey, text):
    data = {"note": text}
    return updateSobject(server, sKey, data)
    # return server.update(sKey, {"note": text})


def updateSobject(server, sKey, data):
    return server.update(sKey, data)


def updateMultipleSobjects(server, data):
    return server.update_multiple(data)


def deleteSObject(server, sKey, dependece):
    server.delete_sobject(sKey, dependece)


def checkinNote(server, noteSobj, files):
    noteSKey = noteSobj.get('__search_key__')
    process = noteSobj.get('process')
    context = "notes/attachment"
    description = "note snapshot"

    snapshot = createSnapshot(server, noteSKey, context, description=description, process=process)
    snapshot_code = snapshot.get('code')

    server.add_file(snapshot_code, files.pop(), mode='upload', create_icon=True)

    fileTypes = ["f" + str(idx) for idx in range(len(files))]

    try:
        server.add_file(snapshot_code, files, file_type=fileTypes, mode='upload', create_icon=False)
    except Fault as err:
        exceptionUtils.pathError(err.faultString).displayMessageIcon()
        print(err.faultString)


def createSnapshot(server, search_key, context, snapshot_type="file", description="No description", process="", is_current=True, level_key=None, is_revision=False, triggers=True):
    return server.create_snapshot(search_key, context, snapshot_type=snapshot_type, description=description,
                                  is_current=is_current, level_key=level_key, is_revision=is_revision, triggers=triggers)

# def checkinIcon(server, sKey, context, filePath, description):
#     server.simple_checkin(note, context, file_path, description=snapshotDesctription,
#                           mode="upload", create_icon=True, checkin_type="strict", process=process)


def updatePipelineDependencies(server, prj_code):
    exp = "@SOBJECT(sthpw/pipeline['project_code','" + prj_code + "']['search_type', 'NEQ', '.*task'])"
    prjPipelines = server.eval(exp)

    class_name = "tactic.ui.tools.pipeline_wdg.PipelineSaveCbk"

    for pipeline in prjPipelines:
        args = {'search_key': pipeline.get('__search_key__'),
                'pipeline': pipeline.get('pipeline'),
                'color': str(pipeline.get('color')),
                'description': pipeline.get('description'),
                'project_code': prj_code,
                'timestamp': pipeline.get('timestamp')}
        try:
            ret_val = server.execute_cmd(class_name, args=args)
            print("Updating pipeline result: {}".format(ret_val))
        except Fault as err:
            print("Updating pipeline '{}' error. {}".format(pipeline.get('code'), err))
