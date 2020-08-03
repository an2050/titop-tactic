import os
import sys

tacticAPI_path = os.path.join(os.path.abspath("."), "client", "tactic_client_lib")
sys.path += [tacticAPI_path]

import tactic_server_stub

serverIp = "192.168.88.197"
project = "koxoball"
userName = "super"
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



def getExpression_sObj(sType, field, values, field2, values2):
    field = "'" + field + "'"
    field2 = "'" + field2 + "'"
    values = "'" + "|".join(values) + "'"
    values2 = "'" + "|".join(values2) + "'"
    expElemets = ["@SOBJECT(", sType, "[", field, ", 'in', ", values, "][", field2, ", 'NEQ', ", values2, "])"]
    exp = "".join(expElemets)
    return(exp)

def getSearchType(itemName, prj_code, mainPrj="sthpw"):
    serachType = server.build_search_type("/".join([mainPrj, itemName]), prj_code)
    return serachType


def __getTaskData(skey):
    projectData = server.query(skey)
    return projectData


def createShot():
    data = {"name": "Tst Shot", "episode_code": "EPISODE00002"}
    shot = server.insert("titop/shot", data)
    print("SHOT = ", shot)
    return shot.get("__search_key__")

def createTask(shtoSKey="titop/shot?project=fau_test&code=SHOT00003"):
    task = server.create_task(shtoSKey, process="comp", subcontext=None, description=None, bid_start_date=None, bid_end_date=None, bid_duration=None, assigned=None)
    print("TASK = ", task)
    server.update(task.get("__search_key__"), {"status": "Assignment"})
    # return task
    # server.update("sthpw/task?code=TASK00000359", {"status": "Assignment"})


def getPipeline():
    # return server.query("sthpw/pipeline", [("code", "fau_teest/PIPELINE00035")])
    # exp = getExpression_sObj("sthpw/pipeline", "project_code", [project], "search_type", [".*task"])
    exp = "@SOBJECT(sthpw/pipeline['project_code','" + project + "']['search_type', 'NEQ', '.*task'])"
    print(exp)
    pipelines = server.eval(exp)
    # print(pipelines)

    args_set = []
    for pipline in pipelines:
        args = {'search_key': pipline.get('__search_key__'),
                'pipeline': pipline.get('pipeline'),
                'color': str(pipline.get('color')),
                'description': pipline.get('description'),
                'project_code': project,
                'timestamp': pipline.get('timestamp')}
        args_set.append(args)


    class_name = "tactic.ui.tools.pipeline_wdg.PipelineSaveCbk"

    # server.start()
    for args in args_set:
        print(args)
        ret_val = server.execute_cmd(class_name, args=args)
        print(ret_val)
    # return server.query("sthpw/pipeline", [("project_code", project)], ["code"])
    # server.finish()

def getXMLPipeline(sKey):
    xmlInfo = server.get_pipeline_xml_info(sKey, include_hierarchy=False)
    return xmlInfo

def getProcessInfo():
    server.set_project("api_project")
    info = server.get_pipeline_processes_info("sthpw/task?code=TASK00000359")
    return info

def getTask():
    server.set_project("api_project")
    return server.query("sthpw/task", [("code", "TASK00000137")]) # '__search_key__': 'sthpw/task?code=TASK00000137'

def getShot():
    shot = server.query("titop/shot", [("code", "SHOT00002")])
    print(shot)
    return(shot)

def deleteTask():
    server.delete_sobject("sthpw/task?code=TASK00000145")


def updatePipelineCmd(xml):
    # server.start("Create Project", "Project creation for {} of type {}".format(prj_code, template_code))
    # try:
    args = {'search_key': "sthpw/pipeline?code=fau_teset/PIPELINE00035",
            'pipeline': xml,
            'color': "",
            'description': "",
            'project_code': project}

    class_name = "tactic.ui.tools.pipeline_wdg.PipelineSaveCbk"

    ret_val = server.execute_cmd(class_name, args=args)

# def test():
#     templates = server.query("sthpw/project", [("is_template", "True")], columns=["code"])
#     return templates
# print(test())

# skey = getSearchType("shot", "api_project", "titop")
# print(__getTaskData(skey))
# print(createShot())
# deleteTask()
# createTask(createShot())
# createTask()
# print(getPipline())
# print(getProcessInfo())def getPipeline()
def updatePipeline():
    data = {"pipeline": '<pipeline>\n  <process name="asset" type="manual" xpos="0" ypos="0" task_pipeline="titop/asset" process_code="SPT_PROCESS00137"/>\n  <process name="layout" type="manual" xpos="295" ypos="183" task_pipeline="titop/layout" process_code="SPT_PROCESS00138"/>\n  <process name="vfx" type="manual" xpos="485" ypos="100" task_pipeline="titop/vfx" process_code="SPT_PROCESS00139"/>\n  <process name="anim" type="manual" xpos="492" ypos="288" task_pipeline="titop/anim" process_code="SPT_PROCESS00140"/>\n  <process name="slr" type="manual" xpos="851" ypos="196" task_pipeline="titop/slr" process_code="SPT_PROCESS00141"/>\n  <process name="comp" type="manual" xpos="1074" ypos="500" task_pipeline="titop/comp" process_code="SPT_PROCESS00142"/>\n  <connect from="anim" to="slr"/>\n  <connect from="asset" to="layout"/>\n  <connect from="layout" to="vfx"/>\n  <connect from="layout" to="anim"/>\n  <connect from="slr" to="comp"/>\n  <connect from="vfx" to="slr"/>\n</pipeline>\n'}
    # data = dict()
    data['autocreate_tasks'] = "False"
    server.insert_update("sthpw/pipeline?code=fau_teset/PIPELINE00035", data)

def updateShotPipeline(sKey):
    data = {"pipeline_code": "fau_teset/PIPELINE00035"}
    server.update(sKey, data)

# print(createTask(getShot()[0].get("__search_key__")))
# print(updateShotPipeline(getShot()[0].get("__search_key__")))
# updatePipeline()
# print(getPipeline())
# print(getTask())
# print(getShot())

# xml = getXMLPipeline("titop/shot?project=fau_teset&code=SHOT00002").get('xml')
# print(xml)
# updatePipelineCmd(xml)

