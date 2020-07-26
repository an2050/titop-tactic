from .treeTaskList import TreeTaskList


class TreeTaskList_supervisor(TreeTaskList):
    """docstring for TreeTaskList_supervisor"""
    def __init__(self, parent):
        super(TreeTaskList_supervisor, self).__init__(parent)
        # self.arg = arg
        self.setColumnCount(3)
        self.setColumnHidden(2, False)
        # self.setHeaderLabels(["Task", "Status", "User"])
