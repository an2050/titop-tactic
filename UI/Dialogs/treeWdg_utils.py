from PySide2.QtWidgets import QTreeWidgetItem
from PySide2.QtCore import Qt


def collectTreeData(treeWidget, parent=None):
    parent = treeWidget.invisibleRootItem() if parent is None else parent
    childrenCount = parent.childCount()
    treeData = []

    for childIndx in range(childrenCount):
        item = parent.child(childIndx)

        keyItem = item.text(0)
        itemData = {keyItem: []}
        for cl in range(1, treeWidget.columnCount()):
            itemData[keyItem] += [item.text(cl)]
        if item.childCount() > 0:
            itemData[keyItem] += [collectTreeData(treeWidget, item)]
            treeData.append(itemData)
        else:
            treeData.append(itemData)
    return treeData


def completeTree(treeWidget, data, parent=None, editable=False):
    if parent is None:
        parent = treeWidget.invisibleRootItem()

    for itemData in data:
        for k, v in itemData.items():
            item = QTreeWidgetItem()
            item.setText(0, k)
            if editable:
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
            for idx, cl in enumerate(v, 0):
                if isinstance(cl, list):
                    completeTree(treeWidget, cl, item, editable)
                else:
                    item.setText(idx + 1, cl)
            parent.addChild(item)


def expandAllTree(treeWidget, parent=None, dLimit=3, d=0):
    if parent is None:
        parent = treeWidget.invisibleRootItem()

    d += 1
    if d >= dLimit:
        return
    childrenCount = parent.childCount()
    for idx in range(childrenCount):
        item = parent.child(idx)
        item.setExpanded(True)
        if item.childCount() > 0:
            expandAllTree(treeWidget, item, d=d)


def collapseAllTree(treeWidget, parent=None):
    if parent is None:
        parent = treeWidget.invisibleRootItem()

    childrenCount = parent.childCount()
    for idx in range(childrenCount):
        item = parent.child(idx)
        if item.parent() is None:
            item.setExpanded(True)
        else:
            item.setExpanded(False)
        if item.childCount() > 0:
            collapseAllTree(treeWidget, item)


def getSimpleStructureData(treeWidget, parent=None):
    parent = treeWidget.invisibleRootItem() if parent is None else parent
    childrenCount = parent.childCount()
    structData = []

    for childIndx in range(childrenCount):
        item = parent.child(childIndx)
        if item.childCount() > 0:
            structData.append({item.text(0): getSimpleStructureData(treeWidget, item)})
        else:
            structData.append({item.text(0): []})
    return structData


def getPathsData(simpleStructureData):
    paths = []
    collectPathsData(simpleStructureData, paths)
    return paths


def collectPathsData(simpleStructureData, paths, pathsHook=None):
    for folder in simpleStructureData:

        if pathsHook is None:
            pathsHook = [[]]
        else:
            pathsHook.append(list(pathsHook[-1]))

        folderName = list(folder.keys())[0]
        pathsHook[-1].append(folderName)
        if list(folder.values())[0]:
            str(collectPathsData(list(folder.values())[0], paths, pathsHook))
            pathsHook.pop()
            continue
        else:
            paths += [pathsHook.pop()]

