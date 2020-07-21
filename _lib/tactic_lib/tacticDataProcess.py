import os
# import sys
import json
import xml.etree.ElementTree as ET
# from tacticUserProcess import getTacticSerever

tacticProjectFileCache = os.path.join(os.getenv('APPDATA'), "cgpipeline", "tacticProjectCache.json")
tacticTaskFileCache = os.path.join(os.getenv('APPDATA'), "cgpipeline", "tacticTaskCache.json")


def createSthpwUserFile(user):
    filePath = os.path.join("C:/sthpw/etc", user + ".tacticrc")
    if os.path.exists(os.path.dirname(filePath)):
        pass
    else:
        os.makedirs(os.path.dirname(filePath))
    f = open(filePath, "w")
    f.close()


# Search key ========================
def getTaskElementBySearchKey(data, searchKey):
    return __runTaskDataSearchKey(data, searchKey)


def __runTaskDataSearchKey(data, searchKey):
    for element in data:
        if element['__search_key__'] == searchKey:
            return element

        elif element.get('children') is not None:
            element = __runTaskDataSearchKey(element['children'], searchKey)
            if element is not None:
                return element
        else:
            element = None
    return element
# =======================


def filterElementsData(data, filters=[], fields=False):
    # print(data)
    newData = []
    for element in data:
        # print("==========", element)
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
    element = getTaskElementBySearchKey(taskData, elementSKey)
    keys = element.keys()

    if "children" in keys:
        code = filterElementsData([element], fields=["code"])[0]
        code = list(code.values())[0]
        note = filterElementsData(notesData, filters=[("search_code", code)])

    elif "process" in keys:
        parentSKey = element.get('parent_search_key')
        parentElement = getTaskElementBySearchKey(taskData, parentSKey)

        code = filterElementsData([parentElement], fields=["code"])[0]
        task = filterElementsData([element], fields=["process"])[0]

        code = list(code.values())[0]
        task = list(task.values())[0]

        note = filterElementsData(notesData, filters=[("search_code", code), ("process", task)])

    return note


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

