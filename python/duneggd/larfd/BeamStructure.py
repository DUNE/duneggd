#!/usr/bin/env python
'''
Subbuilder of BeamStructure
'''

import gegede.builder
from gegede import Quantity as Q


class BeamStructureBuilder(gegede.builder.Builder):
    '''
    Build the BeamS.
    '''

    def configure(self,
                  nBeam          = None,
                  BeamSeparation = None,
                  IPEBeamHeight  = None,
                  IPEBeamBase    = None,
                  IPEBeamThick1  = None,
                  IPEBeamThick2  = None,
                  plane          = None):
        self.nBeam          = nBeam         
        self.BeamSeparation = BeamSeparation
        self.IPEBeamHeight  = IPEBeamHeight
        self.IPEBeamBase    = IPEBeamBase  
        self.IPEBeamThick1  = IPEBeamThick1
        self.IPEBeamThick2  = IPEBeamThick2
        self.plane          = plane
        self.IPEBeamLength  = Q(1308.0975, 'centimeter')



             
    def ConstructBeam(self, geom, num, length, pos, rot, plane_lv):
        print ("constructing beam "+str(num))
        name = "Beam_"+str(num)
        SurroundingBox = geom.shapes.Box(name+'Box',
                                         dz=0.5*self.IPEBeamHeight,
                                         dy=0.5*length,
                                         dx=0.5*self.IPEBeamBase)
        
        SubBoxDim = [self.IPEBeamBase/2-self.IPEBeamThick2/2,
                     length,
                     self.IPEBeamHeight-self.IPEBeamThick1*2]
        
        SubtractionBox = geom.shapes.Box(name+'SubtractionBox',
                                         dx=0.5*SubBoxDim[0], 
                                         dy=0.5*SubBoxDim[1],
                                         dz=0.5*SubBoxDim[2])
        
        Pos1 = geom.structure.Position(name+'_BeamSubPos1',
                                       Q('0m'), Q('0m'),  self.IPEBeamBase/2 - SubBoxDim[0]/2)
        Pos2 = geom.structure.Position(name+'_BeamSubPos2',
                                       Q('0m'), Q('0m'), -self.IPEBeamBase/2 + SubBoxDim[0]/2)

        FirstSub = geom.shapes.Boolean(name+"_BoolSub1",
                                       type='subtraction',
                                       first=SurroundingBox,
                                       second=SubtractionBox,
                                       pos=Pos1)
        FinalSub = FirstSub# geom.shapes.Boolean(name+"_Final",
                            #            type='subtraction',
                            #            first=FirstSub,
                            #            second=SubtractionBox,
                            #            pos=Pos2)
       
        Beam_lv = geom.structure.Volume('vol'+name, material='Steel', shape=FinalSub)
        Position_Beam  = geom.structure.Position("pos"+name, pos[0], pos[1], pos[2])
        Placement_Beam = geom.structure.Placement("place"+name, volume = Beam_lv, pos=Position_Beam,
                                                  rot = rot)
        plane_lv.placements.append(Placement_Beam.name)
        

    def ConstructAllBeams(self, geom, plane_lv):
        print ("Constructing all the beams")

        for i in range(self.nBeam):
            pos = [self.planeDim[0]/2,
                   self.planeDim[1]/2,
                   i * self.BeamSeparation + self.IPEBeamBase]
            rot = 'identity'
            self.ConstructBeam(geom, i, self.planeDim[1], pos, rot, plane_lv)
            
    def construct(self, geom):
        self.planeDim = [Q('0m'),Q('0m'),Q('0m')]
        if self.plane == 'PosX':
            self.planeDim[0] = self.IPEBeamHeight
            self.planeDim[1] = self.IPEBeamLength
            self.planeDim[2] = self.nBeam * (self.BeamSeparation + self.IPEBeamBase)

        BeamPlaneBox = geom.shapes.Box('BeamPlane' + self.plane,
                                       dx=0.5*self.planeDim[0], 
                                       dy=0.5*self.planeDim[1],
                                       dz=0.5*self.planeDim[2])
        BeamPlane_lv = geom.structure.Volume('volBeamPlane' + self.plane, material='Air', shape=BeamPlaneBox)
        
        self.add_volume(BeamPlane_lv)
        print ("add "+ 'volBeamPlane' + self.plane)
        self.ConstructAllBeams(geom, BeamPlane_lv)
