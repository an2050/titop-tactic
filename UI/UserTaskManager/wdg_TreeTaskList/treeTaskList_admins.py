import os
from PySide2.QtWidgets import QMenu
from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor

from .treeTaskList import TreeTaskList
from _lib.tactic_lib import tacticPostUtils, tacticDataProcess
from _lib import configUtils, pathUtils


class TreeTaskList_coordinator(TreeTaskList):
    def __init__(self, parent):

        super(TreeTaskList_coordinator, self).__init__(parent)
        self.setColumnCount(3)
        self.setColumnHidden(2, False)

        self.appendCoordinatorConntectMenu()

    def appendCoordinatorConntectMenu(self):
        self.menu.addAction('Update Frames', self.updateFramesCount)

    def callContextMenu(self, pos):
        self.menu.exec_(QCursor.pos())

    def updateFramesCount(self):
        from _lib.ffmpeg_lib import ffprobeUtils
        from UI.UserTaskManager.utils import projectUtils

        nkConifg = configUtils.nukeConfigFile

        fps = configUtils.loadConfigData(nkConifg).get('FPS')
        project = self.taskManagerWdg.getActiveProject()
        items = self.itemUtils.getSelected_shotItems()

        server = self.taskManagerWdg.userServerCore.server
        server.start()
        for item in items:
            keyPrjData = projectUtils.getKeyPrjData(project, item)

            prm = pathUtils.getPRM_filePath(keyPrjData)
            duration = ffprobeUtils.getDuration(prm) if prm else 0
            frames = round(duration * int(fps))
            skey = item.data(0, Qt.UserRole)
            tacticPostUtils.updateSobject(server, skey, {"frames_count": frames})

            print(f"Shot {keyPrjData.get('shot')} duration is '{frames}' frames")
        server.finish()


class TreeTaskList_supervisor(TreeTaskList_coordinator):

    def __init__(self, parent):
        super(TreeTaskList_supervisor, self).__init__(parent)

        self.setColumnCount(3)
        self.setColumnHidden(2, False)

        self.appendSupervisorConntectMenu()

    def appendSupervisorConntectMenu(self):
        self.processMenu = QMenu("Processes", self.menu)
        self.proceesAddSubMenu = QMenu("Add", self.processMenu)
        self.processMenu.addMenu(self.proceesAddSubMenu)
        self.processMenu.addAction("Remove", self.removeProcess)
        self.menu.addMenu(self.processMenu)

    def callContextMenu(self, pos):
        self.proceesAddSubMenu.clear()
        self.createProcessAddMenu(self.proceesAddSubMenu)
        self.menu.exec_(QCursor.pos())

    def createProcessAddMenu(self, processMenu):
        items = self.itemUtils.getSelected_shotItems()
        processesList = self.getProcessList(items)
        sKeysList = [it.data(0, Qt.UserRole) for it in items]

        server = self.taskManagerWdg.userServerCore.server
        server.start()
        for process in processesList:
            processMenu.addAction("{}".format(process), lambda x=process: self.addTaskAction(server, sKeysList, x))
        server.finish()

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
            tacticPostUtils.deleteSObject(server, sKey, True)
