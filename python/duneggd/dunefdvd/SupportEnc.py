import gegede.builder
from gegede import Quantity as Q
from utils import *

#Globals
#--------------------#
fht = Q('841.1cm')
fst = Q('896.4cm') #+ Q('3.1cm')
fzpl = Q('6473.2cm') + Q('0.1cm')

fSpacing = Q('157.86cm')
fIFlangeWidth = Q('40.2cm')
fIFlangeThick = Q('4cm')
fIFlangeWaist = Q('2.2cm')
fIFlangeHeight = Q('110.8cm')
fIPortSpacing = Q('400cm')
fITopLength = Q('1783.2cm') + fIFlangeHeight
fISideLength = Q('1473.2cm') + fIFlangeHeight
fIPortHoleRad = Q('40cm')

class SupportEncBuilder(gegede.builder.Builder):
    def configure(self, **kwds):
        if not set(kwds).issubset(globals.Cryostat): # no unknown keywords
            msg = 'Unknown parameter in: "%s"' % (', '.join(sorted(kwds.keys())), )
            raise ValueError(msg)

        # The builder hierarchy takes care of all the configuration parameters
        globals.Cryostat = kwds

    def construct(self, geom):
        globals.SetDerived()

        supportencBox = geom.shapes.Box(self.name,
                                     dx=0.5*globals.get("Cavern_x") - Q('100cm')- Q('5cm'),
                                     dy=0.5*globals.get("Cavern_y") - Q('10cm') - Q('2cm'),
                                     dz=0.5*globals.get("Cavern_z") - Q('10cm') - Q('2cm'))
        supportencLV = geom.structure.Volume('vol'+self.name, material="Air", shape=supportencBox)
        self.add_volume(supportencLV)
        supportencLV = self.construct_place_IBeams(geom, supportencLV)
        supportencLV = self.construct_place_Belts(geom, supportencLV)
        supportencLV = self.construct_place_ShieldingWalls(geom, supportencLV)
        supportencLV = self.construct_place_ShieldingFloors(geom, supportencLV)
        return

    def construct_place_ShieldingFloors(self, geom, supportencLV):
        BlockThickness = Q('0.40m')
        zbsp = fSpacing
        BlockWidth = fSpacing-fIFlangeWaist-Q('0.001m') - Q('0.050m')
        box_shape = geom.shapes.Box('box_name', dy=(zbsp-Q('0.050m'))/2, dx=(BlockThickness/2.0), dz=(BlockWidth/2))
        boxshapevolume = geom.structure.Volume('boxshapeVol', material='Water', shape=box_shape)

        eps = Q('21.5cm')
        zbsp = fSpacing
        zpl=zbsp/2
        for ii in range(20):
                for jj in range(-5, 6):
                        box_name = f'ShieldingFloor_{jj}_{ii}'

                        #box_lv = geom.structure.Volume(box_name + '_lv', material=geom.get_material("Water"), shape=box_shape)
                        #box_lv.params.append(("color", "blue"))

                        xpos = -fht + eps
                        ypos = (jj) * zbsp
                        zpos = zpl

                        #pos_name = f'ShieldingFloor_pos'
                        #placement_name = f'ShieldingFloor_{jj}_{ii}_placement'

                        placement = geom.structure.Placement(
                                        f'ShieldingFloor_{jj}_{ii}',
                                        volume = boxshapevolume,
                                        pos = geom.structure.Position(f'ShieldingFloor_{jj}_{ii}_position', x=xpos, y=ypos, z=zpos))
                        supportencLV.placements.append(placement.name)
                zpl+=zbsp

        zpl=-zbsp/2
        for ii in range(0, -20, -1):
                for jj in range(-5, 6):
                        box_name = f'ShieldingFloor_{jj}_{ii}'

                        #box_lv = geom.structure.Volume(box_name + '_lv', material=geom.get_material("Water"), shape=box_shape)
                        #box_lv.params.append(("color", "blue"))

                        xpos = -fht + eps
                        ypos = (jj) * zbsp
                        zpos = zpl

                        #pos_name = f'ShieldingFloor_pos'
                        #placement_name = f'ShieldingFloor2_{jj}_{ii}_placement'

                        placement = geom.structure.Placement(
                                f'ShieldingFloor2_{jj}_{ii}',
                                volume = boxshapevolume,
                                pos = geom.structure.Position(f'ShieldingFloor2_{jj}_{ii}_position', x=xpos, y=ypos, z=zpos)
                        )
                        supportencLV.placements.append(placement.name)
                zpl-=zbsp
        return supportencLV

    def construct_place_ShieldingWalls(self, geom, supportencLV):
        eps = Q('21.5cm')
        ht = fht
        st = fst + Q('3.1cm')
        fzpl = Q('6473.2cm')
        yTopHole = -((fISideLength / 2) +(fIFlangeHeight / 2) - Q('590.7cm') -(3.0 * fIPortSpacing) +(9 * fIPortHoleRad)) / 2
        yBotHole = -((fISideLength / 2) +(fIFlangeHeight / 2) - Q('590.7cm') -(-1.0 * fIPortSpacing) +(9 * fIPortHoleRad)) / 2
        y1HoleUp = -((fISideLength / 2) +(fIFlangeHeight / 2) - Q('590.7cm') -(1.0 * fIPortSpacing) +(9 * fIPortHoleRad)) / 2
        yTop = (ht-eps)


        BlockWidth = fSpacing - fIFlangeWaist - Q('0.1cm') - Q('5cm')
        BlockHeight = fIPortSpacing - Q('5cm')
        BlockHeightTop = BlockHeight * 0.63
        BlockHeightBottom = BlockHeight * 0.15

        fBlockThickness = Q('23cm')


        ShieldBlock = geom.shapes.Box('ShieldBlock',
					dy = (fBlockThickness /2),
					dx = (BlockHeight /2),
					dz = (BlockWidth /2))

        ShieldBlockTop = geom.shapes.Box('ShieldBlockTop',
					dy = (fBlockThickness /2),
					dx = (BlockHeightTop /2),
					dz = (BlockWidth /2))

        ShieldBlockBot = geom.shapes.Box('ShieldBlockBot',
					dy = (fBlockThickness /2),
					dx = (BlockHeightBottom /2),
					dz = (BlockWidth /2))

        fcRotation = geom.structure.Rotation('fcRotation', x= "0deg", y= "0deg",z= "0deg")
        fc2Rotation = geom.structure.Rotation('fc2Rotation',x= "90deg", y= "0deg",z= "0deg")
        fc3Rotation = geom.structure.Rotation('fc3Rotation', x= "0deg", y= "0deg",z= "90deg")

        ShieldBlockLog = geom.structure.Volume('ShieldBlockLog', material='Water', shape=ShieldBlock)
        ShieldBlockTopLog = geom.structure.Volume('ShieldBlockTopLog', material='Water', shape=ShieldBlockTop)
        ShieldBlockBotLog = geom.structure.Volume('ShieldBlockBotLog', material='Water', shape=ShieldBlockBot)

        zbsp = fSpacing
        zpl = zbsp /2
        xpl = Q('0cm')

        for ii in range(20):
            for jj in range(5):
                y = "0cm"
                shield = ShieldBlockLog
                if(jj ==3):
                    y = yTopHole + BlockHeight/2 + BlockHeightTop/2 + Q('5cm')
                    shield = ShieldBlockTopLog
                if(jj==2):
                    y = yBotHole
                if(jj==1):
                    y = y1HoleUp
                if(jj==0):
                    y =yTopHole
                if(jj==4):
                    y= (yBotHole)-(BlockHeight/2) - (0.05*BlockHeightBottom)- (Q('5cm'))
                    shield = ShieldBlockBotLog

                if(jj== 0 or jj==3):
                    continue


                #pdb.set_trace()
                shieldLeftPosition = geom.structure.Position(f'ShieldLeftPosition{ii}{jj}',y,-st,-zpl)
                shieldLeft = geom.structure.Placement(f'ShieldLeftPlacement{ii}{jj}',volume=shield,pos=shieldLeftPosition,rot= fcRotation)
                supportencLV.placements.append(shieldLeft.name)

                shieldRightPosition = geom.structure.Position(f'ShieldRightPosition{ii}{jj}',y,st,-zpl)
                shieldRight = geom.structure.Placement(f'ShielRightPlacement{ii}{jj}',volume=shield,pos=shieldRightPosition,rot=fcRotation)
                supportencLV.placements.append(shieldRight.name)

                shieldLeftPosition = geom.structure.Position(f'ShieldLeft2Position{ii}{jj}',y,-st,zpl)
                shieldLeft = geom.structure.Placement(f'ShieldLeft2Placement{ii}{jj}',volume=shield,pos=shieldLeftPosition,rot=fcRotation)
                supportencLV.placements.append(shieldLeft.name)

                shieldRightPosition = geom.structure.Position(f'ShieldRight2Position{ii}{jj}',y,st,zpl)
                shieldRight = geom.structure.Placement(f'ShieldRight2Placement{ii}{jj}',volume=shield,pos=shieldRightPosition,rot=fcRotation)
                supportencLV.placements.append(shieldRight.name)

            zpl += zbsp

        xpl = zbsp/2
        zpl = fzpl/2
        for ii in range(5):
            for jj in range(5):
                y = "0cm"
                shield = ShieldBlockLog
                if(jj==3):
                    y = yTopHole + BlockHeight/2 + BlockHeightTop/2 + Q('5cm')
                    shield = ShieldBlockTopLog

                if(jj==2):
                    y = yBotHole

                if(jj==1):
                    y = y1HoleUp
                if(jj==0):
                    y =yTopHole
                if(jj==4):
                    y = yBotHole -BlockHeight/2 - 0.5*BlockHeightBottom - Q('5cm')
                    shield = ShieldBlockBotLog

                ShieldBackPositon = geom.structure.Position(f'ShieldBackPosition{ii}{jj}',y,-xpl, -zpl)
                ShielBackPlacement = geom.structure.Placement(f'ShieldBackPlacement{ii}{jj}',volume=shield,pos=ShieldBackPositon,rot=fc2Rotation)
                supportencLV.placements.append(ShielBackPlacement.name)

                ShieldBackPositon = geom.structure.Position(f'ShieldBack2Position{ii}{jj}',y,xpl, -zpl)
                ShielBackPlacement = geom.structure.Placement(f'ShieldBack2Placement{ii}{jj}',volume=shield,pos=ShieldBackPositon,rot=fc2Rotation)
                supportencLV.placements.append(ShielBackPlacement.name)

                ShieldFrontPosition = geom.structure.Position(f'ShieldFrontposition{ii}{jj}',y,-xpl,zpl)
                ShieldFrontPlacement = geom.structure.Placement(f'ShieldFrontPlacement{ii}{jj}',volume=shield,pos=ShieldFrontPosition,rot=fc2Rotation)
                supportencLV.placements.append(ShieldFrontPlacement.name)

                ShieldFrontPosition = geom.structure.Position(f'ShieldFront2position{ii}{jj}',y,xpl,zpl)
                ShieldFrontPlacement = geom.structure.Placement(f'ShieldFront2Placement{ii}{jj}',volume=shield,pos=ShieldFrontPosition,rot=fc2Rotation)
                supportencLV.placements.append(ShieldFrontPlacement.name)
            xpl+=zbsp
        return supportencLV

    def construct_place_Belts(self, geom, supportencLV):
        ht = fht
        st = fst

        BeltFlange = geom.shapes.Box('BeltFlange',
					dy = Q('10cm'),
					dx = (fIFlangeWaist /2),
					dz = ((fSpacing /2) - (fIFlangeWaist/2) - Q('0.1cm')))

        BeltMid = geom.shapes.Box('BeltMid',
					dy = (fIFlangeWaist/2),
					dx = (fIFlangeHeight /4),
					dz = ((fSpacing /2) - (fIFlangeWaist/2) - Q('0.1cm')))

        IBeamPort = geom.shapes.Tubs('BeltPortHole',
					rmin = Q('0cm'),
					rmax = Q('25cm'),
					dz = (fIFlangeThick /2),
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


        tr1 = geom.structure.Position('tr1', y= Q('0cm'), x=(fIFlangeHeight/4), z= Q('0cm'))
        tr2 = geom.structure.Position('tr2', y= Q('0cm'), x=(-fIFlangeHeight /4), z= Q('0cm'))

        Union1 = geom.shapes.Boolean('Union1', type = 'union',
						first = BeltHole,
						second = BeltFlange,
						pos = tr1)
        BeltHoleUni = geom.shapes.Boolean('BeltHoleUnion', type = 'union',
						first = Union1,
						second = BeltFlange,
						pos = tr2)


        BeltHoleUniLog = geom.structure.Volume('BeltHoleUni', material='AirSteelMixture', shape=BeltHoleUni)


        Union2 = geom.shapes.Boolean('Union2', type = 'union',
						first = BeltMid,
						second = BeltFlange,
						pos = tr1)
        BeltUni = geom.shapes.Boolean('BeltUnion', type = 'union',
						first = Union2,
						second = BeltFlange,
						pos = tr2)

        BeltUniLog = geom.structure.Volume('BeltUni', material='AirSteelMixture', shape=BeltUni)


        zbsp = fSpacing
        zpl = (zbsp/2)
        xpl = Q('0cm')
        eps = Q('21.5cm')
        cpIT = Q('0cm')
        cpIB = Q('0cm')
        cpIL = Q('0cm')
        cpIR = Q('0cm')
        fzpl = Q('6473.2cm')

        for ii in range (19):
            for jj in range(-5,5):
                BeltBot = geom.structure.Placement(f'BeltBottom_{jj}_{ii}',

                                                                pos = geom.structure.Position(f'BeltBottomPlacement_{jj}_{ii}',
                                                                y = ((jj + 0.5) * zbsp),
                                                                x =  (-ht + eps),
                                                                z = (zpl)),
                                                            	volume = BeltHoleUniLog)
                supportencLV.placements.append(BeltBot.name)

                BeltBot = geom.structure.Placement(f'BeltBottom2_{jj}_{ii}',

                                                                pos = geom.structure.Position(f'BeltBottomPlacement2_{jj}_{ii}',
                                                                y = ((jj + 0.5) * zbsp),
                                                                x =  (-ht + eps),
                                                                z = (-zpl)),
                                                            	volume = BeltHoleUniLog)
                supportencLV.placements.append(BeltBot.name)

                if abs(jj) in (1, 2, 4):

                    BeltTop = geom.structure.Placement(f'BeltTop_{jj}_{ii}',

                                                                pos = geom.structure.Position(f'BeltTopPlacement_{jj}_{ii}',
                                                                y = ((jj + 0.5) * zbsp),
                                                                x =  (ht - eps),
                                                                z = (zpl)),
                                                            	volume = BeltUniLog)
                    supportencLV.placements.append(BeltTop.name)

                    BeltTop = geom.structure.Placement(f'BeltTop2_{jj}_{ii}',

                                                                pos = geom.structure.Position(f'BeltTopPlacement2_{jj}_{ii}',
                                                                y = ((jj + 0.5) * zbsp),
                                                                x =  (ht - eps),
                                                                z = (-zpl)),
                                                            	volume = BeltUniLog)
                    supportencLV.placements.append(BeltTop.name)


            for kk in range(4):
                yvar = None
                belt = BeltHoleUniLog

                if kk == 3:
                    yvar = ht-eps
                    belt = BeltUniLog
                    if ii % 3:
                        belt = BeltHoleUniLog
                if kk == 2:
                    yvar = -((fISideLength / 2) +(fIFlangeHeight / 2) -Q('590.7cm') +(0.0 * fIPortSpacing) +(9 * fIPortHoleRad)) / 2

                if kk ==1:
                    yvar = -((fISideLength / 2) +(fIFlangeHeight / 2) -Q('590.7cm') -(2.0 * fIPortSpacing) +(9 * fIPortHoleRad)) / 2
                    belt = BeltUniLog
                    if (ii+1) % 3:
                        belt =BeltHoleUniLog

                if kk == 0:
                    yvar  = -((fISideLength / 2) +(fIFlangeHeight / 2) -Q('590.7cm') -(4.0 * fIPortSpacing) +(9 * fIPortHoleRad)) / 2
                    belt = BeltUniLog
                    if ((ii+2) %3):
                        belt = BeltHoleUniLog

                if ii ==20:
                    belt = BeltUniLog

                BeltLeft = geom.structure.Placement(f'BeltLeft{kk}_{ii}',

                                                                pos = geom.structure.Position(f'BeltLeftPlacement{kk}_{ii}',
                                                                y = -st,
                                                                x = yvar ,
                                                                z = (-zpl)),
                                                            	volume = belt,
                                                                rot= fcRotation)
                supportencLV.placements.append(BeltLeft.name)

                BeltRight = geom.structure.Placement(f'BeltRight{kk}_{ii}',

                                                                pos = geom.structure.Position(f'BeltRigthPlacement{kk}_{ii}',
                                                                y = st,
                                                                x = yvar ,
                                                                z = (-zpl)),
                                                            	volume = belt,
                                                                rot= fcRotation)
                supportencLV.placements.append(BeltRight.name)

                BeltLeft = geom.structure.Placement(f'BeltLeft_{kk}_{ii}',

                                                                pos = geom.structure.Position(f'BeltLeftPlacement_{kk}_{ii}',
                                                                y = -st,
                                                                x = yvar ,
                                                                z = (zpl)),
                                                            	volume = belt,
                                                                rot= fcRotation)
                supportencLV.placements.append(BeltLeft.name)

                BeltRight = geom.structure.Placement(f'BeltRight_{kk}_{ii}',

                                                                pos = geom.structure.Position(f'BeltRigthPlacement_{kk}_{ii}',
                                                                y = st,
                                                                x = yvar ,
                                                                z = zpl),
                                                            	volume = belt,
                                                                rot= fcRotation)
                supportencLV.placements.append(BeltRight.name)
            zpl+=zbsp

        cpBF =0
        cpBBK =0
        xpl = zbsp/2
        zpl = fzpl / 2 + Q('0.10cm')
        for ii in range(5):
            for jj in range (4):
                yvar = None
                belt = BeltHoleUniLog

                if jj == 3:
                    yvar = ht
                    belt = BeltUniLog
                    if (ii % 3):
                        belt = BeltHoleUniLog
                if jj == 2:
                    yvar = -((fISideLength / 2) +(fIFlangeHeight / 2) -Q('590.7cm') +(0.0 * fIPortSpacing) +(9 * fIPortHoleRad)) / 2
                if jj ==1:
                    yvar = -((fISideLength / 2) +(fIFlangeHeight / 2) -Q('590.7cm') -(2.0 * fIPortSpacing) +(9 * fIPortHoleRad)) / 2
                    belt = BeltUniLog
                    if ((ii +1) % 3):
                        belt = BeltHoleUniLog
                if jj == 0:
                    yvar = -((fISideLength / 2) +(fIFlangeHeight / 2) -Q('590.7cm') -(4.0 * fIPortSpacing) +(9 * fIPortHoleRad)) / 2
                    belt = BeltUniLog
                    if ((ii +2) %3 ):
                        belt = BeltHoleUniLog


                if ii == 20:
                    belt = BeltUniLog


                BeltBack = geom.structure.Placement(f'BeltBack_{jj}_{ii}',
                                                                pos = geom.structure.Position(f'BeltBackPlacement_{jj}_{ii}',
                                                                y = -xpl,
                                                                x = yvar ,
                                                                z = -zpl),
                                                            	volume = belt,
                                                                rot= fc3Rotation)
                supportencLV.placements.append(BeltBack.name)

                BeltBack = geom.structure.Placement(f'BeltBack2_{jj}_{ii}',
                                                                pos = geom.structure.Position(f'BeltBackPlacement2_{jj}_{ii}',
                                                                y = xpl,
                                                                x = yvar ,
                                                                z = -zpl),
                                                            	volume = belt,
                                                                rot= fc3Rotation)
                supportencLV.placements.append(BeltBack.name)

                BeltFront = geom.structure.Placement(f'BeltFront_{jj}_{ii}',

                                                                pos = geom.structure.Position(f'BeltFrontPlacement_{jj}_{ii}',
                                                                y = -xpl,
                                                                x = yvar ,
                                                                z = zpl),
                                                            	volume = belt,
                                                                rot= fc3Rotation)
                supportencLV.placements.append(BeltFront.name)

                BeltFront = geom.structure.Placement(f'BeltFront2_{jj}_{ii}',

                                                                pos = geom.structure.Position(f'BeltFrontPlacement2_{jj}_{ii}',
                                                                y = xpl,
                                                                x = yvar ,
                                                                z = zpl),
                                                            	volume = belt,
                                                                rot= fc3Rotation)
                supportencLV.placements.append(BeltFront.name)



            xpl += zbsp
        return supportencLV

    def construct_place_IBeams(self, geom, supportencLV):
        IBeamTopFlange = geom.shapes.Box('IBeamTopFlange',
					dy = (fIFlangeWidth /2),
					dx = (fIFlangeThick /2),
					dz = (fITopLength /2))#creating a IBeamTopFlanfe object
        IBeamTopMid = geom.shapes.Box('IBeamTopMid',
					dy = (fIFlangeWaist /2),
					dx = (fIFlangeHeight /2),
					dz = (fITopLength /2))#creating a IBeamTopMid object
        IBeamSideFlange = geom.shapes.Box('IBeamSideFlange',
					dy = (fIFlangeWidth /2),
					dx = (fIFlangeThick /2),
					dz = (fISideLength /2))#creating a IBeamSideFlange object
        IBeamSideMidtmp0 = geom.shapes.Box('IBeamSideMid',
					dy = (fIFlangeWaist /2),
					dx = (fIFlangeHeight /2),
					dz = (fISideLength /2))#creating a IBeamSideMid object
        IBeamPort = geom.shapes.Tubs('IBeamPortTub',
					rmin = Q('0cm'),
					rmax = fIPortHoleRad,
					dz = (fIFlangeThick /2),
					sphi = Q('0deg'),
					dphi = Q('360deg'))

        fcRotation = geom.structure.Rotation('fc', x= "90deg", y= "0deg",z= "0deg")
        fc2Rotation = geom.structure.Rotation('fc2',x= "0deg", y= "90deg",z= "90deg")
        fc3Rotation = geom.structure.Rotation('fc3', x= "0deg", y= "90deg",z= "0deg")

        IBeamBotMidtmp = geom.shapes.Boolean('IBeamBottomtmp', type = 'subtraction',
						first = IBeamTopMid,
						second = IBeamPort,
						pos = geom.structure.Position('PosOfIBeam', x="0cm", y="0cm", z=fIPortSpacing/2),
						rot = fcRotation)
        IBeamBotMid = geom.shapes.Boolean('IBeamBottom', type = 'subtraction',
						first = IBeamBotMidtmp,
						second = IBeamPort,
						pos = geom.structure.Position('PosOfIBeam2', x="0cm", y="0cm", z=-fIPortSpacing/2),
						rot = fcRotation)
        IBeamSideMidtmp1 = geom.shapes.Boolean('IBeamSidetmp', type = 'subtraction',
						first = IBeamSideMidtmp0,
						second = IBeamPort,
						pos = geom.structure.Position('PosOfIBeam3', x="0cm", y="0cm", z=((fISideLength/2) + (fIFlangeHeight/2) - Q('590.7cm'))),
						rot =fcRotation)
        IBeamSideMidtmp2 = geom.shapes.Boolean('IBeamSidetmp2', type = 'subtraction',
						first = IBeamSideMidtmp1,
						second = IBeamPort,
						pos = geom.structure.Position('PosOfIBeam4', x="0cm", y="0cm", z=((fISideLength/2) + (fIFlangeHeight/2) - Q('590.7cm') - fIPortSpacing)),
						rot =fcRotation)
        IBeamSideMid = geom.shapes.Boolean('IBeamSide', type = 'subtraction',
						first = IBeamSideMidtmp2,
						second = IBeamPort,
						pos = geom.structure.Position('PosOfIBeam5', x="0cm", y="0cm", z=((fISideLength/2) + (fIFlangeHeight/2) - Q('590.7cm') - (2*fIPortSpacing))),
						rot =fcRotation)

        IBeamTopPosition = geom.structure.Position('TopPosition', y= Q('0cm'), x=((fIFlangeHeight /2) + (fIFlangeThick /2)), z= Q('0cm'))
        IBeamBottomPosition = geom.structure.Position('BottomPosition', y= Q('0cm'), x=((-fIFlangeHeight /2) - (fIFlangeThick /2)), z= Q('0cm'))


        fBeamTopVol1 = geom.shapes.Boolean('TopBeamUnion', type = 'union',
						first = IBeamTopMid,
						second = IBeamTopFlange,
						pos = IBeamTopPosition)
        fBeamTopVol2 = geom.shapes.Boolean('TopBeamUnion2.1', type = 'union',
						first = fBeamTopVol1,
						second = IBeamTopFlange,
						pos = IBeamBottomPosition)
        fIBeamTopLog = geom.structure.Volume('IBeamTop', material='ShotRock', shape=fBeamTopVol2)

        fBeamBotVol1 = geom.shapes.Boolean('TopBeamUnion1.1', type = 'union',
						first = IBeamBotMid,
						second = IBeamTopFlange,
						pos = IBeamTopPosition)
        fBeamBotVol2 = geom.shapes.Boolean('TopBeamUnion2.2', type = 'union',
						first = fBeamBotVol1,
						second = IBeamTopFlange,
						pos = IBeamBottomPosition)
        fIBeamBotLog = geom.structure.Volume('IBeamBot', material='ShotRock', shape=fBeamBotVol2)

        fBeamSideVol1 = geom.shapes.Boolean('TopBeamUnion1.3', type = 'union',
						first = IBeamSideMid,
						second = IBeamSideFlange,
						pos = IBeamTopPosition)
        fBeamSideVol2 = geom.shapes.Boolean('TopBeamUnion2.3', type = 'union',
						first = fBeamSideVol1,
						second = IBeamSideFlange,
						pos = IBeamBottomPosition)
        fIBeamSideLog = geom.structure.Volume('IBeamSide', material='ShotRock', shape=fBeamSideVol2)
        #big box for ibeams volume

        ht = fht
        st = fst
        zbsp = fSpacing
        cpIT = Q('0')
        cpIB = Q('0')
        cpIL = Q('0')
        cpIR = Q('0')
        zpl = Q('0cm')
        mIL  = Q('0')
        cpIF = Q('0')
        cpIBk = Q('0')
        xpl = Q('0cm')
        fzpl = Q('6473.2cm')

        for i in range(20):
                  IBeamTopPlacement = geom.structure.Placement(f'IBeamTopPLacement{i}',
                                                               rot = fcRotation,
                                                               volume = fIBeamTopLog,
                                                                pos = geom.structure.Position(f'IBeamTopPlacementPos{i}',
                                                                y = "0cm",
                                                                x =  ht,
                                                                z = zpl),
                                                            	)
                  supportencLV.placements.append(IBeamTopPlacement.name)

                  IBeamBotPlacement = geom.structure.Placement(f'IBeamBotPLacement{i}',
                                                               rot = fcRotation,
                                                               volume = fIBeamBotLog,
                                                                pos = geom.structure.Position(f'IBeamBackPlacementPos{i}',
                                                                y = "0cm",
                                                                x =  - ht,
                                                                z = zpl)
                                                            	)
                  supportencLV.placements.append(IBeamBotPlacement.name)

                  IBeamLeftPlacement = geom.structure.Placement(f'IBeamLeftPLacement{i}',
                                                               rot = fc2Rotation,
                                                               volume = fIBeamSideLog,
                                                                pos = geom.structure.Position(f'IBeamLeftPlacementPos{i}',
                                                                y = - st,
                                                                x =  "0cm",
                                                                z = zpl)
                                                            	)
                  supportencLV.placements.append(IBeamLeftPlacement.name)

                  IBeamRightPlacement = geom.structure.Placement(f'IBeamRightPLacement{i}',
                                                                rot = fc2Rotation,
                                                                pos = geom.structure.Position(f'IBeamRightPlacementPos{i}',
                                                                y = st,
                                                                x =  "0cm",
                                                                z = zpl),
                                                            	volume = fIBeamSideLog)
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
                  supportencLV.placements.append(IBeamTopPlacement.name)

                  IBeamBotPlacement = geom.structure.Placement(f'IBeamBotPLacement2{i}',
                                                                 rot = fcRotation,
                                                                pos = geom.structure.Position(f'IBeamBotPlacementPos2{i}',
                                                                y = "0cm",
                                                                x =  -(ht),
                                                                z = -(zpl)),
                                                            	volume = fIBeamBotLog)
                  supportencLV.placements.append(IBeamBotPlacement.name)

                  IBeamLeftPlacement = geom.structure.Placement(f'IBeamLeftPLacement2{i}',
                                                                rot = fc2Rotation,
                                                                pos = geom.structure.Position(f'IBeamLeftPlacementPos2{i}',
                                                                y = -(st),
                                                                x =  "0cm",
                                                                z = -(zpl)),
                                                            	volume = fIBeamSideLog)
                  supportencLV.placements.append(IBeamLeftPlacement.name)

                  IBeamRightPlacement = geom.structure.Placement(f'IBeamRightPLacement2{i}',
                                                                 rot = fc2Rotation,
                                                                pos = geom.structure.Position(f'IBeamRightPlacementPos2{i}',
                                                                y = st,
                                                                x =  "0cm",
                                                                z = -(zpl)),
                                                            	volume = fIBeamSideLog)
                  supportencLV.placements.append(IBeamRightPlacement.name)

                  zpl += zbsp


        xpl = Q('0cm')
        zpl = (fzpl /2)
        for i in range(5):
            IBeamFrontPlacement = geom.structure.Placement(f'IBeamFrontPLacement{i}',
                                                                rot = fc3Rotation,
                                                                pos = geom.structure.Position(f'IBeamFrontPlacementPos{i}',
                                                                y = xpl,
                                                                x =  "0cm",
                                                                z = zpl),
                                                            	volume = fIBeamSideLog)
            supportencLV.placements.append(IBeamFrontPlacement.name)

            IBeamBackPlacement = geom.structure.Placement(f'IBeamBackPlacement{i}',
                                                                rot = fc3Rotation,
                                                                pos = geom.structure.Position(f'IBeamBackPlacementPos2ndLoop{i}',
                                                                y = xpl,
                                                                x =  "0cm",
                                                                z = -zpl),
                                                            	volume = fIBeamSideLog)
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
            supportencLV.placements.append(IBeamFrontPlacement.name)

            IBeamBackPlacement = geom.structure.Placement(f'IBeamBackPlacement2{i}',
                                                                rot = fc3Rotation,
                                                                pos = geom.structure.Position(f'IBeamBackPlacementPos2{i}',
                                                                y = -xpl,
                                                                x =  "0cm",
                                                                z = -zpl),
                                                            	volume = fIBeamSideLog)
            supportencLV.placements.append(IBeamBackPlacement.name)


            xpl += zbsp
        return supportencLV
