import re
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt
import datetime

from _lib import configUtils


class TableCommentList(QTableWidget):

    def __init__(self, commentBlockWidget, taskManagerWdg):
        super(TableCommentList, self).__init__(taskManagerWdg)

        self.taskManagerWdg = taskManagerWdg
        self.commentBlockWidget = commentBlockWidget

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setColumnCount(4)
        self.setColumnWidth(0, 200)

        self.horizontalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().hide()

        # # ======================= CONNECTS ===============================
        self.currentItemChanged.connect(self.commentItemChanged)
        # self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.callContextMenu)

    def callContextMenu():
        pass

    def completeTable(self, data, parentSkey=""):
        self.clear()
        self.setRowCount(0)

        if not data:
            return ""

        data.sort(key=sortByTimeStamp, reverse=True)
        snapshotsData = self.taskManagerWdg.userServerCore.snapshotNotesData

        self.setRowCount(len(data))

        for idx, dataItem in enumerate(data):

            watchFiles = self.getWatchFilesNote(dataItem.get('code'), snapshotsData)
            timestamp = datetime.datetime.strptime(dataItem.get("timestamp"), "%Y-%m-%d %H:%M:%S.%f")
            time = timestamp.strftime("%d-%m-%y %H:%M:%S")

            item0 = QTableWidgetItem(dataItem.get("login"))
            item1 = QTableWidgetItem(dataItem.get("process"))
            item2 = QTableWidgetItem(time)
            item3 = QTableWidgetItem(str(len(watchFiles)))

            UserRoleData = {"sKey": dataItem.get('__search_key__'), "note": dataItem.get('note'),
                            "process": dataItem.get('process'), "watchFiles": watchFiles, "parentSkey": parentSkey}

            item0.setData(Qt.UserRole, UserRoleData)
            item1.setData(Qt.UserRole, UserRoleData)
            item2.setData(Qt.UserRole, UserRoleData)
            item3.setData(Qt.UserRole, UserRoleData)
            self.setItem(idx, 0, item0)
            self.setItem(idx, 1, item1)
            self.setItem(idx, 2, item2)
            self.setItem(idx, 3, item3)

        # self.selectRow(0)
        self.setCurrentCell(-1, -1)

    def commentItemChanged(self, current, previous):
        if current is None:
            return None
        self.commentBlockWidget.setDescriptionText(current.data(Qt.UserRole).get('note'))
        self.commentBlockWidget.selectedCommentItem = current

    def getWatchFilesNote(self, noteCode, snapData):
        files = []
        for snap in snapData:
            if snap.get('search_code') == noteCode:
                files += snap.get('watchFilePaths')
        files = [re.sub(re.findall(r"(.*?)\/assets", file)[0], configUtils.tacticAssetsPath, file) for file in files]
        return files

def sortByTimeStamp(element):
    elementTime = datetime.datetime.strptime(element.get("timestamp"), "%Y-%m-%d %H:%M:%S.%f")
    return (elementTime - datetime.datetime(1970, 1, 1)).total_seconds()
