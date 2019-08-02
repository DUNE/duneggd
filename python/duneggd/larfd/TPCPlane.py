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
                  APAFrameDim         = None,
                  g10Thickness        = Q('0.125in'),
                  wrapCover           = Q('0.0625in'),
                  view                = None,
                  **kwds):

        if APAFrameDim is None:
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
        self.APAFrameDim        = APAFrameDim
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
        self.apaPhysicalDim = list(self.APAFrameDim)
        self.apaPhysicalDim[1] += (4*g10 + g10wrap)  # 4x from Z, V, U, gridplane
        self.APAFrameDim[2] -= (4*g10 + 2*g10wrap)  # V & U g10, and cover on both sides

        self.planeDim = list(self.APAFrameDim)
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
    def CalcWireEndPoints(self, wire_length, wire_angle, wire_position, wire_number):

        wire_length_y = wire_length * cos(self.wireAngle.to('radians'))
        wire_length_z = wire_length * sin(self.wireAngle.to('radians'))

        wire_attach_points_z = [] 
        wire_attach_points_y = []       

        if (self.view == "U"):
            wire_attach_points_z.append(wire_position[2] - (0.5 * wire_length_z))
            wire_attach_points_z.append(wire_position[2] + (0.5 * wire_length_z))
            wire_attach_points_y.append(wire_position[1] + (0.5 * wire_length_y))
            wire_attach_points_y.append(wire_position[1] - (0.5 * wire_length_y))
            
        if (self.view == "V"):
            wire_attach_points_z.append(wire_position[2] - (0.5 * wire_length_z))
            wire_attach_points_z.append(wire_position[2] + (0.5 * wire_length_z))
            wire_attach_points_y.append(wire_position[1] - (0.5 * wire_length_y))
            wire_attach_points_y.append(wire_position[1] + (0.5 * wire_length_y))
            
        words = "Wire " + str(wire_number) + " attachment positions"
        print("\n   " + words + "   ")
        print("-"*(len(words) + 6))

        print(str(wire_attach_points_z[0]) + ", \t\t" + str(wire_attach_points_y[0]))
        print(str(wire_attach_points_z[1]) + ", \t\t" + str(wire_attach_points_y[1]))

    def CalcWirePitch(self, wire_info_a, wire_info_b):
        # wire_info = [wire_length, wire_angle, wire_position, wire_number]
        # If the wire number is less than half the number of wires, base the pitch
        # on wire a to wire b.
        # If the wire number is greater than half the number of wires, base the pitch
        # on wire b to a.
        pass
    

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
        
        zwire_lv = geom.structure.Volume('volTPCWireVertInner', material='CuBe', shape=zwire)
        
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
                                        material='CuBe', shape=wire)

        self.PlaceWire( geom, num, plane_lv, wirePos, wireRot, wire_lv  )

        
    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def MakeInductionPlane(self, geom, plane_lv):
        print("="*80)
        words = "Making induction wires ("+self.view+")"
        if (len(words)%2 != 0):
            space = str(" " * int(0.5*(81 - len(words))))
        else:
            space = str(" " * int(0.5*(80 - len(words))))            
        print(space + words + space)
        print("="*80)

        pitch = [Q('0cm'),
                  self.wirePitch / sin(self.wireAngle.to('radians')),
                  self.wirePitch / cos(self.wireAngle.to('radians')) ]        

        if (self.view == "U"):
            g10 = self.g10Thickness
            firstWireOffset = Q('.55cm') + g10 + 2 * g10 * tan(self.wireAngle.to('radians')) - pitch[2]
            degAboutX       = Q(90, 'degree') + self.wireAngle
            wireRot         = geom.structure.Rotation( 'rUWire', degAboutX, '0deg','0deg'  )
            firstWirePos    = [ Q('0cm'), 
                              - 0.5*self.planeDim[1] + 0.5 * firstWireOffset / tan(self.wireAngle.to('radians')), 
                              - 0.5*self.planeDim[2] + 0.5 * firstWireOffset  ]
 
            
        if (self.view == 'V'):
            firstWireOffset = Q('0.5cm')
            degAboutX       = Q(90, 'degree') - self.wireAngle
            wireRot         = geom.structure.Rotation( 'rVWire', degAboutX, '0deg','0deg'  )
            firstWirePos    = [ Q('0cm'), 
                              - 0.5*self.planeDim[1] + 0.5 * firstWireOffset / tan(self.wireAngle.to('radians')), 
                              - 1 * (- 0.5*self.planeDim[2] + 0.5 * firstWireOffset) ]
            
        print("*"*3 + " Placing the bottom wires " + "*"*3)
        
        mid_point = [firstWirePos[0], firstWirePos[1], firstWirePos[2]] 
        wire_ends = [0, 0]
        wire_num  = 0

        
        if (self.view == "U"):
            while (mid_point[2] < 0):

                base_dist     = (0.5 * self.planeDim[2]) - abs(mid_point[2])
                wire_length   = 2 * base_dist / sin(self.wireAngle.to('radians'))
                wire_position = mid_point
                mid_point[1] += 0.5 * pitch[1]
                mid_point[2] += 0.5 * pitch[2]
                wire_ends[0] = wire_ends[1] 
                wire_ends[1] = wire_length * cos(self.wireAngle.to('radians'))
                wire_num     += 1
                self.MakeAndPlaceWire(geom, wire_num, plane_lv, wire_position, wireRot, wire_length)
                # self.CalcWireEndPoints(wire_length, self.wireAngle, mid_point, wire_num)

                
        if (self.view == "V"):
            while (mid_point[2] > 0):
                base_dist     = (0.5 * self.planeDim[2]) - abs(mid_point[2])
                wire_length   = 2 * base_dist / sin(self.wireAngle.to('radians'))
                wire_position = mid_point
                mid_point[1] += 0.5 * pitch[1]
                mid_point[2] -= 0.5 * pitch[2]
                wire_ends[0] = wire_ends[1] 
                wire_ends[1] = wire_length * cos(self.wireAngle.to('radians'))
                wire_num     += 1
                self.MakeAndPlaceWire(geom, wire_num, plane_lv, wire_position, wireRot, wire_length)

        print("*"*3 + " Placing the middle wires " + "*"*3)

        middle_wire_length = self.planeDim[2] / sin(self.wireAngle.to('radians'))
        delta              = wire_ends[1] - wire_ends[0]
        previous_mid       = [mid_point[0], mid_point[1]-(0.5*pitch[1]), mid_point[2] - (0.5*pitch[2])]
        
        base_dist          = (0.5 * self.planeDim[2]) - abs(previous_mid[2])
        wire_length        = 2 * base_dist / sin(self.wireAngle.to('radians'))
        wire_height        = wire_length * cos(self.wireAngle.to('radians'))
        next_height        = wire_height + delta
                           
        length_z           = self.planeDim[2]
        length_y           = length_z / tan(self.wireAngle.to('radians'))
                           
        new_middle         = (next_height - 0.5 * self.planeDim[1]) - (0.5 * length_y)
                           
        mid_point[1]       = new_middle
        mid_point[2]       = Q('0cm')
            
        while (mid_point[1] + (self.planeDim[2]/(2*tan(self.wireAngle.to('radians')))) < 0.5 * self.planeDim[1]):
            wire_position = mid_point
            wire_num     +=1
            self.MakeAndPlaceWire(geom, wire_num, plane_lv, wire_position, wireRot, middle_wire_length)
            mid_point[1] += wire_ends[1] - wire_ends[0]
            
        print("*"*3 + " Placing the top wires    " + "*"*3 + "\n")

        big_side_len  = self.planeDim[2] / tan(self.wireAngle.to('radians'))
        temp_center_y = (big_side_len/2) + (0.5*self.planeDim[1]) - mid_point[1]
        new_center_y  = (0.5*self.planeDim[1]) - (temp_center_y/2)
        temp_center_z = temp_center_y * tan(self.wireAngle.to('radians'))
        new_center_z  = 0.5 * (self.planeDim[2] - temp_center_z)
        mid_point[1]  = new_center_y
        mid_point[2]  = new_center_z

        if (self.view == "U"):
            while (mid_point[1] < 0.5 * self.planeDim[1]):

                base_dist     = (0.5 * self.planeDim[2]) - mid_point[2]
                wire_length   = 2 * base_dist / sin(self.wireAngle.to('radians'))
                wire_position = mid_point
                mid_point[1] += 0.5 * pitch[1]
                mid_point[2] += 0.5 * pitch[2]
                wire_num     += 1
                self.MakeAndPlaceWire(geom, wire_num, plane_lv, wire_position, wireRot, wire_length)

        if (self.view == "V"):
            while (mid_point[1] < 0.5 * self.planeDim[1]):
                base_dist     = (0.5 * self.planeDim[2]) - abs(mid_point[2])
                wire_length   = 2 * base_dist / sin(self.wireAngle.to('radians'))
                wire_position = mid_point
                mid_point[1] += 0.5 * pitch[1]
                mid_point[2] -= 0.5 * pitch[2]
                wire_num     += 1
                self.MakeAndPlaceWire(geom, wire_num, plane_lv, wire_position, wireRot, wire_length)


