import nuke


def setupNodeParms(node, parms, expr=[], new=None):
    if new:
        node = nuke.createNode(new)
    for k, v in parms:
        node[k].setValue(v)
    for k, v in expr:
        node[k].setExpression(v)
    return node

# def setupReadWriteNode(rNode, wrNode):
#     firstFrame = '[value {}.first]'.fomrat(wrNode)
#     lastFrame = '[value {}.last]'.fomrat(wrNode)

#     file = '[value {}.file]'.format(wrNodeName)
#     dnsReadNodeParms = [('file', file), ('first', firstFrame), ('last', lastFrame), ('origfirst', firstFrame), ('origlast', lastFrame)]
#     dnsReadNode = nuke.toNode(dnsReadName)
#     dnsReadNode = nkUtils.setupNodeParms(dnsReadNodeParms, dnsReadNode)
#     pass