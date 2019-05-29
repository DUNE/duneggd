#!/usr/bin/env python
'''
Subbuilder of DetEncBuilder
'''

import gegede.builder
from gegede import Quantity as Q


class CryostatBuilder(gegede.builder.Builder):
    '''
    Build the Cryostat.
    '''


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, 
                  membraneThickness   = Q('0.5in'),
                  cathodeThickness    = Q('0.016cm'),
                  outerAPAs           = False,
                  nAPAs               = None,
                  sideLAr             = Q('15cm'),
                  APAToFloor          = Q('49.2cm'),
                  APAToGAr            = Q('40.7cm'),
                  APAToUpstreamWall   = Q('301.2cm'),
                  APAToDownstreamWall = Q('49.2cm'),
                  **kwds):

        if nAPAs is None:
            raise ValueError("No value given for nAPAs")
        assert nAPAs[1] <= 2 # can only read out APAs from top or bottom, 2 levels max

        self.membraneThickness    = membraneThickness
        self.cathodeThickness     = cathodeThickness
        self.outerAPAs            = outerAPAs
        self.nAPAs                = nAPAs
        self.sideLAr              = sideLAr
        self.APAToFloor           = APAToFloor
        self.APAToGAr             = APAToGAr
        self.APAToUpstreamWall    = APAToUpstreamWall
        self.APAToDownstreamWall  = APAToDownstreamWall
        
        self.tpcBldr       = self.get_builder('TPC')
        if outerAPAs:
            self.tpcOuterBldr  = self.get_builder('TPCOuter')
        
        
    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        self.g10Thickness         = self.tpcBldr.g10Thickness        
        self.wrapCover            = self.tpcBldr.wrapCover
        self.APAGap_y             = self.tpcBldr.APAGap_y
        self.APAGap_z             = self.tpcBldr.APAGap_z
        self.apaPhysicalDim       = list(self.tpcBldr.apaPhysicalDim)
        self.apaFrameDim          = list(self.tpcBldr.apaFrameDim)
        
        # Using volTPC dimensions, calculate module dimensions
        self.tpcDim = list(self.tpcBldr.tpcDim)
        if self.outerAPAs:
            self.tpcOuterDim = list(self.tpcOuterBldr.tpcDim)
                   
        # Using module dimensions, calculate cryostat dimensions
        APAToAPA     = [ self.apaFrameDim[0] + 2*self.tpcDim[0] + self.cathodeThickness,
                         self.tpcDim[1],
                         self.tpcDim[2]  ]

        # Cryostat dimensions, less the dead LAr on all sides 
        AllAPAsDim   = [ (self.nAPAs[0]-1)*APAToAPA[0],
                         self.nAPAs[1] * self.tpcDim[1],
                         self.nAPAs[2] * self.tpcDim[2]  ]
        if self.outerAPAs:
            AllAPAsDim[0] += self.apaPhysicalDim[0] # half apa on each side 
        else: 
            AllAPAsDim[0] += self.apaFrameDim[0] + 2*self.tpcDim[0] + 2*self.cathodeThickness


        # Add dead LAr on all sides to get inner membrane dimensions
        membraneInDim   = [ AllAPAsDim[0] + 2*self.sideLAr,
                            AllAPAsDim[1] + self.APAToFloor + self.APAToGAr,
                            AllAPAsDim[2] + self.APAToUpstreamWall + self.APAToDownstreamWall ]        
        print ('Cryostat inner dimensions: ' + str(membraneInDim))
        membraneOutDim  = [ membraneInDim[0] + 2*self.membraneThickness, 
                            membraneInDim[1] + 2*self.membraneThickness,
                            membraneInDim[2] + 2*self.membraneThickness ]
        self.cryoInDim    = list(membraneInDim) 
        self.cryoDim    = list(membraneOutDim) 


        # define cryostat shape and volume, will be placed by a builder owning this builder
        cryoBox = geom.shapes.Box( 'Cryostat',              dx=0.5*self.cryoDim[0], 
                                   dy=0.5*self.cryoDim[1],  dz=0.5*self.cryoDim[2]  )
        cryo_lv = geom.structure.Volume('volCryostat', material='LAr', shape=cryoBox)
        self.add_volume(cryo_lv)

        # define the cathode volume 
        cathodeBox = geom.shapes.Box( 'Cathode',              dx=0.5*self.cathodeThickness, 
                                      dy=0.5*self.tpcDim[1],  dz=0.5*self.tpcDim[2]  )
        cathode_lv = geom.structure.Volume('volCathode', material='Steel', shape=cathodeBox)
        self.add_volume(cathode_lv)


        # Get the TPC volume from its builder so we can position and place it
        tpc_lv = self.tpcBldr.get_volume('volTPC')
        if self.outerAPAs:
            tpcOuter_lv = self.tpcOuterBldr.get_volume('volTPCOuter')


        # Position both TPCs, APA Frame volumes for each module, and CPAs around 
        CPANum = 0
        APANum = 0   # 2xAPANum(+1) meant to mimic TPC numbering in LArSoft:
        for z_i in range(self.nAPAs[2]):         # lastly z
            for y_i in range(self.nAPAs[1]):     # then in y
                cpalist = {}
                for x_i in range(self.nAPAs[0]): # increase TPC # first in x

                    outerAPANeg = x_i==0 and self.outerAPAs
                    outerAPAPos = x_i==self.nAPAs[0]-1 and self.outerAPAs

                    # Calculate first APA position
                    zpos = - 0.5*self.cryoInDim[2] + self.APAToUpstreamWall + 0.5*self.apaPhysicalDim[2]
                    ypos = - 0.5*self.cryoInDim[1] + self.APAToFloor + 0.5*self.apaPhysicalDim[1]
                    xpos = - 0.5*self.cryoInDim[0] + self.sideLAr
                    if self.outerAPAs: 
                        xpos += 0.5*self.apaPhysicalDim[0]
                    else:
                        xpos += 0.5*self.cathodeThickness + self.tpcDim[0] + 0.5*self.apaFrameDim[0]

                    # all APA positions relative to first
                    xpos += x_i*APAToAPA[0]
                    ypos += y_i*APAToAPA[1]
                    zpos += z_i*APAToAPA[2]


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
                    tpc0Pos = [ xpos - 0.5*self.apaFrameDim[0] - 0.5*tpc0Dim[0], ypos, zpos ]
                    tpc1Pos = [ xpos + 0.5*self.apaFrameDim[0] + 0.5*tpc1Dim[0], ypos, zpos ]
                    pos0Name = 'TPC-'+ str(2*APANum)     + '_in_Cryo'
                    pos1Name = 'TPC-'+ str(2*APANum + 1) + '_in_Cryo'
                    tpc0_in_cryo = geom.structure.Position(pos0Name, tpc0Pos[0], tpc0Pos[1], tpc0Pos[2])
                    tpc1_in_cryo = geom.structure.Position(pos1Name, tpc1Pos[0], tpc1Pos[1], tpc1Pos[2])
                    
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
                    cryo_lv.placements.append(pTPC0_in_C.name)
                    cryo_lv.placements.append(pTPC1_in_C.name)


                    # Place Photon Detecors
                    

                    # Place steel frames and plastic around it
                    # Sould probably write a function to do this
                    # Around modCenter
                    

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

        print ("Cryostat: Built "+str(self.nAPAs[0])+" wide by "+str(self.nAPAs[1])+" high by "+str(self.nAPAs[2])+" long modules.")



        # make and place the steel membrane
        membraneOut = geom.shapes.Box( 'MembraneOut',            dx=0.5*membraneOutDim[0], 
                                       dy=0.5*membraneOutDim[1], dz=0.5*membraneOutDim[2]) 
        membraneIn = geom.shapes.Box(  'MembraneIn',              dx=0.5*membraneInDim[0], 
                                       dy=0.5*membraneInDim[1],  dz=0.5*membraneInDim[2]) 
        membraneBox = geom.shapes.Boolean( 'Membrane', type='subtraction', first=membraneOut, second=membraneIn ) 
        membrane_lv = geom.structure.Volume('volMembrane', material='Steel', shape=membraneBox)
        membrane_in_cryo = geom.structure.Position('Membrane_in_Cryo', 
                                                  Q('0cm'),Q('0cm'),Q('0cm'))
        pMembrane_in_C  = geom.structure.Placement('placeMembrane_in_Cryo',
                                                   volume = membrane_lv,
                                                   pos = membrane_in_cryo)
        cryo_lv.placements.append(pMembrane_in_C.name)




    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def PlaceCPA( self, geom, cryo_lv, cathode_lv, CPANum, cpaPos, **kwds):

        # CPA is more than just a cathode sheet, TODO: come back to that
        # 
        posCPAName = 'CPA-'+ str(CPANum) + '_in_Cryo'
        cathode_in_cryo = geom.structure.Position(posCPAName, cpaPos[0], cpaPos[1], cpaPos[2])
        pCathode_in_C = geom.structure.Placement('place'+posCPAName,
                                                 volume = cathode_lv,
                                                 pos = cathode_in_cryo)
        cryo_lv.placements.append(pCathode_in_C.name)
