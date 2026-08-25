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
                  WarmSkinMaterial    = None,
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
        self.CryostatInnerDim = CryostatInnerDim
        self.CryostatOuterDim     = list(self.CryostatInnerDim)

        self.Layer1Thickness      = Layer1Thickness
        self.Layer2Thickness      = Layer2Thickness
        self.Layer3Thickness      = Layer3Thickness
        self.Layer1Material       = Layer1Material
        self.Layer2Material       = Layer2Material
        self.Layer3Material       = Layer3Material
        self.WarmSkinMaterial     = WarmSkinMaterial
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

        
    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~
        # This section is just math and loading volumes
        self.ColdInsulationThickness = self.Layer1Thickness         + self.Layer2Thickness + self.Layer3Thickness
        self.WarmCryostatThickness   = self.SteelThickness          + self.IPEBeamHeight
        self.TotalCryoLayer          = self.ColdInsulationThickness + self.WarmCryostatThickness
        
        self.CryostatOuterDim[0] = self.CryostatInnerDim[0] + 2 * self.TotalCryoLayer
        self.CryostatOuterDim[1] = self.CryostatInnerDim[1] + 2 * self.TotalCryoLayer
        self.CryostatOuterDim[2] = self.CryostatInnerDim[2] + 2 * self.TotalCryoLayer

        self.APAGap_y            = self.tpcBldr.APAGap_y
        self.APAGap_z            = self.tpcBldr.APAGap_z
        self.apaFrameDim         = list(self.tpcBldr.APAFrameDim)
        
        self.tpcDim = list(self.tpcBldr.tpcDim)
        if self.outerAPAs: self.tpcOuterDim = list(self.tpcOuterBldr.tpcDim)
           
        APAToAPA = [self.apaFrameDim[0] + 2*self.tpcDim[0] + self.cathodeThickness,
                    self.tpcDim[1],
                    self.tpcDim[2]]
        self.APAToAPA = APAToAPA
        # ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~
        
        cryoBox = geom.shapes.Box('Cryostat',
                                  dx=0.5*self.CryostatOuterDim[0], 
                                  dy=0.5*self.CryostatOuterDim[1],
                                  dz=0.5*self.CryostatOuterDim[2])
        cryo_lv = geom.structure.Volume('volCryostat', material='Air', shape=cryoBox)
        self.add_volume(cryo_lv)

        # Make the GAr volume inside the cryostat
        GArBox   = geom.shapes.Box('GArBox',
                                   dx=0.5 * self.CryostatInnerDim[0],
                                   dy=0.25*(self.CryostatInnerDim[1] - self.LArLevel),
                                   dz=0.5 * self.CryostatInnerDim[2])
        GAr_lv   = geom.structure.Volume('volGaseousArgon', material='GAr', shape=GArBox)
        GArPos_y = 0.25*(self.CryostatInnerDim[1] - self.LArLevel) + 0.5*self.LArLevel
        GArPos   = geom.structure.Position('posGaseousArgon', Q('0m'), GArPos_y, Q('0m'))
        GArPla   = geom.structure.Placement('placeGaseousArgon', volume=GAr_lv, pos=GArPos)
        cryo_lv.placements.append(GArPla.name)
        
        # Make the LAr volume inside the cryostat
        LArBox = geom.shapes.Box('LArBox',
                                 dx=0.5*self.CryostatInnerDim[0], 
                                 dy=0.5*self.CryostatInnerDim[1],
                                 dz=0.5*self.CryostatInnerDim[2])
        LArBox = geom.shapes.Boolean('LArBoxMinusGArBox',
                                     type   = 'subtraction',
                                     first  = LArBox,
                                     second = GArBox,
                                     pos    = GArPos)

        # Define the cathode and TPC volumes
        CathodeBox = geom.shapes.Box('CathodeBox',
                                     dx=0.5*self.cathodeThickness, dy=0.5*self.tpcDim[1], dz=0.5*self.tpcDim[2])
        Cathode_lv = geom.structure.Volume('volCathode', material='Steel', shape=CathodeBox)
        tpc_lv     = self.tpcBldr.get_volume('volTPC')
        if self.outerAPAs:
            tpcOuter_lv = self.tpcOuterBldr.get_volume('volTPCOuter')
            APAFrame_lv = self.APAFrameBldr.get_volume('volAPAFrame')
        CPANum     = 0
        APANum     = 0

        # Recursively place the TPC things
        for z_i in range(self.nAPAs[2]):
            for y_i in range(self.nAPAs[1]):
                for x_i in range(self.nAPAs[0]):

                    if self.IsIgnoredAPAs(APANum):
                        APANum += 1
                        continue
                    
                    outerAPANeg = x_i == 0               and self.outerAPAs
                    outerAPAPos = x_i == self.nAPAs[0]-1 and self.outerAPAs

                    if self.nAPAs[0]%2==1: xpos = Q('0m') - ((self.nAPAs[0]-1)/2)*APAToAPA[0]
                    ypos = - 0.5*self.CryostatInnerDim[1] + self.APAToFloor + 0.5*self.tpcDim[1]
                    zpos = - 0.5*self.CryostatInnerDim[2] + self.APAToUpstreamWall + 0.5*self.tpcDim[2]

                    xpos += x_i*APAToAPA[0]
                    ypos += y_i*(APAToAPA[1] + self.APAGap_y)
                    zpos += z_i*(APAToAPA[2] + self.APAGap_z)

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
                        
                    # Calculate positions of all the components
                    tpc0Pos  = [xpos - 0.5*self.apaFrameDim[0] - 0.5*tpc0Dim[0], ypos, zpos]
                    tpc1Pos  = [xpos + 0.5*self.apaFrameDim[0] + 0.5*tpc1Dim[0], ypos, zpos]
                    FramePos = [xpos, ypos, zpos]
                    
                    pos0Name = 'TPC-'   + str(2*APANum)     + '_in_Cryo'
                    pos1Name = 'TPC-'   + str(2*APANum + 1) + '_in_Cryo'
                    pos2Name = 'Frame-' + str(2*APANum) + '_in_Cryo'

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
                    cryo_lv.placements.append(pTPC0_in_C.name)
                    cryo_lv.placements.append(pTPC1_in_C.name)
                    cryo_lv.placements.append(pAPAFrame_in_C.name)
                    APANum += 1




                    

        
        # Placeing the LAr last becuase there are many subtractions that must happen first
        LAr_lv = geom.structure.Volume('volLArInCryo', material="LAr", shape=LArBox)
        LArPos = geom.structure.Position('posLArInCryo', Q('0m'), Q('0m'), Q('0m'))
        LArPla = geom.structure.Placement('placeLArInCryo', volume=LAr_lv, pos=LArPos)
        cryo_lv.placements.append(LArPla.name)
        self.ConstructOnion(geom, cryo_lv)
        
    # ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~
    def ConstructOnion(self, geom, cryo_lv):
        LayerAddition1 = self.Layer1Thickness
        LayerAddition2 = self.Layer1Thickness+self.Layer2Thickness
        LayerAddition3 = self.Layer1Thickness+self.Layer2Thickness+self.Layer3Thickness
        LayerAddition4 = self.Layer1Thickness+self.Layer2Thickness+self.Layer3Thickness+self.SteelThickness

        InnerBox = geom.shapes.Box("innerBox",
                                   dx=0.5*self.CryostatInnerDim[0], 
                                   dy=0.5*self.CryostatInnerDim[1],
                                   dz=0.5*self.CryostatInnerDim[2])
        Layer1Box = geom.shapes.Box("ColdCryoLayer1",
                                    dx=0.5*self.CryostatInnerDim[0]+LayerAddition1, 
                                    dy=0.5*self.CryostatInnerDim[1]+LayerAddition1,
                                    dz=0.5*self.CryostatInnerDim[2]+LayerAddition1)
        Layer2Box = geom.shapes.Box("ColdCryoLayer2",
                                    dx=0.5*self.CryostatInnerDim[0]+LayerAddition2, 
                                    dy=0.5*self.CryostatInnerDim[1]+LayerAddition2,
                                    dz=0.5*self.CryostatInnerDim[2]+LayerAddition2)
        Layer3Box = geom.shapes.Box("ColdCryoLayer3",
                                    dx=0.5*self.CryostatInnerDim[0]+LayerAddition3, 
                                    dy=0.5*self.CryostatInnerDim[1]+LayerAddition3,
                                    dz=0.5*self.CryostatInnerDim[2]+LayerAddition3)
        Layer4Box = geom.shapes.Box("WarmCryoLayer1",
                                    dx=0.5*self.CryostatInnerDim[0]+LayerAddition4, 
                                    dy=0.5*self.CryostatInnerDim[1]+LayerAddition4,
                                    dz=0.5*self.CryostatInnerDim[2]+LayerAddition4)
        
        subPos    = geom.structure.Position('layerSubtractionPos', Q('0m'), Q('0m'), Q('0m'))

        Layer4Box = geom.shapes.Boolean("Layer4Subtraction",
                                        type   = 'subtraction',
                                        first  = Layer4Box,
                                        second = Layer3Box,
                                        pos    = subPos)
        Layer3Box = geom.shapes.Boolean("Layer3Subtraction",
                                        type   = 'subtraction',
                                        first  = Layer3Box,
                                        second = Layer2Box,
                                        pos    = subPos)
        Layer2Box = geom.shapes.Boolean("Layer2Subtraction",
                                        type   = 'subtraction',
                                        first  = Layer2Box,
                                        second = Layer1Box,
                                        pos    = subPos)
        Layer1Box = geom.shapes.Boolean("Layer1Subtraction",
                                        type   = 'subtraction',
                                        first  = Layer1Box,
                                        second = InnerBox,
                                        pos    = subPos)
        Layer1_lv = geom.structure.Volume('volColdCryoLayer1', material=self.Layer1Material,   shape=Layer1Box)
        Layer2_lv = geom.structure.Volume('volColdCryoLayer2', material=self.Layer2Material,   shape=Layer2Box)
        Layer3_lv = geom.structure.Volume('volColdCryoLayer3', material=self.Layer3Material,   shape=Layer3Box)
        Layer4_lv = geom.structure.Volume('volWarmSkin'      , material=self.WarmSkinMaterial, shape=Layer4Box)
        Layer1Pla = geom.structure.Placement('placeLayer1InCryo', volume=Layer1_lv, pos=subPos)
        Layer2Pla = geom.structure.Placement('placeLayer2InCryo', volume=Layer2_lv, pos=subPos)
        Layer3Pla = geom.structure.Placement('placeLayer3InCryo', volume=Layer3_lv, pos=subPos)
        Layer4Pla = geom.structure.Placement('placeLayer4InCryo', volume=Layer4_lv, pos=subPos)
        cryo_lv.placements.append(Layer1Pla.name)
        cryo_lv.placements.append(Layer2Pla.name)
        cryo_lv.placements.append(Layer3Pla.name)
        cryo_lv.placements.append(Layer4Pla.name)


    def IsIgnoredAPAs(self, APANum):
        for rge in self.IgnoredAPAs:
            if APANum in rge:
                return True
        return False        
