#!/usr/bin/env python
'''
Subbuilder of TPCBuilder
'''

import math
import gegede.builder
from gegede import Quantity as Q
from gegede import units
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

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

    def ParseExcel(self, sheet_name, header, usecols):
        self.WirePosition = pd.read_excel('Fermi test APA_Electronics channel to wire segment mapping-FEMB-WIB-2.xlsx',
                                          sheet_name=sheet_name,
                                          header=header,
                                          usecols=usecols)

        self.XStartIndex = None
        self.YStartIndex = None
        self.XEndIndex   = None
        self.YEndIndex   = None
        self.FrontOrBack = None
            
        for i in range(len(self.WirePosition.columns)):
            print (self.WirePosition.columns[i],i)
            # pandas add a coluymn of index at 0 so have to add 1 to the indices here
            if self.WirePosition.columns[i] == 'X':
                self.XStartIndex = i+1
            elif self.WirePosition.columns[i] == 'Y':
                self.YStartIndex = i+1
            elif self.WirePosition.columns[i] == 'X.1':
                self.XEndIndex = i+1
            elif self.WirePosition.columns[i] == 'Y.1':
                self.YEndIndex = i+1
            elif self.WirePosition.columns[i] == 'Front/Back':
                self.FrontOrBack = i+1
                
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
        self.PositionDumper = open("WirePos"+self.view+".txt", "w")
        if self.view == 'Z':
            self.ParseExcel(sheet_name='X Wires',header=4, usecols='E:J')
            self.planeDim[1] += self.G10ThicknessFoot - self.HeadBoardScrewCentre[1] - self.HeadAPAFrameScrewCentre[1]
            self.planeDim[2] += 2 * (-self.HeadAPAFrameScrewCentre[2] + self.HeadBoardScrewCentre[2])

            
        if self.view == 'V':
            self.ParseExcel(sheet_name='V Wires', header=5, usecols='R:Z')
            self.planeDim[1] += 2 * self.G10ThicknessFoot - self.HeadBoardScrewCentre[1] - self.HeadAPAFrameScrewCentre[1]
            self.planeDim[2] += 2 * self.G10ThicknessSide
            

        if self.view == 'U': 
            self.ParseExcel(sheet_name='V Wires', header=5, usecols='R:Z')
            self.planeDim[1] += 3 * self.G10ThicknessFoot - self.HeadBoardScrewCentre[1] - self.HeadAPAFrameScrewCentre[1]
            self.planeDim[2] += 4 * self.G10ThicknessSide



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

        index=0
        
        for row in self.WirePosition.itertuples():
            if row[self.FrontOrBack] == 'Front':
                d = 0.5 * (Q(row[self.XStartIndex],"mm") + Q(row[self.XEndIndex],"mm"))
                wirePos = [Q('0m'),
                           Q('0m'),
                           d]
                self.PlaceWire( geom, index, readPlane_lv, wirePos, 'r90aboutX', zwire_lv )
                index += 1
        print('DONE - Creating ' + str(index)+' collection wires.')



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

        degAboutX = Q(90, 'degree') + self.wireAngle
        wireRot   = geom.structure.Rotation('r'+self.view+'Wire', degAboutX, '0deg', '0deg')
        nWires = int(0.5*self.nChannels)

        wire_num = 0
        for row in self.WirePosition.itertuples():
            try:
                zstart = float(row[self.XStartIndex])
                ystart = float(row[self.YStartIndex])
                zend   = float(row[self.XEndIndex]  )
                yend   = float(row[self.YEndIndex]  )
            except:
                print ("this wire is not going out of the board, I'm not including it in the geometry. This is expected for a few wires (6) on the induction planes")
            else :
                if row[self.FrontOrBack] == 'Front':
                    wireStartPos = [Q("0mm"),
                                    Q(ystart,"mm"),
                                    Q(zstart,"mm")]

                    wireEndPos   = [Q("0mm"),
                                    Q(yend,"mm"),
                                    Q(zend,"mm")]
                    
                    wirePos = [(wireStartPos[0] + wireEndPos[0]) * 0.5,
                               (wireStartPos[1] + wireEndPos[1]) * 0.5,
                               (wireStartPos[2] + wireEndPos[2]) * 0.5]
                    wire_length = ((wireStartPos[0]-wireEndPos[0])**2 +
                                   (wireStartPos[1]-wireEndPos[1])**2 +
                                   (wireStartPos[2]-wireEndPos[2])**2)**0.5
            
                    
                    self.PositionDumper.write(str(wire_num) + " " +
                                              str(wireStartPos[0].to('cm').magnitude) + " " +
                                              str(wireStartPos[1].to('cm').magnitude) + " " +
                                              str(wireStartPos[2].to('cm').magnitude) + " " +
                                              str(wireEndPos[0].to('cm').magnitude) + " " +
                                              str(wireEndPos[1].to('cm').magnitude) + " " + 
                                              str(wireEndPos[2].to('cm').magnitude) + "\n")
                
                    self.MakeAndPlaceWire(geom, wire_num, plane_lv, wirePos, wireRot, wire_length)
                    wire_num += 1

        self.PositionDumper.close() 
