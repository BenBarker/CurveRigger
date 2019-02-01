
'''Cable Rigging Tool. Drag this script to shelf, or execute from editor to run'''
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
        self.defaults = dict()
        #default UI Values
        self.defaults['joints'] = 10
        self.defaults['ctrls'] = 4
        self.defaults['size']=0.1
        self.defaults['spans']=10
        self.defaults['width']=0.1
        self.defaults['uMin']=0.0
        self.defaults['uMax']=1.0
        self.showWindow()
        
    def showWindow(self):
        window = cmds.window(title='Rig Curve')
        cmds.columnLayout()

        #Read stored options
        if cmds.optionVar(exists='CableRigger_joints'):
            defaultJoints = cmds.optionVar(q='CableRigger_joints')
        else:
            defaultJoints = self.defaults['joints']
        if cmds.optionVar(exists='CableRigger_ctrls'):
            defaultCtrls = cmds.optionVar(q='CableRigger_ctrls')
        else:
            defaultCtrls = self.defaults['ctrls']       
        if cmds.optionVar(exists='CableRigger_size'):
            defaultSize = cmds.optionVar(q='CableRigger_size')
        else:
            defaultSize = self.defaults['size']      
        if cmds.optionVar(exists='CableRigger_spans'):
            defaultSpans = cmds.optionVar(q='CableRigger_spans')
        else:
            defaultSpans = self.defaults['spans']        
        if cmds.optionVar(exists='CableRigger_width'):
            defaultWidth = cmds.optionVar(q='CableRigger_width')
        else:
            defaultWidth = self.defaults['width']    
        if cmds.optionVar(exists='CableRigger_uMin'):
            defaultuMin = cmds.optionVar(q='CableRigger_uMin')
        else:
            defaultuMin = self.defaults['uMin']   
        if cmds.optionVar(exists='CableRigger_uMax'):
            defaultuMax = cmds.optionVar(q='CableRigger_uMax')
        else:
            defaultuMax = self.defaults['uMax']  
        
        #Curve Selector
        sel = cmds.ls(sl=True)
        initialText = ''
        if sel:
            initialText = sel[0]
        self.widgets['curveNameGrp'] = cmds.textFieldButtonGrp( 
            label='Curve:', 
            text=initialText, 
            buttonLabel='<<<<',
            bc=self.curveNameButtonPush 
            )
            
                 
        #Geo
        sel = cmds.ls(sl=True)
        initialText = ''
        self.widgets['geoNameGrp'] = cmds.textFieldButtonGrp( 
            label='Geo:', 
            text=initialText, 
            buttonLabel='<<<<',
            bc=self.geoNameButtonPush 
            )

        
        #Other Widgets\
        cmds.button(label='Reset below to default',width=500,command=self.setDefaults)
        cmds.text(label="Adjust Rig:")
        self.widgets['jointGrp']  = cmds.intSliderGrp(
            label='Joints', 
            field=True,
            fieldMinValue=2,
            minValue=2,
            maxValue=150,
            value=defaultJoints
        )
        self.widgets['controlsGrp'] = cmds.intSliderGrp(
            label='Controls', 
            field=True,
            fieldMinValue=2,
            minValue=2,
            maxValue=50,
            value=defaultCtrls
        )
        self.widgets['sizeGrp'] = cmds.floatSliderGrp(
            label='Control Size',
            field=True,
            fieldMinValue=0.01,
            minValue=.1,
            maxValue=10.0,
            value=defaultSize
        )        
        self.widgets['uMinGrp'] = cmds.floatSliderGrp(
            label='U min',
            field=True,
            fieldMinValue=0.0,
            minValue=0,
            maxValue=1.0,
            fieldMaxValue=1.0,
            value=defaultuMin
        ) 
        self.widgets['uMaxGrp'] = cmds.floatSliderGrp(
            label='U max',
            field=True,
            fieldMinValue=0,
            minValue=0,
            maxValue=1,
            fieldMaxValue=1,
            value=defaultuMax
        )
        cmds.text(label='')
        cmds.text(label="Adjust NURBS Strip:")
        self.widgets['spansGrp'] = cmds.intSliderGrp(
            label='Strip Spans', 
            field=True,
            fieldMinValue=2,
            minValue=2,
            maxValue=150,
            value=defaultSpans
        )
        self.widgets['widthGrp'] = cmds.floatSliderGrp( 
            label='Strip Width', 
            field=True, 
            fieldMinValue=0.005,
            minValue=0.01, 
            maxValue=5.0,
            value=defaultWidth
        )
        cmds.text(label='')
        cmds.button(label="\nRig Curve!",h=60,w=500,command=self.doIt)
        cmds.button(label="Wire Geo Only (Rig already built)",h=30,w=500,command=self.wireOnly)
        cmds.showWindow(window)
        
    def curveNameButtonPush(self,*args,**kwargs):
        '''pops the selection into the text field'''
        sel = cmds.ls(sl=True)
        if not sel:
            raise RuntimeError("select a curve")
        cmds.textFieldButtonGrp(self.widgets['curveNameGrp'],e=True,text=sel[0])
        
    def geoNameButtonPush(self,*args,**kwargs):
        '''pops the selection into the text field'''
        sel = cmds.ls(sl=True)
        if not sel:
            raise RuntimeError("select the cable geo")
        cmds.textFieldButtonGrp(self.widgets['geoNameGrp'],e=True,text=sel[0])
        
    def setDefaults(self,*args,**kwargs):
        '''sets the sliders to defaults'''
        cmds.intSliderGrp(self.widgets['jointGrp'],e=True,v=self.defaults['joints'])
        cmds.intSliderGrp( self.widgets['controlsGrp'], e=True,v=self.defaults['ctrls'])
        cmds.floatSliderGrp(self.widgets['sizeGrp'], e=True,v=self.defaults['size'])
        cmds.intSliderGrp(self.widgets['spansGrp'], e=True,v=self.defaults['spans'])
        cmds.floatSliderGrp(self.widgets['widthGrp'] , e=True,v=self.defaults['width'])
        cmds.floatSliderGrp(self.widgets['uMinGrp'] , e=True,v=self.defaults['uMin'])
        cmds.floatSliderGrp(self.widgets['uMaxGrp'] , e=True,v=self.defaults['uMax'])

    def wireOnly(self,*args,**kwargs):
        '''if the rig already exists, just wire geo'''
        crv = cmds.textFieldButtonGrp(self.widgets["curveNameGrp"],q=True,text=True)
        geo = cmds.textFieldButtonGrp(self.widgets["geoNameGrp"],q=True,text=True)

        if not crv or not geo or not cmds.objExists(geo):
            raise RuntimeError("Specify a curve and a geo to wire to an already existing rig")

        #Find nodes based on name, do some error checking
        rigNode = crv + "_Rig"
        hiddenStuff = crv + "_NOTOUCH"
        wireCrv = crv + "_skinned"
        if not cmds.objExists(rigNode):
            raise RuntimeError("%s not found in scene, rig not built yet?"%rigNode)
        allKids = cmds.listRelatives(rigNode,ad=True)
        if not cmds.objExists(wireCrv) and not wireCrv in allKids:
            raise RuntimeError("wire curve %s not found under %s, wire curve deleted or not rigged?" %(wireCrv,rigNode))
        if not cmds.objExists(hiddenStuff) and not hiddenStuff in allKids:
            raise RuntimeError("Couldn't find the NOTOUCH node for this rig, curve not rigged?")

        #Make wire
        cmds.wire(geo,w=wireCrv,n=crv + "_wire",dds=(0,10),en=1.0,ce=0,li=0)
        print "wire done"


    def doIt(self,*args,**kwargs):
        '''reads widget values and calls rigFromCurve'''
        joints = cmds.intSliderGrp(self.widgets["jointGrp"],q=True,v=True)
        ctrls = cmds.intSliderGrp(self.widgets["controlsGrp"],q=True,v=True)
        size = cmds.floatSliderGrp(self.widgets["sizeGrp"],q=True,v=True)
        spans = cmds.intSliderGrp(self.widgets["spansGrp"],q=True,v=True)
        width = cmds.floatSliderGrp(self.widgets["widthGrp"],q=True,v=True)
        crv = cmds.textFieldButtonGrp(self.widgets["curveNameGrp"],q=True,text=True)
        geo = cmds.textFieldButtonGrp(self.widgets["geoNameGrp"],q=True,text=True)
        uMin = cmds.floatSliderGrp(self.widgets["uMinGrp"],q=True,v=True)
        uMax = cmds.floatSliderGrp(self.widgets["uMaxGrp"],q=True,v=True)

        
        #save options
        cmds.optionVar( iv=('CableRigger_joints', joints))
        cmds.optionVar( iv=('CableRigger_ctrls', ctrls))
        cmds.optionVar( fv=('CableRigger_size', size))
        cmds.optionVar( iv=('CableRigger_spans', spans))
        cmds.optionVar( fv=('CableRigger_width', width))
        cmds.optionVar( fv=('CableRigger_uMin', uMin))
        cmds.optionVar( fv=('CableRigger_uMax', uMax))

        
        if not crv or not cmds.objExists(crv):
            raise RuntimeError("%s not found in scene" % crv)

        shapes = cmds.listRelatives(crv,s=1)
        if not shapes or cmds.nodeType(shapes[0]) != 'nurbsCurve':
            raise RuntimeError("Selection is not a curve")
            
        self.rigFromCurve(crv,numSpans=spans,
            numJoints=joints,
            numCtrls=ctrls,
            stripWidth=width,
            ctrlWidth=size,
            geo=geo,
            uMin=uMin,
            uMax=uMax
        )
        print "cable rig complete"

    def rigFromCurve(self,crv,numSpans=8,numJoints=10,numCtrls=5,stripWidth = 1.0,ctrlWidth=2.0,geo=None,uMin=0.0,uMax=1.0):
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
        cmds.addAttr(topNull, ln='slideAmount',dv=0.0)

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
            cmds.setAttr(locator + ".localScale",stripWidth,stripWidth,stripWidth)
            cmds.parent(locator,hiddenStuff)
            percentage = float(i)/(numJoints-1.0)
            print "percentage:", percentage
            print i
            if i > 1 and i < numJoints-2:
                percentage = uMin + (percentage * (uMax-uMin))
                print "\tinterp percent", percentage
            posNode,aimCnss,moPath,slider = self.attachObjToSurf(locator,surf,offsetCrv,stretchAmountNode,percentage)
            cmds.connectAttr(topNull + ".slideAmount", slider + ".i2")
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
                cmds.addAttr(ctrl,ln='slideAmount',dv=0.0,min=-1.0,max=1.0,k=1,s=1)
                cmds.connectAttr(ctrl + ".noStretch",topNull + ".stretchAmount")
                cmds.connectAttr(ctrl + ".slideAmount",topNull + ".slideAmount")
            else:
                zero,ctrl = self.makeCubeCtrl(crv + "_Ctrl%02d"%i,size=ctrlWidth)
            
            #Make the joint the control. These drive the nurbs strip.
            cmds.select(clear=True)
            jnt = cmds.joint(p=(0,0,0),n=ctrl + "StripJnt")
            cmds.parentConstraint(ctrl,jnt,mo=False)
            cmds.setAttr(jnt + ".radius", stripWidth * 1.3) #just cosmetic
        
            #briefly attach ctrls to strip to align them
            percentage = float(i)/(numCtrls-1.0)
            print "ctrl percentage:",percentage
            if i > 0 and i < numCtrls-1:
                percentage = uMin + (percentage * (uMax-uMin))
                print '\tinterp percentage:', percentage
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
        
        #rebuild curve and skin to joints
        newCurve = cmds.duplicate(crv)[0]
        newCurve = cmds.rename(newCurve, crv + "_skinned")
        cmds.parent(newCurve, topNull)
        cmds.rebuildCurve(newCurve,ch=0,rpo=1,rt=0,end=1,kr=0,kcp=0,kep=1,kt=0,s=numJoints-2,d=3,tol=0.01)
        skinObjs = skinJoints + [newCurve]
        cmds.skinCluster(skinObjs,
            bindMethod = 0,
            sm = 0,
            ih=True,
            mi=1
            )
        if geo:
            wireDef,wireCrv = cmds.wire(geo,w=newCurve,n=crv + "_wire",dds=(0,10),en=1.0,ce=0,li=0)
            print wireDef
            cmds.parent(wireCrv,hiddenStuff)
            if cmds.objExists(wireCrv+"BaseWire"):
                cmds.parent(wireCrv+"BaseWire",hiddenStuff)

    def attachObjToSurf(self,obj,surf,path,stretchAmountNode,percentage):
        '''Given an object and a surface, attach object.
        Returns created nodes like (poinOnSurface,aimCns)
        '''
        #Make nodes
        aimCns = cmds.createNode('aimConstraint',n=obj + "Cns")
        moPath = cmds.createNode('motionPath', n=obj + "MoPath")
        slider = cmds.createNode('addDoubleLinear',n=obj + "Slider")
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
        cmds.connectAttr(stretchCtrl + ".o", slider + ".i1")
        cmds.connectAttr(slider + ".o", moPath + ".uValue")
        
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
        return (posNode1,aimCns,moPath,slider)

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
