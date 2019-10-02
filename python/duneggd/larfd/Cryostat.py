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
                  HoleDiam            = None,
                  TopBeam             = None,
                  SteelThickness      = None,
                  makeWaterShield     = False,
                  waterBlocks         = False,
                  waterBoxDim         = None,
                  blockSpacing        = Q('30cm'),
                  thickness           = Q('10cm'),
                  LightPaddle_x       = Q('0.476cm'),
                  LightPaddle_y       = Q('10.16cm'),
                  LightPaddle_z       = Q('219.8425cm'),
                  nLightPaddlePerAPA  = None,
                  **kwds):

        if nAPAs is None:
            raise ValueError("No value given for nAPAs")
        assert nAPAs[1] <= 2 # can only read out APAs from top or bottom, 2 levels max
        self.CryostatInnerDim     = CryostatInnerDim
        self.CryostatOuterDim     = list(self.CryostatInnerDim)
        print ('Cryostat inner dimensions: ' + str(self.CryostatInnerDim))

        self.Layer1Thickness      = Layer1Thickness
        self.Layer2Thickness      = Layer2Thickness
        self.Layer3Thickness      = Layer3Thickness
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
        self.HoleDiam             = HoleDiam
        self.TopBeam              = TopBeam
        self.SteelThickness       = SteelThickness

        self.makeWaterShield  = makeWaterShield
        self.waterBlocks      = waterBlocks
        self.waterBoxDim      = waterBoxDim
        self.blockSpacing     = blockSpacing
        self.thickness        = thickness

        self.LightPaddle_x      = LightPaddle_x
        self.LightPaddle_y      = LightPaddle_y
        self.LightPaddle_z      = LightPaddle_z
        self.nLightPaddlePerAPA = nLightPaddlePerAPA

        if makeWaterShield and waterBoxDim is None:
            raise ValueError("No value given for waterBoxDim")

        self.tpcBldr       = self.get_builder('TPC')
        if outerAPAs:
            self.tpcOuterBldr  = self.get_builder('TPCOuter')
        self.APAFrameBldr = self.get_builder('APAFrame')

        self.LightPaddleBldr = self.get_builder('LightPaddle')
        
        self.volume_beam_file = open('volume_beam.txt','w') 



    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        self.APAGap_y             = self.tpcBldr.APAGap_y
        self.APAGap_z             = self.tpcBldr.APAGap_z
        self.LightPaddle_y        = self.LightPaddleBldr.LightPaddle_y
        self.APAFrameZSide_y      = self.LightPaddleBldr.APAFrameZSide_y
        self.apaFrameDim          = list(self.tpcBldr.apaFrameDim)
        self.PaddleYInterval      = (2*self.apaFrameDim[1] +
                                     self.APAGap_y -
                                     self.LightPaddle_y -
                                     2*self.APAFrameZSide_y) / (2*self.nLightPaddlePerAPA - 1)
        self.FrameToPaddleSpace   = (self.PaddleYInterval - self.APAGap_y)/2
        
        # Using volTPC dimensions, calculate module dimensions
        self.tpcDim = list(self.tpcBldr.tpcDim)
        if self.outerAPAs:
            self.tpcOuterDim = list(self.tpcOuterBldr.tpcDim)
           
        # Using module dimensions, calculate cryostat dimensions
        APAToAPA = [self.apaFrameDim[0] + 2*self.tpcDim[0] + self.cathodeThickness,
                    self.tpcDim[1],
                    self.tpcDim[2]]

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
                                 dy=0.5*self.LArLevel,
                                 dz=0.5*self.CryostatInnerDim[2])

        
        # define the cathode volume 
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

        LightPaddle_lv= self.LightPaddleBldr.get_volume('volLightPaddle') 

        # Position both TPCs, APA Frame volumes for each module, and CPAs around 
        CPANum = 0
        APANum = 0   # 2xAPANum(+1) meant to mimic TPC numbering in LArSoft:
        
        betweenAPA = []
        volumesInLAr = {'position':[], 'rotation':[], 'volume':[]}
        
        for z_i in range(self.nAPAs[2]):         # lastly z
            for y_i in range(self.nAPAs[1]):     # then in y
                cpalist = {}
                for x_i in range(self.nAPAs[0]): # increase TPC # first in x
                    
                    if self.IsIgnoredAPAs(APANum):
                        APANum += 1
                        continue
                    
                    outerAPANeg = x_i==0 and self.outerAPAs
                    outerAPAPos = x_i==self.nAPAs[0]-1 and self.outerAPAs

                    # Calculate first APA position
                    xpos = - 0.5*self.CryostatInnerDim[0]
                    ypos = - 0.5*self.CryostatInnerDim[1] + self.APAToFloor + 0.5*self.tpcDim[1]
                    zpos = - 0.5*self.CryostatInnerDim[2] + self.APAToUpstreamWall + 0.5*self.tpcDim[2]
                    
                    if self.outerAPAs:
                        xpos += self.tpcOuterDim[0] + 0.5*self.apaFrameDim[0]
                    else:
                        xpos += 0.5*self.cathodeThickness + self.tpcDim[0] + 0.5*self.apaFrameDim[0]

                    # all APA positions relative to first
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
                    
                    # if (x_i==0)              : print(0.5*self.CryostatInnerDim[0],tpc0Pos[0], tpc0Dim[0])
                    # if (x_i==self.nAPAs[0]-1): print(0.5*self.CryostatInnerDim[0],tpc1Pos[0], tpc1Dim[0])

                    pos0Name = 'TPC-'   + str(2*APANum)     + '_in_Cryo'
                    pos1Name = 'TPC-'   + str(2*APANum + 1) + '_in_Cryo'
                    pos2Name = 'Frame-' + str(2*APANum)     + '_in_Cryo'
                    tpc0_in_cryo = geom.structure.Position(pos0Name, tpc0Pos[0], tpc0Pos[1], tpc0Pos[2])
                    tpc1_in_cryo = geom.structure.Position(pos1Name, tpc1Pos[0], tpc1Pos[1], tpc1Pos[2])
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
                                                          pos = tpc0_in_cryo,
                                                          rot = rot0 )
                    pTPC1_in_C = geom.structure.Placement('place'+pos1Name,
                                                          volume = tpc1_lv,
                                                          pos = tpc1_in_cryo,
                                                          rot = rot1 )
                    pAPAFrame_in_C = geom.structure.Placement('place'+pos2Name,
                                                              volume = APAFrame_lv,
                                                              pos = APAFrame_in_cryo,
                                                              rot=rot0)
                    cryo_lv.placements.append(pTPC0_in_C.name)
                    cryo_lv.placements.append(pTPC1_in_C.name)
                    cryo_lv.placements.append(pAPAFrame_in_C.name)


                    # Define temporary box shapes for the different objects
                    tpc0TempBox = geom.shapes.Box('%s_%s_%s_TPC0_box' % (x_i, y_i, z_i),
                                                  dx=0.5*self.tpcBldr.tpcDim[0],
                                                  dy=0.5*self.tpcBldr.tpcDim[1],
                                                  dz=0.5*self.tpcBldr.tpcDim[2])
                    tpc1TempBox = geom.shapes.Box('%s_%s_%s_TPC1_box' % (x_i, y_i, z_i),
                                                  dx=0.5*self.tpcBldr.tpcDim[0],
                                                  dy=0.5*self.tpcBldr.tpcDim[1],
                                                  dz=0.5*self.tpcBldr.tpcDim[2])
                    APATempBox  = geom.shapes.Box('%s_%s_%s_APA_box' % (x_i, y_i, z_i),
                                                  dx=0.5*self.apaFrameDim[0],
                                                  dy=0.5*self.apaFrameDim[1],
                                                  dz=0.5*self.apaFrameDim[2])

                    # Make the subtractions from the LAr Volume
                    LArBox = geom.shapes.Boolean('%s_%s_%s_TPC0_subtraction' % (x_i, y_i, z_i),
                                                 type   = 'subtraction',
                                                 first  = LArBox,
                                                 second = tpc0TempBox,
                                                 pos    = tpc0_in_cryo,
                                                 rot    = rot0)
                    
                    LArBox = geom.shapes.Boolean('%s_%s_%s_TPC1_subtraction' % (x_i, y_i, z_i),
                                                 type   = 'subtraction',
                                                 first  = LArBox,
                                                 second = tpc1TempBox,
                                                 pos    = tpc1_in_cryo,
                                                 rot    = rot1)
                    
                    LArBox = geom.shapes.Boolean('%s_%s_%s_APA_subtraction' % (x_i, y_i, z_i),
                                                 type   = 'subtraction',
                                                 first  = LArBox,
                                                 second = APATempBox,
                                                 pos    = APAFrame_in_cryo,
                                                 rot    = rot0)

                    
                    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
                    # Place Photon Detecors
                    self.PlaceLightPaddle(geom, cryo_lv, LightPaddle_lv, xpos, ypos, zpos, APANum)

                    
                    # Place steel frames and plastic around it
                    # Sould probably write a function to do this
                    # Around modCenter
                    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^

                    # place CPAs depending on outer APA configuration
                    if not outerAPANeg: 
                        cpa0Pos = ( tpc0Pos[0] - 0.5*self.tpcDim[0] - 0.5*self.cathodeThickness,
                                    ypos, zpos ) # make tuple instead of list so it can be key in a dict
                        if not cpa0Pos in cpalist: self.PlaceCPA( geom, cryo_lv, cathode_lv, CPANum, cpa0Pos )
                        cpalist[cpa0Pos] = 'moot'
                        CPANum += 1                            
                    if not outerAPAPos: 
                        cpa1Pos = ( tpc1Pos[0] + 0.5*self.tpcDim[0] + 0.5*self.cathodeThickness,
                                    ypos, zpos )
                        if not cpa1Pos in cpalist: self.PlaceCPA( geom, cryo_lv, cathode_lv, CPANum, cpa1Pos )
                        cpalist[cpa1Pos] = 'moot'
                        CPANum += 1
                  

                    APANum += 1
                    #print("Constructed APA: " + str(APANum))

        print("Number of APAs: ", APANum)
        print ("Cryostat: Built "+str(self.nAPAs[0])
               +" wide by "+str(self.nAPAs[1])
               +" high by "+str(self.nAPAs[2])
               +" long modules.")
 
        beamInfo = {'shape':[], 'pos':[]}
        
        if (self.Layer1Thickness != None):
            self.ConstructOnion(geom, cryo_lv)

        if (self.nDSSBeam != None):
            self.ConstructDSS(geom, cryo_lv, beamInfo) 
            
        if (self.nBeamX != None):
            self.ConstructAllBeam(geom, cryo_lv)

        # r90aboutX_90aboutY

        for i in beamInfo['shape']:
            print(i)
        print('')
        for i in beamInfo['pos']:
            print(i)

        LAr_lv       = geom.structure.Volume('volLArInCryo', material='LAr', shape=LArBox)
        pLAr_in_cryo = geom.structure.Position('posLArInCryo',
                                               Q('0cm'),
                                               Q('0cm'),
                                               Q('0cm'))
        placement_LAr_in_C  = geom.structure.Placement('placeLAr_in_Cryo',
                                                       volume = LAr_lv,
                                                       pos = pLAr_in_cryo)
        cryo_lv.placements.append(placement_LAr_in_C.name)
        print('Placed the Liquid Argon volume in the cryostat')




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
        #Coldcryostat stops here, now its the warm cryostat
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
        
        Layer1 = geom.shapes.Boolean('ColdCryoLayer1', type='subtraction', first=Layer2In, second=Layer1In) 
        Layer1_lv = geom.structure.Volume('volColdCryoLayer1', material='S460ML', shape=Layer1)
        Layer1_in_cryo = geom.structure.Position('Layer1_in_Cryo', 
                                                 Q('0cm'),Q('0cm'),Q('0cm'))
        placement_Layer1In_in_C  = geom.structure.Placement('placeLayer1_in_Cryo',
                                                            volume = Layer1_lv,
                                                            pos = Layer1_in_cryo)
        cryo_lv.placements.append(placement_Layer1In_in_C.name)

        
        Layer2 = geom.shapes.Boolean('ColdCryoLayer2', type='subtraction', first=Layer3In, second=Layer2In) 
        Layer2_lv = geom.structure.Volume('volColdCryoLayer2', material='Layer2Molecule', shape=Layer2)
        Layer2_in_cryo = geom.structure.Position('Layer2_in_Cryo', 
                                                 Q('0cm'),Q('0cm'),Q('0cm'))
        placement_Layer2In_in_C  = geom.structure.Placement('placeLayer2_in_Cryo',
                                                            volume = Layer2_lv,
                                                            pos = Layer2_in_cryo)
        cryo_lv.placements.append(placement_Layer2In_in_C.name)

        
        Layer3 = geom.shapes.Boolean('ColdCryoLayer3', type='subtraction', first=Layer3Out, second=Layer3In) 
        Layer3_lv = geom.structure.Volume('volColdCryoLayer3', material='Layer3Molecule', shape=Layer3)
        Layer3_in_cryo = geom.structure.Position('Layer3_in_Cryo', 
                                                   Q('0cm'),Q('0cm'),Q('0cm'))
        placement_Layer3_in_C  = geom.structure.Placement('placeLayer3_in_Cryo',
                                                            volume = Layer3_lv,
                                                            pos = Layer3_in_cryo)
        cryo_lv.placements.append(placement_Layer3_in_C.name)

        
        WarmSkin = geom.shapes.Boolean('WarmSkin', type='subtraction', first=BeamInnerBox, second=Layer3Out) 
        WarmSkin_lv = geom.structure.Volume('volWarmSkin', material='S460ML', shape=WarmSkin)
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

            beamInfo['shape'].append(geom.shapes.Box('temp'+name,
                                                     dx=0.5*self.DSSBeamHeight,
                                                     dy=0.5*DSSLength,
                                                     dz=0.5*self.DSSBeamBase))
            beamInfo['pos']  .append(pos)

            
            #x90z90 = geom.structure.Rotation(objname="90x90z",x='90deg',z='90deg')
            Beam_lv = geom.structure.Volume('vol'+name, material='Steel', shape=FinalSub)

            Position_Beam  = geom.structure.Position("pos"+name, pos[0], pos[1], pos[2])
            Placement_Beam = geom.structure.Placement("place"+name, volume = Beam_lv, pos=Position_Beam,
                                                      rot = 'r90aboutX_90aboutY')
            cryo_lv.placements.append(Placement_Beam.name)

        print ("DONE - Constructing the Detector Support Structure")

    # $APAphys_y    = $APAFrame_y + 4*$G10thickness + $WrapCover;

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def PlaceLightPaddle(self, geom, cryo_lv, LightPaddle_lv, APACenter_x, APACenter_y, APACenter_z, APA_i):
        for i in range(0, self.nLightPaddlePerAPA):

            Paddle_y = (APACenter_y
                        - self.apaFrameDim[1]/2
                        + self.FrameToPaddleSpace
                        + self.LightPaddle_y/2 + self.APAFrameZSide_y
                        + self.PaddleYInterval * i)

            # Alternate the paddle orientations
            rot = ''
            if (i%2 == 0) : rot = 'identity'
            else               : rot = 'r180aboutY'
        
            lPos_name           = 'volOpDetSensitive_%s-%s' % (APA_i, i)
            LightPaddle_in_cryo = geom.structure.Position(lPos_name, APACenter_x, Paddle_y, APACenter_z)
            pLightPaddle_in_C   = geom.structure.Placement('place'+lPos_name,
                                                           volume = LightPaddle_lv,
                                                           pos    = LightPaddle_in_cryo)
            cryo_lv.placements.append(pLightPaddle_in_C.name)
                        

    
    def PlaceCPA( self, geom, cryo_lv, cathode_lv, CPANum, cpaPos, **kwds):

        # CPA is more than just a cathode sheet, TODO: come back to that
        # 
        posCPAName = 'CPA-'+ str(CPANum) + '_in_Cryo'
        cathode_in_cryo = geom.structure.Position(posCPAName, cpaPos[0], cpaPos[1], cpaPos[2])
        pCathode_in_C = geom.structure.Placement('place'+posCPAName,
                                                 volume = cathode_lv,
                                                 pos = cathode_in_cryo)
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
        Beam_lv = geom.structure.Volume('vol'+name, material='S460ML', shape=FinalSub)
        Position_Beam  = geom.structure.Position("pos"+name, pos[0], pos[1], pos[2])
        Placement_Beam = geom.structure.Placement("place"+name, volume = Beam_lv, pos=Position_Beam,
                                                  rot = rot)
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
                                       type='subtraction',
                                       first=Beam,
                                       second=SubtractionTub,
                                       pos=Pos)
        volume=math.pi*(0.5*self.HoleDiam)**2*self.IPEBeamThickW
        self.volume_beam_file.write(name+"_hole "+str(volume.to('m^3').magnitude)+"\n")
        Beam_lv        = geom.structure.Volume("vol"+name, material="S460ML", shape=FinalSub)
        Position_Beam  = geom.structure.Position("pos"+name, pos[0], pos[1], pos[2])
        Placement_Beam = geom.structure.Placement("place"+name, volume=Beam_lv, pos=Position_Beam,
                                                  rot=rot)
        box_lv.placements.append(Placement_Beam.name)
        self.num = self.num+1

    def ConstructSmallBeam(self, geom, length, pos, rot, box_lv, plane):
        name = "BeamSmall_"+str(self.num)+plane
        FinalSub = self.BuildBeamShape(geom, name, length,
                                       self.IPEBeamRoofBase,   self.IPEBeamRoofHeight,
                                       self.IPEBeamRoofThickF, self.IPEBeamRoofThickW)
        Beam_lv = geom.structure.Volume('vol'+name, material='S460ML', shape=FinalSub)
        Position_Beam  = geom.structure.Position("pos"+name, pos[0], pos[1], pos[2])
        Placement_Beam = geom.structure.Placement("place"+name, volume = Beam_lv, pos=Position_Beam,
                                                  rot = rot)
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

                    
    def MakeWaterShield(self, geom, detEnc_lv):
        # Build the water boxes
        waterBoxTop    = geom.shapes.Box('WaterBoxTop'   ,
                                         dx=0.5*self.detDim[0], dy=0.5*self.thickness, dz=0.5*self.detDim[2])
        waterBoxLeft   = geom.shapes.Box('WaterBoxLeft'  ,
                                         dx=0.5*self.thickness, dy=0.5*self.detDim[1], dz=0.5*self.detDim[2])
        waterBoxRight  = geom.shapes.Box('WaterBoxRight' ,
                                         dx=0.5*self.thickness, dy=0.5*self.detDim[1], dz=0.5*self.detDim[2]) 
        waterBoxFront  = geom.shapes.Box('WaterBoxFront' ,
                                         dx=0.5*self.detDim[0], dy=0.5*self.detDim[1], dz=0.5*self.thickness)
        waterBoxBack   = geom.shapes.Box('WaterBoxBack'  ,
                                         dx=0.5*self.detDim[0], dy=0.5*self.detDim[1], dz=0.5*self.thickness)
        
            # Define the logical volumes
        waterTop_lv    = geom.structure.Volume('volWaterBoxTop'   , material='Water', shape=waterBoxTop   )
        waterLeft_lv   = geom.structure.Volume('volWaterBoxLeft'  , material='Water', shape=waterBoxLeft  )
        waterRight_lv  = geom.structure.Volume('volWaterBoxRight' , material='Water', shape=waterBoxRight )
        waterFront_lv  = geom.structure.Volume('volWaterBoxFront' , material='Water', shape=waterBoxFront )
        waterBack_lv   = geom.structure.Volume('volWaterBoxBack'  , material='Water', shape=waterBoxBack  ) 
        
            # Add all of the volumes to the detector
        self.add_volume(waterTop_lv   )
        self.add_volume(waterLeft_lv  )
        self.add_volume(waterRight_lv )
        self.add_volume(waterFront_lv )
        self.add_volume(waterBack_lv  )
        
            # Work out all of the positions of the water slabs
        posName_1 = 'Water_Top_around_Enc' 
        posName_3 = 'Water_Lef_around_Enc' 
        posName_4 = 'Water_Rig_around_Enc' 
        posName_5 = 'Water_Fro_around_Enc' 
        posName_6 = 'Water_Bac_around_Enc'
            
            # Define all of the centers to place the water slabs at
        posCenter_1 = geom.structure.Position(posName_1,
                                              self.detCenter[0],
                                              self.detCenter[1] + 0.5*(self.detDim[1]+self.thickness),
                                              self.detCenter[2]) 
        posCenter_3 = geom.structure.Position(posName_3,
                                              self.detCenter[0] + 0.5*(self.detDim[0]+self.thickness),
                                              self.detCenter[1],
                                              self.detCenter[2]) 
        posCenter_4 = geom.structure.Position(posName_4,
                                              self.detCenter[0] - 0.5*(self.detDim[0]+self.thickness),
                                              self.detCenter[1],
                                              self.detCenter[2]) 
        posCenter_5 = geom.structure.Position(posName_5,
                                              self.detCenter[0],
                                              self.detCenter[1],
                                              self.detCenter[2] + 0.5*(self.detDim[2]+self.thickness)) 
        posCenter_6 = geom.structure.Position(posName_6,
                                              self.detCenter[0],
                                              self.detCenter[1],
                                              self.detCenter[2] - 0.5*(self.detDim[2]+self.thickness)) 
        
        pc_1 = geom.structure.Placement('place'+posName_1, volume=waterTop_lv   , pos=posCenter_1)
        pc_3 = geom.structure.Placement('place'+posName_3, volume=waterLeft_lv  , pos=posCenter_3)
        pc_4 = geom.structure.Placement('place'+posName_4, volume=waterRight_lv , pos=posCenter_4)
        pc_5 = geom.structure.Placement('place'+posName_5, volume=waterFront_lv , pos=posCenter_5)        
        pc_6 = geom.structure.Placement('place'+posName_6, volume=waterBack_lv  , pos=posCenter_6)
        
        detEnc_lv.placements.append(pc_1.name)
        detEnc_lv.placements.append(pc_3.name)
        detEnc_lv.placements.append(pc_4.name)
        detEnc_lv.placements.append(pc_5.name)
        detEnc_lv.placements.append(pc_6.name)

        if (self.waterBlocks):

            container_cost   = 178.00
            num_boxes_placed = 0
            LRBoxIndex       = [0, 0]
            TBBoxIndex       = [0, 0]
            FBBoxIndex       = [0, 0]

            # ^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
            # Front and back planes

            # Define the initial position, bottom middle of the front/back planes
            posX   = self.detCenter[0]
            posY   = self.detCenter[1] - (0.5 * self.detDim[1]) + self.waterBoxDim[1]
            posZ_f = self.detCenter[2] + (0.5 * self.detDim[2]) + self.waterBoxDim[0]
            posZ_b = self.detCenter[2] - (0.5 * self.detDim[2]) - self.waterBoxDim[0]

            init_posX   = self.detCenter[0]
            init_posY   = self.detCenter[1] - (0.5 * self.detDim[1]) + (self.waterBoxDim[1])
            init_posZ_f = self.detCenter[2] + (0.5 * self.detDim[2]) + (0.5 * self.waterBoxDim[0])
            init_posZ_b = self.detCenter[2] - (0.5 * self.detDim[2]) - (0.5 * self.waterBoxDim[0])



            while (posY + (0.5 * self.waterBoxDim[1]) + self.blockSpacing - init_posY < (self.detDim[1])):
                num_boxes_placed += 2
                # Place the initial boxes
                waterBoxFB_f = geom.shapes.Box(('WaterBoxFB_f_') + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                               dx = self.waterBoxDim[2],
                                               dy = self.waterBoxDim[1],
                                               dz = self.waterBoxDim[0])
                waterBoxFB_b = geom.shapes.Box(('WaterBoxFB_b_') + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                               dx = self.waterBoxDim[2],
                                               dy = self.waterBoxDim[1],
                                               dz = self.waterBoxDim[0])
                # Define the logical volumes
                waterBoxFB_lv_f = geom.structure.Volume('volWaterBoxFB_f_' + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                        material = 'Water',
                                                        shape    = waterBoxFB_f)
                waterBoxFB_lv_b = geom.structure.Volume('volWaterBoxFB_b_' + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                        material = 'Water',
                                                        shape    = waterBoxFB_b)
                # Name the positions
                posName_f   = 'Water_Box_FB_f_' + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1])
                posName_b   = 'Water_Box_FB_b_' + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1])
                # Define the positions
                posCenter_f = geom.structure.Position(posName_f, posX, posY, posZ_f)
                posCenter_b = geom.structure.Position(posName_b, posX, posY, posZ_b)
                # Define the placements
                pc_f        = geom.structure.Placement('place' + posName_f, volume=waterBoxFB_lv_f, pos=posCenter_f)
                pc_b        = geom.structure.Placement('place' + posName_b, volume=waterBoxFB_lv_b, pos=posCenter_b)
                # Add them to the placements in the detector enclosure
                detEnc_lv.placements.append(pc_f.name)
                detEnc_lv.placements.append(pc_b.name)
                # incriment the position of the box in the y-axis
                FBBoxIndex[0] += 1
                posX          += self.blockSpacing + self.waterBoxDim[2]
                
                
                while (posX - init_posX < (0.5 * self.detDim[0])):
                    num_boxes_placed += 4
                    waterBoxFB_fl = geom.shapes.Box(('WaterBoxFB_fl_') + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                    dx = self.waterBoxDim[2],
                                                    dy = self.waterBoxDim[1],
                                                    dz = self.waterBoxDim[0])
                    waterBoxFB_fr = geom.shapes.Box(('WaterBoxFB_fr_') + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                    dx = self.waterBoxDim[2],
                                                    dy = self.waterBoxDim[1],
                    dz = self.waterBoxDim[0])
                    waterBoxFB_bl = geom.shapes.Box(('WaterBoxFB_bl_') + str(-FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                    dx = self.waterBoxDim[2],
                                                    dy = self.waterBoxDim[1],
                                                    dz = self.waterBoxDim[0])                
                    waterBoxFB_br = geom.shapes.Box(('WaterBoxFB_br_') + str(-FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                    dx = self.waterBoxDim[2],
                                                    dy = self.waterBoxDim[1],
                                                    dz = self.waterBoxDim[0])
                    
                    waterBoxFB_lv_fl = geom.structure.Volume('volWaterBoxFB_fl_' + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxFB_fl)
                    waterBoxFB_lv_fr = geom.structure.Volume('volWaterBoxFB_fr_' + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxFB_fr)
                    waterBoxFB_lv_bl = geom.structure.Volume('volWaterBoxFB_bl_' + str(-FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxFB_bl)
                    waterBoxFB_lv_br = geom.structure.Volume('volWaterBoxFB_br_' + str(-FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxFB_br)
                    
                    posName_fl   = 'Water_Box_FB_fl_' + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1])
                    posName_fr   = 'Water_Box_FB_fr_' + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1])
                    posName_bl   = 'Water_Box_FB_bl_' + str(FBBoxIndex[0]) + "_" + str(-FBBoxIndex[1])
                    posName_br   = 'Water_Box_FB_br_' + str(FBBoxIndex[0]) + "_" + str(-FBBoxIndex[1])
                    
                    posCenter_fl = geom.structure.Position(posName_fl,  posX, posY, posZ_f)
                    posCenter_fr = geom.structure.Position(posName_fr, -posX, posY, posZ_f)
                    posCenter_bl = geom.structure.Position(posName_bl,  posX, posY, posZ_b)
                    posCenter_br = geom.structure.Position(posName_br, -posX, posY, posZ_b)
                    
                    pc_fl        = geom.structure.Placement('place' + posName_fl, volume=waterBoxFB_lv_fl, pos=posCenter_fl)
                    pc_fr        = geom.structure.Placement('place' + posName_fr, volume=waterBoxFB_lv_fr, pos=posCenter_fr)
                    pc_bl        = geom.structure.Placement('place' + posName_bl, volume=waterBoxFB_lv_bl, pos=posCenter_bl)
                    pc_br        = geom.structure.Placement('place' + posName_br, volume=waterBoxFB_lv_br, pos=posCenter_br)
                    
                    detEnc_lv.placements.append(pc_fl.name)
                    detEnc_lv.placements.append(pc_fr.name)
                    detEnc_lv.placements.append(pc_bl.name)
                    detEnc_lv.placements.append(pc_br.name)
                    
                    posX          += self.blockSpacing + self.waterBoxDim[2]
                    FBBoxIndex[0] += 1

                FBBoxIndex[1] += 1
                posY          += self.blockSpacing + self.waterBoxDim[1]
                posX           = init_posX


            # ^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
            # Left and right planes

            # Define the initial position, bottom middle of the left/right planes
            posX_l = self.detCenter[0] - (0.5 * self.detDim[0]) - self.waterBoxDim[0]
            posX_r = self.detCenter[0] + (0.5 * self.detDim[0]) + self.waterBoxDim[0]
            posY   = self.detCenter[1] - (0.5 * self.detDim[1]) + self.waterBoxDim[1]
            posZ   = self.detCenter[2]
            posZ_f = self.detCenter[2]
            posZ_b = self.detCenter[2]
            
            init_posX_l = self.detCenter[0] - (0.5 * self.detDim[0]) + (0.5 * self.waterBoxDim[0])
            init_posX_r = self.detCenter[0] + (0.5 * self.detDim[0]) + (0.5 * self.waterBoxDim[0])
            init_posY   = self.detCenter[1] - (0.5 * self.detDim[1]) + (self.waterBoxDim[1])
            init_posZ   = self.detCenter[2]


            while (posY + (0.5 * self.waterBoxDim[1]) + self.blockSpacing - init_posY < (self.detDim[1])):
                num_boxes_placed += 2
                # Place the initial boxes
                waterBoxLR_l = geom.shapes.Box(('WaterBoxLR_l_') + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                               dx = self.waterBoxDim[0],
                                               dy = self.waterBoxDim[1],
                                               dz = self.waterBoxDim[2])
                waterBoxLR_r = geom.shapes.Box(('WaterBoxLR_r_') + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                               dx = self.waterBoxDim[0],
                                               dy = self.waterBoxDim[1],
                                               dz = self.waterBoxDim[2])
                # Define the logical volumes
                waterBoxLR_lv_l = geom.structure.Volume('volWaterBoxLR_l_' + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                        material = 'Water',
                                                        shape    = waterBoxLR_l)
                waterBoxLR_lv_r = geom.structure.Volume('volWaterBoxLR_r_' + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                        material = 'Water',
                                                        shape    = waterBoxLR_r)
                # Name the positions
                posName_l   = 'Water_Box_LR_l_' + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1])
                posName_r   = 'Water_Box_LR_r_' + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1])
                # Define the positions
                posCenter_l = geom.structure.Position(posName_l, posX_l, posY, posZ)
                posCenter_r = geom.structure.Position(posName_r, posX_r, posY, posZ)
                # Define the placements
                pc_l        = geom.structure.Placement('place' + posName_l, volume=waterBoxLR_lv_l, pos=posCenter_l)
                pc_r        = geom.structure.Placement('place' + posName_r, volume=waterBoxLR_lv_r, pos=posCenter_r)
                # Add them to the placements in the detector enclosure
                detEnc_lv.placements.append(pc_l.name)
                detEnc_lv.placements.append(pc_r.name)
                # incriment the position of the box in the y-axis
                LRBoxIndex[0] += 1
                posZ_f        += (self.blockSpacing + self.waterBoxDim[2])
                posZ_b        -= (self.blockSpacing + self.waterBoxDim[2])
                
                while (posZ_f - init_posZ < (0.5 * self.detDim[2])):
                    num_boxes_placed += 4
                    waterBoxLR_lb = geom.shapes.Box(('WaterBoxLR_lb_') + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                    dx = self.waterBoxDim[0],
                                                    dy = self.waterBoxDim[1],
                                                    dz = self.waterBoxDim[2])
                    waterBoxLR_lf = geom.shapes.Box(('WaterBoxLR_lf_') + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                    dx = self.waterBoxDim[0],
                                                    dy = self.waterBoxDim[1],
                                                    dz = self.waterBoxDim[2])
                    waterBoxLR_rb = geom.shapes.Box(('WaterBoxLR_rb_') + str(-LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                    dx = self.waterBoxDim[0],
                                                    dy = self.waterBoxDim[1],
                                                    dz = self.waterBoxDim[2])                
                    waterBoxLR_rf = geom.shapes.Box(('WaterBoxLR_rf_') + str(-LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                    dx = self.waterBoxDim[0],
                                                    dy = self.waterBoxDim[1],
                                                    dz = self.waterBoxDim[2])
                                    
                    waterBoxLR_lv_lb = geom.structure.Volume('volWaterBoxLR_lb_' + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxLR_lb)
                    waterBoxLR_lv_lf = geom.structure.Volume('volWaterBoxLR_lf_' + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxLR_lf)
                    waterBoxLR_lv_rb = geom.structure.Volume('volWaterBoxLR_rb_' + str(-LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxLR_rb)
                    waterBoxLR_lv_rf = geom.structure.Volume('volWaterBoxLR_fr_' + str(-LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxLR_rf)
                    
                    posName_lb   = 'Water_Box_LR_lb_' + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1])
                    posName_lf   = 'Water_Box_LR_lf_' + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1])
                    posName_rb   = 'Water_Box_LR_rb_' + str(LRBoxIndex[0]) + "_" + str(-LRBoxIndex[1])
                    posName_rf   = 'Water_Box_LR_rf_' + str(LRBoxIndex[0]) + "_" + str(-LRBoxIndex[1])
                    
                    posCenter_lb = geom.structure.Position(posName_lb, posX_l, posY,  posZ_f)
                    posCenter_lf = geom.structure.Position(posName_lf, posX_l, posY,  posZ_b)
                    posCenter_rb = geom.structure.Position(posName_rb, posX_r, posY,  posZ_f)
                    posCenter_rf = geom.structure.Position(posName_rf, posX_r, posY,  posZ_b)
                    
                    pc_lb        = geom.structure.Placement('place' + posName_lb, volume=waterBoxLR_lv_lb, pos=posCenter_lb)
                    pc_lf        = geom.structure.Placement('place' + posName_lf, volume=waterBoxLR_lv_lf, pos=posCenter_lf)
                    pc_rb        = geom.structure.Placement('place' + posName_rb, volume=waterBoxLR_lv_rb, pos=posCenter_rb)
                    pc_rf        = geom.structure.Placement('place' + posName_rf, volume=waterBoxLR_lv_rf, pos=posCenter_rf)
                    
                    detEnc_lv.placements.append(pc_lb.name)
                    detEnc_lv.placements.append(pc_lf.name)
                    detEnc_lv.placements.append(pc_rb.name)
                    detEnc_lv.placements.append(pc_rf.name)
                    
                    posZ_f        += (self.blockSpacing + self.waterBoxDim[2])
                    posZ_b        -= (self.blockSpacing + self.waterBoxDim[2]) 
                    LRBoxIndex[0] += 1

                LRBoxIndex[1] += 1
                posY          += self.blockSpacing + self.waterBoxDim[1]
                posZ_f        = init_posZ 
                posZ_b        = init_posZ                  
                
            # ^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
            # Top plane
            
            # Define the initial position, bottom middle of the front/back planes
            posX   = self.detCenter[0]
            posY   = self.detCenter[1] + (0.5 * self.detDim[1]) + self.waterBoxDim[0]
            posZ_b = self.detCenter[2]
            posZ_f = self.detCenter[2]
            
            init_posX = self.detCenter[0]
            init_posY = self.detCenter[1] + (0.5 * self.detDim[1]) + (0.5 * self.waterBoxDim[0])
            init_posZ = self.detCenter[2]

            num_boxes_placed += 1
            # Place the initial box
            waterBoxTB = geom.shapes.Box(('WaterBoxTB_') + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                          dx = self.waterBoxDim[2],
                                          dy = self.waterBoxDim[0],
                                          dz = self.waterBoxDim[1])
            # Define the logical volumes
            waterBoxTB_lv = geom.structure.Volume('volWaterBoxTB_' + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                                   material = 'Water',
                                                   shape    = waterBoxTB)
            # Name the position
            posName   = 'Water_Box_TB_' + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1])
            # Define the position
            posCenter = geom.structure.Position(posName, posX, posY, posZ)
            # Define the placement
            pc        = geom.structure.Placement('place' + posName, volume=waterBoxTB_lv, pos=posCenter)
            # Add them to the placements in the detector enclosure
            detEnc_lv.placements.append(pc.name)

            # incriment the position of the box in the y-axis
            TBBoxIndex[0] += 1
            posX += self.waterBoxDim[2] + self.blockSpacing
            
            while (posX - init_posX < (0.5 * self.detDim[0])):
                num_boxes_placed += 2
                waterBoxTB_l = geom.shapes.Box(('WaterBoxTB_l_') + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                             dx = self.waterBoxDim[2],
                                             dy = self.waterBoxDim[0],
                                             dz = self.waterBoxDim[1])
                waterBoxTB_r = geom.shapes.Box(('WaterBoxTB_r') + str(-TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                             dx = self.waterBoxDim[2],
                                             dy = self.waterBoxDim[0],
                                             dz = self.waterBoxDim[1])
                waterBoxTB_lv_l = geom.structure.Volume('volWaterBoxTB_' + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                                        material = 'Water',
                                                        shape    = waterBoxTB_l)
                waterBoxTB_lv_r = geom.structure.Volume('volWaterBoxTB_' + str(-TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                                        material = 'Water',
                                                        shape    = waterBoxTB_r)
                posName_l   = 'Water_Box_TB_l_' + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1])
                posName_r   = 'Water_Box_TB_r_' + str(-TBBoxIndex[0]) + "_" + str(TBBoxIndex[1])
                posCenter_l = geom.structure.Position(posName_l,  posX, posY, posZ_f)
                posCenter_r = geom.structure.Position(posName_r, -posX, posY, posZ_f)
                pc_l        = geom.structure.Placement('place' + posName_l, volume=waterBoxTB_lv_l, pos=posCenter_l)
                pc_r        = geom.structure.Placement('place' + posName_r, volume=waterBoxTB_lv_r, pos=posCenter_r)
                detEnc_lv.placements.append(pc_l.name)
                detEnc_lv.placements.append(pc_r.name)

                posX += self.waterBoxDim[2] + self.blockSpacing
                TBBoxIndex[0] += 1

            posZ_b        += (self.waterBoxDim[1] + self.blockSpacing)
            posZ_f        -= (self.waterBoxDim[1] + self.blockSpacing)
            posX           = init_posX
            TBBoxIndex[1] += 1
            TBBoxIndex[0]  = 1            
            
            while (posZ_f - init_posZ < (0.5 * self.detDim[2])):
                num_boxes_placed += 2
                waterBoxTB_b = geom.shapes.Box(('WaterBoxTB_b_') + str(TBBoxIndex[0]) + "_" + str(-TBBoxIndex[1]),
                                             dx = self.waterBoxDim[2],
                                             dy = self.waterBoxDim[0],
                                             dz = self.waterBoxDim[1])
                waterBoxTB_f = geom.shapes.Box(('WaterBoxTB_f') + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                             dx = self.waterBoxDim[2],
                                             dy = self.waterBoxDim[0],
                                             dz = self.waterBoxDim[1])
                waterBoxTB_lv_b = geom.structure.Volume('volWaterBoxTB_b_' + str(TBBoxIndex[0]) + "_" + str(-TBBoxIndex[1]),
                                                        material = 'Water',
                                                        shape    = waterBoxTB_b)
                waterBoxTB_lv_f = geom.structure.Volume('volWaterBoxTB_f_' + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                                        material = 'Water',
                                                        shape    = waterBoxTB_f)
                posName_b   = 'Water_Box_TB_b_' + str(TBBoxIndex[0]) + "_" + str(-TBBoxIndex[1])
                posName_f   = 'Water_Box_TB_f_' + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1])
                posCenter_b = geom.structure.Position(posName_b, posX, posY, posZ_b)
                posCenter_f = geom.structure.Position(posName_f, posX, posY, posZ_f)
                pc_b        = geom.structure.Placement('place' + posName_b, volume=waterBoxTB_lv_b, pos=posCenter_b)
                pc_f        = geom.structure.Placement('place' + posName_f, volume=waterBoxTB_lv_f, pos=posCenter_f)
                detEnc_lv.placements.append(pc_b.name)
                detEnc_lv.placements.append(pc_f.name)


                # incriment the position of the box in the y-axis
                TBBoxIndex[0] = 1
                posX += self.waterBoxDim[2] + self.blockSpacing
                while (posX - init_posX < (0.5 * self.detDim[0])):
                    num_boxes_placed += 4
                    waterBoxTB_lb = geom.shapes.Box(('WaterBoxTB_lb_') + str(-TBBoxIndex[0]) + "_" + str(-TBBoxIndex[1]),
                                                   dx = self.waterBoxDim[2],
                                                   dy = self.waterBoxDim[0],
                                                   dz = self.waterBoxDim[1])
                    waterBoxTB_lf = geom.shapes.Box(('WaterBoxTB_lf_') + str(-TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                                   dx = self.waterBoxDim[2],
                                                   dy = self.waterBoxDim[0],
                                                   dz = self.waterBoxDim[1])
                    waterBoxTB_rb = geom.shapes.Box(('WaterBoxTB_rb') + str(TBBoxIndex[0]) + "_" + str(-TBBoxIndex[1]),
                                                   dx = self.waterBoxDim[2],
                                                   dy = self.waterBoxDim[0],
                                                   dz = self.waterBoxDim[1])
                    waterBoxTB_rf = geom.shapes.Box(('WaterBoxTB_rf') + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                                   dx = self.waterBoxDim[2],
                                                   dy = self.waterBoxDim[0],
                                                   dz = self.waterBoxDim[1])
                    waterBoxTB_lv_lb = geom.structure.Volume('volWaterBoxTB_lb_' + str(-TBBoxIndex[0]) + "_" + str(-TBBoxIndex[1]),
                                                            material = 'Water',
                                                            shape    = waterBoxTB_lb)
                    waterBoxTB_lv_lf = geom.structure.Volume('volWaterBoxTB_lf_' + str(-TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                                            material = 'Water',
                                                            shape    = waterBoxTB_lf)
                    waterBoxTB_lv_rb = geom.structure.Volume('volWaterBoxTB_rb_' + str(TBBoxIndex[0]) + "_" + str(-TBBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxTB_rb)
                    waterBoxTB_lv_rf = geom.structure.Volume('volWaterBoxTB_rf_' + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxTB_rf)
                    posName_lb   = 'Water_Box_TB_lb_' + str(-TBBoxIndex[0]) + "_" + str(-TBBoxIndex[1])
                    posName_lf   = 'Water_Box_TB_lf_' + str(-TBBoxIndex[0]) + "_" + str(TBBoxIndex[1])
                    posName_rb   = 'Water_Box_TB_rb_' + str(TBBoxIndex[0]) + "_" + str(-TBBoxIndex[1])
                    posName_rf   = 'Water_Box_TB_rf_' + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1])
                    posCenter_lb = geom.structure.Position(posName_lb, -posX, posY, posZ_b)
                    posCenter_lf = geom.structure.Position(posName_lf, -posX, posY, posZ_f)
                    posCenter_rb = geom.structure.Position(posName_rb, posX, posY, posZ_b)
                    posCenter_rf = geom.structure.Position(posName_rf, posX, posY, posZ_f)
                    pc_lb        = geom.structure.Placement('place' + posName_lb, volume=waterBoxTB_lv_lb, pos=posCenter_lb)
                    pc_lf        = geom.structure.Placement('place' + posName_lf, volume=waterBoxTB_lv_lf, pos=posCenter_lf)
                    pc_rb        = geom.structure.Placement('place' + posName_rb, volume=waterBoxTB_lv_rb, pos=posCenter_rb)
                    pc_rf        = geom.structure.Placement('place' + posName_rf, volume=waterBoxTB_lv_rf, pos=posCenter_rf)
                    detEnc_lv.placements.append(pc_lb.name)
                    detEnc_lv.placements.append(pc_lf.name)
                    detEnc_lv.placements.append(pc_rb.name)
                    detEnc_lv.placements.append(pc_rf.name)

                    posX += self.waterBoxDim[2]+ self.blockSpacing
                    TBBoxIndex[0] += 1

                posX = self.detCenter[0]
                posZ_f += (self.waterBoxDim[1] + self.blockSpacing)
                posZ_b -= (self.waterBoxDim[1] + self.blockSpacing)
                TBBoxIndex[1] += 1



            print('='*80)
            words = 'number of boxes placed: ' + str(num_boxes_placed)
            if (len(words)%2 == 0):
                space = (80 - len(words)) / 2
            else:
                space = (81 - len(words)) / 2
            print(' '*space + str(words) + ' '*space)
            # print(' '*space + 'Cost of boxes: $' + str(container_cost * num_boxes_placed / 1000000) + "M")
            print('='*80)
