import nuke

import os
import json
import sys
import re

sys.path = list(set(sys.path + [os.environ.get('CGPIPELINE')]))
from _lib import configUtils, pathUtils, sequenceUtils, keyDataProjectUtils
from _lib.ffmpeg_lib import ffprobeUtils

import nkUtils

mainNkData = dict()

firstFrame = configUtils.firstFrame
padding = pathUtils.padding
baseVer = "0".zfill(padding)

seqPadding = 0
extension = ""

# Init script nodes
srcReadName = "SRC"
dnsWriteName = "DNS_OUT"
dnsReadName = "DNS"

hresWriteName = "HiRes_OUT"
hresReadName = 'HiRes'

dliesWriteName = "Daylies_OUT"
dliesReadName = "Daylies"

prmReadName = "PRM"


def getInit(args):
    global mainNkData
    mainNkData = args.get('mainNkData')
    nkFile = args.get('nkFile')
    keyPrjData = args.get('keyPrjData')
    extraJobData = args.get('extraJobData')

    prjFolder = keyDataProjectUtils.getProjectFolder(keyPrjData)
    masterScriptPath = prjFolder + "/config.nk"

    if os.path.exists(masterScriptPath):
        setupFromMasterScirpt(keyPrjData, extraJobData, nkFile, masterScriptPath)
    else:
        if initMasterScript(masterScriptPath, keyPrjData, extraJobData, ):
            setupFromMasterScirpt(keyPrjData, extraJobData, nkFile, masterScriptPath)


def setupFromMasterScirpt(keyPrjData, extraJobData, nkFile, masterScriptPath):
    nuke.scriptOpen(masterScriptPath)
    root = nuke.Root()

    metaNode = setupMetadataNode(keyPrjData)
    srcReadNode = setupSrcReadNode(keyPrjData)
    setupDnsWriteNode(keyPrjData)
    setupDnsReadNode()
    setupHresWriteNode(keyPrjData, srcReadNode)
    setupHresReadNode(srcReadNode)
    dliesWriteNode = setupDliesWriteNode(keyPrjData)

    prmReadNode = setupPrmReadNode(keyPrjData)
    setupDliesReadNode(dliesWriteNode, prmReadNode)

    setFrameRange(extraJobData.get('frames'), root, prmReadNode['file'].value(), metaNode)
    saveInitNkScript(nkFile)


def setupMetadataNode(keyPrjData):
    metaNode = nuke.toNode('project_metadata')
    metaNode.knob('episodName').setValue(keyPrjData.get('episod'))
    metaNode.knob('shotName').setValue(keyPrjData.get('shot'))
    metaNode.knob('padding').setValue(mainNkData.get('PADDING'))
    metaNode.knob('ver').setValue("1".zfill(int(mainNkData.get('PADDING'))))
    return metaNode


def setupSrcReadNode(keyPrjData):
    def setReadNodeProperties(seqRepr, seqFile, readNode=None):
        matchRange = re.search(r'\ \((\d*)-(\d*)\)$', seqRepr)
        startFrame = int(matchRange.group(1))
        endFrame = int(matchRange.group(2))
        seqPath = "/".join([srcPath, seqFile])

        readNode = readNode if readNode else nuke.createNode('Read')
        readNode.setName(srcReadName)
        readNode['file'].setValue(seqPath)
        readNode['frame_mode'].setValue(1)
        readNode['frame'].setValue(str(firstFrame))
        readNode['first'].setValue(startFrame)
        readNode['last'].setValue(endFrame)
        readNode['origfirst'].setValue(startFrame)
        readNode['origlast'].setValue(endFrame)
        return readNode

    srcPath = pathUtils.getSRC_Path(keyPrjData)
    if not os.path.exists(srcPath):
        print("=> SRC Erorr: the path not found {}".format(srcPath))
        return nuke.toNode(srcReadName)
    seq = sequenceUtils.getSequecneRepresentation(os.listdir(srcPath), countType='nuke')
    if not seq:
        return nuke.toNode(srcReadName)

    seqRepr = list(seq.keys())[0]
    seqFile = seq.get(seqRepr)
    seq.pop(seqRepr)

    global seqPadding, extension
    seqPadding = re.search(r'%0(\d{1,2})d', seqFile).group(1)
    extension = os.path.splitext(seqFile)[1]

    readNode = nuke.toNode(srcReadName)
    readNode = setReadNodeProperties(seqRepr, seqFile, readNode)

    if len(seq.items()) > 0:
        for seqRepr, seqFile in seq.items():
            setReadNodeProperties(seqRepr, seqFile)

    return readNode


def setupDnsWriteNode(keyPrjData):
    global seqPadding, extension
    dnsPath = 'footage/dns/v{ver}/{shotName}_dns_v{ver}.%0{padding}d{ext}'.format(ver='[value project_metadata.ver]',
                                                                                          shotName=keyPrjData.get('shot'),
                                                                                          padding=seqPadding,
                                                                                          ext=extension)
    dnsWriteNode = nuke.toNode(dnsWriteName)
    dnsWriteNode['file'].setValue(dnsPath)
    dnsWriteNode['frame'].setValue('[value SRC.first] + (frame - input.first_frame)')


def setupDnsReadNode():
    first = '[value {}.first]'.format(srcReadName)
    last = '[value {}.last]'.format(srcReadName)
    file = '[value {}.file]'.format(dnsWriteName)

    dnsReadNodeParms = [('file', file), ('frame_mode', 1), ('frame', str(firstFrame))]
    dnsReadNodeExpr = [('first', first), ('last', last), ('origfirst', first), ('origlast', last)]
    dnsReadNode = nuke.toNode(dnsReadName)
    dnsReadNode = nkUtils.setupNodeParms(dnsReadNode, dnsReadNodeParms, dnsReadNodeExpr)
    return dnsReadNode


def setupHresWriteNode(keyPrjData, srcReadName):
    hresPathTemplate = pathUtils.hiresPath_templ
    hresPath = pathUtils.handleTemplate(keyPrjData, hresPathTemplate, root_dependence=True)
    hrsOrigName = mainNkData.get('HIRES_ORIG_NAME')

    bodyNameTamlate = mainNkData.get('HIRES_TEMPLATE')
    outPadding = int(mainNkData.get('PADDING'))
    bodyName = bodyNameTamlate.format(shotName=keyPrjData.get('shot'), ver="1".zfill(outPadding))

    if hrsOrigName == 'false':
        global seqPadding, extension
        fileName = bodyName + "." + "%0" + str(seqPadding) + "d" + extension
        hresPath = "/".join([hresPath, bodyName, fileName])
    else:
        fileName = os.path.basename(srcReadName['file'].getValue())
        hresPath = "/".join([hresPath, bodyName, fileName])

    hresWriteNode = nuke.toNode(hresWriteName)
    hresWriteNode['file'].setValue(hresPath)
    hresWriteNode['frame'].setValue('[value SRC.first] + (frame - input.first_frame)')
    # hresWriteNode['frame_mode'].setValue(2)
    # try:
    #     offset = srcReadName['first'].value() - int(srcReadName['frame'].value())
    #     hresWriteNode['frame'].setValue(str(offset))
    # except ValueError as err:
    #     print(err)


def setupHresReadNode(srcReadNode):
    first = '[value {}.first]'.format(srcReadName)
    last = '[value {}.last]'.format(srcReadName)
    file = '[value {}.file]'.format(hresWriteName)

    hresReadNodeParms = [('file', file), ('frame_mode', 1), ('frame', str(firstFrame))]
    hresReadNodeExpr = [('first', first), ('last', last), ('origfirst', first), ('origlast', last)]
    hresReadNode = nuke.toNode(hresReadName)
    hresReadNode = nkUtils.setupNodeParms(hresReadNode, hresReadNodeParms, hresReadNodeExpr)
    return hresReadNode
    # hresReadNode = nuke.toNode(hresReadName)

    # hresReadNode['frame_mode'].setValue(srcReadNode['frame_mode'].value())
    # hresReadNode['frame'].setValue(srcReadNode['frame'].value())
    # hresReadNode['first'].setValue(int(srcReadNode['first'].value()))
    # hresReadNode['last'].setValue(int(srcReadNode['last'].value()))
    # hresReadNode['origfirst'].setValue(int(srcReadNode['origfirst'].value()))
    # hresReadNode['origlast'].setValue(int(srcReadNode['origlast'].value()))
    # return hresReadNode


def setupDliesWriteNode(keyPrjData):
    dliesPathTemplate = pathUtils.dailiesPath_templ
    dliesPath = pathUtils.handleTemplate(keyPrjData, dliesPathTemplate, root_dependence=True)
    fileName = keyPrjData.get('shot') + "_v" + "1".zfill(padding) + ".mov"

    dliesPath = "/".join([dliesPath, fileName])

    dliesWriteNode = nuke.toNode(dliesWriteName)
    dliesWriteNode['file'].setValue(dliesPath)
    return dliesWriteNode


def setupDliesReadNode(dliesWriteNode, prmReadNode):
    readNode = nuke.toNode(dliesReadName)
    if not readNode:
        return

    readNode['frame_mode'].setValue(1)
    readNode['frame'].setValue(prmReadNode['frame'].value())
    readNode['first'].setValue(prmReadNode['first'].value())
    readNode['last'].setValue(prmReadNode['last'].value())
    readNode['origfirst'].setValue(prmReadNode['origfirst'].value())
    readNode['origlast'].setValue(prmReadNode['origlast'].value())

    frRangeNode = nuke.createNode('FrameRange')
    frRangeNode.setInput(0, readNode)
    frRangeNode.knob('first_frame').setValue(firstFrame)
    frRangeNode.knob('last_frame').setValue(firstFrame + readNode.knob('last').value() - 1)
    setPosUnderTheNode(frRangeNode, readNode, 100)


def setupPrmReadNode(keyPrjData):
    def setPrmNodeProperties(prm, readNode=None):
        readNode = readNode if readNode else nuke.createNode('Read')
        readNode.setName(prmReadName)
        readNode.knob('file').fromUserText(prm)
        readNode['frame_mode'].setValue(1)
        readNode['frame'].setValue(str(firstFrame))

        frRangeNode = nuke.createNode('FrameRange')
        frRangeNode.setInput(0, readNode)
        frRangeNode.knob('first_frame').setValue(firstFrame)
        frRangeNode.knob('last_frame').setValue(firstFrame + readNode.knob('last').value() - 1)
        return readNode

    path = pathUtils.getPRM_Path(keyPrjData)
    try:
        catalogList = os.listdir(path)
    except FileNotFoundError:
        print("=> PRM Error: Folder does not exists! : {}".format(path))
        return nuke.toNode(prmReadName)

    shotName = keyPrjData.get('shot')
    prmList = ["/".join([path, file]) for file in catalogList if file.lower().find(shotName.lower()) >= 0]

    if len(prmList) == 0:
        print("=> PRM Error: prm not found for shot {}!".format(shotName))
        return nuke.toNode(prmReadName)

    prm = prmList.pop()
    readNode = nuke.toNode(prmReadName)
    readNode = setPrmNodeProperties(prm, readNode)

    if len(prmList) > 0:
        for prm in prmList:
            setPrmNodeProperties(prm)
    return readNode


def setScriptFormat(keyPrjData, root):
    prjName = keyPrjData.get('project')

    prjFormat = nuke.addFormat("{} {}".format(mainNkData.get('RESX'), mainNkData.get('RESY')))
    prjFormat.setName("PRJ_{}".format(prjName))
    prjFormat.setPixelAspect(int(mainNkData.get("PIXEL_APECT")))

    root['format'].setValue(prjFormat)


def setFrameRange(frames, root, prm, metaNode):
    framesCount = frames if frames else getFramesFromPrm(prm)
    root['first_frame'].setValue(firstFrame)
    root['last_frame'].setValue(firstFrame + int(framesCount) - 1)
    metaNode.knob('duration').setValue(str(framesCount))


def getFramesFromPrm(prm):
    fps = nkConfig.get('FPS')
    if prm == 'file not specified':
        return "100"
    print("PRM IS ", prm)
    duration = ffprobeUtils.getDuration(prm)
    frames = round(duration * int(fps))
    return frames


def initMasterScript(masterScriptPath, keyPrjData, extraJobData):
    print("=> Creating nk config script.")

    def createReadNode(name, file):
        readNode = nuke.createNode('Read')
        readNode.setName(name)
        readNode['file'].setValue(file)
        return readNode

    def createWriteNode(name, parms):
        writeNode = nuke.createNode('Write')
        writeNode.setName(name)
        for k, v in parms:
            writeNode[k].setValue(v)
        return writeNode

    root = nuke.Root()
    root.knob('project_directory').setValue('[python {nuke.script_directory()}]')
    setScriptFormat(keyPrjData, root)
    root['fps'].setValue(int(mainNkData.get('FPS')))

    # - metadata Node
    metaNode = nuke.createNode('project_metadata')
    metaNode.setName('project_metadata')
    metaNode.knob('projectName').setValue(keyPrjData.get('project'))

    # - source readNode
    srcReadNode = createReadNode(srcReadName, 'file not specified')

    # - denoise writeNode
    # afterRender = "import thread; rld = nuke.toNode('" + dnsReadName + "')['reload']; thread.start_new_thread(rld.execute, ())"
    dnsWriteNodeParms = [('file', 'file not specified'), ('create_directories', 1)]  # , ('afterRender', afterRender)]
    dnsWriteNode = createWriteNode(dnsWriteName, dnsWriteNodeParms)
    setPosUnderTheNode(dnsWriteNode, srcReadNode, 500)
    dnsWriteNode.setInput(0, srcReadNode)

    # - denoise ReadNode
    dnsReadNode = createReadNode(dnsReadName, "[python {nuke.toNode('%s')['file'].value()}]" % dnsWriteNode.name())
    setPosUnderTheNode(dnsReadNode, dnsWriteNode)

    # - hires writeNode
    # afterRender = "import thread; rld = nuke.toNode('" + hresReadName + "')['reload']; thread.start_new_thread(rld.execute, ())"
    hresWriteNodeParms = [('file', 'file not specified'), ('create_directories', 1)]  # , ('afterRender', afterRender)]
    hresWriteNode = createWriteNode(hresWriteName, hresWriteNodeParms)
    setPosUnderTheNode(hresWriteNode, dnsReadNode, 800)
    hresWriteNode.setInput(0, dnsReadNode)

    # - hires readNode
    hresReadNode = createReadNode(hresReadName, "[python {nuke.toNode('%s')['file'].value()}]" % hresWriteNode.name())
    setPosUnderTheNode(hresReadNode, hresWriteNode)

    # - daylies writeNode
    dliesWriteNodeParms = [('file', 'file not specified'), ('create_directories', 1), ('file_type', 'move'),
                           ('meta_codec', 'jpeg'), ('mov64_quality_min', 1), ('mov64_quality_max', 2)]
    dliesWriteNode = createWriteNode(dliesWriteName, dliesWriteNodeParms)
    setPosUnderTheNode(dliesWriteNode, hresReadNode)
    dliesWriteNode.setInput(0, hresReadNode)

    # - daylies readNode
    dliesReadNode = createReadNode(dliesReadName, "[value %s.file]" % dliesWriteName)
    setPosUnderTheNode(dliesReadNode, dliesWriteNode)

    # - prm readNode
    prmReadNode = createReadNode(prmReadName, 'file not specified')
    prmReadNode.setXYpos(srcReadNode.xpos() + 300, srcReadNode.ypos())

    return nuke.scriptSave(masterScriptPath)


def saveInitNkScript(nkFile):
    folder = os.path.dirname(nkFile)
    if not os.path.exists(folder):
        os.makedirs(folder)

    baseNkFile = re.sub(r'(.*)(_v\d{1,5})(\..*$)', '\\1_v{}\\3'.format(baseVer), nkFile)
    nuke.scriptSave(baseNkFile)
    nuke.scriptSave(nkFile)


def setPosUnderTheNode(node2, node1, offset=100):
    node2.setXYpos(node1.xpos(), node1.ypos() + offset)


if not sys.stdin.isatty():
    args = sys.stdin.readline().decode("utf-8")
    args = json.loads(args)
    getInit(args)
    print("=> nkython bridge process finished.")
else:
    print("=> nkython bridge has no args.")
