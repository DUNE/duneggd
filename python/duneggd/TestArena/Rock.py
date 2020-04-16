#!/usr/bin/env python

import gegede.builder
import math as m
from gegede import Quantity as Q

class RockBuilder(gegede.builder.Builder):

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self,
                  detEncDim          = None, 
                  archRadius         = None,
                  archHalfAngle      = None,
                  ConcreteBeamGap    = None,
                  RadioRockThickness = None,
                  RadioRockMaterial  = None,
                  **kwds):

        self.detEncMat          = 'Air'
        self.detEncDim          = detEncDim
        self.archRadius         = archRadius    
        self.archHalfAngle      = archHalfAngle
        self.ConcreteBeamGap    = ConcreteBeamGap
        self.RadioRockThickness = RadioRockThickness
        self.RadioRockMaterial  = RadioRockMaterial

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Define the box for the detector enclosure
        detEncBox = geom.shapes.Box('EnclosureBox',
                                    dx=2.0*self.detEncDim[0], 
                                    dy=2.0*self.detEncDim[1],
                                    dz=2.0*self.detEncDim[2])

        detEnc_lv = geom.structure.Volume('volEnc', material='Air', shape=detEncBox)
        self.add_volume(detEnc_lv)


        # Define the box for the detector enclosure
        encBox = geom.shapes.Box('DetEnclosureBox',
                                 dx=0.5*self.detEncDim[0], 
                                 dy=0.5*self.detEncDim[1],
                                 dz=0.5*self.detEncDim[2])

        # Define the arched roof of the detector enclosure
        encArch = geom.shapes.Tubs('DetEnclosureArch',
                                   rmin = Q('0cm'),
                                   rmax = self.archRadius,
                                   dz   = 0.5*self.detEncDim[2],
                                   sphi = Q('90deg')-self.archHalfAngle,
                                   dphi = self.archHalfAngle*2)

        elevation = self.detEncDim[1]/2 - m.cos(self.archHalfAngle.to('radians')) * self.archRadius
                
        Pos = geom.structure.Position(self.name+'_ArchPos',
                                      Q('0m'), elevation, Q('0m'))

        # Join the arched roof and box together
        encTotal = geom.shapes.Boolean(self.name+"BoolAdd",
                                       type   = 'union',
                                       first  = encBox,
                                       second = encArch,
                                       pos    = Pos)
        enc_lv = geom.structure.Volume('volDetEnc', material='Air', shape=encTotal)
        pos    = geom.structure.Position('posDetEnc', Q('0m'), Q('0m'), Q('0m'))
        place  = geom.structure.Placement('placeDetEnc', volume=enc_lv, pos=pos)
        detEnc_lv.placements.append(place.name)

        
        # Place a rock layer around the detector enclosure
        RockBox   = geom.shapes.Box('RadioRockBox',
                                    dx=0.5*(self.detEncDim[0])+self.RadioRockThickness,
                                    dy=0.5*(self.detEncDim[1])+0.5*self.RadioRockThickness,
                                    dz=0.5*(self.detEncDim[2])+self.RadioRockThickness)

        # Define the arched roof of the detector enclosure
        x = self.detEncDim[0]+2*self.RadioRockThickness
        r = self.archRadius+self.RadioRockThickness
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

        pos    = geom.structure.Position('posFirstSub', Q('0m'), 0.5*self.RadioRockThickness, Q('0m'))
        RockBox   = geom.shapes.Boolean('FirstSub',
                                        type   = 'subtraction',
                                        first  = RockBox,
                                        second = encTotal,
                                        pos    = pos)


        
        rock_lv   = geom.structure.Volume('volRadioRockShell', material=self.RadioRockMaterial, shape=RockBox)
        rock_pos  = geom.structure.Position('posRock', Q('0m'), -0.5*(self.RadioRockThickness), Q('0m'))
        placeRock = geom.structure.Placement('placeRock', volume=rock_lv, pos=rock_pos)
        
        detEnc_lv.placements.append(placeRock.name)
        # detEnc_lv.placements.append(placeTube.name)
