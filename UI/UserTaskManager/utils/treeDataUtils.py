def filterTreeData(data, field, value):
    filteredData = []

    for element in data:
        element = dict(element)
        if element.get('children'):
            children = filterTreeData(element['children'], field, value)
            element['children'] = children
            filteredData.append(element)

        elif element.get(field) == value:
            filteredData.append(element)

        if element.get('children') is not None:
            if len(element['children']) == 0:
                idx = filteredData.index(element)
                filteredData.pop(idx)
    return filteredData
