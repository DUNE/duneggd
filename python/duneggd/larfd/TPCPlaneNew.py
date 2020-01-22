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

    def ParseExcel(self,
                   sheet_name, header, usecols,
                   filename='Electronics channel to wire segment mapping.xlsx'):
                   # filename='Aran-Sheet.xlsx'):
        self.WirePosition = pd.read_excel(filename,
                                          sheet_name=sheet_name,
                                          header=header,
                                          usecols=usecols)

        self.WirePosition.dropna(inplace = True)
        self.XStartIndex = None
        self.YStartIndex = None
        self.XEndIndex   = None
        self.YEndIndex   = None
        self.FrontOrBack = None
        newcolumns = self.WirePosition.columns.tolist()

        for i in range(len(newcolumns)):
            if (newcolumns[i].find('X'         ) is -1 and
                newcolumns[i].find('Y'         ) is -1 and
                newcolumns[i].find('Front/Back') is -1):
                self.WirePosition.drop([newcolumns[i]], axis=1, inplace=True)

        newcolumns = self.WirePosition.columns.tolist()
                
        for i in range(len(self.WirePosition.columns)):
            # pandas add a column of index at 0 so have to add 1 to the indices here
            if   self.WirePosition.columns[i] == 'X'   or self.WirePosition.columns[i] == 'X.2':
                newcolumns[i] = 'XStart'
                self.XStartIndex = i+1
            elif self.WirePosition.columns[i] == 'Y'   or self.WirePosition.columns[i] == 'Y.2':
                newcolumns[i] = 'YStart'
                self.YStartIndex = i+1
            elif self.WirePosition.columns[i] == 'X.1' or self.WirePosition.columns[i] == 'X.3':
                newcolumns[i] = 'XEnd'
                self.XEndIndex = i+1
            elif self.WirePosition.columns[i] == 'Y.1' or self.WirePosition.columns[i] == 'Y.3':
                newcolumns[i] = 'YEnd'
                self.YEndIndex = i+1
            elif self.WirePosition.columns[i].find('Front/Back') is not -1:
                newcolumns[i] = 'Front'
                self.FrontOrBack = i+1



        if (self.XStartIndex is None or
            self.YStartIndex is None or
            self.XEndIndex   is None or
            self.YEndIndex   is None or
            self.FrontOrBack is None):
            string = ("There was a problem while parsing the excel file: \""+filename+"\", sheet: \""+sheet_name+"\". Make sure the file exist in PWD and that the code in TPCPlaney is correct. Columns are:" +
                      "\nself.XStartIndex = " + str(self.XStartIndex) + 
                      "\nself.YStartIndex = " + str(self.YStartIndex) + 
                      "\nself.XEndIndex   = " + str(self.XEndIndex  ) + 
                      "\nself.YEndIndex   = " + str(self.YEndIndex  ) + 
                      "\nself.FrontOrBack = " + str(self.FrontOrBack))
            raise Exception(string)

        self.WirePosition.columns = newcolumns
        self.WirePosition['XStart'] = self.WirePosition['XStart'].astype(float) 
        self.WirePosition['YStart'] = self.WirePosition['YStart'].astype(float) 
        self.WirePosition['XEnd'  ] = self.WirePosition['XEnd'  ].astype(float) 
        self.WirePosition['YEnd'  ] = self.WirePosition['YEnd'  ].astype(float)
        self.WirePosition['Front' ] = self.WirePosition['Front' ].apply(lambda st: st.upper() == 'FRONT')
        
    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # N.B. -- the names 'volTPCPlane*' and 'volTPCWire*' are required by LArSoft
        # Define wire shape and volume
        #
        # TODO: rework configuration of frame vs phys dimensions
        #       
        # apaFameDim config: z dim includes g10 plastic, y doesn't 

        self.planeDim = list(self.APAFrameDim)
        self.planeDim[0] = self.wireDiam;
        self.PositionDumper = open("WirePos"+self.view+".txt", "w")
        if self.view == 'Z':
            self.ParseExcel(sheet_name='X Wires',header=1, usecols='E:J')
            self.planeDim[1] += - self.HeadBoardScrewCentre[1] - self.HeadAPAFrameScrewCentre[1]
            self.planeDim[2] += 2 * (-self.HeadAPAFrameScrewCentre[2] + self.HeadBoardScrewCentre[2])
            # print("X Plane Dimenstions: ", self.planeDim)
            
        if self.view == 'V':
            self.ParseExcel(sheet_name='V Wires', header=3, usecols='R:Z')
            self.planeDim[1] += 1 * self.G10ThicknessFoot - self.HeadBoardScrewCentre[1] - self.HeadAPAFrameScrewCentre[1]
            self.planeDim[2] -= self.G10ThicknessSide
            # print("Plane Dimenstions: ", self.planeDim)            

        if self.view == 'U':
            self.ParseExcel(sheet_name='U Wires', header=3, usecols='S:AA')
            self.planeDim[1] += 2 * self.G10ThicknessFoot - self.HeadBoardScrewCentre[1] - self.HeadAPAFrameScrewCentre[1]
            self.planeDim[2] -= 2 * self.G10ThicknessSide
            # print("Plane Dimenstions: ", self.planeDim, "\n")


        # define readout plane shape and volume
        #  nudge y and z dim so corners of wire endpoints fit in plane 
        readPlaneBox = geom.shapes.Box('TPCPlane' + self.view,  dx=0.5*self.planeDim[0], 
                                       dy=0.5*self.planeDim[1] + self.wireDiam,
                                       dz=0.5*self.planeDim[2] + self.wireDiam )
        readPlane_lv = geom.structure.Volume('volTPCPlane' + self.view, material='LAr', shape=readPlaneBox)

        self.add_volume(readPlane_lv)

        if not self.nowires:
            if (self.view == 'Z'):
                self.MakeCollectionPlane(geom,readPlane_lv, readPlaneBox)
            if (self.view == 'U'):
                self.MakeInductionPlane(geom,readPlane_lv, readPlaneBox)
            if (self.view == 'V'):
                self.MakeInductionPlane(geom,readPlane_lv, readPlaneBox)

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def MakeCollectionPlane( self, geom, readPlane_lv, readPlaneBox):
        print('\nCreating collection wires.')
        print(readPlaneBox)
        zwire    = geom.shapes.Tubs('TPCWire' + self.view,
                                    rmin = Q('0cm'),
                                    rmax = 0.5*self.wireDiam, 
                                    dz   = 0.5*self.planeDim[1] )
        zwire_lv = geom.structure.Volume('volTPCWireVertInner', material='CuBe', shape=zwire)

        index = 0

        maxX = Q(max(max(self.WirePosition['XStart'].values), max(self.WirePosition['XEnd'].values)), "mm")
        minX = Q(min(min(self.WirePosition['XStart'].values), min(self.WirePosition['XEnd'].values)), "mm")
        maxY = Q(max(max(self.WirePosition['YStart'].values), max(self.WirePosition['YEnd'].values)), "mm")
        minY = Q(min(min(self.WirePosition['YStart'].values), min(self.WirePosition['YEnd'].values)), "mm")
        
        dX = maxX - minX
        dY = maxY - minY

        if abs((self.planeDim[1] - dY).to('mm').magnitude) > 0.1:
            raise Exception("Inconsistent Y dim. dx: ", dY, " and y dim of the plane: ", self.planeDim[1])

        # if abs((self.planeDim[2] - dX).to('mm').magnitude) > 0.1:
        #     raise Exception("Inconsistent Z dim. dz: ", dX, " and z dim of the plane: ", self.planeDim[2])
        
        for row in self.WirePosition.itertuples():
            if row[self.FrontOrBack]:
                d = 0.5 * (Q(row[self.XStartIndex],"mm") + Q(row[self.XEndIndex],"mm"))
                wirePos = [Q('0m'),
                           Q('0m'),
                           d]
                self.PlaceWire( geom, index, readPlane_lv, wirePos, 'r90aboutX', zwire_lv )
                index += 1

        print('DONE - Creating ' + str(index)+' collection wires.')        


        
    def MakeInductionPlane(self, geom, plane_lv, readPlaneBox):
        print('\nCreating '+self.view+' wires.')

        print(readPlaneBox)


        
        degAboutX = Q(90, 'degree') + self.wireAngle
        wireRot   = geom.structure.Rotation('r'+self.view+'Wire', degAboutX, '0deg', '0deg')
        
        maxX = Q(max(max(self.WirePosition['XStart'].values), max(self.WirePosition['XEnd'].values)), "mm")
        minX = Q(min(min(self.WirePosition['XStart'].values), min(self.WirePosition['XEnd'].values)), "mm")
        maxY = Q(max(max(self.WirePosition['YStart'].values), max(self.WirePosition['YEnd'].values)), "mm")
        minY = Q(min(min(self.WirePosition['YStart'].values), min(self.WirePosition['YEnd'].values)), "mm")
        
        dX = maxX - minX
        dY = maxY - minY

        # Somehow this check isn't valid
        # if abs((self.planeDim[1] - dY).to('mm').magnitude) > 0.1:
        #     raise Exception("Inconsistent Y dim. dx: ", dY, " and y dim of the plane: ", self.planeDim[1])

        if abs((self.planeDim[2] - dX).to('mm').magnitude) > 1:
            raise Exception("Inconsistent Z dim. dz: ", dX, " and z dim of the plane: ", self.planeDim[2])
        
        wire_num = 0
        for row in self.WirePosition.itertuples():
            zstart = row[self.XStartIndex]
            ystart = row[self.YStartIndex]
            zend   = row[self.XEndIndex]  
            yend   = row[self.YEndIndex]  
            if (row[self.FrontOrBack]):
            # if (True):
                wireStartPos = [Q("0mm"),
                                Q(ystart,"mm") - self.planeDim[1]*0.5,
                                Q(zstart,"mm")]

                wireEndPos   = [Q("0mm"),
                                Q(yend,"mm") - self.planeDim[1]*0.5,
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

        print('DONE - Creating ' + str(wire_num)+' '+self.view+' wires.')
        
        self.PositionDumper.close() 
    

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def MakeAndPlaceWire( self, geom, num, plane_lv,
                          wirePos, wireRot, wireLen):

        wire    = geom.shapes.Tubs('TPCWire' + self.view + '_' + str(num), 
                                    rmin = '0cm',
                                    rmax = 0.5*self.wireDiam, 
                                    dz   = 0.5*wireLen )
        # if ((num < 430 or num>700) and self.view is 'U'):
        #     print (num, wirePos, wireLen, self.wireDiam)
        wire_lv = geom.structure.Volume('volTPCWire' + self.view + str(num)+'Inner', 
                                        material='CuBe', shape=wire)

        self.PlaceWire( geom, num, plane_lv, wirePos, wireRot, wire_lv  )

        
    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def PlaceWire( self, geom, num, plane_lv, wirePos, wireRot, wire_lv ):

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



