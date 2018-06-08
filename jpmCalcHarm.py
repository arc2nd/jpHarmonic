import maya.cmds as cmds

def calcHarm( driver, harmNode, start=0.0, end=0.0 ):
	startFrame = cmds.playbackOptions( q=1, min=1 )
	endFrame = cmds.playbackOptions( q=1, max=1 )
	
	if not start:
		start = startFrame
	if not end:
		end = endFrame
	
	#make sure the time node is connected to the harmNode
	try:
		cmds.connectAttr("time1.outTime", harmNode + ".currentFrame")
	except:
		print "I think the time is already connected"
	
	##make a locator in world space
	thisLoc = cmds.spaceLocator( name=( driver + "_" + harmNode + "_loc"))[0]
	
	##pointConstrain it to our driver object
	thisPoint = cmds.parentConstraint( driver, thisLoc, mo=0 )
	
	##bake locator transforms
	cmds.bakeResults( (thisLoc + ".translate"), sb=1, t=(start,end), pok=1, sac=0 )
	
	##clear out any existing curves on harmNode's storage translates
	cmds.cutKey( harmNode, cl=1, t=(start,end), at="storageTransX" )
	cmds.cutKey( harmNode, cl=1, t=(start,end), at="storageTransY" )
	cmds.cutKey( harmNode, cl=1, t=(start,end), at="storageTransZ" )
	
	##copy baked locator curves to harmNode's storage translates
	cmds.copyKey( thisLoc, time=(start,end), attribute='translateX', option="curve" )
	cmds.pasteKey( harmNode, attribute='storageTransX' )
	cmds.copyKey( thisLoc, time=(start,end), attribute='translateY', option="curve" )
	cmds.pasteKey( harmNode, attribute='storageTransY' )
	cmds.copyKey( thisLoc, time=(start,end), attribute='translateZ', option="curve" )
	cmds.pasteKey( harmNode, attribute='storageTransZ' )

	##delete locator and pointConstraint
	cmds.delete( thisPoint )
	cmds.delete( thisLoc )