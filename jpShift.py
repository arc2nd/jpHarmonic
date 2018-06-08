#cmds.deformer( type='jpShiftNode' )

import sys
 
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx
 
kPluginNodeTypeName = "jpShiftNode"

jpShiftNodeId = OpenMaya.MTypeId(0x5201) #range: 0-0x7ffff

# Node definition
class jpShiftNode(OpenMayaMPx.MPxDeformerNode):
	# class variables
	shiftX = OpenMaya.MObject()
	shiftY = OpenMaya.MObject()
	shiftZ = OpenMaya.MObject()
	# constructor
	def __init__(self):
		OpenMayaMPx.MPxDeformerNode.__init__(self)
	# deform
	def deform(self,dataBlock,geomIter,matrix,multiIndex):  
		#
		# get the shifts from the datablock
		shiftXHandle = dataBlock.inputValue( self.shiftX )
		shiftXValue = shiftXHandle.asDouble()
		shiftYHandle = dataBlock.inputValue( self.shiftY )
		shiftYValue = shiftYHandle.asDouble()
		shiftZHandle = dataBlock.inputValue( self.shiftZ )
		shiftZValue = shiftZHandle.asDouble()
		#
		# get the envelope
		envelope = OpenMayaMPx.cvar.MPxDeformerNode_envelope
		envelopeHandle = dataBlock.inputValue( envelope )
		envelopeValue = envelopeHandle.asFloat()
		#
		# iterate over the object and change the points
		while geomIter.isDone() == False:
			point = geomIter.position()

			point.x = point.x + shiftXValue*envelopeValue
			point.y = point.y + shiftYValue*envelopeValue
			point.z = point.z + shiftZValue*envelopeValue

			geomIter.setPosition( point )
			geomIter.next()
			
# creator
def nodeCreator():
	return OpenMayaMPx.asMPxPtr( jpShiftNode() )

# initializer
def nodeInitializer():
	# shift
	nAttr = OpenMaya.MFnNumericAttribute()
	jpShiftNode.shiftX = nAttr.create( "shiftX", "shX", OpenMaya.MFnNumericData.kDouble, 0.0 )
	nAttr.setKeyable(True)

	nAttr = OpenMaya.MFnNumericAttribute()
	jpShiftNode.shiftY = nAttr.create( "shiftY", "shY", OpenMaya.MFnNumericData.kDouble, 0.0 )
	nAttr.setKeyable(True)

	nAttr = OpenMaya.MFnNumericAttribute()
	jpShiftNode.shiftZ = nAttr.create( "shiftZ", "shZ", OpenMaya.MFnNumericData.kDouble, 0.0 )
	nAttr.setKeyable(True)

	# add attribute
	#try:
	outputGeom = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom

	jpShiftNode.addAttribute( jpShiftNode.shiftX )
	jpShiftNode.addAttribute( jpShiftNode.shiftY )
	jpShiftNode.addAttribute( jpShiftNode.shiftZ )

	jpShiftNode.attributeAffects( jpShiftNode.shiftX, outputGeom )
	jpShiftNode.attributeAffects( jpShiftNode.shiftY, outputGeom )
	jpShiftNode.attributeAffects( jpShiftNode.shiftZ, outputGeom )
	#except:
	#	sys.stderr.write( "Failed to create attributes of %s node\n", kPluginNodeTypeName )

# initialize the script plug-in
def initializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.registerNode( kPluginNodeTypeName, jpShiftNodeId, nodeCreator, nodeInitializer, OpenMayaMPx.MPxNode.kDeformerNode )
	except:
		sys.stderr.write( "Failed to register node: %s\n" % kPluginNodeTypeName )

# uninitialize the script plug-in
def uninitializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.deregisterNode( jpShiftNodeId )
	except:
		sys.stderr.write( "Failed to unregister node: %s\n" % kPluginNodeTypeName )