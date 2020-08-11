from PySide2.QtWidgets import QMenu
from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor

from .treeTaskList import TreeTaskList
from _lib.tactic_lib import tacticPostUtils, tacticDataProcess
from _lib import configUtils


class TreeTaskList_coordinator(TreeTaskList):
    def __init__(self, parent):

        super(TreeTaskList_coordinator, self).__init__(parent)
        self.setColumnCount(3)
        self.setColumnHidden(2, False)


class TreeTaskList_supervisor(TreeTaskList):

    def __init__(self, parent):
        super(TreeTaskList_supervisor, self).__init__(parent)

        self.setColumnCount(3)
        self.setColumnHidden(2, False)

    def callContextMenu(self, pos):
        menu = QMenu(parent=self)

        processMenu = QMenu("Processes", menu)
        proceesAddSubMenu = QMenu("Add", processMenu)

        processMenu.addMenu(proceesAddSubMenu)
        self.createProcessAddMenu(proceesAddSubMenu)

        processMenu.addAction("Remove", self.removeProcess)

        menu.addMenu(processMenu)

        menu.addAction('expand All', self.expandAllTree)
        menu.addAction('collapse All', self.collapseAllTree)
        menu.addSeparator()

        menu.exec_(QCursor.pos())

    def createProcessAddMenu(self, processMenu):
        items = self.itemUtils.getSelected_shotItems()
        processesList = self.getProcessList(items)
        sKeysList = [it.data(0, Qt.UserRole) for it in items]

        server = self.taskManagerWdg.userServerCore.server
        server.start()
        for process in processesList:
            processMenu.addAction("{}".format(process), lambda x=process: self.addTaskAction(server, sKeysList, x))
        server.finish()

    def addTaskAction(self, server, sKeysList, process):
        for sKey in sKeysList:
            taskData = self.taskManagerWdg.userServerCore.taskData
            itemData = tacticDataProcess.getTaskElementBySearchField(taskData, "__search_key__", sKey)
            existingProcesses = tacticDataProcess.getActiveProcessesList([itemData])

            if process in existingProcesses:
                continue
            task = tacticPostUtils.createTask(server, sKey, process)
            tacticPostUtils.updateSobject(server, task.get('__search_key__'),
                                          {"status": configUtils.tctStatusElements.get('assignment')})

    def getProcessList(self, items):
        def getItemType(sKey):
            idx0 = sKey.find('/')
            idx1 = sKey.find('?')
            return sKey[idx0:idx1]

        def compareItemTypes(code, types):
            idx = code.find('/')
            processType = code[idx:]
            return processType in types

        itemTypes = []
        for item in items:
            sKey = item.data(0, Qt.UserRole)
            itemTypes.append(getItemType(sKey))

        itemTypes = list(set(itemTypes))

        processesData = self.taskManagerWdg.getProcessesData()
        filteredData = list(filter(lambda x: compareItemTypes(x['code'], itemTypes), processesData))

        processesList = []
        for data in filteredData:
            processesList += data.get("processes")
        return processesList

    def removeProcess(self):
        items = self.itemUtils.getSelected_ProcessItems(getMultiple=True)
        if not isinstance(items, list):
            items = [items]

        server = self.taskManagerWdg.userServerCore.server
        for item in items:
            sKey = item.data(0, Qt.UserRole)
            if sKey.find("task") < 0:
                continue
            print(sKey)
            tacticPostUtils.deleteNote(server, sKey, True)
