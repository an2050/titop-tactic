import re


class sequenceError(BaseException):
    pass


class sequenceFileObject:
    """docstring for sequenceFileObject"""

    def __init__(self, countType="houdini"):

        self.active = False

        self.countType = countType
        self.countTypes = {"houdini": "${F%p%}", "nuke": "%0%p%d"}

        # self.pattern = r"(.+?\.\D*?)(\d+)(\D*?(\..+))"
        self.pattern = r"^(?P<body>.+?(?P<ver>[vV]\d{1,4})?(\.|_))(?P<counter>\d+?)(?P<ext>\.[\w\d]{2,4})$"
        self.body = ""
        self.ext = ""
        self.counter = ""
        self.counterList = []
        self.extensions = [".exr", ".dpx", ".jpeg", ".jpg"]

    def addSequenceElement(self, fileName):
        matchPattern = re.match(self.pattern, fileName)
        if not matchPattern:
            raise sequenceError("File does not match for sequence: " + fileName)

        ext = matchPattern.group('ext')
        if ext not in self.extensions:
            print("Unexpected file extension '{}'".format(ext))
            return False

        if self.active:
            match = self.checkProperties(matchPattern)
            if not match:
                return False
        else:
            self.active = True
            self.setSeqProperties(matchPattern)

        self.counterList.append(matchPattern.group('counter'))
        return True

    def setSeqProperties(self, matchPattern):
        self.body = matchPattern.group('body')
        self.ext = matchPattern.group('ext')

    def checkProperties(self, matchPattern):
        body = self.body == matchPattern.group('body')

        if body:
            return True
        else:
            return False

    def getCountGroups(self):
        countGroups = []
        first = None
        last = None

        self.counterList.sort()
        for idx, element in enumerate(self.counterList):
            elementInt = int(element)
            if first is None:
                first = elementInt
            try:
                nextElement = int(self.counterList[idx + 1])
                if nextElement - elementInt != 1:
                    last = elementInt
                    countGroups += self.__closeSeqGroup(first, last)
                    first = None
                    last = None
            except IndexError:
                last = elementInt
                countGroups += self.__closeSeqGroup(first, last)

        countGroups = sorted(countGroups, key=lambda x: int(re.match(r"\d+", x).group(0)))
        return countGroups

    def __closeSeqGroup(self, first, last):
        if first != last:
            return ["{}-{}".format(first, last)]
        else:
            return [str(last)]

    def getPadding(self):
        padd = list(set([len(x) for x in self.counterList]))
        if len(padd) == 1:
            return padd[0]
        else:
            return ""

    def getSequenceTemplate(self):
        padding = self.getPadding()
        counter = self.countTypes[self.countType].replace("%p%", str(padding))
        return "{}{}{}".format(self.body, counter, self.ext)

    def getSequenceRepr(self):
        return "{} ({})".format(self.getSequenceTemplate(), " :: ".join(self.getCountGroups()))

    def __repr__(self):
        return self.getSequenceRepr()


def getSeqObj(fileList, processedFiles, noSequencefiles, countType='houdini'):
    seqObj = sequenceFileObject(countType)
    for fileName in fileList:
        if fileName in processedFiles:
            continue
        try:
            if seqObj.addSequenceElement(fileName):
                processedFiles.append(fileName)
        except sequenceError:
            processedFiles.append(fileName)
            noSequencefiles.append(fileName)

    return seqObj


def getSequecneRepresentation(fileNameList, countType='houdini'):
    processedFiles = []
    noSequencefiles = []
    seqObjList = []
    while len(processedFiles) < len(fileNameList):
        seqObjList.append(getSeqObj(fileNameList, processedFiles, noSequencefiles, countType))

    sequenceReprDict = {}
    for seq in seqObjList:
        sequenceReprDict[seq.getSequenceRepr()] = seq.getSequenceTemplate()

    for file in noSequencefiles:
        sequenceReprDict[file] = file

    return sequenceReprDict
