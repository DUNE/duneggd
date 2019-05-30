#!/usr/bin/env python
'''
Subbuilder of TPCBuilder
'''

from math import cos, sin, tan
import gegede.builder
from gegede import Quantity as Q
from gegede import units

class TPCPlaneBuilder(gegede.builder.Builder):
    '''
    Build the Cryostat.
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, 
                  wireDiam            = Q('150um'),
                  wirePitch           = None,
                  wireAngle           = None,
                  nChannels           = None,
                  nowires             = False,
                  apaFrameDim         = None,
                  g10Thickness        = Q('0.125in'),
                  wrapCover           = Q('0.0625in'),
                  view                = None,
                  **kwds):

        if apaFrameDim is None:
            raise ValueError("No value given for apaFrameDim")
        if view is None:
            raise ValueError("No value given for view") 
        if wirePitch is None:
            raise ValueError("No value given for wirePitch")
        if wireAngle is None:
            raise ValueError("No value given for wireAngle")
        if nChannels is None:
            raise ValueError("No value given for nChannels")

        self.wireDiam           = wireDiam
        self.wirePitch          = wirePitch
        self.wireAngle          = wireAngle
        self.nChannels          = nChannels
        self.nowires            = nowires
        self.apaFrameDim        = apaFrameDim
        self.g10Thickness       = g10Thickness 
        self.wrapCover          = wrapCover
        self.view               = view

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # N.B. -- the names 'volTPCPlane*' and 'volTPCWire*' are required by LArSoft

        # Define wire shape and volume
        #
        # TODO: fix material
        #

        g10 = self.g10Thickness
        g10wrap = self.wrapCover

        #
        # TODO: rework configuration of frame vs phys dimensions
        #       
        # apaFameDim config: z dim includes g10 plastic, y doesn't 
        self.apaPhysicalDim = list(self.apaFrameDim)
        self.apaPhysicalDim[1] += (4*g10 + g10wrap)  # 4x from Z, V, U, gridplane
        self.apaFrameDim[2] -= (4*g10 + 2*g10wrap)  # V & U g10, and cover on both sides

        self.planeDim = list(self.apaFrameDim)
        self.planeDim[0] = self.wireDiam;

        if self.view == 'Z': 
            self.planeDim[1] +=  1*g10 
            #self.planeDim[2] -= (4*g10 + 2*g10wrap) # 228.415 too small ?
            # calculate for now:
            self.planeDim[2] = (int(self.nChannels/2)-1)*self.wirePitch + self.wireDiam
        if self.view == 'V': 
            self.planeDim[1] +=  1*g10
            self.planeDim[2] -= (2*g10 + 2*g10wrap)
        if self.view == 'U': 
            self.planeDim[1] +=  2*g10
            self.planeDim[2] -= (0*g10 + 2*g10wrap)


        # define readout plane shape and volume
        #  nudge y and z dim so corners of wire endpoints fit in plane 
        readPlaneBox = geom.shapes.Box( 'TPCPlane' + self.view,  dx=0.5*self.planeDim[0], 
                                        dy=0.5*self.planeDim[1] + self.wireDiam,
                                        dz=0.5*self.planeDim[2] + self.wireDiam )
        readPlane_lv = geom.structure.Volume('volTPCPlane' + self.view, material='LAr', shape=readPlaneBox)
        self.add_volume(readPlane_lv)


        if not self.nowires:
            if (self.view == 'Z'):
                self.MakeCollectionPlane(geom,readPlane_lv)
            if (self.view == 'V' or self.view == 'U'):
                self.MakeInductionPlane(geom,readPlane_lv)




    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def MakeCollectionPlane( self, geom, readPlane_lv ):
        print('Creating collection wires.')
        nWires = int(0.5*self.nChannels)
        wireSpan_z = (nWires-1) * self.wirePitch # center to center
        if (wireSpan_z > self.planeDim[2]):
            raise Exception('Wire span ' + str(wireSpan_z) + ' excedes ' + str(self.planeDim[2]))
        
        zwire    = geom.shapes.Tubs('TPCWire' + self.view, 
                                    rmin = Q('0cm'),
                                    rmax = 0.5*self.wireDiam, 
                                    dz   = 0.5*self.planeDim[1] )
        
        zwire_lv = geom.structure.Volume('volTPCWireVertInner', material='Steel', shape=zwire)
        
        for i in range(nWires):       
            wirePos = [ Q('0cm'), Q('0cm'), -0.5 * wireSpan_z + i*self.wirePitch ]
            self.PlaceWire( geom, i, readPlane_lv, wirePos, 'r90aboutX', zwire_lv )
        print('DONE - Creating collection wires.')



    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def PlaceWire( self, geom, num, plane_lv,
                   wirePos, wireRot, wire_lv ):

        posName = 'Wire-'+str(num)+'_in_Plane-' + self.view
        wire_in_plane = geom.structure.Position(posName, 
                                                wirePos[0],
                                                wirePos[1],
                                                wirePos[2])
        
        pWire_in_Plane = geom.structure.Placement('place_'+posName,
                                                  volume = wire_lv,
                                                  pos = wire_in_plane,
                                                  rot = wireRot)
        plane_lv.placements.append(pWire_in_Plane.name)



    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def MakeAndPlaceWire( self, geom, num, plane_lv,
                          wirePos, wireRot, wireLen):

        wire    = geom.shapes.Tubs('TPCWire' + self.view + '_' + str(num), 
                                    rmin = '0cm',
                                    rmax = 0.5*self.wireDiam, 
                                    dz   = 0.5*wireLen )
        wire_lv = geom.structure.Volume('volTPCWire' + self.view + str(num)+'Inner', 
                                        material='Steel', shape=wire)

        self.PlaceWire( geom, num, plane_lv, wirePos, wireRot, wire_lv  )

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def MakeInductionPlane( self, geom, plane_lv ):
        print('Creating induction wires ('+self.view+').')

        pitch = [ Q('0cm'), 
                  self.wirePitch / sin(self.wireAngle.to('radians')),
                  self.wirePitch / cos(self.wireAngle.to('radians')) ]

        nWires     = int( self.planeDim[2]/pitch[2] )
        nSideWires = int( self.planeDim[1]/pitch[1] ) - nWires
        print('There are '+str(nWires)+' induction wires at the edge and '+str(nSideWires)+' induction wires wrapped.')
        print('Note these are in reality the same wires.')

        ### if (nWires != int(0.5*self.nChannels)): 
        ###     raise Exception(self.view+' Plane: Calculated '+str(nWires)+', but configured '+str(self.nChannels/2)+"\nThis needs to be reconciled")
                   
        if (self.view == 'U'):
            firstWireOffset = Q('.55cm') + self.g10Thickness + 2*self.g10Thickness*tan(self.wireAngle.to('radians')) - pitch[2]
            degAboutX = Q( 90, 'degree') + self.wireAngle
            wireRot = geom.structure.Rotation( 'rUWire', degAboutX, '0deg','0deg'  )
            order = 1
        if (self.view == 'V'):
            firstWireOffset = Q( .5, 'cm' )
            degAboutX = Q( 90, 'degree') - self.wireAngle
            wireRot = geom.structure.Rotation( 'rVWire', degAboutX, '0deg','0deg'  )
            order = -1

          # Starting with the bottom corner wires:
           # x=0 to center the wires in the plane
           # y positioning: (-0.5*$TPCWirePlaneHeight) starts the incremental increase
             # from the bottom of the plane, and trigonometry gives the increment
           # z positioning: Looking at the plane from the positive x direction,
             # (0.5*$TPCWirePlaneLength) starts the incremental increase from
             # the lower left corner.

        
        firstWirePos = [ Q('0cm'), 
                         - 0.5*self.planeDim[1] + 0.5*firstWireOffset/tan(self.wireAngle.to('radians')), 
                         order * ( - 0.5*self.planeDim[2] + 0.5*firstWireOffset) ]

        #print (self.planeDim)


        wireNum=0
      #  print("now moving to unwrapped")
        # anchored corner wire segments
        for i in range(nWires):
            wireLen = ( firstWireOffset + i*pitch[2] ) / sin(self.wireAngle.to('radians'))
            wirePos = [ Q('0cm'), 
                        firstWirePos[1] + i * 0.5 * pitch[1],
                        firstWirePos[2] + order * i * 0.5 * pitch[2] ]
            self.MakeAndPlaceWire( geom, wireNum, plane_lv, 
                                   wirePos, wireRot, wireLen )
            wireNum += 1
            #print("wireLen: " + str(wireLen) + "; wirePos Y: " + str(wirePos[1]) + "; wirePos Z: " + str(wirePos[2]))
        
       # print("now moving to wrapped")
        # wrapped common wire segments
        wireLen = self.planeDim[2]/sin(self.wireAngle.to('radians'))
        for i in range(nSideWires):
            wirePos = [ Q('0cm'), 
                        firstWirePos[1] + (0.5 * nWires + i) * pitch[1],
                        firstWirePos[2] + order * (nWires-1) * 0.5 * pitch[2] ]
            #print("wireLen: " + str(wireLen) + "; wirePos Y: " + str(wirePos[1]) + "; wirePos Z: " + str(wirePos[2]))
            self.MakeAndPlaceWire( geom, wireNum, plane_lv, 
                                   wirePos, wireRot, wireLen )
            wireNum += 1
        
       # print("now moving to unwrapped")
        # readout corner wire segments
        for i in range(nWires):
            wireLen = self.planeDim[2]/sin(self.wireAngle.to('radians')) - ( firstWireOffset + i*pitch[2] ) / sin(self.wireAngle.to('radians'))
            
            wirePos = [ Q('0cm'), 
                        firstWirePos[1] + (0.5 * nWires + nSideWires + 0.5 * i) * pitch[1],
                        firstWirePos[2] + order * (nWires-1 + i) * 0.5 * pitch[2] ]
            #print("wireLen: " + str(wireLen) + "; wirePos Y: " + str(wirePos[1]) + "; wirePos Z: " + str(wirePos[2]))
            self.MakeAndPlaceWire( geom, wireNum, plane_lv, 
                                   wirePos, wireRot, wireLen )
            wireNum += 1
        print('DONE - Creating induction wires ('+self.view+').')
