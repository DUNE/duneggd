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
                  membraneThickness   = Q('0.5in'),  # <-- just default values,
                  readPlaneToCryoWall = Q('10cm'),   #     they really come from 
                  cageToCryoWall_y    = Q('10cm'),   #     the cfg file
                  cageToCryoWall_z    = Q('10cm'), 
                  cathodeThickness    = Q('0.016cm'), 
                  **kwds):

        self.membraneThickness    = membraneThickness
        self.cathodeThickness     = cathodeThickness
        self.readPlaneToCryoWall  = readPlaneToCryoWall
        self.cageToCryoWall_y     = cageToCryoWall_y
        self.cageToCryoWall_z     = cageToCryoWall_z


        self.tpcBldr = self.get_builder('TPC')


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):


        # get the volTPC dimensions and use them to define volCryostat dimensions
        tpcDim = list(self.tpcBldr.tpcDim)
        self.cryoDim = [ 2*tpcDim[0] + 2*self.readPlaneToCryoWall 
                                     + self.cathodeThickness
                                     + 2*self.membraneThickness, 
                         tpcDim[1] + 2*self.cageToCryoWall_y
                                   + 2*self.membraneThickness,
                         tpcDim[2] + 2*self.cageToCryoWall_z
                                   + 2*self.membraneThickness  ]

        membraneOutDim = list(self.cryoDim)
        membraneInDim  = [ membraneOutDim[0] - 2*self.membraneThickness, 
                           membraneOutDim[1] - 2*self.membraneThickness,
                           membraneOutDim[2] - 2*self.membraneThickness]


        # define cryostat shape and volume, will be placed by a builder owning this builder
        cryoBox = geom.shapes.Box( 'Cryostat',              dx=0.5*self.cryoDim[0], 
                                   dy=0.5*self.cryoDim[1],  dz=0.5*self.cryoDim[2]  )
        cryo_lv = geom.structure.Volume('volCryostat', material='LAr', shape=cryoBox)
        self.add_volume(cryo_lv)


        # Get the TPC volume from its builder so we can position and place it
        tpc_lv = self.tpcBldr.get_volume('volTPC')


        # Calculate volTPC positions assuming cathode is centered in x
        # Also assume TPC is centered in y and z for now.
        tpc0Pos = [ -0.5*self.cathodeThickness - 0.5*tpcDim[0], '0cm', '0cm' ]
        tpc1Pos = [  0.5*self.cathodeThickness + 0.5*tpcDim[0], '0cm', '0cm' ]
        tpc0_in_cryo = geom.structure.Position('TPC0_in_Cryo', tpc0Pos[0], tpc0Pos[1], tpc0Pos[2])
        tpc1_in_cryo = geom.structure.Position('TPC1_in_Cryo', tpc1Pos[0], tpc1Pos[1], tpc1Pos[2])

        # place each TPC in the cryostat, making sure to rotate the right one
        pTPC0_in_C = geom.structure.Placement('placeTPC0_in_Cryo',
                                              volume = tpc_lv,
                                              pos = tpc0_in_cryo)
        pTPC1_in_C = geom.structure.Placement('placeTPC1_in_Cryo',
                                              volume = tpc_lv,
                                              pos = tpc1_in_cryo,
                                              rot = 'r180aboutY')
        cryo_lv.placements.append(pTPC0_in_C.name)
        cryo_lv.placements.append(pTPC1_in_C.name)



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
