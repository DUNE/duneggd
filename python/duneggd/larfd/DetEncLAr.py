#!/usr/bin/env python
'''
Subbuilder of WorldBuilder
'''

# Water Brick website https://practicalpreppers.com/product/10-pack-of-waterbrick-standard-3-5-gallon-tan/
# Water Brich dimensions 9" W x 18" L x 6" H
# Recomended stacking height is 4' so that is 8 height
# Assing the Super structure of these blocks will be 18" by 36" by 48"

import gegede.builder
import math as m
from gegede import Quantity as Q

# for the cavern dimensions, I used the 60% CF for the FD Submission drawings
#http://docs.dunescience.org/cgi-bin/RetrieveFile?docid=11239&filename=EXC%2060PCT%20FD%20Page%20Turn%20Presentation.pdf&version=2

class DetEncLArBuilder(gegede.builder.Builder):
    '''
    Build the Detector Enclosure.
    '''


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, 
                  detEncDim          = None, 
                  archRadius         = None,
                  archHalfAngle      = None,
                  ConcreteBeamGap    = None,
                  RadioRockThickness = None,
                  RadioRockMaterial  = None,
                  ShotCreteThickness = None,
                  ShotCreteMaterial  = None,
                  ConcreteThickness  = None,
                  ConcreteMaterial   = None,
                  GroutThickness     = None,
                  GroutMaterial      = None,
                  **kwds):
        
        if detEncDim is None:
            raise ValueError("No value given for detEncDim")
        
        self.detEncMat          = 'Air'
        self.detEncDim          = detEncDim
        self.archRadius         = archRadius    
        self.archHalfAngle      = archHalfAngle
        self.ConcreteBeamGap    = ConcreteBeamGap
        self.RadioRockThickness = RadioRockThickness
        self.RadioRockMaterial  = RadioRockMaterial
        self.ShotCreteThickness = ShotCreteThickness
        self.ShotCreteMaterial  = ShotCreteMaterial 
        self.ConcreteThickness  = ConcreteThickness
        self.ConcreteMaterial   = ConcreteMaterial
        self.GroutThickness     = GroutThickness
        self.GroutMaterial      = GroutMaterial 
        print ("Size of the det enclosure " + str(self.detEncDim))
        # Space from negative face of volDetEnc to closest face of detector
        #  This positions the detector in the enclosure

        self.CryoBldr   = self.get_builder("Cryostat")


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Calculate position of detector in the enclosure
        self.CryostatOuterDim = list(self.CryoBldr.CryostatOuterDim)
        self.MainDetCenter = [Q('0m'), 
                              (-0.5*self.detEncDim[1]
                               + self.ConcreteBeamGap[1]
                               + self.ConcreteThickness # move the crypstat up
                               + self.GroutThickness
                               + 0.5*self.CryostatOuterDim[1]
                               + 0.5*self.RadioRockThickness),
                              -0.5*self.detEncDim[2] + self.ConcreteBeamGap[2] + 0.5*self.CryostatOuterDim[2]]

        # Define the box for the detector enclosure
        encBox    = geom.shapes.Box('DetEnclosureBox',
                                    dx=0.5*self.detEncDim[0], 
                                    dy=0.5*self.detEncDim[1],
                                    dz=0.5*self.detEncDim[2])
        encArch   = geom.shapes.Tubs('DetEnclosureArch',
                                     rmin = Q('0cm'),
                                     rmax = self.archRadius,
                                     dz   = 0.5*self.detEncDim[2],
                                     sphi = Q('90deg')-self.archHalfAngle,
                                     dphi = self.archHalfAngle*2)
        elevation = self.detEncDim[1]/2 - m.cos(self.archHalfAngle.to('radians')) * self.archRadius
        Pos       = geom.structure.Position(self.name+'_ArchPos', Q('0m'), elevation, Q('0m'))
        encTotal  = geom.shapes.Boolean(self.name+"BoolAdd",
                                        type   = 'union',
                                        first  = encBox,
                                        second = encArch,
                                        pos    = Pos)
        
        # Place RadioRock shell around the detector enclosure
        RockBox   = geom.shapes.Box('RadioRockBox',
                                    dx=0.5*(self.detEncDim[0])+self.RadioRockThickness,
                                    dy=0.5*(self.detEncDim[1])+0.5*self.RadioRockThickness,
                                    dz=0.5*(self.detEncDim[2])+self.RadioRockThickness)        
        
        x         = self.detEncDim[0]+2*self.RadioRockThickness
        r         = self.archRadius+self.RadioRockThickness
        RockAngle = m.degrees(m.asin(x/(2*r)))
        elevation = self.detEncDim[1]/2 - m.cos(m.radians(RockAngle)) * r + 0.5*self.RadioRockThickness
        Tube_pos  = geom.structure.Position('posTube', Q('0m'), elevation, Q('0m'))
        
        RockTup = geom.shapes.Tubs('RockArch',
                                   rmin = Q('0cm'),
                                   rmax = self.archRadius + self.RadioRockThickness,
                                   dz   = 0.5*self.detEncDim[2] + self.RadioRockThickness,
                                   sphi = Q('90deg')-Q(RockAngle, 'deg'),
                                   dphi = 2*Q(RockAngle, 'deg'))

        RockBox = geom.shapes.Boolean('RockAddition',
                                      type   = 'union',
                                      first  = RockBox,
                                      second = RockTup,
                                      pos    = Tube_pos)

        detEnc_lv = geom.structure.Volume('volDetEnclosure', material=self.detEncMat, shape=RockBox)
        self.add_volume(detEnc_lv)        
        
        pos       = geom.structure.Position('posFirstSub', Q('0m'), 0.5*self.RadioRockThickness, Q('0m'))
        RockBox   = geom.shapes.Boolean('FirstSub',
                                        type   = 'subtraction',
                                        first  = RockBox,
                                        second = encTotal,
                                        pos    = pos)

        rock_lv   = geom.structure.Volume('volRadioRockShell', material=self.RadioRockMaterial, shape=RockBox)
        rock_pos  = geom.structure.Position('posRock', Q('0m'), Q('0m'), Q('0m'))
        placeRock = geom.structure.Placement('placeRock', volume=rock_lv, pos=rock_pos)
        detEnc_lv.placements.append(placeRock.name)

        # ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~
        # Place Concrete on the floor
        ConcreteBox   = geom.shapes.Box('ConcreteBox',
                                        dx=0.5*self.detEncDim[0],
                                        dy=0.5*self.ConcreteThickness,
                                        dz=0.5*self.detEncDim[2])
        GroutBox      = geom.shapes.Box('GroutBox',
                                        dx=0.5*self.detEncDim[0],
                                        dy=0.5*self.GroutThickness,
                                        dz=0.5*self.detEncDim[2])

        Concrete_lv   = geom.structure.Volume   ('volConcrete', material=self.ConcreteMaterial, shape=ConcreteBox)
        Grout_lv      = geom.structure.Volume   ('volGrout'   , material=self.GroutMaterial   , shape=GroutBox   )

        ConcretePos   = geom.structure.Position ('posConcrete',
                                                 Q('0m'), (-0.5*self.detEncDim[1]
                                                           + 0.5*self.RadioRockThickness
                                                           + 0.5*self.ConcreteThickness),
                                                 Q('0m'))
        GroutPos      = geom.structure.Position ('posGrout',
                                                 Q('0m'), (-0.5*self.detEncDim[1]
                                                           + 0.5*self.RadioRockThickness
                                                           + self.ConcreteThickness
                                                           + 0.5*self.GroutThickness),
                                                 Q('0m'))
        
        placeConcrete = geom.structure.Placement('placeConcreteInDetEnc', volume=Concrete_lv, pos=ConcretePos)
        placeGrout    = geom.structure.Placement('placeGroutInDetEnc'   , volume=Grout_lv   , pos=GroutPos   )
        detEnc_lv.placements.append(placeConcrete.name)
        detEnc_lv.placements.append(placeGrout   .name)

        # ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~
        # Place shotcrete shell on walls and ceiling
        ShotOuterBox    = geom.shapes.Box('ShotOuterBox',
                                    dx=0.5*self.detEncDim[0], 
                                    dy=0.5*self.detEncDim[1],
                                    dz=0.5*self.detEncDim[2])
        ShotOuterArch   = geom.shapes.Tubs('ShotOuterArch',
                                     rmin = Q('0cm'),
                                     rmax = self.archRadius,
                                     dz   = 0.5*self.detEncDim[2],
                                     sphi = Q('90deg')-self.archHalfAngle,
                                     dphi = self.archHalfAngle*2)
        elevation     = self.detEncDim[1]/2 - m.cos(self.archHalfAngle.to('radians')) * self.archRadius
        Pos           = geom.structure.Position('ShotOuterArchPos', Q('0m'), elevation, Q('0m'))
        ShotOuterBox  = geom.shapes.Boolean("ShotOuterBoolAdd",
                                        type   = 'union',
                                        first  = ShotOuterBox,
                                        second = ShotOuterArch,
                                        pos    = Pos)

        ShotInnerBox    = geom.shapes.Box('ShotInnerBox',
                                    dx=0.5*self.detEncDim[0] - self.ShotCreteThickness, 
                                    dy=0.5*self.detEncDim[1] - 0.5*self.ShotCreteThickness,
                                    dz=0.5*self.detEncDim[2] - self.ShotCreteThickness)

        x         = self.detEncDim[0]- 2*self.ShotCreteThickness
        r         = self.archRadius  -   self.ShotCreteThickness
        RockAngle = m.degrees(m.asin(x/(2*r)))
        elevation = self.detEncDim[1]/2 - m.cos(m.radians(RockAngle)) * r + 0.5*self.ShotCreteThickness
        Tube_pos  = geom.structure.Position('posInnerTube', Q('0m'), elevation, Q('0m'))
        ShotInnerArch   = geom.shapes.Tubs('ShotInnerArch',
                                     rmin = Q('0cm'),
                                     rmax = self.archRadius - self.ShotCreteThickness,
                                     dz   = 0.5*self.detEncDim[2] - self.ShotCreteThickness,
                                     sphi = Q('90deg')-Q(RockAngle, 'deg'),
                                     dphi = Q(RockAngle, 'deg')*2)
        elevation     = self.detEncDim[1]/2 - m.cos(self.archHalfAngle.to('radians')) * self.archRadius
        Pos           = geom.structure.Position('ShotInnerArchPos', Q('0m'), elevation, Q('0m'))
        ShotInnerBox  = geom.shapes.Boolean("ShotInnerBoolAdd",
                                        type   = 'union',
                                        first  = ShotInnerBox,
                                        second = ShotInnerArch,
                                        pos    = Pos)
        ShotInPos = geom.structure.Position('posShotInBox', Q('0m'), 0.5*(self.RadioRockThickness +
                                                                          self.ShotCreteThickness), Q('0m'))
        ShotOuterBox  = geom.shapes.Boolean('ShotOuterMinusShotInner',
                                            type   = 'subtraction',
                                            first  = ShotOuterBox,
                                            second = ShotInnerBox,
                                            pos    = ShotInPos)
        ConcSubBox = geom.shapes.Box('ConcSubBox',
                                     dx=0.5*self.detEncDim[0],
                                     dy=0.5*(self.ConcreteThickness + self.GroutThickness),
                                     dz=0.5*self.detEncDim[2])
        ConcSubPos = geom.structure.Position('ConcSubPos', Q('0m'), (-0.5*self.detEncDim[1]
                                                                     + 0.5*self.RadioRockThickness
                                                                     + 0.5*self.ConcreteThickness
                                                                     + 0.5*self.GroutThickness
                                                                     - 0.5*self.RadioRockThickness),
                                             Q('0m'))
        ShotOuterBox  = geom.shapes.Boolean('ShotOuterMinusBox',
                                            type   = 'subtraction',
                                            first  = ShotOuterBox,
                                            second = ConcSubBox,
                                            pos    = ConcSubPos)

        Shot_lv = geom.structure.Volume('volShotbox', shape=ShotOuterBox, material=self.ShotCreteMaterial)
        ShotPos = geom.structure.Position('posShotBox', Q('0m'), 0.5*self.RadioRockThickness, Q('0m'))
        ShotPla = geom.structure.Placement('placeShotBox', volume=Shot_lv, pos=ShotPos)
        detEnc_lv.placements.append(ShotPla.name)
        
        # ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~               
        # Place Cryostat
        posName     = 'Cryo_in_enc'
        cryo_lv     = self.CryoBldr.get_volume('volCryostat')
        cryo_in_enc = geom.structure.Position(posName,
                                              self.MainDetCenter[0],
                                              self.MainDetCenter[1],
                                              self.MainDetCenter[2])
        
        place_cryo_in_E = geom.structure.Placement('place'+posName,
                                                    volume = cryo_lv,
                                                    pos    = cryo_in_enc)
        detEnc_lv.placements.append(place_cryo_in_E.name)
