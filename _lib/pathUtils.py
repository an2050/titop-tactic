import os
import re
from _lib import keyDataProjectUtils, exceptionUtils


padding = 3
version = "0".zfill(padding)


# otlPaths = [{"OTLPath_prj": "{projectName}\\_ASSETS\\{assetName}\\hda"},
#             {"OTLPath_epi": "{episodName}\\_ASSETS\\{assetName}\\hda"},
#             {"OTLPath_shot": "{shotName}\\_ASSETS\\{assetName}\\hda"}]

workPaths = [{"workPath_prj": r"{projectName}/_ASSETS/{assetName}/{taskName}"},
             {"workPath_epi": r"{episodName}/_ASSETS/{assetName}/{taskName}"},
             {"workPath_shot": r"{shotName}/{taskName}"}]

jobOutPath = [{"jobOut_prj": r"{projectName}/_ASSETS/{assetName}/{taskName}/OUT"},
              {"jobOut_episod": r"{episodeName}/_ASSETS/{assetName}/{taskName}/OUT"},
              {"jobOut_shot": r"{shotName}/{assetName}/OUT"}]

srcPath_templ = r"{projectName}/IN/src/{episodName}/{shotName}"

prmPath_templ = r"{projectName}/IN/prm/{episodName}"

hiresPath_templ = r"{projectName}/OUT/HiRes/{episodName}/{shotName}"

dailiesPath_templ = r"{projectName}/OUT/Dailies/{episodName}/{shotName}"


def getWork_Path(keyPrjData, taskData, create=False):
    keyPrjData = keyPrjData.copy()
    depth = keyDataProjectUtils.getDepth(keyPrjData) - 1
    template = list(workPaths[depth].values())[0]

    path = handleTemplate(keyPrjData, template, taskData)

    if not os.path.exists(path) and create is True:
        os.makedirs(path)
    return path


def getSRC_Path(keyPrjData):
    depth = keyDataProjectUtils.getDepth(keyPrjData)
    if depth < 3:  # if the depth is less than 3, then this is not a shot and it haven't HiRes
        print("expected shot data")
        return ""
    return handleTemplate(keyPrjData, srcPath_templ, root_dependence=True)


def getPRM_Path(keyPrjData):
    depth = keyDataProjectUtils.getDepth(keyPrjData)
    if depth < 2:  # if the depth is less than 2, then this is not an episod and it haven't prms
        print("expected episod data")
        return ""
    return handleTemplate(keyPrjData, prmPath_templ, root_dependence=True)


def getHires_Path(keyPrjData, version=None):
    version = None if version is False else version
    depth = keyDataProjectUtils.getDepth(keyPrjData)
    if depth < 3:  # if the depth is less than 3, then this is not a shot and it haven't HiRes
        print("expected shot data")
        return

    rawPath = handleTemplate(keyPrjData, hiresPath_templ, root_dependence=True)
    versionFile = ""
    try:
        versionFile = getVersioinFile(rawPath, version=version)[0]
    except exceptionUtils.pathError as err:
        err.displayMessageIcon()
        return
    return "/".join([rawPath, versionFile])


def getDailies_Path(keyPrjData, version=None):
    depth = keyDataProjectUtils.getDepth(keyPrjData)
    if depth < 3:  # if the depth is less than 3, then this is not a shot and it haven't Dailies
        print("expected shot data")
        return ""
    return handleTemplate(keyPrjData, dailiesPath_templ, root_dependence=True)


def getJobOut_Path(keyPrjData, taskData, version=None):
    keyPrjData = keyPrjData.copy()
    depth = keyDataProjectUtils.getDepth(keyPrjData) - 1
    template = list(jobOutPath[depth].values())[0]

    path = handleTemplate(keyPrjData, template, taskData, version=version)

    return path


def handleTemplate(keyPrjData, raw_template, taskData={}, version=None, root_dependence=False):

    if root_dependence is False:
        keyPrjPath = keyDataProjectUtils.getKeyPrjPath(keyPrjData)
    else:
        keyPrjPath = keyDataProjectUtils.getProjectFolder(keyPrjData)

    template = re.sub(r"(\{.*?\})", keyPrjPath, raw_template, count=1)

    keyPrjData.update(taskData)
    keyPrjData.update({"ver": version})

    kyeItems = [r'{projectName}', r'{episodName}', r'{shotName}', r'{assetName}', r'{taskName}', r'{ver}']

    keyData = keyPrjData.copy()
    for k, v in keyPrjData.items():
        try:
            new_key = [item for item in kyeItems if item.find(k) >= 0].pop(0)
            keyData[new_key] = keyData.pop(k)
        except IndexError:
            print("Template Error: template kye item - '{}' not found!".format(k))
            pass

    pattern = r"(\{.*?\})"
    path = re.sub(pattern, lambda x: repl(x, keyData), template)
    return path


def repl(match, keyData):
    for k in keyData.keys():
        if match.group(0) == k:
            return keyData[k]

    message = "Template item '{}' was not processed!".format(match.group(0))
    raise Exception(message)


def createFileName(keyPrjData, taskData, ver=None, ext="hip"):

    ver = version if ver is None else ver

    depth = keyDataProjectUtils.getDepth(keyPrjData) - 1
    keyItem = keyPrjData.get(list(keyPrjData.keys())[depth])
    assetName = taskData.get('assetName')
    fileName = "{}_{}_v{}.{}".format(keyItem, assetName, ver, ext)
    return fileName


def getVersioinFile(path, isFile=False, ext=None, version=None):

    catalog = os.path.dirname(path) if os.path.isfile(path) else path

    if not os.path.exists(catalog):
        raise exceptionUtils.pathError("Folder does not exists! : {}".format(catalog))

    if len(os.listdir(catalog)) == 0:
        raise exceptionUtils.pathError("Folder is empty! : {}".format(catalog))

    # Set pattern and get list of desired types files (files or directoreis).
    if isFile:
        catalogList = list(filter(lambda x: os.path.isfile(os.path.join(catalog, x)), os.listdir(catalog)))
        ext = r"\w{2,4}$" if ext is None else ext
        pattern = r"(?P<name>.+_v)(?P<ver>(?P<major>\d{1,3})([\._](?P<minor>\d{1,3}))?)(?P<ext>\." + ext + ")"
    else:
        catalogList = list(filter(lambda x: os.path.isdir(os.path.join(catalog, x)), os.listdir(catalog)))
        pattern = r"(?P<name>(^|.+_)v)(?P<ver>\d{1,3})$"

    # Filter files by pattern
    matchFiles = list(filter(lambda x: re.search(pattern, x, flags=re.IGNORECASE) is not None, catalogList))
    if len(matchFiles) == 0:
        pathError = exceptionUtils.pathError("{}: No versions found!".format(catalog))
        pathError.text = "No versions found! : {}".format(catalog)
        raise pathError

    if isFile is False:
        if version is None:  # Get latest version

            # Get latest file form match list
            resultFile = sorted(matchFiles, key=lambda x: re.search(pattern, x, flags=re.IGNORECASE).group('ver'))[-1]
        else:
            # Get desired version file
            try:
                resultFile = list(filter(lambda x: re.search(pattern, x, flags=re.IGNORECASE).group('ver') == version, matchFiles))[-1]
            except IndexError:
                pathError = exceptionUtils.pathError("Version '{}' for {} not found!".format(version, catalog))
                pathError.text = "Version '{}' for {} not found!".format(version, catalog)
                raise pathError

        collection = {"name": re.search(pattern, resultFile, flags=re.IGNORECASE).group('name'),
                      "vesion": re.search(pattern, resultFile, flags=re.IGNORECASE).group('ver')}
        return [resultFile, collection]

    else:
        if version is None:
            # Get list of all major versions
            major = [re.search(pattern, x, flags=re.IGNORECASE).group('major') for x in matchFiles]
            # Get the highest version
            maxMajor = sorted(major, key=lambda x: int(x))[-1]
            # If files have both major and minor version it also shold be sorted.
            maxMajorFiles = list(filter(lambda x: re.search(pattern, x, flags=re.IGNORECASE).group('major') == maxMajor, matchFiles))

            try:
                resultFile = sorted(maxMajorFiles, key=lambda x: re.search(pattern, x, flags=re.IGNORECASE).group('minor'))[-1]
            except TypeError:
                resultFile = maxMajorFiles[-1]

        else:
            resultFile = list(filter(lambda x: re.search(pattern, x, flags=re.IGNORECASE).group('ver') == version, matchFiles))[-1]

        collection = {"name": re.search(pattern, resultFile, flags=re.IGNORECASE).group('name'),
                      "version": re.search(pattern, resultFile, flags=re.IGNORECASE).group('ver'),
                      "major": re.search(pattern, resultFile, flags=re.IGNORECASE).group('major'),
                      "minor": re.search(pattern, resultFile, flags=re.IGNORECASE).group('minor'),
                      "extansion": re.search(pattern, resultFile, flags=re.IGNORECASE).group('ext')}
        return [resultFile, collection]


