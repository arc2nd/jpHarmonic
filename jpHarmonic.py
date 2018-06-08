#cmds.deformer( type='jpHarmonicNode' )
#cmds.calcHarm( driver, harmNode)
import sys
import math
import decimal
 
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx

##Deformer Node
kPluginNodeTypeName = "jpHarmonicNode"
jpHarmonicNodeId = OpenMaya.MTypeId(0x5282) #range: 0-0x7ffff

decimal.getcontext().prec = 4

# Node definition
class jpHarmonicNode(OpenMayaMPx.MPxDeformerNode):
	# class variables
	# inputs
	currentFrame = OpenMaya.MObject()
	wavelength = OpenMaya.MObject()
	ampDecay = OpenMaya.MObject()
	waveNum = OpenMaya.MObject()
	waveScaleX = OpenMaya.MObject()
	waveScaleY = OpenMaya.MObject()
	waveScaleZ = OpenMaya.MObject()
	waveScale = OpenMaya.MObject()
	storageTransX = OpenMaya.MObject()
	storageTransY = OpenMaya.MObject()
	storageTransZ = OpenMaya.MObject()
	storageTranslate = OpenMaya.MObject()
	hitFrameX = OpenMaya.MObject()
	hitFrameY = OpenMaya.MObject()
	hitFrameZ = OpenMaya.MObject()
	hitFrames = OpenMaya.MObject()
	ampX = OpenMaya.MObject()
	ampY = OpenMaya.MObject()
	ampZ = OpenMaya.MObject()
	amps = OpenMaya.MObject()
	outputX = OpenMaya.MObject()
	outputY = OpenMaya.MObject()
	outputZ = OpenMaya.MObject()
	outputTranslate =  OpenMaya.MObject()
	
	# constructor
	def __init__(self):
		OpenMayaMPx.MPxDeformerNode.__init__(self)
	
	def getAnimCurve(self, attribute):
		inputPlug= OpenMaya.MPlug(self.thisMObject(), attribute)
		connectedPlugs = OpenMaya.MPlugArray()

		asDst = True
		asSrc = False
		sourcePlug=None
		sourceObj=None
		source2Plug=None
		source2Obj=None

		inputPlug.connectedTo(connectedPlugs,asDst, asSrc)

		if (connectedPlugs.length() > 0):
			sourcePlug = connectedPlugs[0]
			sourceObj = sourcePlug.node()
			if (sourceObj.hasFn(OpenMaya.MFn.kAnimCurve)):
				return sourceObj;
			else:
				sourcePlug.connectedTo(connectedPlugs, asDst, asSrc);

				if (connectedPlugs.length() > 0):
					source2Plug = connectedPlugs[0]
					source2Obj = source2Plug.node()
					if (source2Obj.hasFn(OpenMaya.MFn.kAnimCurve)):
						return  source2Obj
		return None

	# deform
	def deform(self,dataBlock,geomIter,matrix,multiIndex):
		eConst = 2.718#2.71828
	
		# get the envelope
		envelope = OpenMayaMPx.cvar.MPxDeformerNode_envelope
		envelopeHandle = dataBlock.inputValue( envelope )
		envelopeFloat = envelopeHandle.asFloat()
		
		#Get the current frame
		currentFrameHandle = dataBlock.inputValue(self.currentFrame)
		currentFrameFloat = currentFrameHandle.asFloat()
		currentFrameTime = currentFrameHandle.asTime()
		
		#Set time units and granularity
		#	Double
		timeGranFloat = 1.0
		fut1Double = currentFrameFloat + timeGranFloat
		last1Double = currentFrameFloat - timeGranFloat
		last2Double = last1Double - timeGranFloat
		
		#	MTime
		timeGranTime = OpenMaya.MTime(1.0, OpenMaya.MTime.uiUnit())
		curTime = OpenMaya.MTime(int(currentFrameFloat),OpenMaya.MTime.uiUnit())
		last2Time = OpenMaya.MTime(int(currentFrameFloat) - (int(timeGranFloat) * 2),OpenMaya.MTime.uiUnit())
		last1Time = OpenMaya.MTime(int(currentFrameFloat) - int(timeGranFloat),OpenMaya.MTime.uiUnit())
		fut1Time = OpenMaya.MTime(int(currentFrameFloat) + int(timeGranFloat),OpenMaya.MTime.uiUnit())
		fut2TIme = OpenMaya.MTime(int(currentFrameFloat) + (int(timeGranFloat) * 2), OpenMaya.MTime.uiUnit())
		
		#Get the wavelength
		wavelengthHandle = dataBlock.inputValue(self.wavelength)
		wavelengthFloat = wavelengthHandle.asFloat()
		
		#Get the amplitude decay
		ampDecayHandle = dataBlock.inputValue(self.ampDecay)
		ampDecayFloat = ampDecayHandle.asFloat()
		
		#Get the number of waves
		waveNumHandle = dataBlock.inputValue(self.waveNum)
		waveNumFloat = waveNumHandle.asFloat()
		
		#Get the waveScaleX,Y,Z values
		waveScaleXHandle = dataBlock.inputValue(self.waveScaleX)
		waveScaleXFloat = waveScaleXHandle.asFloat()
		waveScaleYHandle = dataBlock.inputValue(self.waveScaleY)
		waveScaleYFloat = waveScaleYHandle.asFloat()
		waveScaleZHandle = dataBlock.inputValue(self.waveScaleZ)
		waveScaleZFloat = waveScaleZHandle.asFloat()
		
		#Get the storageTransX,Y,Z values
		storageTransXHandle = dataBlock.inputValue(self.storageTransX)
		storageTransXFloat = storageTransXHandle.asFloat()
		storageTransYHandle = dataBlock.inputValue(self.storageTransY)
		storageTransYFloat = storageTransYHandle.asFloat()
		storageTransZHandle = dataBlock.inputValue(self.storageTransZ)
		storageTransZFloat = storageTransZHandle.asFloat()
		
		#Get the hitFrameX,Y,Z values
		hitFrameXHandle = dataBlock.inputValue(self.hitFrameX)
		hitFrameXFloat = hitFrameXHandle.asFloat()
		hitFrameYHandle = dataBlock.inputValue(self.hitFrameY)
		hitFrameYFloat = hitFrameYHandle.asFloat()
		hitFrameZHandle = dataBlock.inputValue(self.hitFrameZ)
		hitFrameZFloat = hitFrameZHandle.asFloat()
		
		#Get the ampX,Y,Z values
		ampXHandle = dataBlock.inputValue(self.ampX)
		ampXFloat = ampXHandle.asFloat()
		ampYHandle = dataBlock.inputValue(self.ampY)
		ampYFloat = ampYHandle.asFloat()
		ampZHandle = dataBlock.inputValue(self.ampZ)
		ampZFloat = ampZHandle.asFloat()
		
		#Get the storageTransX,Y,Z curves
		transXCurve = self.getAnimCurve(self.storageTransX)
		transYCurve = self.getAnimCurve(self.storageTransY)
		transZCurve = self.getAnimCurve(self.storageTransZ)
		
		#preset variables
		harmX = 0.0
		harmY = 0.0
		harmZ = 0.0
		
		harmMin = 0.001
		
		hitFrmX = 0.0
		hitFrmY = 0.0
		hitFrmZ = 0.0
		
		##Calculate an X harmonic
		if transXCurve:
			transXCurveFn = OpenMayaAnim.MFnAnimCurve(transXCurve)
			
			#Get the animCurve values
			last2X = transXCurveFn.evaluate(last2Time) ##`getAttr -time twoLstTime storageTransX
			last1X = transXCurveFn.evaluate(last1Time) ##`getAttr -time lstTime storageTransX
			curX = transXCurveFn.evaluate(curTime) ##`getAttr -time curTime storageTransX
			fut1X = transXCurveFn.evaluate(fut1Time) ##`getAttr -time furTime storageTransX
			
			#Calculate some distances and velocities
			distXLst = (last1X - last2X) ## distance between 2 frames ago and 1 frame ago
			distX = (fut1X - last1X)	## distance between 1 frame ago and 1 frame from now
			distXNxt = (fut1X - curX) ## distance between current frame and 1 frame from now
			speXCur = (distX/2.0) ## half of distance between last frame and next frame
			velXLst = abs(distXLst) ## absolute value of previous distance (effectively the velocity)
			velXCur = abs(speXCur) ## absolute value of half of last and next distance (effectively the velocity)
			velXNxt = abs(distXNxt) ## absolute value of next distance (effectively the velocity)

			accX = ((last1X - 2.0 * curX + fut1X)) * waveNumFloat ## acceleration?

			if velXCur != velXNxt:
				hitFrmX = currentFrameFloat
				hitFrameOutHandle = dataBlock.outputValue(self.hitFrameX)
				hitFrameOutHandle.setFloat(currentFrameFloat)
			else:
				#hitFrmX = hitFrmX
				hitFrmX = hitFrameXFloat

			if accX != 0:
				AmpX = (accX * waveNumFloat) * waveScaleXFloat
				ampXOutHandle = dataBlock.outputValue(self.ampX)
				ampXOutHandle.setFloat(float(AmpX))
			else:
				AmpX = ampXFloat

			if hitFrmX:
				#expX = math.exp((float(hitFrmX) - float(currentFrameFloat)) * ampDecayFloat)
				#expX = math.e**(float(hitFrmX) - float(currentFrameFloat)) * ampDecayFloat
				#expX = decimal.Decimal(str(math.exp(float(hitFrmX) - float(currentFrameFloat) * ampDecayFloat)))
				expX = eConst ** ((hitFrmX - currentFrameFloat) * ampDecayFloat)
				sinX = decimal.Decimal(str(math.sin((float(hitFrmX) - float(currentFrameFloat))) * 1.0/wavelengthFloat))
				harmX = float(AmpX) * float(sinX) * float(expX)
				
				#print "Acceleration  X :: ", accX
				#print "HitFrameX       :: ", hitFrmX
				#print "Amp X           :: ", AmpX
				#print "Exp X           :: ", expX
				#print "Sin X           :: ", sinX
			
			outputXHandle = dataBlock.outputValue(self.outputX)
			outputXHandle.setFloat(float(harmX))
			
			#numKeys = transXCurveFn.numKeys()
		else:
			# There is no key so exit compute
			print "No keys set in the storageTransX channel. Harmonic not calced."
			#return
			
		##Calculate a Y harmonic
		if transYCurve:
			transYCurveFn = OpenMayaAnim.MFnAnimCurve(transYCurve)
			
			last2Y = transYCurveFn.evaluate(last2Time)
			last1Y = transYCurveFn.evaluate(last1Time)
			curY = transYCurveFn.evaluate(curTime)
			fut1Y = transYCurveFn.evaluate(fut1Time)
			
			#Calculate some distances and velocities
			distYLst = (last1Y - last2Y)
			distY = (fut1Y - last1Y)
			distYNxt = (fut1Y - curY)
			speYCur = (distY/2.0)
			velYLst = abs(distYLst)
			velYCur = abs(speYCur)
			velYNxt = abs(distYNxt)

			accY = ((last1Y - 2.0 * curY + fut1Y)) * waveNumFloat

			if velYCur != velYNxt:
				hitFrmY = currentFrameFloat
				hitFrameOutHandle = dataBlock.outputValue(self.hitFrameY)
				hitFrameOutHandle.setFloat(float(currentFrameFloat))
			else:
				#hitFrmX = hitFrmX
				hitFrmY = hitFrameYFloat

			if accY != 0:
				AmpY = (accY * waveNumFloat) * waveScaleYFloat
				ampYOutHandle = dataBlock.outputValue(self.ampY)
				ampYOutHandle.setFloat(float(AmpY))
			else:
				AmpY = ampYFloat

			#if hitFrmY:
				#expY = math.exp((float(hitFrmY) - float(currentFrameFloat)) * ampDecayFloat)
				#expY = math.e**(float(hitFrmY) - float(currentFrameFloat)) * ampDecayFloat
				#expY = decimal.Decimal(str(math.exp(float(hitFrmY) - float(currentFrameFloat) * ampDecayFloat)))
				expY = eConst ** ((hitFrmY - currentFrameFloat) * ampDecayFloat)
				sinY = decimal.Decimal(str(math.sin((float(hitFrmY) - float(currentFrameFloat))) * 1.0/wavelengthFloat))
				harmY = AmpY * float(sinY) * float(expY)
			
			outputYHandle = dataBlock.outputValue(self.outputY)
			outputYHandle.setFloat(float(harmY))
		else:
			# There is no key so exit compute
			print "No keys set in the storageTransY channel. Harmonic not calced."
			#return
			
		##Calculate a Z harmonic
		if transZCurve:
			transZCurveFn = OpenMayaAnim.MFnAnimCurve(transZCurve)
			
			last2Z = transZCurveFn.evaluate(last2Time)
			last1Z = transZCurveFn.evaluate(last1Time)
			curZ = transZCurveFn.evaluate(curTime)
			fut1Z = transZCurveFn.evaluate(fut1Time)
			
			#Calculate some distances and velocities
			distZLst = (last1Z - last2Z)
			distZ = (fut1Z - last1Z)
			distZNxt = (fut1Z - curZ)
			speZCur = (distZ/2.0)
			velZLst = abs(distZLst)
			velZCur = abs(speZCur)
			velZNxt = abs(distZNxt)

			accZ = ((last1Z - 2.0 * curZ + fut1Z)) * waveNumFloat

			if velZCur != velZNxt:
				hitFrmZ = currentFrameFloat
				hitFrameOutHandle = dataBlock.outputValue(self.hitFrameZ)
				hitFrameOutHandle.setFloat(float(currentFrameFloat))
			else:
				hitFrmZ = hitFrameZFloat

			if accZ != 0:
				AmpZ = (accZ * waveNumFloat) * waveScaleZFloat
				ampZOutHandle = dataBlock.outputValue(self.ampZ)
				ampZOutHandle.setFloat(float(AmpZ))
			else:
				AmpZ = ampZFloat

			if hitFrmZ:
			#	expZ = math.exp((float(hitFrmZ) - float(currentFrameFloat)) * ampDecayFloat)
			#	expZ = math.e**(float(hitFrmZ) - float(currentFrameFloat)) * ampDecayFloat
			#	expZ = decimal.Decimal(str(math.exp(float(hitFrmZ) - float(currentFrameFloat) * ampDecayFloat)))
				expZ = eConst ** ((hitFrmZ - currentFrameFloat) * ampDecayFloat)
				sinZ = decimal.Decimal(str(math.sin((float(hitFrmZ) - float(currentFrameFloat))) * 1.0/wavelengthFloat))
				harmZ = AmpZ * float(sinZ) * float(expZ)
				
				#print "Acceleration  Z :: ", accZ
				#print "HitFrameZ       :: ", float(hitFrmZ)
				#print "Amp Z           :: ", AmpZ
				#print "Exp Z           :: ", expZ
				#print "Sin Z           :: ", sinZ
			
			outputZHandle = dataBlock.outputValue(self.outputZ)
			outputZHandle.setFloat(float(harmZ))
		else:
			# There is no key so exit compute
			print "No keys set in the storageTransZ channel. Harmonic not calced."
			#return

		if abs(harmX) < harmMin:
			harmX = 0.0
		if abs(harmY) < harmMin:
			harmY = 0.0
		if abs(harmZ) < harmMin:
			harmZ = 0.0
			
		harmVec = OpenMaya.MVector(float(harmX), float(harmY), float(harmZ))
		#worldMatrix = OpenMayaMPxTransform(self).worldMatrix
		localHarmVec = harmVec.transformAsNormal(matrix)
		multHarmVec = localHarmVec * harmVec.length()		
		
		#iterate over the object and change the points
		while geomIter.isDone() == False:
			point = geomIter.position()

			#point.x = point.x + float(harmX)*envelopeFloat
			#point.y = point.y + float(harmY)*envelopeFloat
			#point.z = point.z + float(harmZ)*envelopeFloat
			
			point = point + (multHarmVec * envelopeFloat)

			geomIter.setPosition(point)
			geomIter.next()

		#Printy
		#print matrix[0][0], matrix[0][1], matrix[0][2], matrix[0][3]
		#print matrix[1][0], matrix[1][1], matrix[1][2], matrix[1][3]
		#print matrix[2][0], matrix[2][1], matrix[2][2], matrix[2][3]
		#print matrix[3][0], matrix[3][1], matrix[3][2], matrix[3][3]

		#print tempMatrix
		print "Harm X          :: ", multHarmVec.x * envelopeFloat
		print "Harm Y          :: ", multHarmVec.y * envelopeFloat
		print "Harm Z          :: ", multHarmVec.z * envelopeFloat
		print "\n"

		#print "\tAttributes"
		#print "Envelope          :: ", str(envelopeFloat)
		#print "Current Frame     :: ", str(currentFrameFloat)	
		#print "Future 1 Time     :: ", str(fut1Double)
		#print "Last 1 Time       :: ", str(last1Double)
		#print "Last 2 Time       :: ", str(last2Double)
		#print "Wavelength        :: ", str(wavelengthFloat)
		#print "Amplitude Decay   :: ", str(ampDecayFloat)
		#print "Number of Waves   :: ", str(waveNumFloat)
		#print "Wave Scale        :: ", str(waveScaleXFloat), str(waveScaleYFloat), str(waveScaleZFloat)
		#print "Storage Translate :: ", str(storageTransXFloat), str(storageTransYFloat), str(storageTransZFloat)
		#print "Hit Frames        :: ", str(hitFrmX), str(hitFrmY), str(hitFrmZ)
		#print "\n"
		
		
			
#creator
def nodeCreator():
	return OpenMayaMPx.asMPxPtr( jpHarmonicNode() )

#initializer
def nodeInitializer():
	#harmonic input channels
	nAttr = OpenMaya.MFnNumericAttribute()	
	
	#currentFrame channel
	jpHarmonicNode.currentFrame = nAttr.create( "currentFrame", "cf", OpenMaya.MFnNumericData.kFloat, 0.0 )
	nAttr.setKeyable(True)
	
	#wavelength channel
	jpHarmonicNode.wavelength = nAttr.create( "wavelength", "wle", OpenMaya.MFnNumericData.kFloat, 3.0 )
	nAttr.setKeyable(True)
	
	#ampDecay channel
	jpHarmonicNode.ampDecay = nAttr.create( "ampDecay", "ad", OpenMaya.MFnNumericData.kFloat, 0.08 )
	nAttr.setKeyable(True)
	
	#waveNum channel
	jpHarmonicNode.waveNum = nAttr.create( "waveNum", "wn", OpenMaya.MFnNumericData.kFloat, 3.0 )
	nAttr.setKeyable(True)
	
	#waveScale channels
	jpHarmonicNode.waveScaleX = nAttr.create( "waveScaleX", "wsx", OpenMaya.MFnNumericData.kFloat, 1.0 )
	nAttr.setKeyable(True)
	jpHarmonicNode.waveScaleY = nAttr.create( "waveScaleY", "wsy", OpenMaya.MFnNumericData.kFloat, 1.0 )
	nAttr.setKeyable(True)
	jpHarmonicNode.waveScaleZ = nAttr.create( "waveScaleZ", "wsz", OpenMaya.MFnNumericData.kFloat, 1.0 )
	nAttr.setKeyable(True)
	jpHarmonicNode.waveScale =  nAttr.create("waveScale", "wsa", jpHarmonicNode.waveScaleX, jpHarmonicNode.waveScaleY, jpHarmonicNode.waveScaleZ)
	nAttr.setKeyable(True)
	
	#harmonic storage channels
	jpHarmonicNode.storageTransX = nAttr.create( "storageTransX", "stx", OpenMaya.MFnNumericData.kFloat, 0.0 )
	nAttr.setKeyable(True)
	jpHarmonicNode.storageTransY = nAttr.create( "storageTransY", "sty", OpenMaya.MFnNumericData.kFloat, 0.0 )
	nAttr.setKeyable(True)
	jpHarmonicNode.storageTransZ = nAttr.create( "storageTransZ", "stz", OpenMaya.MFnNumericData.kFloat, 0.0 )
	nAttr.setKeyable(True)
	jpHarmonicNode.storageTranslate =  nAttr.create("storageTranslate", "stT", jpHarmonicNode.storageTransX, jpHarmonicNode.storageTransY, jpHarmonicNode.storageTransZ)
	nAttr.setKeyable(True)
	
	#hitFrame storage channels
	jpHarmonicNode.hitFrameX = nAttr.create( "hitFrameX", "hfx", OpenMaya.MFnNumericData.kFloat, 0.0 )
	#nAttr.setKeyable(True)
	jpHarmonicNode.hitFrameY = nAttr.create( "hitFrameY", "hfy", OpenMaya.MFnNumericData.kFloat, 0.0 )
	#nAttr.setKeyable(True)
	jpHarmonicNode.hitFrameZ = nAttr.create( "hitFrameZ", "hfz", OpenMaya.MFnNumericData.kFloat, 0.0 )
	#nAttr.setKeyable(True)
	jpHarmonicNode.hitFrames =  nAttr.create("hitFrames", "hfa", jpHarmonicNode.hitFrameX, jpHarmonicNode.hitFrameY, jpHarmonicNode.hitFrameZ)
	#nAttr.setKeyable(True)
	
	#amp storage channels
	jpHarmonicNode.ampX = nAttr.create( "ampX", "apx", OpenMaya.MFnNumericData.kFloat, 0.0 )
	#nAttr.setKeyable(True)
	jpHarmonicNode.ampY = nAttr.create( "ampY", "apy", OpenMaya.MFnNumericData.kFloat, 0.0 )
	#nAttr.setKeyable(True)
	jpHarmonicNode.ampZ = nAttr.create( "ampZ", "apz", OpenMaya.MFnNumericData.kFloat, 0.0 )
	#nAttr.setKeyable(True)
	jpHarmonicNode.amps =  nAttr.create("amps", "amp", jpHarmonicNode.ampX, jpHarmonicNode.ampY, jpHarmonicNode.ampZ)
	#nAttr.setKeyable(True)
	
	#amp storage channels
	jpHarmonicNode.outputX = nAttr.create( "outputX", "otx", OpenMaya.MFnNumericData.kFloat, 0.0 )
	nAttr.setKeyable(True)
	jpHarmonicNode.outputY = nAttr.create( "outputY", "oty", OpenMaya.MFnNumericData.kFloat, 0.0 )
	nAttr.setKeyable(True)
	jpHarmonicNode.outputZ = nAttr.create( "outputZ", "otz", OpenMaya.MFnNumericData.kFloat, 0.0 )
	nAttr.setKeyable(True)
	jpHarmonicNode.outputs =  nAttr.create("outputs", "ots", jpHarmonicNode.outputX, jpHarmonicNode.outputY, jpHarmonicNode.outputZ)
	nAttr.setKeyable(True)

	# add attribute
	#try:
	outputGeom = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom

	#single attributes
	jpHarmonicNode.addAttribute(jpHarmonicNode.currentFrame)
	jpHarmonicNode.addAttribute(jpHarmonicNode.wavelength)
	jpHarmonicNode.addAttribute(jpHarmonicNode.ampDecay)
	jpHarmonicNode.addAttribute(jpHarmonicNode.waveNum)
	
	#multi attributes
	jpHarmonicNode.addAttribute(jpHarmonicNode.waveScale)
	jpHarmonicNode.addAttribute(jpHarmonicNode.storageTranslate)
	jpHarmonicNode.addAttribute(jpHarmonicNode.hitFrames)
	jpHarmonicNode.addAttribute(jpHarmonicNode.amps)
	jpHarmonicNode.addAttribute(jpHarmonicNode.outputs)

	#attribute affects
	jpHarmonicNode.attributeAffects(jpHarmonicNode.currentFrame, outputGeom)
	jpHarmonicNode.attributeAffects(jpHarmonicNode.wavelength, outputGeom)
	jpHarmonicNode.attributeAffects(jpHarmonicNode.ampDecay, outputGeom)
	jpHarmonicNode.attributeAffects(jpHarmonicNode.waveNum, outputGeom)
	jpHarmonicNode.attributeAffects(jpHarmonicNode.waveScaleX, outputGeom)
	jpHarmonicNode.attributeAffects(jpHarmonicNode.waveScaleY, outputGeom)
	jpHarmonicNode.attributeAffects(jpHarmonicNode.waveScaleZ, outputGeom)
	jpHarmonicNode.attributeAffects(jpHarmonicNode.hitFrameX, outputGeom)
	jpHarmonicNode.attributeAffects(jpHarmonicNode.hitFrameY, outputGeom)
	jpHarmonicNode.attributeAffects(jpHarmonicNode.hitFrameY, outputGeom)
	jpHarmonicNode.attributeAffects(jpHarmonicNode.ampX, outputGeom)
	jpHarmonicNode.attributeAffects(jpHarmonicNode.ampY, outputGeom)
	jpHarmonicNode.attributeAffects(jpHarmonicNode.ampZ, outputGeom)
	jpHarmonicNode.attributeAffects(jpHarmonicNode.outputX, outputGeom)
	jpHarmonicNode.attributeAffects(jpHarmonicNode.outputY, outputGeom)
	jpHarmonicNode.attributeAffects(jpHarmonicNode.outputZ, outputGeom)


	#except:
	#	sys.stderr.write( "Failed to create attributes of %s node\n", kPluginNodeTypeName )


	
# initialize the script plug-in
def initializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.registerNode( kPluginNodeTypeName, jpHarmonicNodeId, nodeCreator, nodeInitializer, OpenMayaMPx.MPxNode.kDeformerNode )
	except:
		sys.stderr.write( "Failed to register node: %s\n" % kPluginNodeTypeName )
		raise

# uninitialize the script plug-in
def uninitializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.deregisterNode( jpHarmonicNodeId )
	except:
		sys.stderr.write( "Failed to unregister node: %s\n" % kPluginNodeTypeName )
		raise
		
		
		