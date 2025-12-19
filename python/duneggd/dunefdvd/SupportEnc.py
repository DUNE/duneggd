import gegede.builder
from gegede import Quantity as Q
from utils import *

class SupportEncBuilder(gegede.builder.Builder):
    def configure(self, **kwds):
        if not set(kwds).issubset(globals.Cryostat): # no unknown keywords
            msg = 'Unknown parameter in: "%s"' % (', '.join(sorted(kwds.keys())), )
            raise ValueError(msg)

        # The builder hierarchy takes care of all the configuration parameters
        globals.Cryostat = kwds
        # fetch other various relevant dimensions here
        self.fSpacing = globals.get("Spacing")
        self.fIFlangeWidth = globals.get("IFlangeWidth")
        self.fIFlangeThick = globals.get("IFlangeThick")
        self.fIFlangeWaist = globals.get("IFlangeWaist")
        self.fIFlangeHeight = globals.get("IFlangeHeight")
        self.fBeamDepth = globals.get("BeamDepth")
        self.fITopLength = globals.get("ITopLength")
        self.fISideLength = globals.get("ISideLength")
        self.fIPortSpacing = globals.get("IPortSpacing")
        self.fISidePortLoc = globals.get("ISidePortLoc")
        self.fIBotPortLoc = globals.get("IBotPortLoc")
        self.fIPortHoleRad = globals.get("IPortHoleRad")

        self.fzpl = Q('65.84m') - self.fBeamDepth
        self.fst = 0.5*(Q('18.94m') - self.fBeamDepth) # y : set to be vertical (cryostat width in reality)
        self.fht = 0.5*(Q('17.84m') - self.fBeamDepth) # x : set to be lateral (cryostat height in reality)

        self.fShieldWallThickness = globals.get("ShieldWallThickness")
        self.fShieldWallHeight = globals.get("ShieldWallHeight")
        self.fShieldWallWidth = globals.get("ShieldWallWidth")
        self.fBeltBuffer = globals.get("BeltBuffer")

    def construct(self, geom):
        globals.SetDerived()

        supportencBox = geom.shapes.Box(self.name,
                                     dx=0.5*(globals.get("FullCryostat_x")),  # have shield blocks of 23cm thickness (from Juergen)
                                     dy=0.5*(globals.get("FullCryostat_y")),  # have shield blocks of 23cm thickness (from Juergen)
                                     dz=0.5*(globals.get("FullCryostat_z")))
        supportencLV = geom.structure.Volume('vol'+self.name, material="Air", shape=supportencBox)
        self.add_volume(supportencLV)
        supportencLV = self.construct_place_IBeams(geom, supportencLV)
        supportencLV = self.construct_place_Belts(geom, supportencLV)
        supportencLV = self.construct_place_ShieldingFloors(geom, supportencLV)
        supportencLV = self.construct_place_ShieldingWalls(geom, supportencLV)

        cryostat = self.get_builder("CryostatEnc")
        cryostatLV = cryostat.get_volume()
        cryostat_place = geom.structure.Placement('place'+cryostat.name,
                                                  volume = cryostatLV,
                                                  pos = "posCenter")
        supportencLV.placements.append(cryostat_place.name)
        return

    #-------------------------------------------------
    def construct_place_ShieldingFloors(self, geom, supportencLV):
        BlockThickness = Q('0.30m')
        BlockThicknessPb = Q('2.5cm')
        clearance = Q('2mm')
        BlockWidth = self.fSpacing-self.fIFlangeWaist-clearance
        box_shape = geom.shapes.Box('box_name', dy=(BlockWidth)/2, dx=(BlockThickness/2.0), dz=(BlockWidth/2))
        boxshapevolume = geom.structure.Volume('boxshapeVol', material='BP', shape=box_shape)
        box_shape_pb = geom.shapes.Box('box_namePb', dy=(BlockWidth)/2, dx=(BlockThicknessPb/2.0), dz=(BlockWidth/2))
        boxshapevolumePb = geom.structure.Volume('boxshapeLeadVol', material='lead', shape=box_shape_pb)

        # start the loop
        zbsp = self.fSpacing
        yPbBlock = -self.fht - 0.5*self.fIFlangeHeight + 0.5*BlockThicknessPb
        yBlock  = yPbBlock + BlockThicknessPb + 0.5*BlockThickness
        for ii in range(-1, 41):
                zpos_i = (ii-1-19)*zbsp + zbsp/2
                for jj in range(-1, 11):
                        xpos_i = (jj-1-4)*zbsp + zbsp/2
                        box_name = f'ShieldingFloor_{jj}_{ii}'

                        placement = geom.structure.Placement(
                                        f'ShieldingFloor_{jj}_{ii}',
                                        volume = boxshapevolume,
                                        pos = geom.structure.Position(f'ShieldingFloor_{jj}_{ii}_position', x=yBlock, y=xpos_i, z=zpos_i))
                        supportencLV.placements.append(placement.name)

                        placement2 = geom.structure.Placement(
                                        f'ShieldingFloorPb_{jj}_{ii}',
                                        volume = boxshapevolumePb,
                                        pos = geom.structure.Position(f'ShieldingFloorPb_{jj}_{ii}_position', x=yPbBlock, y=xpos_i, z=zpos_i))
                        supportencLV.placements.append(placement2.name)
        return supportencLV

    #-------------------------------------------------
    def construct_place_ShieldingWalls(self, geom, supportencLV):
        BlockThickness = self.fShieldWallThickness
        BlockHeight = self.fShieldWallHeight
        BlockWidth = self.fShieldWallWidth
        ContainerThickness = Q('2mm')
        WaterThickness = BlockThickness - 2*ContainerThickness
        WaterHeight = BlockHeight - 2*ContainerThickness
        WaterWidth = BlockWidth - 2*ContainerThickness
        nBlocksLongSide = 64
        nBlocksShortSide = 19
        nBlocksStack = 9

        ShieldBlockContainer = geom.shapes.Box('ShieldBlockContainer',
					dy = (BlockThickness/2),
					dx = (BlockHeight/2),
					dz = (BlockWidth /2))
        ShieldBlockWater = geom.shapes.Box('ShieldBlockWater',
					dy = (WaterThickness/2),
					dx = (WaterHeight/2),
					dz = (WaterWidth /2))
        ShieldBlockContainerLog = geom.structure.Volume('ShieldBlockContainerLog', material='BP', shape=ShieldBlockContainer)
        ShieldBlockWaterLog = geom.structure.Volume('ShieldBlockWaterLog', material='Water', shape=ShieldBlockWater)
        waterPos = geom.structure.Placement('WaterInContainer', volume=ShieldBlockWaterLog)
        ShieldBlockContainerLog.placements.append(waterPos.name)

        origin_z = -nBlocksLongSide * BlockWidth/2 + BlockWidth/2
        origin_y = -self.fht - 0.5*self.fBeamDepth + BlockHeight/2
        xLatWall = self.fITopLength/2 + BlockThickness/2

        # start the loop (lateral walls)
        for ii in range(nBlocksLongSide+2):
            zpos = origin_z + (ii - 1) * BlockWidth
            for jj in range(nBlocksStack-1):
                ypos = origin_y + (jj) * BlockHeight
                shieldPosPlus = geom.structure.Position(f'ShieldLatContainerPlusXPos_{ii}_{jj}', ypos, xLatWall, zpos)
                shieldPosMinus = geom.structure.Position(f'ShieldLatContainerMinusXPos_{ii}_{jj}', ypos, -xLatWall, zpos)
                shieldRight = geom.structure.Placement(f'ShieldLatContainerPlusXPlace_{ii}_{jj}',
                                                      volume = ShieldBlockContainerLog,
                                                      pos=shieldPosPlus)
                supportencLV.placements.append(shieldRight.name)
                shieldLeft = geom.structure.Placement(f'ShieldLatContainerMinusXPlace_{ii}_{jj}',
                                                      volume = ShieldBlockContainerLog,
                                                      pos=shieldPosMinus)
                supportencLV.placements.append(shieldLeft.name)

        # start the loop (front and back)
        origin_x = -self.fst - 0.5*self.fBeamDepth + 0.5*BlockWidth
        zFrontWall = 0.5*(self.fzpl + self.fBeamDepth + BlockThickness) + self.fBeltBuffer
        fc2Rotation = geom.structure.Rotation('fc2Rotation',x= "90deg", y= "0deg",z= "0deg")
        for ii in range(2*nBlocksStack):
            ypos = origin_y + (ii) * BlockHeight
            for jj in range(nBlocksShortSide):
                xpos = origin_x + (jj)*BlockWidth
                shieldPosFront = geom.structure.Position(f'ShieldLatContainerFrontZPos_{ii}_{jj}', ypos, xpos, zFrontWall)
                shieldPosBack = geom.structure.Position(f'ShieldLatContainerBackZPos_{ii}_{jj}', ypos, xpos, -zFrontWall)
                shieldFront = geom.structure.Placement(f'ShieldLatContainerFrontZPlace_{ii}_{jj}',
                                                      volume = ShieldBlockContainerLog,
                                                      pos=shieldPosFront, rot=fc2Rotation)
                supportencLV.placements.append(shieldFront.name)
                shieldBack = geom.structure.Placement(f'ShieldLatContainerBackZPlace_{ii}_{jj}',
                                                      volume = ShieldBlockContainerLog,
                                                      pos=shieldPosBack, rot=fc2Rotation)
                supportencLV.placements.append(shieldBack.name)

        return supportencLV

    #-------------------------------------------------
    def construct_place_Belts(self, geom, supportencLV):
        ht = self.fht
        st = self.fst
        half_spacingZ = ((self.fSpacing/2) - (self.fIFlangeWaist/2))

        BeltFlange = geom.shapes.Box('BeltFlange',
					dy = (self.fIFlangeWidth/2),
					dx = (self.fIFlangeWaist/2),
					dz = half_spacingZ - (self.fIFlangeWidth/2))
        BeltFlangeTop = geom.shapes.Box('BeltFlangeTop',
                        dy = (self.fIFlangeWidth/3),
                        dx = (self.fIFlangeWaist/2),
                        dz = half_spacingZ)

        BeltMid = geom.shapes.Box('BeltMid',
					dy = (self.fIFlangeWaist/2),
					dx = (self.fIFlangeHeight/2),
					dz = half_spacingZ)
        BeltMidTop = geom.shapes.Box('BeltMidTop',
					dy = (self.fIFlangeWaist/2),
					dx = (self.fIFlangeHeight/3),
					dz = half_spacingZ)

        IBeamPort = geom.shapes.Tubs('BeltPortHole',
					rmin = Q('0cm'),
					rmax = self.fIPortHoleRad,
					dz = (self.fIFlangeThick /2),
					sphi = Q('0deg'),
					dphi = Q('360deg'))

        fcRotation = geom.structure.Rotation('fcBelt', x= "0deg", y= "0deg",z= "90deg")
        fc2Rotation = geom.structure.Rotation('fc2Belt',x= "0deg", y= "90deg",z= "90deg")
        fc3Rotation = geom.structure.Rotation('fc3Belt', x= "90deg", y= "0deg",z= "90deg")

        BeltHole = geom.shapes.Boolean('BeltHole', type = 'subtraction',
						first = BeltMid,
						second = IBeamPort,
						pos = geom.structure.Position('BeltHoleSub', x="0cm", y="0cm", z="0cm"),
						rot = fc2Rotation)

        tr1 = geom.structure.Position('tr1', y= Q('0cm'), x=(self.fIFlangeHeight/2 + self.fIFlangeThick/2), z= Q('0cm'))
        tr2 = geom.structure.Position('tr2', y= Q('0cm'), x=(-self.fIFlangeHeight/2 - self.fIFlangeThick/2), z= Q('0cm'))
        tr1Top = geom.structure.Position('tr1Top', y= Q('0cm'), x=(self.fIFlangeHeight/3 + self.fIFlangeThick/2), z= Q('0cm'))
        tr2Top = geom.structure.Position('tr2Top', y= Q('0cm'), x=(-self.fIFlangeHeight/3 - self.fIFlangeThick/2), z= Q('0cm'))

        Union1 = geom.shapes.Boolean('Union1', type = 'union',
						first = BeltHole,
						second = BeltFlange,
						pos = tr1)
        BeltHoleUni = geom.shapes.Boolean('BeltHoleUnion', type = 'union',
						first = Union1,
						second = BeltFlange,
						pos = tr2)
        BeltHoleUniLog = geom.structure.Volume('BeltHoleUni', material='fDuneSteel', shape=BeltHoleUni)


        Union2 = geom.shapes.Boolean('Union2', type = 'union',
						first = BeltMid,
						second = BeltFlange,
						pos = tr1)
        BeltUni = geom.shapes.Boolean('BeltUnion', type = 'union',
						first = Union2,
						second = BeltFlange,
						pos = tr2)
        BeltUniLog = geom.structure.Volume('BeltUni', material='fDuneSteel', shape=BeltUni)

        Union3 = geom.shapes.Boolean('Union3', type = 'union',
						first = BeltMidTop,
						second = BeltFlangeTop,
						pos = tr1Top)
        BeltUniTop = geom.shapes.Boolean('BeltUnionTop', type = 'union',
						first = Union3,
						second = BeltFlangeTop,
						pos = tr2Top)
        BeltUniTopLog = geom.structure.Volume('BeltUniTop', material='fDuneSteel', shape=BeltUniTop)

        # start the loop
        zbsp = self.fSpacing
        for ii in range(-1, 39):
            zpos_i = (-19*zbsp) + ii*zbsp + zbsp/2
            for jj in range(-4,5):
                BeltBot = geom.structure.Placement(f'BeltBottom_{jj}_{ii}',

                                                                pos = geom.structure.Position(f'BeltBottomPlacement_{jj}_{ii}',
                                                                y = ((jj) * zbsp),
                                                                x =  (-ht),
                                                                z = (zpos_i)),
                                                            	volume = BeltHoleUniLog)
                BeltTop = geom.structure.Placement(f'BeltTop_{jj}_{ii}',

                                                            pos = geom.structure.Position(f'BeltTopPlacement_{jj}_{ii}',
                                                            y = ((jj) * zbsp),
                                                            x =  (ht),
                                                            z = (zpos_i)),
                                                            volume = BeltUniTopLog)
                supportencLV.placements.append(BeltBot.name)
                supportencLV.placements.append(BeltTop.name)

            for kk in range(4):
                yvar = ht - ((kk-0.5)*self.fIPortSpacing) - 2*self.fIPortHoleRad
                belt = BeltUniLog
                if kk == 0:
                    yvar =  ht - (kk*self.fIPortSpacing)
                if (ii+kk+2 % 3 == 0) or (kk == 3):
                    belt = BeltHoleUniLog

                BeltLeft = geom.structure.Placement(f'BeltLeft_{kk}_{ii}',

                                                                pos = geom.structure.Position(f'BeltLeftPlacement_{kk}_{ii}',
                                                                y = -st,
                                                                x = yvar ,
                                                                z = (zpos_i)),
                                                            	volume = belt,
                                                                rot= fcRotation)
                BeltRight = geom.structure.Placement(f'BeltRight_{kk}_{ii}',

                                                                pos = geom.structure.Position(f'BeltRightPlacement_{kk}_{ii}',
                                                                y = st,
                                                                x = yvar ,
                                                                z = zpos_i),
                                                            	volume = belt,
                                                                rot= fcRotation)
                supportencLV.placements.append(BeltLeft.name)
                supportencLV.placements.append(BeltRight.name)

        xpl = zbsp/2
        zpl = self.fzpl/2 + self.fBeltBuffer
        for ii in range(10):
            xpos_i = (ii-4)*zbsp - xpl
            for jj in range (4):
                yvar = ht - ((jj-0.5)*self.fIPortSpacing) - 2*self.fIPortHoleRad
                belt = BeltUniLog
                if jj == 0:
                    yvar =  ht - (jj*self.fIPortSpacing)
                if (ii+jj+2 % 3 == 0) or (jj == 0):
                    belt = BeltHoleUniLog

                BeltBack = geom.structure.Placement(f'BeltBack_{jj}_{ii}',
                                                                pos = geom.structure.Position(f'BeltBackPlacement_{jj}_{ii}',
                                                                y = xpos_i,
                                                                x = yvar,
                                                                z = -zpl),
                                                            	volume = belt,
                                                                rot= fc3Rotation)
                BeltFront = geom.structure.Placement(f'BeltFront_{jj}_{ii}',

                                                                pos = geom.structure.Position(f'BeltFrontPlacement_{jj}_{ii}',
                                                                y = xpos_i,
                                                                x = yvar ,
                                                                z = zpl),
                                                            	volume = belt,
                                                                rot= fc3Rotation)
                supportencLV.placements.append(BeltBack.name)
                supportencLV.placements.append(BeltFront.name)

        return supportencLV

    #-------------------------------------------------
    def construct_place_IBeams(self, geom, supportencLV):
        IBeamTopFlange = geom.shapes.Box('IBeamTopFlange',
					dy = (self.fIFlangeWidth/2),
					dx = (self.fIFlangeThick/2),
					dz = (self.fITopLength/2))  #creating a IBeamTopFlange object
        IBeamTopMid = geom.shapes.Box('IBeamTopMid',
					dy = (self.fIFlangeWaist/2),
					dx = (self.fIFlangeHeight/2),
					dz = (self.fITopLength/2))  #creating a IBeamTopMid object
        IBeamSideFlange = geom.shapes.Box('IBeamSideFlange',
					dy = (self.fIFlangeWidth/2),
					dx = (self.fIFlangeThick/2),
					dz = (self.fISideLength/2))  #creating a IBeamSideFlange object
        IBeamSideMidtmp0 = geom.shapes.Box('IBeamSideMid',
					dy = (self.fIFlangeWaist/2),
					dx = (self.fIFlangeHeight/2),
					dz = (self.fISideLength/2))  #creating a IBeamSideMid object
        IBeamPort = geom.shapes.Tubs('IBeamPortTub',
					rmin = Q('0cm'),
					rmax = self.fIPortHoleRad,
					dz = (self.fIFlangeThick/2),
					sphi = Q('0deg'),
					dphi = Q('360deg'))

        fcRotation = geom.structure.Rotation('fc', x= "90deg", y= "0deg",z= "0deg")
        fc2Rotation = geom.structure.Rotation('fc2',x= "0deg", y= "90deg",z= "90deg")
        fc3Rotation = geom.structure.Rotation('fc3', x= "0deg", y= "90deg",z= "0deg")

        IBeamBotMidtmp = geom.shapes.Boolean('IBeamBottomtmp', type = 'subtraction',
						first = IBeamTopMid,
						second = IBeamPort,
						pos = geom.structure.Position('PosOfIBeam', x="0cm", y="0cm", z=self.fIPortSpacing/2),
						rot = fcRotation)
        IBeamBotMid = geom.shapes.Boolean('IBeamBottom', type = 'subtraction',
						first = IBeamBotMidtmp,
						second = IBeamPort,
						pos = geom.structure.Position('PosOfIBeam2', x="0cm", y="0cm", z=-self.fIPortSpacing/2),
						rot = fcRotation)
        IBeamSideMidtmp1 = geom.shapes.Boolean('IBeamSidetmp', type = 'subtraction',
						first = IBeamSideMidtmp0,
						second = IBeamPort,
						pos = geom.structure.Position('PosOfIBeam3', x="0cm", y="0cm", z=((self.fISideLength/2) - self.fISidePortLoc)),
						rot =fcRotation)
        IBeamSideMidtmp2 = geom.shapes.Boolean('IBeamSidetmp2', type = 'subtraction',
						first = IBeamSideMidtmp1,
						second = IBeamPort,
						pos = geom.structure.Position('PosOfIBeam4', x="0cm", y="0cm", z=((self.fISideLength/2) - self.fISidePortLoc - self.fIPortSpacing)),
						rot =fcRotation)
        IBeamSideMid = geom.shapes.Boolean('IBeamSide', type = 'subtraction',
						first = IBeamSideMidtmp2,
						second = IBeamPort,
						pos = geom.structure.Position('PosOfIBeam5', x="0cm", y="0cm", z=((self.fISideLength/2) - self.fISidePortLoc - (2*self.fIPortSpacing))),
						rot =fcRotation)

        IBeamTopPosition = geom.structure.Position('TopPosition', y= Q('0cm'), x=((self.fIFlangeHeight/2) + (self.fIFlangeThick/2)), z= Q('0cm'))
        IBeamBottomPosition = geom.structure.Position('BottomPosition', y= Q('0cm'), x=((-self.fIFlangeHeight/2) - (self.fIFlangeThick/2)), z= Q('0cm'))

        fBeamTopVol1 = geom.shapes.Boolean('TopBeamUnion', type = 'union',
						first = IBeamTopMid,
						second = IBeamTopFlange,
						pos = IBeamTopPosition)
        fBeamTopVol2 = geom.shapes.Boolean('TopBeamUnion2.1', type = 'union',
						first = fBeamTopVol1,
						second = IBeamTopFlange,
						pos = IBeamBottomPosition)
        fIBeamTopLog = geom.structure.Volume('IBeamTop', material='fDuneSteel', shape=fBeamTopVol2)

        fBeamBotVol1 = geom.shapes.Boolean('TopBeamUnion1.1', type = 'union',
						first = IBeamBotMid,
						second = IBeamTopFlange,
						pos = IBeamTopPosition)
        fBeamBotVol2 = geom.shapes.Boolean('TopBeamUnion2.2', type = 'union',
						first = fBeamBotVol1,
						second = IBeamTopFlange,
						pos = IBeamBottomPosition)
        fIBeamBotLog = geom.structure.Volume('IBeamBot', material='fDuneSteel', shape=fBeamBotVol2)

        fBeamSideVol1 = geom.shapes.Boolean('TopBeamUnion1.3', type = 'union',
						first = IBeamSideMid,
						second = IBeamSideFlange,
						pos = IBeamTopPosition)
        fBeamSideVol2 = geom.shapes.Boolean('TopBeamUnion2.3', type = 'union',
						first = fBeamSideVol1,
						second = IBeamSideFlange,
						pos = IBeamBottomPosition)
        fIBeamSideLog = geom.structure.Volume('IBeamSide', material='fDuneSteel', shape=fBeamSideVol2)

        #big box for ibeams volume
        ht = self.fht
        st = self.fst
        zbsp = self.fSpacing
        zpl = Q('0cm')
        xpl = Q('0cm')
        # start the loop
        for i in range(20):
                  IBeamTopPlacement = geom.structure.Placement(f'IBeamTopPLacement{i}',
                                                               rot = fcRotation,
                                                               volume = fIBeamTopLog,
                                                                pos = geom.structure.Position(f'IBeamTopPlacementPos{i}',
                                                                y = "0cm",
                                                                x =  ht,
                                                                z = zpl),
                                                            	)
                  IBeamBotPlacement = geom.structure.Placement(f'IBeamBotPLacement{i}',
                                                               rot = fcRotation,
                                                               volume = fIBeamBotLog,
                                                                pos = geom.structure.Position(f'IBeamBackPlacementPos{i}',
                                                                y = "0cm",
                                                                x =  - ht,
                                                                z = zpl)
                                                            	)
                  supportencLV.placements.append(IBeamTopPlacement.name)
                  supportencLV.placements.append(IBeamBotPlacement.name)

                  IBeamLeftPlacement = geom.structure.Placement(f'IBeamLeftPLacement{i}',
                                                               rot = fc2Rotation,
                                                               volume = fIBeamSideLog,
                                                                pos = geom.structure.Position(f'IBeamLeftPlacementPos{i}',
                                                                y = - st,
                                                                x =  "0cm",
                                                                z = zpl)
                                                            	)
                  IBeamRightPlacement = geom.structure.Placement(f'IBeamRightPLacement{i}',
                                                                rot = fc2Rotation,
                                                                pos = geom.structure.Position(f'IBeamRightPlacementPos{i}',
                                                                y = st,
                                                                x =  "0cm",
                                                                z = zpl),
                                                            	volume = fIBeamSideLog)
                  supportencLV.placements.append(IBeamLeftPlacement.name)
                  supportencLV.placements.append(IBeamRightPlacement.name)

                  if i == 0:
                       zpl += zbsp
                       continue

                  IBeamTopPlacement = geom.structure.Placement(f'IBeamTopPLacement2{i}',
                                                                 rot = fcRotation,
                                                                pos = geom.structure.Position(f'IBeamTopPlacementPos2{i}',
                                                                y = "0cm",
                                                                x =  ht,
                                                                z = -(zpl)),
                                                            	volume = fIBeamTopLog)
                  IBeamBotPlacement = geom.structure.Placement(f'IBeamBotPLacement2{i}',
                                                                 rot = fcRotation,
                                                                pos = geom.structure.Position(f'IBeamBotPlacementPos2{i}',
                                                                y = "0cm",
                                                                x =  -(ht),
                                                                z = -(zpl)),
                                                            	volume = fIBeamBotLog)
                  supportencLV.placements.append(IBeamTopPlacement.name)
                  supportencLV.placements.append(IBeamBotPlacement.name)

                  IBeamLeftPlacement = geom.structure.Placement(f'IBeamLeftPLacement2{i}',
                                                                rot = fc2Rotation,
                                                                pos = geom.structure.Position(f'IBeamLeftPlacementPos2{i}',
                                                                y = -(st),
                                                                x =  "0cm",
                                                                z = -(zpl)),
                                                            	volume = fIBeamSideLog)
                  IBeamRightPlacement = geom.structure.Placement(f'IBeamRightPLacement2{i}',
                                                                 rot = fc2Rotation,
                                                                pos = geom.structure.Position(f'IBeamRightPlacementPos2{i}',
                                                                y = st,
                                                                x =  "0cm",
                                                                z = -(zpl)),
                                                            	volume = fIBeamSideLog)
                  supportencLV.placements.append(IBeamLeftPlacement.name)
                  supportencLV.placements.append(IBeamRightPlacement.name)

                  zpl += zbsp

        xpl = Q('0cm')
        zpl = (self.fzpl/2) + self.fBeltBuffer # from Luis' modifications, extra space for last belts
        for i in range(5):
            IBeamFrontPlacement = geom.structure.Placement(f'IBeamFrontPLacement{i}',
                                                                rot = fc3Rotation,
                                                                pos = geom.structure.Position(f'IBeamFrontPlacementPos{i}',
                                                                y = xpl,
                                                                x =  "0cm",
                                                                z = zpl),
                                                            	volume = fIBeamSideLog)
            IBeamBackPlacement = geom.structure.Placement(f'IBeamBackPlacement{i}',
                                                                rot = fc3Rotation,
                                                                pos = geom.structure.Position(f'IBeamBackPlacementPos2ndLoop{i}',
                                                                y = xpl,
                                                                x =  "0cm",
                                                                z = -zpl),
                                                            	volume = fIBeamSideLog)
            supportencLV.placements.append(IBeamFrontPlacement.name)
            supportencLV.placements.append(IBeamBackPlacement.name)

            if i == 0:
                xpl +=zbsp
                continue

            IBeamFrontPlacement = geom.structure.Placement(f'IBeamFrontPLacement2{i}',
                                                                rot = fc3Rotation,
                                                                pos = geom.structure.Position(f'IBeamFrontPlacementPos2{i}',
                                                                y = -xpl,
                                                                x =  "0cm",
                                                                z = zpl),
                                                            	volume = fIBeamSideLog)
            IBeamBackPlacement = geom.structure.Placement(f'IBeamBackPlacement2{i}',
                                                                rot = fc3Rotation,
                                                                pos = geom.structure.Position(f'IBeamBackPlacementPos2{i}',
                                                                y = -xpl,
                                                                x =  "0cm",
                                                                z = -zpl),
                                                            	volume = fIBeamSideLog)
            supportencLV.placements.append(IBeamFrontPlacement.name)
            supportencLV.placements.append(IBeamBackPlacement.name)

            xpl += zbsp

        return supportencLV
