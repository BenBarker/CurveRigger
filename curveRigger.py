'''Curve Rigging Tool. Drag this script to shelf, or execute from editor to run'''
import maya.cmds as cmds

class RigCurveTool(object):
    '''Creates a rig from the given curve.
    Rig is a NURBS strip that is skinned to the controls.
    The strip in turn has a series of locators attached to it using
    a setup meant to slide and stretch nicely.
    A chain of "skin joints" is created and attached to the locators.
    Use the skin joints to drive your mesh.
    
    The stretch attr is put on the first control, which is larger.
    Rigging the same curve twice may cause errors, since everything is named
    based on the curve name.
    '''
    def __init__(self):
        object.__init__(self)
        self.widgets = dict()
        self.showWindow()
        
    def showWindow(self):
        window = cmds.window(title='Rig Curve')
        cmds.columnLayout()
        
        #Curve Selector
        sel = cmds.ls(sl=True)
        initialText = 'Enter Curve Name'
        if sel:
            initialText = sel[0]
        self.widgets['curveNameGrp'] = cmds.textFieldButtonGrp( 
            label='Curve:', 
            text=initialText, 
            buttonLabel='<<<<',
            bc=self.curveNameButtonPush 
            )
        
        #Other Widgets
        cmds.text(label="Adjust Rig:")
        self.widgets['jointGrp']  = cmds.intSliderGrp(
            label='Joints', 
            field=True,
            fieldMinValue=2,
            minValue=2,
            maxValue=50,
            value=10
        )
        self.widgets['controlsGrp'] = cmds.intSliderGrp(
            label='Controls', 
            field=True,
            fieldMinValue=2,
            minValue=2,
            maxValue=10,
            value=4
        )
        self.widgets['sizeGrp'] = cmds.floatSliderGrp(
            label='Control Size',
            field=True,
            fieldMinValue=0.01,
            minValue=1.0,
            maxValue=10.0,
            value=2.0
        )
        cmds.text(label='')
        cmds.text(label="Adjust NURBS Strip:")
        self.widgets['spansGrp'] = cmds.intSliderGrp(
            label='Strip Spans', 
            field=True,
            fieldMinValue=2,
            minValue=2,
            maxValue=50,
            value=8
        )
        self.widgets['widthGrp'] = cmds.floatSliderGrp( 
            label='Strip Width', 
            field=True, 
            fieldMinValue=0.01,
            minValue=0.01, 
            maxValue=5.0,value=1.0 
        )
        cmds.text(label='')
        cmds.button(label="Rig Curve!",h=20,w=500,align='center',command=self.doIt)
        cmds.showWindow(window)
        
    def curveNameButtonPush(self,*args,**kwargs):
        '''pops the selection into the text field'''
        sel = cmds.ls(sl=True)
        if not sel:
            raise RuntimeError("select a curve")
        cmds.textFieldButtonGrp(self.widgets['curveNameGrp'],e=True,text=sel[0])
        
    def doIt(self,*args,**kwargs):
        '''reads widget values and calls rigFromCurve'''
        joints = cmds.intSliderGrp(self.widgets["jointGrp"],q=True,v=True)
        ctrls = cmds.intSliderGrp(self.widgets["controlsGrp"],q=True,v=True)
        size = cmds.floatSliderGrp(self.widgets["sizeGrp"],q=True,v=True)
        spans = cmds.intSliderGrp(self.widgets["spansGrp"],q=True,v=True)
        width = cmds.floatSliderGrp(self.widgets["widthGrp"],q=True,v=True)
        crv = cmds.textFieldButtonGrp(self.widgets["curveNameGrp"],q=True,text=True)
        
        if not crv or not cmds.objExists(crv):
            raise RuntimeError("%s not found in scene" % crv)

        shapes = cmds.listRelatives(crv,s=1)
        if not shapes or cmds.nodeType(shapes[0]) != 'nurbsCurve':
            raise RuntimeError("Selection is not a curve")
            
        self.rigFromCurve(crv,spans,joints,ctrls,width,size)

    def rigFromCurve(self,crv,numSpans=8,numJoints=10,numCtrls=5,stripWidth = 1.0,ctrlWidth=2.0):
        '''make a cable rig from the given curve
            numSpans = number of spans in Nurbs strip
            numJoints = number of joints riding on nurbs strip
            numCtrls = number of controls to make  
            stripWidth = width of nurbs strip (can make it easier to paint weights if wider) 
            ctrlWidth = size of ctrls 
        '''
    
        shapes = cmds.listRelatives(crv,s=1)
        crvShape = shapes[0]

        #Make rig top nulls to parent stuff under
        topNull = cmds.createNode('transform',n=crv + "_Rig")
        hiddenStuff = cmds.createNode('transform',n=crv + "_NOTOUCH",p=topNull)
        cmds.setAttr(hiddenStuff + ".inheritsTransform", 0)
        cmds.setAttr(hiddenStuff + ".visibility", 0)
        cmds.addAttr(topNull, ln="stretchAmount",dv=1.0,min=0,max=1)

        #make nurbs strip using extrude
        crossCurve = cmds.curve(d=1,p=[(0,0,-0.5 * stripWidth),(0,0,0.5 * stripWidth)],k=(0,1))
        cmds.select([crossCurve,crv],r=1)
        surf = cmds.extrude(ch=False,po=0,et=2,ucp=1,fpt=1,upn=1,rotation=0,scale=1,rsp=1)[0]
        cmds.delete(crossCurve)
        surf = cmds.rename(surf, crv + "_driverSurf")
        cmds.parent(surf,hiddenStuff)

        #Rebuild strip to proper number of spans
        cmds.rebuildSurface(surf,ch=0,rpo=1,rt=0,end=1,kr=0,kcp=0,kc=1,sv=numSpans,su=0,du=1,tol=0.01,fr=0,dir=2)

        #make live curve on surface down the middle 
        #this is used later for noStretch
        curvMaker = cmds.createNode('curveFromSurfaceIso', n = surf+"CurveIso")
        cmds.setAttr(curvMaker + ".isoparmValue", 0.5)
        cmds.setAttr(curvMaker + ".isoparmDirection", 1)
        cmds.connectAttr(surf + ".worldSpace[0]", curvMaker + ".inputSurface")

        offsetCrvShp = cmds.createNode("nurbsCurve", n=crv + "_driverSurfCrvShape")
        offsetCrv = cmds.listRelatives(p=1)[0]
        offsetCrv = cmds.rename(offsetCrv,crv + "_driverSurfCrv")
        cmds.connectAttr(curvMaker + ".outputCurve", offsetCrvShp + ".create")
        cmds.parent(offsetCrv, hiddenStuff)
    
        #Measure curve length and divide by start length. 
        #This turns curve length into a normalized value that is
        #useful for multiplying by UV values later to control stretch
        crvInfo = cmds.createNode('curveInfo', n=offsetCrv + "Info")
        cmds.connectAttr(offsetCrv + ".worldSpace[0]", crvInfo + ".ic")
        arcLength = cmds.getAttr(crvInfo + ".al")
        stretchAmountNode = cmds.createNode('multiplyDivide', n=offsetCrv + "Stretch")
        cmds.setAttr(stretchAmountNode + ".op" , 2) #divide
        cmds.setAttr(stretchAmountNode + ".input1X", arcLength)
        cmds.connectAttr( crvInfo + ".al",stretchAmountNode + ".input2X")
    
        #Stretch Blender blends start length with current length
        #and pipes it back into stretchAmoundNode's startLength, to "trick" it into
        #thinking there is no stretch..
        #That way, when user turns on this "noStretch" attr, the startLength will
        #be made to equal current length, and stretchAmountNode will always be 1.
        #so the chain will not stretch. 
        stretchBlender = cmds.createNode('blendColors', n =offsetCrv + "StretchBlender")
        cmds.setAttr(stretchBlender + ".c1r", arcLength)
        cmds.connectAttr(crvInfo + ".al", stretchBlender + ".c2r")
        cmds.connectAttr(stretchBlender + ".opr", stretchAmountNode + ".input1X")
        cmds.connectAttr(topNull + ".stretchAmount",stretchBlender + ".blender")
    
        #make skin joints and attach to surface
        skinJoints = []
        skinJointParent = cmds.createNode('transform',n=crv + "_skinJoints",p=topNull)
        for i in range(numJoints):
            cmds.select(clear=True)
            jnt = cmds.joint(p=(0,0,0),n=crv + "_driverJoint%02d"%i) 
            locator = cmds.spaceLocator(n=crv + "driverLoc%02d"%i)[0]
            cmds.parent(locator,hiddenStuff)
            percentage = float(i)/(numJoints-1.0)
            posNode,aimCns = self.attachObjToSurf(locator,surf,offsetCrv,stretchAmountNode,percentage)
            cmds.parentConstraint(locator,jnt,mo=False)
            if len(skinJoints):
                cmds.parent(jnt,skinJoints[-1])
            else:
                cmds.parent(jnt,skinJointParent)
            skinJoints.append(jnt)
            cmds.setAttr(jnt + ".radius",stripWidth) #just cosmetic
        
        #add controls
        ctrls = []
        stripJoints = []
        stripJointParent = cmds.createNode('transform',n=crv + "_stripJoints",p=hiddenStuff)
        ctrlParent = cmds.createNode('transform',n=crv+"_Ctrls",p=topNull)
    
        for i in range(numCtrls):
            #The first control is larger, and has the stretch attr
            if i == 0:
                zero,ctrl = self.makeCubeCtrl(crv + "_Ctrl%02d"%i,size=ctrlWidth*1.8)
                cmds.addAttr(ctrl,ln="noStretch",dv=0.0,min=0,max=1,k=1,s=1)
                cmds.connectAttr(ctrl + ".noStretch",topNull + ".stretchAmount")
            else:
                zero,ctrl = self.makeCubeCtrl(crv + "_Ctrl%02d"%i,size=ctrlWidth)
            
            #Make the joint the control. These drive the nurbs strip.
            cmds.select(clear=True)
            jnt = cmds.joint(p=(0,0,0),n=ctrl + "StripJnt")
            cmds.parentConstraint(ctrl,jnt,mo=False)
            cmds.setAttr(jnt + ".radius", stripWidth * 1.3) #just cosmetic
        
            #briefly attach ctrls to strip to align them
            percentage = float(i)/(numCtrls-1.0)
            cmds.delete(self.attachObjToSurf(zero,surf,offsetCrv,stretchAmountNode,percentage))
            ctrls.append(ctrl)
            cmds.parent(jnt,stripJointParent)
            stripJoints.append(jnt)
            cmds.parent(zero,ctrlParent)
        
        #skin strip to controls
        #Can get some different behavior by chaning the strip's weights
        #or perhaps using dual quat. mode on the skinCluster
        skinObjs = stripJoints + [surf]
        cmds.skinCluster(skinObjs,
            bindMethod=0, #closest Point
            sm=0, #standard bind method
            ih=True, #ignore hierarchy
        )    

    def attachObjToSurf(self,obj,surf,path,stretchAmountNode,percentage):
        '''Given an object and a surface, attach object.
        Returns created nodes like (poinOnSurface,aimCns)
        '''
        #Make nodes
        aimCns = cmds.createNode('aimConstraint',n=obj + "Cns")
        moPath = cmds.createNode('motionPath', n=obj + "MoPath")
        cmds.setAttr(moPath + ".uValue", percentage)
        closePnt = cmds.createNode('closestPointOnSurface', n=obj + "ClsPnt")
        posNode1 = cmds.pointOnSurface(surf,
            constructionHistory=True,
            normal=True,
            normalizedNormal=True, 
            normalizedTangentU=True, 
            normalizedTangentV=True, 
            parameterV=0.5, 
            parameterU=0.5, 
            turnOnPercentage=True
        ) 
    
        #Connect motion Path to closest point, then closest point to surface info node
        cmds.setAttr(moPath + ".fractionMode", 1) #distance instead of param
        cmds.connectAttr(path + ".worldSpace[0]", moPath + ".geometryPath")
        cmds.connectAttr(surf + ".worldSpace[0]", closePnt + ".inputSurface")
        cmds.connectAttr(moPath + ".xCoordinate", closePnt + ".ipx")
        cmds.connectAttr(moPath + ".yCoordinate", closePnt + ".ipy")
        cmds.connectAttr(moPath + ".zCoordinate", closePnt + ".ipz")
        cmds.connectAttr(closePnt + ".result.u", posNode1 + ".u")
        cmds.connectAttr(closePnt + ".result.v", posNode1 + ".v") 
    
        #Create Stretch Setup using stretchAmountNode node
        stretchCtrl = cmds.createNode("multDoubleLinear", n=obj + "StretchCtrl")
        cmds.setAttr(stretchCtrl + ".i1", percentage)
        cmds.connectAttr(stretchAmountNode + ".outputX",stretchCtrl + ".i2")
        cmds.connectAttr(stretchCtrl + ".o", moPath + ".uValue")
    
        #Hook up surface info attrs to aimCns to calculate rotation values
        #Then hook pointOnSurface and aimCns to locator
        posNode1 = cmds.rename(posNode1,obj + 'SurfInfo')
        cmds.setAttr(aimCns + ".worldUpType", 3)
        cmds.connectAttr(posNode1 + ".position", obj + ".translate")
        cmds.connectAttr(posNode1 + '.tv',aimCns + '.target[0].targetTranslate')
        cmds.connectAttr(posNode1 + '.tu',aimCns + '.worldUpVector')
        for axis in ('X','Y','Z'):
            cmds.connectAttr(aimCns + ".constraintRotate" + axis, obj + ".rotate" + axis)
        cmds.parent(aimCns,obj) #just for tidyness, doesn't matter
        return (posNode1,aimCns)

    def makeCubeCtrl(self,name,size=1.0):
        '''
        Make a nurbs curve cube with given name. Also can take size.
        Returns the cube parented under a zero null
        '''
        wd = 0.5*size
        crn = [
            (-wd,wd,-wd),
            (wd,wd,-wd),
            (wd,-wd,-wd),
            (-wd,-wd,-wd),
            (-wd,wd,wd),
            (wd,wd,wd),
            (wd,-wd,wd),
            (-wd,-wd,wd),
            ]
        verts = (crn[0],crn[1],crn[2],crn[3],crn[0],crn[4],crn[5],crn[6],
            crn[7],crn[4],crn[5],crn[1],crn[0],crn[4],crn[7],crn[3],crn[0],
            crn[1],crn[2],crn[6])
        crv = cmds.curve(d=1,
            p=verts,
            k=range(len(verts))
            )
        crv = cmds.rename(crv,name)
        zero = cmds.createNode('transform',n=crv + "_Zero")
        self.hideChannels(zero)
        for attr in ('sx','sy','sz'):
            cmds.setAttr(crv + "." + attr,l=True,k=False,cb=False)
        cmds.parent(crv,zero)
        return (zero,crv)

    def hideChannels(self,obj,lock=False):
        '''hide anim channels on given obj'''
        for attr in ('s','r','t'):
            for axis in ('x','y','z'):
                cmds.setAttr(obj + ".%s%s"%(attr,axis), keyable=False,channelBox=False,lock=lock)
        cmds.setAttr(obj + ".v", keyable=False,channelBox=False)

 
#Run the tool   
RigCurveTool()
