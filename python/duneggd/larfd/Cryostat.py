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
                  nAPAs               = None,
                  **kwds):

        if nAPAs is None:
            raise ValueError("No value given for nAPAs")

        self.membraneThickness    = membraneThickness
        self.cathodeThickness     = cathodeThickness
        self.nAPAs                = nAPAs
        
        self.tpcBldr   = self.get_builder('TPC')


        
        
    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        self.G10Thickness         = self.tpcBldr.G10Thickness        
        self.wrapCover            = self.tpcBldr.wrapCover
        self.APAGap_y             = self.tpcBldr.APAGap_y
        self.APAGap_z             = self.tpcBldr.APAGap_z
        self.apaFrameDim          = list(self.tpcBldr.apaFrameDim)
        
        # Using volTPC dimensions, calculate module dimensions
        tpcDim = list(self.tpcBldr.tpcDim)

                   
        # Using module dimensions, calculate cryostat dimensions
        APAGroupDim     = [ 2 * tpcDim[0] + self.apaFrameDim[0], 
                            tpcDim[1],
                            tpcDim[2]  ]
        AllAPAsDim     = [ self.nAPAs[0] * APAGroupDim[0], 
                            self.nAPAs[1] * tpcDim[1],
                            self.nAPAs[2] * tpcDim[2]  ]
        membraneInDim   = [ AllAPAsDim[0],AllAPAsDim[1],AllAPAsDim[2]] # add proper spacing

        membraneOutDim  = [ membraneInDim[0] + 2*self.membraneThickness, 
                            membraneInDim[1] + 2*self.membraneThickness,
                            membraneInDim[2] + 2*self.membraneThickness]
        self.cryoDim    = list(membraneOutDim) 


        # define cryostat shape and volume, will be placed by a builder owning this builder
        cryoBox = geom.shapes.Box( 'Cryostat',              dx=0.5*self.cryoDim[0], 
                                   dy=0.5*self.cryoDim[1],  dz=0.5*self.cryoDim[2]  )
        cryo_lv = geom.structure.Volume('volCryostat', material='LAr', shape=cryoBox)
        self.add_volume(cryo_lv)

        # define the cathode volume 
        # TODO -- material?
        # cathodeBox = geom.shapes.Box( 'Cathode',               dx=0.5*self.cathodeThickness, 
        #                               dy=0.5*g10CageInDim[1],  dz=0.5*g10CageInDim[2]  )
        # cathode_lv = geom.structure.Volume('volCathode', material='Steel', shape=cathodeBox)
        # self.add_volume(cathode_lv)


        # Get the TPC volume from its builder so we can position and place it
        tpc_lv = self.tpcBldr.get_volume('volTPC')


        # Position both TPCs, APA Frame volumes for each module, and CPAs around 
        APANum = 0     # Meant to mimic TPC numbering in LArSoft
        for x_i in range(self.nAPAs[0]):
            for y_i in range(self.nAPAs[1]):
                for z_i in range(self.nAPAs[2]):

                    # Calculate APA positions
                    xpos = - 0.5*self.cryoDim[0] + (x_i+0.5)*APAGroupDim[0]
                    ypos = - 0.5*self.cryoDim[1] + (y_i+0.5)*APAGroupDim[1]
                    zpos = - 0.5*self.cryoDim[2] + (z_i+0.5)*APAGroupDim[2]
                                        
                    # Calculate volTPC positions around module center
                    tpc0Pos = [ xpos - 0.5*self.apaFrameDim[0] - 0.5*tpcDim[0], ypos, zpos ]
                    tpc1Pos = [ xpos + 0.5*self.apaFrameDim[0] + 0.5*tpcDim[0], ypos, zpos ]
                    pos0Name = 'TPC-'+ str(2*APANum)     + '_in_Cryo'
                    pos1Name = 'TPC-'+ str(2*APANum + 1) + '_in_Cryo'
                    tpc0_in_cryo = geom.structure.Position(pos0Name, tpc0Pos[0], tpc0Pos[1], tpc0Pos[2])
                    tpc1_in_cryo = geom.structure.Position(pos1Name, tpc1Pos[0], tpc1Pos[1], tpc1Pos[2])

                    # Place the TPCs, making sure to rotate the right one
                    pTPC0_in_C = geom.structure.Placement('place'+pos0Name,
                                                          volume = tpc_lv,
                                                          pos = tpc0_in_cryo)
                    pTPC1_in_C = geom.structure.Placement('place'+pos1Name,
                                                          volume = tpc_lv,
                                                          pos = tpc1_in_cryo,
                                                          rot = 'r180aboutY')
                    cryo_lv.placements.append(pTPC0_in_C.name)
                    cryo_lv.placements.append(pTPC1_in_C.name)




                    # Place Photon Detecors

                    

                    # Place steel frames and plastic around it
                    # Sould probably write a function to do this
                    # Around modCenter
                    


                    # CPA frames and plastic around it
                    # Don't forget the 4 tubes around it

                    APANum += 1
                    print("Constructed APA: " + str(APANum))

        print "Cryostat: Built "+str(self.nAPAs[0])+" wide by "+str(self.nAPAs[1])+" high by "+str(self.nAPAs[2])+" long modules."



        # make and place the steel membrane
        membraneOut = geom.shapes.Box( 'MembraneOut',                 dx=0.5*membraneOutDim[0], 
                                       dy=0.5*membraneOutDim[1], dz=0.5*membraneOutDim[2]) 
        membraneIn = geom.shapes.Box(  'MembraneIn',                  dx=0.5*membraneInDim[0], 
                                       dy=0.5*membraneInDim[1],  dz=0.5*membraneInDim[2]) 
        membraneBox = geom.shapes.Boolean( 'Membrane', type='subtraction', first=membraneOut, second=membraneIn ) 
        membrane_lv = geom.structure.Volume('volMembrane', material='Steel', shape=membraneBox)
        membrane_in_cryo = geom.structure.Position('Membrane_in_Cryo', 
                                                  '0cm','0cm','0cm')
        pMembrane_in_C  = geom.structure.Placement('placeMembrane_in_Cryo',
                                                   volume = membrane_lv,
                                                   pos = membrane_in_cryo)
        cryo_lv.placements.append(pMembrane_in_C.name)
