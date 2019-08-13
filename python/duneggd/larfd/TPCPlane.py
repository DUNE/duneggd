#!/usr/bin/env python
'''
Subbuilder of TPCBuilder
'''

from math import cos, sin, tan, sqrt, pow
import gegede.builder
from gegede import Quantity as Q
from gegede import units

class TPCPlaneBuilder(gegede.builder.Builder):
    '''
    Build the TPCPlane.
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, 
                  wireDiam                = None,
                  wirePitch               = None,
                  wireAngle               = None,
                  nChannels               = None,
                  nowires                 = None,
                  APAFrameDim             = None,
                  G10ThicknessFoot        = None,
                  G10ThicknessSide        = None,
                  HeadBoardScrewCentre    = None,
                  HeadAPAFrameScrewCentre = None,
                  SideWrappingBoardOffset = None,
                  SideBoardScrewCentre    = None,
                  SideAPAFrameScrewCentre = None,
                  wrapCover               = None,
                  view                    = None,
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

        self.wireDiam                = wireDiam
        self.wirePitch               = wirePitch
        self.wireAngle               = wireAngle
        self.nChannels               = nChannels
        self.nowires                 = nowires
        self.APAFrameDim             = APAFrameDim
        self.G10ThicknessFoot        = G10ThicknessFoot
        self.G10ThicknessSide        = G10ThicknessSide
        self.HeadBoardScrewCentre    = HeadBoardScrewCentre
        self.HeadAPAFrameScrewCentre = HeadAPAFrameScrewCentre 
        self.SideWrappingBoardOffset = SideWrappingBoardOffset
        self.SideBoardScrewCentre    = SideBoardScrewCentre
        self.SideAPAFrameScrewCentre = SideAPAFrameScrewCentre 
        self.wrapCover               = wrapCover
        self.view                    = view

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # N.B. -- the names 'volTPCPlane*' and 'volTPCWire*' are required by LArSoft
        # Define wire shape and volume
        #
        # TODO: fix material
        #
        #
        # TODO: rework configuration of frame vs phys dimensions
        #       
        # apaFameDim config: z dim includes g10 plastic, y doesn't 
        self.planeDim = list(self.APAFrameDim)
        self.planeDim[0] = self.wireDiam;
        self.FirstWireStartPos = list(self.APAFrameDim)
        self.FirstSideWireStartPos = list(self.APAFrameDim)
        self.PositionDumper = open("WirePos"+self.view+".txt", "w")
        if self.view == 'Z':
            # Extra length at the foot, less from the bottom with the board shadoing the wires
            # use the central left screw to calculate this
            # 8760104 for the board and 8760012 for the head frame beam
            self.planeDim[1] += self.G10ThicknessFoot - self.HeadBoardScrewCentre[1] - self.HeadAPAFrameScrewCentre[1]
            self.planeDim[2] += 2 * (-self.HeadAPAFrameScrewCentre[2] + self.HeadBoardScrewCentre[2])
            self.FirstWireStartPos[0] = Q('0m')
            self.FirstWireStartPos[1] = -self.planeDim[1] / 2
            self.FirstWireStartPos[2] = -self.planeDim[2] / 2

            
        if self.view == 'V': 
            self.planeDim[1] += 2 * self.G10ThicknessFoot - self.HeadBoardScrewCentre[1] - self.HeadAPAFrameScrewCentre[1]
            self.planeDim[2] += 2 * self.G10ThicknessSide
            machined = (- Q('5801.0mm') + self.APAFrameDim[1] - Q('116.60mm') - Q('167.40mm')) / 2
            print ("machined "+ str(machined))
            self.yClearance = -Q('136.00mm') - Q('11.08mm') + Q('32.7mm') - machined
            print ("clearance " + str(self.yClearance))
            self.FirstWireStartPos[0] = Q('0m')
            self.FirstWireStartPos[1] = -self.planeDim[1] / 2
            self.FirstWireStartPos[2] = -self.APAFrameDim[2] / 2 + self.HeadAPAFrameScrewCentre[2] - self.HeadBoardScrewCentre[2]
            

        if self.view == 'U': 
            self.planeDim[1] += 3 * self.G10ThicknessFoot - self.HeadBoardScrewCentre[1] - self.HeadAPAFrameScrewCentre[1]
            self.planeDim[2] += 4 * self.G10ThicknessSide
            machined = (- Q('5801.0mm') + self.APAFrameDim[1] - Q('116.60mm') - Q('167.40mm')) / 2
            print ("machined "+ str(machined))
            self.yClearance = -Q('136.00mm') - Q('11.08mm') + Q('32.7mm') - machined
            print ("clearance " + str(self.yClearance))
            self.FirstWireStartPos[0] = Q('0m')
            self.FirstWireStartPos[1] = -self.planeDim[1] / 2
            self.FirstWireStartPos[2] = -(-self.APAFrameDim[2] / 2 + self.HeadAPAFrameScrewCentre[2] - self.HeadBoardScrewCentre[2])

        print("planeDim " + str(self.planeDim))
        print("FirstWireStartPos "+str(self.FirstWireStartPos))


        # define readout plane shape and volume
        #  nudge y and z dim so corners of wire endpoints fit in plane 
        readPlaneBox = geom.shapes.Box('TPCPlane' + self.view,  dx=0.5*self.planeDim[0], 
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
            wirePos = [ Q('0cm'), Q('0cm'), self.FirstWireStartPos[2] + i*self.wirePitch ]
            self.PlaceWire( geom, i, readPlane_lv, wirePos, 'r90aboutX', zwire_lv )
        print('DONE - Creating ' + str(nWires)+' collection wires.')



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
                 self.wirePitch / cos(self.wireAngle.to('radians'))]

        print("*"*3 + " Placing the bottom wires " + "*"*3)
        increment=0
        if self.view == 'V':
            increment=1
        else:
            increment=-1
        degAboutX = Q(90, 'degree') - increment*self.wireAngle
        wireRot   = geom.structure.Rotation('r'+self.view+'Wire', degAboutX, '0deg', '0deg')
        nWires = int(0.5*self.nChannels)

        wire_num = 0
        nwirebottom = 0

        FirstWireEndPos = [self.FirstWireStartPos[0],
                           self.FirstWireStartPos[1] + (self.planeDim[2]*0.5 - increment*self.FirstWireStartPos[2]) / tan(self.wireAngle.to('radians')),
                           increment*self.planeDim[2]/2]

        for i in range(nWires):
            wireStartPos = [self.FirstWireStartPos[0],
                            self.FirstWireStartPos[1],
                            self.FirstWireStartPos[2] + increment*i*pitch[2]]

            wireEndPos = [wireStartPos[0],
                          self.FirstWireStartPos[1] + (self.planeDim[2]*0.5 - increment*wireStartPos[2]) / tan(self.wireAngle.to('radians')),
                          increment*self.planeDim[2]/2]
            wire_length = ((wireEndPos[0] - wireStartPos[0])**2 +
                           (wireEndPos[1] - wireStartPos[1])**2 +
                           (wireEndPos[2] - wireStartPos[2])**2)**0.5

            wire_position = list(wireStartPos)
            
            wire_position[0] = (wireEndPos[0] + wireStartPos[0]) / 2
            wire_position[1] = (wireEndPos[1] + wireStartPos[1]) / 2
            wire_position[2] = (wireEndPos[2] + wireStartPos[2]) / 2
            self.PositionDumper.write(str(wire_num) + " " +
                                      str(wireStartPos[0].to('cm').magnitude) + " " +
                                      str(wireStartPos[1].to('cm').magnitude) + " " +
                                      str(wireStartPos[2].to('cm').magnitude) + " " +
                                      str(wireEndPos[0].to('cm').magnitude) + " " +
                                      str(wireEndPos[1].to('cm').magnitude) + " " + 
                                      str(wireEndPos[2].to('cm').magnitude) + "\n")

            self.MakeAndPlaceWire(geom, wire_num, plane_lv, wire_position, wireRot, wire_length)
            wire_num    += 1
            nwirebottom += 1

        print("... placed "+ str(nwirebottom) + " wires.")
        endofplane = False
        # take "advantage" of the wraping here.
        # the end of the last wire will be the next one + a tiny offset visible
        # in 8760024 (the first wire pins are not *exactly* horizontal)
        # of course you have to be very careful of the orientation of the board!
        wireStartPos = [FirstWireEndPos[0],
                        FirstWireEndPos[1],
                        FirstWireEndPos[2]]
        print (wireStartPos)
        print("*"*3 + " Placing the middle wires " + "*"*3)

        nwiremiddle=0

        while (not endofplane):
            wireStartPos = [wireStartPos[0],
                            wireStartPos[1] + pitch[1],
                            wireStartPos[2]]
            if (wireEndPos[1] <= -0.5*self.APAFrameDim[1] + Q('6in') + self.yClearance):
                print("this wire goes too low")
                
            if (wireStartPos[1] >= 0.5*self.APAFrameDim[1] - Q('4in') - self.yClearance):
                endofplane = True
                break

            wireEndPos = [wireStartPos[0],
                          wireStartPos[1] - self.planeDim[2] / tan(self.wireAngle.to('rad')),
                          - self.planeDim[2]/2]
            
            wire_length = ((wireEndPos[0] - wireStartPos[0])**2 +
                           (wireEndPos[1] - wireStartPos[1])**2 +
                           (wireEndPos[2] - wireStartPos[2])**2)**0.5

            wire_position = list(wireStartPos)
                
            wire_position[0] = (wireEndPos[0] + wireStartPos[0]) / 2
            wire_position[1] = (wireEndPos[1] + wireStartPos[1]) / 2
            wire_position[2] = (wireEndPos[2] + wireStartPos[2]) / 2

            self.PositionDumper.write(str(wire_num) + " " +
                                      str(wireStartPos[0].to('cm').magnitude) + " " +
                                      str(wireStartPos[1].to('cm').magnitude) + " " +
                                      str(wireStartPos[2].to('cm').magnitude) + " " +
                                      str(wireEndPos[0].to('cm').magnitude) + " " +
                                      str(wireEndPos[1].to('cm').magnitude) + " " + 
                                      str(wireEndPos[2].to('cm').magnitude) + "\n")
            self.MakeAndPlaceWire(geom, wire_num, plane_lv, wire_position, wireRot, wire_length)
            wire_num    += 1
            nwiremiddle += 1

        print("... placed "+ str(nwiremiddle) + " wires.")

        print("*"*3 + " Placing the top wires    " + "*"*3)

        endofplane = False
        nwiretop = 0
            
        # here continue to add the wires from the left end by increasing y
        # not the pitch as already be added from the while loop
        wireStartPos = [wireEndPos[0],
                        wireEndPos[1],
                        wireEndPos[2]]
        # for i in range(nWires):
        while(not endofplane):
            wireStartPos = [wireStartPos[0],
                            wireStartPos[1] + pitch[1],
                            wireStartPos[2]]
            wireEndPos = [wireStartPos[0],
                          self.planeDim[1] / 2,
                          -self.planeDim[2] / 2 + (self.planeDim[1] / 2 - wireStartPos[1]) * tan(self.wireAngle.to('rad'))]

            if (wireStartPos[2] >= wireEndPos[2]):
                endofplane = True
                break
            
            wire_length = ((wireEndPos[0] - wireStartPos[0])**2 +
                           (wireEndPos[1] - wireStartPos[1])**2 +
                           (wireEndPos[2] - wireStartPos[2])**2)**0.5

            wire_position = list(wireStartPos)
                
            wire_position[0] = (wireEndPos[0] + wireStartPos[0]) / 2
            wire_position[1] = (wireEndPos[1] + wireStartPos[1]) / 2
            wire_position[2] = (wireEndPos[2] + wireStartPos[2]) / 2

            self.PositionDumper.write(str(wire_num) + " " +
                                 str(wireStartPos[0].to('cm').magnitude) + " " +
                                 str(wireStartPos[1].to('cm').magnitude) + " " +
                                 str(wireStartPos[2].to('cm').magnitude) + " " +
                                 str(wireEndPos[0].to('cm').magnitude) + " " +
                                 str(wireEndPos[1].to('cm').magnitude) + " " + 
                                 str(wireEndPos[2].to('cm').magnitude) + "\n")
            self.MakeAndPlaceWire(geom, wire_num, plane_lv, wire_position, wireRot, wire_length)
            wire_num += 1
            nwiretop += 1
        print("... placed "+ str(nwiretop) + " wires.")
        self.PositionDumper.close() 
