#!/usr/bin/env python
'''
Subbuilder of DetEncBuilder
'''

import gegede.builder
import math
from gegede import Quantity as Q
from pint import UnitRegistry
import pandas as pd
ureg = UnitRegistry()

class CryostatBuilder(gegede.builder.Builder):
    '''
    Build the Cryostat.
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self,
                  CryostatInnerDim    = [Q('15100mm'),Q('14000mm'),Q('62000mm')],
                  cathodeThickness    = Q('0.016cm'),
                  outerAPAs           = False,
                  nAPAs               = None,
                  IgnoredAPAs         = None,
                  sideLAr             = Q('15cm'),
                  APAToFloor          = Q('49.2cm'),
                  LArLevel            = None,
                  APAToUpstreamWall   = Q('301.2cm'),
                  APAToDownstreamWall = Q('49.2cm'),
                  Layer1Thickness     = Q('0.745m'),
                  Layer2Thickness     = Q('0.045m'),
                  Layer3Thickness     = Q('0.010m'),
                  Layer1Material      = None,
                  Layer2Material      = None,
                  Layer3Material      = None,
                  DSSClearance        = None,
                  nDSSBeam            = None,
                  DSSBeamHeight       = None,
                  DSSBeamBase         = None,
                  DSSBeamThickW       = None,
                  DSSBeamThickF       = None,
                  nBeamX              = None,
                  BeamSeparationX     = None,
                  nBeamY              = None,
                  BeamSeparationY     = None,
                  nBeamZ              = None,
                  BeamSeparationZ     = None,
                  IPEBeamHeight       = None,
                  IPEBeamBase         = None,
                  IPEBeamThickW       = None,
                  IPEBeamThickF       = None,
                  IPEBeamRoofHeight   = None,
                  IPEBeamRoofBase     = None,
                  IPEBeamRoofThickW   = None,
                  IPEBeamRoofThickF   = None,
                  BeamFloors          = None,
                  BeamMaterial        = None,
                  HoleDiam            = None,
                  TopBeam             = None,
                  SteelThickness      = None,
                  FieldCageBarWidth   = None,
                  FieldCageBarHeight  = None,
                  FieldCageMaterial   = None,
                  doWaterShielding    = False,
                  waterThickness      = Q("10cm"),
                  **kwds):

        if nAPAs is None:
            raise ValueError("No value given for nAPAs")
        assert nAPAs[1] <= 2 # can only read out APAs from top or bottom, 2 levels max
        self.CryostatInnerDim     = CryostatInnerDim
        self.CryostatOuterDim     = list(self.CryostatInnerDim)
        # print ('Cryostat inner dimensions: ' + str(self.CryostatInnerDim))

        self.Layer1Thickness      = Layer1Thickness
        self.Layer2Thickness      = Layer2Thickness
        self.Layer3Thickness      = Layer3Thickness
        self.Layer1Material       = Layer1Material
        self.Layer2Material       = Layer2Material
        self.Layer3Material       = Layer3Material
        self.cathodeThickness     = cathodeThickness
        self.outerAPAs            = outerAPAs
        self.nAPAs                = nAPAs
        self.IgnoredAPAs          = IgnoredAPAs
        self.sideLAr              = sideLAr
        self.APAToFloor           = APAToFloor
        self.LArLevel             = LArLevel
        self.APAToUpstreamWall    = APAToUpstreamWall
        self.APAToDownstreamWall  = APAToDownstreamWall
        self.DSSClearance         = DSSClearance        
        self.nDSSBeam             = nDSSBeam            
        self.DSSBeamHeight        = DSSBeamHeight       
        self.DSSBeamBase          = DSSBeamBase         
        self.DSSBeamThickW        = DSSBeamThickW       
        self.DSSBeamThickF        = DSSBeamThickF       

        self.nBeamX               = nBeamX         
        self.BeamSeparationX      = BeamSeparationX
        self.nBeamY               = nBeamY         
        self.BeamSeparationY      = BeamSeparationY
        self.nBeamZ               = nBeamZ         
        self.BeamSeparationZ      = BeamSeparationZ
        self.IPEBeamHeight        = IPEBeamHeight
        self.IPEBeamBase          = IPEBeamBase  
        self.IPEBeamThickW        = IPEBeamThickW
        self.IPEBeamThickF        = IPEBeamThickF
        self.IPEBeamRoofHeight    = IPEBeamRoofHeight
        self.IPEBeamRoofBase      = IPEBeamRoofBase  
        self.IPEBeamRoofThickW    = IPEBeamRoofThickW
        self.IPEBeamRoofThickF    = IPEBeamRoofThickF
        self.BeamFloors           = BeamFloors
        self.BeamMaterial         = BeamMaterial
        self.HoleDiam             = HoleDiam
        self.TopBeam              = TopBeam
        self.SteelThickness       = SteelThickness

        self.FieldCageBarWidth    = FieldCageBarWidth
        self.FieldCageBarHeight   = FieldCageBarHeight
        self.FieldCageMaterial    = FieldCageMaterial

        self.doWaterShielding  = doWaterShielding
        self.waterThickness    = waterThickness
        


        self.tpcBldr          = self.get_builder('TPC')
        if outerAPAs:
            self.tpcOuterBldr = self.get_builder('TPCOuter')
        self.APAFrameBldr     = self.get_builder('APAFrame')
        self.volume_beam_file = open('volume_beam.txt','w') 



    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        self.APAGap_y    = self.tpcBldr.APAGap_y
        self.APAGap_z    = self.tpcBldr.APAGap_z
        self.apaFrameDim = list(self.tpcBldr.APAFrameDim)
        
        # Using volTPC dimensions, calculate module dimensions
        self.tpcDim = list(self.tpcBldr.tpcDim)
        if self.outerAPAs:
            self.tpcOuterDim = list(self.tpcOuterBldr.tpcDim)
           
        # Using module dimensions, calculate cryostat dimensions
        APAToAPA = [self.apaFrameDim[0] + 2*self.tpcDim[0] + self.cathodeThickness,
                    self.tpcDim[1],
                    self.tpcDim[2]]
        self.APAToAPA = APAToAPA

        self.ColdInsulationThickness = self.Layer1Thickness + self.Layer2Thickness + self.Layer3Thickness
        self.WarmCryostatThickness   = self.SteelThickness + self.IPEBeamHeight
        self.TotalCryoLayer          = self.ColdInsulationThickness + self.WarmCryostatThickness
        
        self.CryostatOuterDim[0] = self.CryostatInnerDim[0] + 2 * self.TotalCryoLayer
        self.CryostatOuterDim[1] = self.CryostatInnerDim[1] + 2 * self.TotalCryoLayer
        self.CryostatOuterDim[2] = self.CryostatInnerDim[2] + 2 * self.TotalCryoLayer
        
        # define cryostat shape and volume, will be placed by a builder owning this builder
        cryoBox = geom.shapes.Box('Cryostat',
                                  dx=0.5*self.CryostatOuterDim[0], 
                                  dy=0.5*self.CryostatOuterDim[1],
                                  dz=0.5*self.CryostatOuterDim[2])
        cryo_lv = geom.structure.Volume('volCryostat', material='Air', shape=cryoBox)
        self.add_volume(cryo_lv)

        LArBox = geom.shapes.Box('LiquidArgon',
                                 dx=0.5*self.CryostatInnerDim[0],
                                 dy=0.5*self.CryostatInnerDim[1],
                                 dz=0.5*self.CryostatInnerDim[2])

        
        GArDim_y = 0.5*(self.CryostatInnerDim[1] - self.LArLevel)
        GArBox = geom.shapes.Box('GaseousArgon',
                                 dx=0.5*self.CryostatInnerDim[0],
                                 dy=0.5*GArDim_y,
                                 dz=0.5*self.CryostatInnerDim[2])

        GArPos_y = 0.25*(self.CryostatInnerDim[1] - self.LArLevel) + 0.5*self.LArLevel
        GArPos   = geom.structure.Position('posGArInCryo', Q('0m'), GArPos_y, Q('0m'))
        LArBox   = geom.shapes.Boolean('subGArFromLAr',
                                       type   = 'subtraction',
                                       first  = LArBox,
                                       second = GArBox,
                                       pos    = GArPos)
        
        GAr_lv             = geom.structure.Volume('volGaseousArgon', material='GAr', shape=GArBox)
        placement_GAr_in_C = geom.structure.Placement('placeGAr_in_Cryo', volume=GAr_lv, pos=GArPos)
        cryo_lv.placements.append(placement_GAr_in_C.name)
        
        # Define the cathode volume 
        cathodeBox = geom.shapes.Box('Cathode',
                                     dx=0.5*self.cathodeThickness, 
                                     dy=0.5*self.tpcDim[1],
                                     dz=0.5*self.tpcDim[2])
        cathode_lv = geom.structure.Volume('volCathode', material='Steel', shape=cathodeBox)
        self.add_volume(cathode_lv)

        # Get the TPC volume from its builder so we can position and place it
        tpc_lv = self.tpcBldr.get_volume('volTPC')
        if self.outerAPAs:
            tpcOuter_lv = self.tpcOuterBldr.get_volume('volTPCOuter')
            APAFrame_lv = self.APAFrameBldr.get_volume('volAPAFrame')
            
        # Position both TPCs, APA Frame volumes for each module, and CPAs around 
        CPANum = 0
        APANum = 0   # 2xAPANum(+1) meant to mimic TPC numbering in LArSoft:
        
        # for i in range(3):
            # print(self.CryostatInnerDim[i] - 2*self.DSSClearance[i])
        
        betweenAPA = []
        volumesInLAr = {'position':[], 'rotation':[], 'volume':[]}

        # print(self.IPEBeamBase,self.IPEBeamHeight, self.IPEBeamThickF, self.IPEBeamThickW)    

        # ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~
        for z_i in range(self.nAPAs[2]):         # lastly z
            for y_i in range(self.nAPAs[1]):     # then in y
                cpalist = {}
                for x_i in range(self.nAPAs[0]): # increase TPC # first in x
                    
                    if self.IsIgnoredAPAs(APANum):
                        APANum += 1
                        continue
                    
                    outerAPANeg = x_i == 0               and self.outerAPAs
                    outerAPAPos = x_i == self.nAPAs[0]-1 and self.outerAPAs

                    if self.nAPAs[0]%2==1:
                        xpos = Q('0m') - ((self.nAPAs[0]-1)/2)*APAToAPA[0]                        
                    ypos = - 0.5*self.CryostatInnerDim[1] + self.APAToFloor + 0.5*self.tpcDim[1]
                    zpos = - 0.5*self.CryostatInnerDim[2] + self.APAToUpstreamWall + 0.5*self.tpcDim[2]

                    xpos += x_i*APAToAPA[0]
                    ypos += y_i*(APAToAPA[1] + self.APAGap_y)
                    zpos += z_i*(APAToAPA[2] + self.APAGap_z)
                         
                    betweenAPA.append([xpos,ypos,zpos])
                    
                    # Outer APA version needs smaller TPCs on outside
                    tpc0_lv = tpc_lv
                    tpc1_lv = tpc_lv
                    tpc0Dim = list(self.tpcDim)
                    tpc1Dim = list(self.tpcDim)
                    
                    if outerAPANeg:
                        tpc0Dim = list(self.tpcOuterDim)
                        tpc0_lv = tpcOuter_lv
                    if outerAPAPos:
                        tpc1Dim = list(self.tpcOuterDim)
                        tpc1_lv = tpcOuter_lv
                
                    # Calculate volTPC positions around module center
                    tpc0Pos  = [xpos - 0.5*self.apaFrameDim[0] - 0.5*tpc0Dim[0], ypos, zpos]
                    tpc1Pos  = [xpos + 0.5*self.apaFrameDim[0] + 0.5*tpc1Dim[0], ypos, zpos]
                    FramePos = [xpos, ypos, zpos]
                    
                    pos0Name = 'TPC-'   + str(2*APANum)     + '_in_Cryo'
                    pos1Name = 'TPC-'   + str(2*APANum + 1) + '_in_Cryo'
                    pos2Name = 'Frame-' + str(2*APANum)     + '_in_Cryo'

                    tpc0_in_cryo     = geom.structure.Position(pos0Name,  tpc0Pos[0],  tpc0Pos[1],  tpc0Pos[2])
                    tpc1_in_cryo     = geom.structure.Position(pos1Name,  tpc1Pos[0],  tpc1Pos[1],  tpc1Pos[2])
                    APAFrame_in_cryo = geom.structure.Position(pos2Name, FramePos[0], FramePos[1], FramePos[2])
                    
                    if y_i == self.nAPAs[1]-1: # readout at top, no X rotation
                        rot0 = 'identity'
                        rot1 = 'r180aboutY'
                    else:                      # otherwise put readout on bottom with 180 about X
                        rot0 = 'r180aboutX'
                        rot1 = 'r180aboutX_180aboutY'

                    # Place the TPCs, making sure to rotate the right one
                    pTPC0_in_C = geom.structure.Placement('place'+pos0Name,
                                                          volume = tpc0_lv,
                                                          pos    = tpc0_in_cryo,
                                                          rot    = rot0 )
                    pTPC1_in_C = geom.structure.Placement('place'+pos1Name,
                                                          volume = tpc1_lv,
                                                          pos    = tpc1_in_cryo,
                                                          rot    = rot1 )
                    pAPAFrame_in_C = geom.structure.Placement('place'+pos2Name,
                                                              volume = APAFrame_lv,
                                                              pos    = APAFrame_in_cryo,
                                                              rot    =rot0)

                    # Define temporary box shapes for the different objects
                    tpc0TempBox = geom.shapes.Box('TPC0_%s_%s_%s_Tempbox' % (x_i, y_i, z_i),
                                                  dx=0.5*self.tpcBldr.tpcDim[0],
                                                  dy=0.5*self.tpcBldr.tpcDim[1],
                                                  dz=0.5*self.tpcBldr.tpcDim[2])
                    tpc1TempBox = geom.shapes.Box('TPC1_%s_%s_%s_Tempbox' % (x_i, y_i, z_i),
                                                  dx=0.5*self.tpcBldr.tpcDim[0],
                                                  dy=0.5*self.tpcBldr.tpcDim[1],
                                                  dz=0.5*self.tpcBldr.tpcDim[2])
                    APATempBox  = geom.shapes.Box('APA_%s_%s_%s_Tempbox' % (x_i, y_i, z_i),
                                                  dx=0.5*self.apaFrameDim[0],
                                                  dy=0.5*self.apaFrameDim[1],
                                                  dz=0.5*self.apaFrameDim[2])

                    # Make the subtractions from the LAr Volume
                    LArBox = geom.shapes.Boolean('TPC0_%s_%s_%s_subtraction' % (x_i, y_i, z_i),
                                                 type   = 'subtraction',
                                                 first  = LArBox,
                                                 second = tpc0TempBox,
                                                 pos    = tpc0_in_cryo,
                                                 rot    = rot0)
                    
                    LArBox = geom.shapes.Boolean('TPC1_%s_%s_%s_subtraction' % (x_i, y_i, z_i),
                                                 type   = 'subtraction',
                                                 first  = LArBox,
                                                 second = tpc1TempBox,
                                                 pos    = tpc1_in_cryo,
                                                 rot    = rot1)
                    
                    LArBox = geom.shapes.Boolean('APA_%s_%s_%s_subtraction' % (x_i, y_i, z_i),
                                                 type   = 'subtraction',
                                                 first  = LArBox,
                                                 second = APATempBox,
                                                 pos    = APAFrame_in_cryo,
                                                 rot    = rot0)

                    cryo_lv.placements.append(pTPC0_in_C.name)
                    cryo_lv.placements.append(pTPC1_in_C.name)
                    cryo_lv.placements.append(pAPAFrame_in_C.name)

                    APANum += 1

                    # ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~
                    # Place steel frames and plastic around it
                    # Sould probably write a function to do this
                    # Around modCenter
                    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^

                    # place CPAs depending on outer APA configuration
                    if not outerAPANeg: 
                        cpa0Pos = ( tpc0Pos[0] - 0.5*self.tpcDim[0] - 0.5*self.cathodeThickness,
                                    ypos, zpos ) # make tuple instead of list so it can be key in a dict
                        if not cpa0Pos in cpalist: self.PlaceCPA( geom, cryo_lv, cathode_lv, CPANum, cpa0Pos, cathodeBox, LArBox )
                        cpalist[cpa0Pos] = 'moot'
                        CPANum += 1                            
                    if not outerAPAPos: 
                        cpa1Pos = ( tpc1Pos[0] + 0.5*self.tpcDim[0] + 0.5*self.cathodeThickness,
                                    ypos, zpos )
                        if not cpa1Pos in cpalist: self.PlaceCPA( geom, cryo_lv, cathode_lv, CPANum, cpa1Pos, cathodeBox, LArBox )
                        cpalist[cpa1Pos] = 'moot'
                        CPANum += 1
                  

        print ("Cryostat: Built "+str(self.nAPAs[0])
               +" wide by "+str(self.nAPAs[1])
               +" high by "+str(self.nAPAs[2])
               +" long modules.")
 
        self.beamInfo = {'shape':[], 'pos':[], 'rot':[]}

        # Adding in the field  cage
        lenHorizontalBar = self.nAPAs[2]*self.tpcDim[2] + (self.nAPAs[2]-1)*self.APAGap_z
        lenVerticalBar   = self.nAPAs[1]*self.tpcDim[1] + (self.nAPAs[1]-1)*self.APAGap_y + 2*self.FieldCageBarHeight

        # Get the center of the APA array
        xCenter = Q("0")

        yCenter = (- 0.5*self.CryostatInnerDim[1]
                   + self.APAToFloor
                   + self.apaFrameDim[1]
                   + 0.5*self.APAGap_y)
        
        zCenter = (-0.5*self.CryostatInnerDim[2]+
                   self.APAToUpstreamWall +
                   0.5*(self.nAPAs[2]*self.tpcDim[2] + (self.nAPAs[2]-1)*self.APAGap_z))

        horizontalBarBox = geom.shapes.Box("FieldCageHorizontalBar",
                                           dx=0.5*self.FieldCageBarWidth,
                                           dy=0.5*self.FieldCageBarHeight,
                                           dz=0.5*lenHorizontalBar)
        verticalBarBox   = geom.shapes.Box("FieldCageVerticalBar",
                                           dx=0.5*self.FieldCageBarWidth,
                                           dy=0.5*lenVerticalBar,
                                           dz=0.5*self.FieldCageBarHeight)

        horizontalBar_lv = geom.structure.Volume("volFieldCageHorBar", material=self.FieldCageMaterial, shape=horizontalBarBox)
        verticalBar_lv   = geom.structure.Volume("volFieldCageVerBar", material=self.FieldCageMaterial, shape=verticalBarBox  )

        yOffset = 0.5*self.APAGap_y + self.apaFrameDim[1] + 0.5*self.FieldCageBarHeight
        zOffset = 0.5*lenHorizontalBar + 0.5*self.FieldCageBarHeight

        posLong  = [Q("3cm"), yCenter, zCenter]
        posShort = [Q("3cm"), yCenter, zCenter]


        for bar in range(123):
            horizontalBarTopRPos = geom.structure.Position("TopFCRBeam_"+str(bar),
                                                            posLong[0], posLong[1]+yOffset, posLong[2])
            horizontalBarTopLPos = geom.structure.Position("TopFCLBeam_"+str(bar),
                                                           -posLong[0], posLong[1]+yOffset, posLong[2])
            horizontalBarBotRPos = geom.structure.Position("BotFCRBeam_"+str(bar),
                                                            posLong[0], posLong[1]-yOffset, posLong[2])
            horizontalBarBotLPos = geom.structure.Position("BotFCLBeam_"+str(bar),
                                                           -posLong[0], posLong[1]-yOffset, posLong[2])

            verticalBarFroRPos = geom.structure.Position("FroFCRBeam_"+str(bar),
                                                         posShort[0], posShort[1], posShort[2]+zOffset)
            verticalBarFroLPos = geom.structure.Position("FroFCLBeam_"+str(bar),
                                                         -posShort[0], posShort[1], posShort[2]+zOffset)
            verticalBarBacRPos = geom.structure.Position("BacFCRBeam_"+str(bar),
                                                         posShort[0], posShort[1], posShort[2]-zOffset)
            verticalBarBacLPos = geom.structure.Position("BacFCLBeam_"+str(bar),
                                                         -posShort[0], posShort[1], posShort[2]-zOffset)
            
            Placement_TopFCRBar = geom.structure.Placement("placeTopFCRBar_"+str(bar),
                                                           volume=horizontalBar_lv, pos=horizontalBarTopRPos)
            Placement_TopFCLBar = geom.structure.Placement("placeTopFCLBar_"+str(bar),
                                                           volume=horizontalBar_lv, pos=horizontalBarTopLPos)
            Placement_BotFCRBar = geom.structure.Placement("placeBotFCRBar_"+str(bar),
                                                           volume=horizontalBar_lv, pos=horizontalBarBotRPos)
            Placement_BotFCLBar = geom.structure.Placement("placeBotFCLBar_"+str(bar),
                                                           volume=horizontalBar_lv, pos=horizontalBarBotLPos)

            Placement_FroFCRBar = geom.structure.Placement("placeFroFCRBar_"+str(bar),
                                                           volume=verticalBar_lv, pos=verticalBarFroRPos)
            Placement_FroFCLBar = geom.structure.Placement("placeFroFCLBar_"+str(bar),
                                                           volume=verticalBar_lv, pos=verticalBarFroLPos)
            Placement_BacFCRBar = geom.structure.Placement("placeBacFCRBar_"+str(bar),
                                                           volume=verticalBar_lv, pos=verticalBarBacRPos)
            Placement_BacFCLBar = geom.structure.Placement("placeBacFCLBar_"+str(bar),
                                                           volume=verticalBar_lv, pos=verticalBarBacLPos)

            
            LArBox = geom.shapes.Boolean("subHorizFCBarTopR_"+str(bar),
                                         type   = 'subtraction',
                                         first  = LArBox,
                                         second = horizontalBarBox,
                                         pos    = horizontalBarTopRPos)
            LArBox = geom.shapes.Boolean("subHorizFCBarTopL_"+str(bar),
                                         type   = 'subtraction',
                                         first  = LArBox,
                                         second = horizontalBarBox,
                                         pos    = horizontalBarTopLPos)
            LArBox = geom.shapes.Boolean("subHorizFCBarBotR_"+str(bar),
                                         type   = 'subtraction',
                                         first  = LArBox,
                                         second = horizontalBarBox,
                                         pos    = horizontalBarBotRPos)
            LArBox = geom.shapes.Boolean("subHorizFCBarBotL_"+str(bar),
                                         type   = 'subtraction',
                                         first  = LArBox,
                                         second = horizontalBarBox,
                                         pos    = horizontalBarBotLPos)

            LArBox = geom.shapes.Boolean("subVertiFCBarFroR_"+str(bar),
                                         type   = 'subtraction',
                                         first  = LArBox,
                                         second = verticalBarBox,
                                         pos    = verticalBarFroRPos)
            LArBox = geom.shapes.Boolean("subVertiFCBarFroL_"+str(bar),
                                         type   = 'subtraction',
                                         first  = LArBox,
                                         second = verticalBarBox,
                                         pos    = verticalBarFroLPos)
            LArBox = geom.shapes.Boolean("subVertiFCBarBacR_"+str(bar),
                                         type   = 'subtraction',
                                         first  = LArBox,
                                         second = verticalBarBox,
                                         pos    = verticalBarBacRPos)
            LArBox = geom.shapes.Boolean("subVertiFCBarBacL_"+str(bar),
                                         type   = 'subtraction',
                                         first  = LArBox,
                                         second = verticalBarBox,
                                         pos    = verticalBarBacLPos)

            cryo_lv.placements.append(Placement_TopFCRBar.name)
            cryo_lv.placements.append(Placement_TopFCLBar.name)
            cryo_lv.placements.append(Placement_BotFCRBar.name)
            cryo_lv.placements.append(Placement_BotFCLBar.name)

            cryo_lv.placements.append(Placement_FroFCRBar.name)
            cryo_lv.placements.append(Placement_FroFCLBar.name)
            cryo_lv.placements.append(Placement_BacFCRBar.name)
            cryo_lv.placements.append(Placement_BacFCLBar.name)
            
            posLong [0]  += Q("6cm")
            posShort[0]  += Q("6cm")










        
        
        if (self.Layer1Thickness != None):
            self.ConstructOnion(geom, cryo_lv)
            
        if (self.nDSSBeam != None):
            self.ConstructDSS(geom, cryo_lv, self.beamInfo) 
            
        if (self.nBeamX != None):
            self.ConstructAllBeam(geom, cryo_lv)

        if (self.doWaterShielding):
            self.PlaceWaterLayer(geom, cryo_lv, self.waterThickness, self.beamInfo)
            

        LAr_lv       = geom.structure.Volume('volLArInCryo', material='LAr', shape=LArBox)
        pLAr_in_cryo = geom.structure.Position('posLArInCryo',
                                               Q('0cm'),
                                               Q('0cm'),
                                               Q('0cm'))
        placement_LAr_in_C  = geom.structure.Placement('placeLAr_in_Cryo',
                                                       volume = LAr_lv,
                                                       pos = pLAr_in_cryo)
        cryo_lv.placements.append(placement_LAr_in_C.name)


        
    def ConstructOnion(self, geom, cryo_lv):
        print ("Constructing onion cold cryostat and warm skin")
        # make and place the membranes
        Layer1In  = geom.shapes.Box("ColdCryoLayer1In",
                                    dx=0.5*self.CryostatInnerDim[0], 
                                    dy=0.5*self.CryostatInnerDim[1],
                                    dz=0.5*self.CryostatInnerDim[2])
        Layer2In  = geom.shapes.Box("ColdCryoLayer2In",
                                    dx=0.5*self.CryostatInnerDim[0]+self.Layer1Thickness, 
                                    dy=0.5*self.CryostatInnerDim[1]+self.Layer1Thickness,
                                    dz=0.5*self.CryostatInnerDim[2]+self.Layer1Thickness)
        Layer3In  = geom.shapes.Box("ColdCryoLayer3In",
                                    dx=0.5*self.CryostatInnerDim[0]+self.Layer1Thickness+self.Layer2Thickness, 
                                    dy=0.5*self.CryostatInnerDim[1]+self.Layer1Thickness+self.Layer2Thickness,
                                    dz=0.5*self.CryostatInnerDim[2]+self.Layer1Thickness+self.Layer2Thickness)
        Layer3Out = geom.shapes.Box("ColdCryoLayer3Out",
                                    dx=0.5*self.CryostatInnerDim[0]+self.Layer1Thickness+self.Layer2Thickness+self.Layer3Thickness, 
                                    dy=0.5*self.CryostatInnerDim[1]+self.Layer1Thickness+self.Layer2Thickness+self.Layer3Thickness,
                                    dz=0.5*self.CryostatInnerDim[2]+self.Layer1Thickness+self.Layer2Thickness+self.Layer3Thickness)

        
        # Cold cryostat stops here, now its the warm cryostat
        BeamInnerBox = geom.shapes.Box('BeamInner',
                                       dx=0.5*self.CryostatInnerDim[0]+self.Layer1Thickness+self.Layer2Thickness+self.Layer3Thickness+self.SteelThickness, 
                                       dy=0.5*self.CryostatInnerDim[1]+self.Layer1Thickness+self.Layer2Thickness+self.Layer3Thickness+self.SteelThickness,
                                       dz=0.5*self.CryostatInnerDim[2]+self.Layer1Thickness+self.Layer2Thickness+self.Layer3Thickness+self.SteelThickness)


        vol_cryostat = ((self.CryostatInnerDim[0]) *
                        (self.CryostatInnerDim[1]) *
                        (self.CryostatInnerDim[2]))
        
        vol_membrane = ((self.CryostatInnerDim[0]+2*self.Layer1Thickness) * 
                        (self.CryostatInnerDim[1]+2*self.Layer1Thickness) *
                        (self.CryostatInnerDim[2]+2*self.Layer1Thickness))
        
        vol_layer2 = ((self.CryostatInnerDim[0]+2*(self.Layer1Thickness+self.Layer2Thickness)) * 
                      (self.CryostatInnerDim[1]+2*(self.Layer1Thickness+self.Layer2Thickness)) *
                      (self.CryostatInnerDim[2]+2*(self.Layer1Thickness+self.Layer2Thickness)))

        vol_layer3 = ((self.CryostatInnerDim[0]+2*(self.Layer1Thickness+self.Layer2Thickness+self.Layer3Thickness)) * 
                      (self.CryostatInnerDim[1]+2*(self.Layer1Thickness+self.Layer2Thickness+self.Layer3Thickness)) *
                      (self.CryostatInnerDim[2]+2*(self.Layer1Thickness+self.Layer2Thickness+self.Layer3Thickness)))

        vol_warm_skin = ((self.CryostatInnerDim[0]+2*(self.Layer1Thickness+self.Layer2Thickness+self.Layer3Thickness+self.SteelThickness)) * 
                         (self.CryostatInnerDim[1]+2*(self.Layer1Thickness+self.Layer2Thickness+self.Layer3Thickness+self.SteelThickness)) *
                         (self.CryostatInnerDim[2]+2*(self.Layer1Thickness+self.Layer2Thickness+self.Layer3Thickness+self.SteelThickness)))
        
        self.volume_beam_file.write("membrane "+str((vol_membrane -vol_cryostat).to('m^3').magnitude)+"\n")
        self.volume_beam_file.write("layer2 "  +str((vol_layer2   -vol_membrane).to('m^3').magnitude)+"\n")
        self.volume_beam_file.write("layer3 "  +str((vol_layer3   -vol_layer2  ).to('m^3').magnitude)+"\n")
        self.volume_beam_file.write("warmskin "+str((vol_warm_skin-vol_layer3  ).to('m^3').magnitude)+"\n")


        BeamOuterBox = geom.shapes.Box('BeamOut',
                                       dx=0.5*self.CryostatOuterDim[0], 
                                       dy=0.5*self.CryostatOuterDim[1],
                                       dz=0.5*self.CryostatOuterDim[2])
        
        Layer1         = geom.shapes.Boolean('ColdCryoLayer1',
                                             type   = 'subtraction',
                                             first  = Layer2In,
                                             second = Layer1In)
        
        Layer1_lv      = geom.structure.Volume('volColdCryoLayer1', material=self.Layer1Material, shape=Layer1)
        Layer1_in_cryo = geom.structure.Position('Layer1_in_Cryo', 
                                                 Q('0cm'),Q('0cm'),Q('0cm'))
        placement_Layer1In_in_C  = geom.structure.Placement('placeLayer1_in_Cryo',
                                                            volume = Layer1_lv,
                                                            pos    = Layer1_in_cryo)
        cryo_lv.placements.append(placement_Layer1In_in_C.name)

        
        Layer2    = geom.shapes.Boolean  ('ColdCryoLayer2', type='subtraction', first=Layer3In, second=Layer2In) 
        Layer2_lv = geom.structure.Volume('volColdCryoLayer2', material=self.Layer2Material, shape=Layer2)
        Layer2_in_cryo = geom.structure.Position('Layer2_in_Cryo', 
                                                 Q('0cm'),Q('0cm'),Q('0cm'))
        placement_Layer2In_in_C  = geom.structure.Placement('placeLayer2_in_Cryo',
                                                            volume = Layer2_lv,
                                                            pos = Layer2_in_cryo)
        cryo_lv.placements.append(placement_Layer2In_in_C.name)

        Layer3    = geom.shapes.Boolean  ('ColdCryoLayer3', type='subtraction', first=Layer3Out, second=Layer3In)
        Layer3_lv = geom.structure.Volume('volColdCryoLayer3', material=self.Layer3Material, shape=Layer3)
        Layer3_in_cryo = geom.structure.Position('Layer3_in_Cryo', Q('0cm'), Q('0cm'), Q('0cm'))
        placement_Layer3_in_C  = geom.structure.Placement('placeLayer3_in_Cryo',
                                                          volume = Layer3_lv,
                                                          pos = Layer3_in_cryo)
        cryo_lv.placements.append(placement_Layer3_in_C.name)

        
        WarmSkin    = geom.shapes.Boolean  ('WarmSkin', type='subtraction', first=BeamInnerBox, second=Layer3Out) 
        WarmSkin_lv = geom.structure.Volume('volWarmSkin', material=self.Layer1Material, shape=WarmSkin)
        WarmSkin_in_cryo = geom.structure.Position("WarmSkin_in_Cryo",
                                                   Q('0m'), Q('0m'), Q('0m'))
        placement_WarmSkin_in_C = geom.structure.Placement('placeWarmSkinInBeamStruct',
                                                           volume = WarmSkin_lv,
                                                           pos = WarmSkin_in_cryo)
        cryo_lv.placements.append(placement_WarmSkin_in_C.name)
        print ("DONE - Constructing the onion cold cryostat and warm skin")

        
    def ConstructDSS(self, geom, cryo_lv, beamInfo):
         
        print ("Constructing the Detector Support Structure")
        for i in range(self.nDSSBeam):
            name="DSS"+str(i)
            DSSLength = self.CryostatInnerDim[2] - 2*self.DSSClearance[2]
            FinalSub = self.BuildBeamShape(geom, name, DSSLength,
                                           self.DSSBeamBase, self.DSSBeamHeight,
                                           self.DSSBeamThickF, self.DSSBeamThickW)
        
            pos = [(self.CryostatInnerDim[0]/2-self.DSSClearance[0])/2 * (i-(self.nDSSBeam-1)/2),
                   self.CryostatInnerDim[1]/2-self.DSSClearance[1],
                   Q("0m")]
            
            Beam_lv        = geom.structure.Volume   ('vol'+name, material='Steel', shape=FinalSub)
            Position_Beam  = geom.structure.Position ("pos"+name, pos[0], pos[1], pos[2])
            Placement_Beam = geom.structure.Placement("place"+name, volume = Beam_lv, pos=Position_Beam,
                                                      rot = 'r90aboutX_90aboutY')
            
            cryo_lv.placements.append(Placement_Beam.name)

        print ("DONE - Constructing the Detector Support Structure")

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    
    def PlaceCPA( self, geom, cryo_lv, cathode_lv, CPANum, cpaPos, cathodeBox, LArBox, **kwds):

        # CPA is more than just a cathode sheet, TODO: come back to that
        # 
        posCPAName      = 'CPA-'+ str(CPANum) + '_in_Cryo'
        cathode_in_cryo = geom.structure.Position(posCPAName, cpaPos[0], cpaPos[1], cpaPos[2])
        pCathode_in_C   = geom.structure.Placement('place'+posCPAName,
                                                   volume = cathode_lv,
                                                   pos    = cathode_in_cryo)

        LArBox = geom.shapes.Boolean('cathode_%s_subtraction_from_LAr' %CPANum,
                                     type   = 'subtraction',
                                     first  = LArBox,
                                     second = cathodeBox,
                                     pos    = cathode_in_cryo)
        
        cryo_lv.placements.append(pCathode_in_C.name)


    def IsIgnoredAPAs(self, APANum):
        for rge in self.IgnoredAPAs:
            if APANum in rge:
                return True
        return False


    def BuildBeamShape(self, geom, name, length, base, height, thickf, thickw):
        SurroundingBox = geom.shapes.Box(name+'Box',
                                         dx=0.5*height,
                                         dy=0.5*length,
                                         dz=0.5*base)
        SubBoxDim = [height-thickf*2,
                     length,
                     base/2-thickw/2]
        SubtractionBox = geom.shapes.Box(name+'SubtractionBox',
                                         dx=0.5*SubBoxDim[0], 
                                         dy=0.5*SubBoxDim[1],
                                         dz=0.5*SubBoxDim[2])
        shift = base/2 - SubBoxDim[2]/2
        Pos1 = geom.structure.Position(name+'_BeamSubPos1',
                                       Q('0m'), Q('0m'),  shift)
        Pos2 = geom.structure.Position(name+'_BeamSubPos2',
                                       Q('0m'), Q('0m'), -shift)

        FirstSub = geom.shapes.Boolean(name+"_BoolSub1",
                                       type='subtraction',
                                       first=SurroundingBox,
                                       second=SubtractionBox,
                                       pos=Pos1)
        FinalSub = geom.shapes.Boolean(name+"_Final",
                                       type='subtraction',
                                       first=FirstSub,
                                       second=SubtractionBox,
                                       pos=Pos2)

        volume = length * base * height - 2 * (SubBoxDim[0] * SubBoxDim[1] * SubBoxDim[2])
        self.volume_beam_file.write(name+" "+str(volume.to('m^3').magnitude)+"\n")
        return FinalSub
        
    def ConstructBeam(self, geom, length, pos, rot, box_lv, plane):
        name = "Beam_"+str(self.num)+plane
        FinalSub = self.BuildBeamShape(geom, name, length,
                                       self.IPEBeamBase,   self.IPEBeamHeight,
                                       self.IPEBeamThickF, self.IPEBeamThickW)
        Beam_lv       = geom.structure.Volume  ('vol'+name, material=self.BeamMaterial, shape=FinalSub)
        Position_Beam = geom.structure.Position("pos"+name, pos[0], pos[1], pos[2])
        self.beamInfo['shape'].append(FinalSub)
        self.beamInfo["pos"]  .append(Position_Beam)
        self.beamInfo["rot"]  .append(rot)
        Placement_Beam = geom.structure.Placement("place"+name,
                                                  volume = Beam_lv,
                                                  pos    = Position_Beam,
                                                  rot    = rot)
        box_lv.placements.append(Placement_Beam.name)
        self.num = self.num+1

    def ConstructBeamFloor(self, geom, length, pos, rot, box_lv, plane):
        name = "BeamFloor_"+str(self.num)+plane
        SubtractionTub = geom.shapes.Tubs(name+'SubtractionHole',
                                          rmin = Q('0cm'),
                                          rmax = 0.5*self.HoleDiam, 
                                          dz   = 0.5*self.IPEBeamThickW*2)
        Pos = geom.structure.Position(name+'_BeamSubPosHole',
                                      Q('0m'), Q('0m'),  Q('0m'))
        Beam = self.BuildBeamShape(geom, name, length,
                                   self.IPEBeamBase,   self.IPEBeamHeight,
                                   self.IPEBeamThickF, self.IPEBeamThickW)
        FinalSub = geom.shapes.Boolean(name+"_Hole",
                                       type   = 'subtraction',
                                       first  = Beam,
                                       second = SubtractionTub,
                                       pos    = Pos)
        volume=math.pi*(0.5*self.HoleDiam)**2*self.IPEBeamThickW
        self.volume_beam_file.write(name+"_hole "+str(volume.to('m^3').magnitude)+"\n")
        Beam_lv        = geom.structure.Volume   ("vol"+name, material=self.BeamMaterial, shape=FinalSub)
        Position_Beam  = geom.structure.Position ("pos"+name, pos[0], pos[1], pos[2])
        Placement_Beam = geom.structure.Placement("place"+name,
                                                  volume = Beam_lv,
                                                  pos    = Position_Beam,
                                                  rot    = rot)
        self.beamInfo['shape'].append(FinalSub)
        self.beamInfo["pos"]  .append(Position_Beam)
        self.beamInfo["rot"]  .append(rot)
        box_lv.placements.append(Placement_Beam.name)
        self.num = self.num+1

    def ConstructSmallBeam(self, geom, length, pos, rot, box_lv, plane):
        name = "BeamSmall_"+str(self.num)+plane
        FinalSub = self.BuildBeamShape(geom, name, length,
                                       self.IPEBeamRoofBase,   self.IPEBeamRoofHeight,
                                       self.IPEBeamRoofThickF, self.IPEBeamRoofThickW)
        Beam_lv = geom.structure.Volume('vol'+name, material=self.BeamMaterial, shape=FinalSub)
        Position_Beam  = geom.structure.Position("pos"+name, pos[0], pos[1], pos[2])
        Placement_Beam = geom.structure.Placement("place"+name, volume = Beam_lv, pos=Position_Beam,
                                                  rot = rot)
        self.beamInfo['shape'].append(FinalSub)        
        self.beamInfo["pos"]  .append(Position_Beam)
        self.beamInfo["rot"]  .append(rot)
        box_lv.placements.append(Placement_Beam.name)
        self.num = self.num+1


    def GetPosBeam(self,
                   x=None,
                   y=None,
                   z=None,
                   opposite=False):
        
        if x is not None:
            pos = [(self.CryostatOuterDim[0] + self.BeamInnerDim[0]) / 4,
                   Q('0m'),
                   x * self.BeamSeparationX - 0.5 * (self.nBeamX-1) * self.BeamSeparationX]
            if not opposite:
                return pos
            else:
                pos[0] = - pos[0]
                return pos
            
        if y is not None:
            pos = [Q('0m'),
                   (self.CryostatOuterDim[1] + self.BeamInnerDim[1]) / 4,
                   y * self.BeamSeparationY - 0.5 * (self.nBeamY-1) * self.BeamSeparationY]
            if not opposite:
                return pos
            else:
                pos[1] = - pos[1]
                return pos
            
        if z is not None:
            pos = [z * self.BeamSeparationZ - 0.5 * (self.nBeamZ-1) * self.BeamSeparationZ,
                   Q('0m'),
                   (self.CryostatOuterDim[2] + self.BeamInnerDim[2]) / 4]
            if not opposite:
                return pos
            else:
                pos[2] = - pos[2]
                return pos
            
    def GetPosBeamFloor(self,
                        x=None,
                        y=None,
                        z=None,
                        floor=None,
                        opposite=False):
        
        if x is not None:
            pos = self.GetPosBeam(x=x,opposite=opposite)
            return [pos[0],
                    (self.BeamFloors[floor]) - self.CryostatOuterDim[1]/2,
                    pos[2]+self.BeamSeparationX/2]
        
        if y is not None:
            pos = self.GetPosBeam(y=y,opposite=opposite)
            return [floor * self.BeamSeparationZ - 0.5 * (self.nBeamZ-1) * self.BeamSeparationZ,
                    pos[1],
                    pos[2] + self.BeamSeparationY/2]

        if z is not None:
            pos = self.GetPosBeam(z=z,opposite=opposite)
            return [pos[0]+self.BeamSeparationZ/2,
                    (self.BeamFloors[floor]) - self.CryostatOuterDim[1]/2,
                    pos[2]]
       

    def ConstructAllBeam(self, geom, box_lv):
        
        print ("Constructing all the external beams")
        self.BeamInnerDim = [self.CryostatInnerDim[0] + 2 * (self.ColdInsulationThickness + self.SteelThickness),
                             self.CryostatInnerDim[1] + 2 * (self.ColdInsulationThickness + self.SteelThickness),
                             self.CryostatInnerDim[2] + 2 * (self.ColdInsulationThickness + self.SteelThickness)]
        self.num=0

        
        for i in range(self.nBeamX):
            pos = self.GetPosBeam(x=i)
            length = self.BeamInnerDim[1]+2*self.IPEBeamHeight
            rot = 'identity'
            self.ConstructBeam(geom, length, pos, rot, box_lv, 'PosX')

            pos = self.GetPosBeam(x=i, opposite=True)
            self.ConstructBeam(geom, length, pos, rot, box_lv, 'NegX')
            for ii in range(len(self.BeamFloors)):
                posfloor = self.GetPosBeamFloor(x=i, floor=ii)
                lengthfloor = self.BeamSeparationX - self.IPEBeamBase
                rot = 'r90aboutX'
                self.ConstructBeamFloor(geom, lengthfloor, posfloor, rot, box_lv, 'PosX')
                    
                posfloor = self.GetPosBeamFloor(x=i, floor=ii, opposite=True)
                self.ConstructBeamFloor(geom, lengthfloor, posfloor, rot, box_lv, 'NegX')
                
                if i is 0:
                    posfloor = self.GetPosBeamFloor(x=-1, floor=ii)
                    self.ConstructBeamFloor(geom, lengthfloor, posfloor, rot, box_lv, 'PosX')
                    
                    posfloor = self.GetPosBeamFloor(x=-1, floor=ii, opposite=True)
                    self.ConstructBeamFloor(geom, lengthfloor, posfloor, rot, box_lv, 'NegX')
        print ("DONE - Constructing the X external beams")

        for i in range(self.nBeamY):
            pos = self.GetPosBeam(y=i)
            length = self.BeamInnerDim[0]
            rot = 'r90aboutZ'
            self.ConstructBeam(geom, length, pos, rot, box_lv, 'PosY')
            
            pos = self.GetPosBeam(y=i, opposite=True)
            self.ConstructBeam(geom, length, pos, rot, box_lv, 'NegY')
            
            for ii in range(self.nBeamZ):
                if ii in self.TopBeam:
                    posfloor = self.GetPosBeamFloor(y=i, floor=ii)
                    lengthfloor = self.BeamSeparationY-self.IPEBeamBase
                    rot = 'r90aboutX_90aboutY'
                    self.ConstructSmallBeam(geom, lengthfloor, posfloor, rot, box_lv, 'PosY')
                        
                    posfloor = self.GetPosBeamFloor(y=i, floor=ii, opposite=True)
                    self.ConstructBeamFloor(geom, lengthfloor, posfloor, rot, box_lv, 'NegY')
                                      
                    if i is 0:
                        posfloor = self.GetPosBeamFloor(y=-1, floor=ii)
                        self.ConstructSmallBeam(geom, lengthfloor, posfloor, rot, box_lv, 'PosX')
                    
                        posfloor = self.GetPosBeamFloor(y=-1, floor=ii, opposite=True)
                        self.ConstructBeamFloor(geom, lengthfloor, posfloor, rot, box_lv, 'NegX')  
        print ("DONE - Constructing the Y external beams")

        for i in range(self.nBeamZ):
            pos = self.GetPosBeam(z=i)
            length = self.BeamInnerDim[1]+2*self.IPEBeamHeight
            rot = 'r90aboutY'
            self.ConstructBeam(geom, length, pos, rot, box_lv, 'PosZ')

            pos = self.GetPosBeam(z=i,opposite=True)
            self.ConstructBeam(geom, length, pos, rot, box_lv, 'NegZ')

            for ii in range(len(self.BeamFloors)):
                posfloor = self.GetPosBeamFloor(z=i, floor=ii)
                lengthfloor = self.BeamSeparationX - self.IPEBeamBase
                rot = 'r90aboutX_90aboutZ'
                self.ConstructBeamFloor(geom, lengthfloor, posfloor, rot, box_lv, 'PosX')
           
                posfloor = self.GetPosBeamFloor(z=i, floor=ii, opposite=True)
                self.ConstructBeamFloor(geom, lengthfloor, posfloor, rot, box_lv, 'NegX')
                if i is 0:
                    posfloor = self.GetPosBeamFloor(z=-1, floor=ii)
                    self.ConstructBeamFloor(geom, lengthfloor, posfloor, rot, box_lv, 'PosX')
                    
                    posfloor = self.GetPosBeamFloor(z=-1, floor=ii, opposite=True)
                    self.ConstructBeamFloor(geom, lengthfloor, posfloor, rot, box_lv, 'NegX')  
        print ("DONE - Constructing the Z external beams")

        print ("DONE - Constructing all the external beams")


    def PlaceWaterLayer(self, geom, cryo_lv, waterThickness, beamInfo):

        self.BeamInnerDim = [self.CryostatInnerDim[0] + 2 * (self.ColdInsulationThickness + self.SteelThickness),
                             self.CryostatInnerDim[1] + 2 * (self.ColdInsulationThickness + self.SteelThickness),
                             self.CryostatInnerDim[2] + 2 * (self.ColdInsulationThickness + self.SteelThickness)]
        
        WaterBox_outer = geom.shapes.Box('WaterBox_outer',
                                         dx=0.5*(self.BeamInnerDim[0]+waterThickness),
                                         dy=0.5*(self.BeamInnerDim[1]+waterThickness),
                                         dz=0.5*(self.BeamInnerDim[2]+waterThickness))
        WaterBox_inner = geom.shapes.Box('WaterBox_inner',
                                         dx=0.5*(self.BeamInnerDim[0]),
                                         dy=0.5*(self.BeamInnerDim[1]),
                                         dz=0.5*(self.BeamInnerDim[2]))
        WaterBottomSub = geom.shapes.Box('WaterBox_lower',
                                         dx=0.5*(self.BeamInnerDim[0]+waterThickness),
                                         dy=0.5*(waterThickness                     ),
                                         dz=0.5*(self.BeamInnerDim[2]+waterThickness))
        subtractionPos = geom.structure.Position('waterPosition',
                                                 Q('0m'), Q('0m'), Q('0m'))
        bottomSubPos   = geom.structure.Position('waterBottomSubPos',
                                                 Q('0m'),
                                                 0.5*(self.BeamInnerDim[1]+waterThickness),
                                                 Q('0m'))

        bottomSubVol   = geom.shapes.Boolean('water_bottomSub',
                                             type   = 'subtraction',
                                             first  = WaterBox_outer,
                                             second = WaterBottomSub,
                                             pos    = bottomSubPos)
        
        subtractionVol = geom.shapes.Boolean('water_BoolSub',
                                             type   = 'subtraction',
                                             first  = bottomSubVol,
                                             second = WaterBox_inner,
                                             pos    = subtractionPos)

        for i in range(len(beamInfo['shape'])):

            subtractionVol = geom.shapes.Boolean('water_BoolSub_'+str(i),
                                                 type   = 'subtraction',
                                                 first  = subtractionVol,
                                                 second = beamInfo['shape'][i],
                                                 pos    = beamInfo['pos'][i],
                                                 rot    = beamInfo['rot'][i])
        
        water_lv    = geom.structure.Volume('volWaterShielding', material='Water', shape=subtractionVol)
        self.add_volume(water_lv)
        place_water = geom.structure.Placement('placeWaterShielding', volume=water_lv, pos=subtractionPos)
        cryo_lv.placements.append(place_water.name)
