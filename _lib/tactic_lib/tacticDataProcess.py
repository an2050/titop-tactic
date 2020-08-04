import os
import re
# import sys
import json
import xml.etree.ElementTree as ET
# from tacticUserProcess import getTacticSerever
from UI.CredentialWindow import CredentialtWindow

mainProject = "titop"
tacticTicket = os.path.join(os.path.expanduser("~"), ".tactic", "etc", os.getlogin() + ".tacticrc")
tacticProjectFileCache = os.path.join(os.getenv('APPDATA'), "cgpipeline", "tacticProjectCache.json")
tacticTaskFileCache = os.path.join(os.getenv('APPDATA'), "cgpipeline", "tacticTaskCache.json")


def getCredentialDialog(text):
    credential = CredentialtWindow.CredentialDialog()
    credential.infoLable.setText(text)
    accepted = credential.exec_()
    if accepted:
        credentialData = credential.getData()
        return credentialData


def getTicketData():
    file = open(tacticTicket, "r")
    text = file.read()
    file.close()
    data = dict()
    try:
        data['login'] = re.search(r'login=(.*)\b', text).group(1)
        data['IpAdress'] = re.search(r'server=(.*)\b', text).group(1)
        data['ticket'] = re.search(r'ticket=(.*)\b', text).group(1)
        data['project'] = re.search(r'project=(.*)\b', text).group(1)
    except AttributeError:
        print("Wrong user ticket file. Ticket not found!")
    return data


def storeUserTicket(Ip, userName, ticket):
    if not os.path.exists(os.path.dirname(tacticTicket)):
        os.makedirs(os.path.dirname(tacticTicket))
    file = open(tacticTicket, "w")
    file.write("login=" + userName + "\n")
    file.write("server=" + Ip + "\n")
    file.write("ticket=" + ticket + "\n")
    file.write("project=" + mainProject + "\n")
    file.close()

def createSthpwUserFile(user):
    filePath = os.path.join("C:/sthpw/etc", user + ".tacticrc")
    if os.path.exists(os.path.dirname(filePath)):
        pass
    else:
        os.makedirs(os.path.dirname(filePath))
    f = open(filePath, "w")
    f.close()


# Search key ========================
def getTaskElementBySearchField(data, field, value):
    return __runTaskDataSearchField(data, field, value)


def __runTaskDataSearchField(data, field, value):
    for element in data:
        if element.get(field) == value:
            return element

        elif element.get('children') is not None:
            element = __runTaskDataSearchField(element['children'], field, value)
            if element is not None:
                return element
        else:
            element = None
    return element


def getExpression_sObj(sType, field, values):
    field = "'" + field + "'"
    values = "'" + "|".join(values) + "'"
    expElemets = ["@SOBJECT(", sType, "[", field, ", 'in', ", values, "])"]
    exp = "".join(expElemets)
    return(exp)

# def getTaskElementBySearchKey(data, searchKey):
#     return __runTaskDataSearchKey(data, searchKey)

# def __runTaskDataSearchKey(data, searchKey):
#     for element in data:
#         if element['__search_key__'] == searchKey:
#             return element

#         elif element.get('children') is not None:
#             element = __runTaskDataSearchKey(element['children'], searchKey)
#             if element is not None:
#                 return element
#         else:
#             element = None
#     return element
# =======================


def filterElementsData(data, filters=[], fields=False):

    newData = []
    for element in data:

        filterStatus = True
        for _filter in filters:
            if element.get(_filter[0]) != _filter[1]:
                filterStatus = False
                break

        if filterStatus:
            if fields is not False:
                newElement = dict()
                for field in fields:
                    if not element.get(field):
                        newElement[field] = ""
                    else:
                        newElement[field] = element[field]

                element = dict(newElement)
                del newElement

            newData.append(element)

    return newData


def getStatusColor(pipelineData, prj, task, status):
    codes = ["{prj}/{task}".format(prj=prj, task=task),
             "{prj}/{task}".format(prj="vfx", task=task),
             "{prj}/{task}".format(prj="vfx", task="comp")]

    for code in codes:
        data = filterElementsData(pipelineData, [("code", code)], ['pipeline'])
        if len(data) > 0:
            root = ET.fromstring(data[0]['pipeline'])

            statusData = [d.attrib for d in root if d.attrib.get('name') == status]

            if statusData:
                color = statusData[0].get('color')
                if color is not None:
                    return color


def getNotesElement(elementSKey, taskData, notesData):

    note = []
    element = getTaskElementBySearchField(taskData, "__search_key__", elementSKey)
    # element = getTaskElementBySearchKey(taskData, elementSKey)
    keys = element.keys()

    if "children" in keys:
        code = filterElementsData([element], fields=["code"])[0]
        code = list(code.values())[0]
        note = filterElementsData(notesData, filters=[("search_code", code)])

    elif "process" in keys:

        parentCode = element.get('search_code')
        # parentSKey = element.get('parent_search_key')
        parentElement = getTaskElementBySearchField(taskData, field="code", value=parentCode)
        # parentElement = getTaskElementBySearchKey(taskData, parentSKey)

        # print("PARENT CODE = ", parentCode)
        # print("PARENT ELEMENT = ", parentElement)
        # print("TASK DATA = ", taskData)

        code = filterElementsData([parentElement], fields=["code"])[0]
        task = filterElementsData([element], fields=["process"])[0]

        code = list(code.values())[0]
        task = list(task.values())[0]

        note = filterElementsData(notesData, filters=[("search_code", code), ("process", task)])
    return note


def getProcessList(taskData):
    def getChild(taskData, lst):
        for e in taskData:
            if e.get('children'):
                getChild(e.get('children'), lst)
            else:
                lst += [e.get('process')]
        return lst

    processList = []
    rawList = getChild(taskData, processList)
    return list(set(rawList))


def saveDiskCache(data, filePath):
    directory = os.path.dirname(filePath)
    if os.path.exists(directory) is False:
        os.mkdir(directory)
    elif os.path.exists(filePath):
        os.remove(filePath)
    with open(filePath, 'w') as f:
        json.dump(data, f)


def readDiskCache(filePath):
    with open(filePath, 'r') as f:
        data = json.load(f)
    return data

