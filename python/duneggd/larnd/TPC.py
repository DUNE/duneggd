#!/usr/bin/env python
'''
Subbuilder of CryostatBuilder
'''

import gegede.builder
from gegede import Quantity as Q


class TPCBuilder(gegede.builder.Builder):
    '''
    Build the Cryostat.
    '''


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, 
                  driftDistance       = Q('1m'),  # <-- just default values,
                  tpcDim              = None,     #     they really come from 
                                                  #     the cfg file
                  **kwds):

        if tpcDim is None:
            raise ValueError("No value configured for tpcDim")

        self.tpcDim             = tpcDim
        self.driftDistance      = driftDistance

        self.planeBldr = self.get_builder('TPCPlane')


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # N.B. -- the names 'volTPCPlane*', 'volTPC*', and 'volTPCActive' are required by LArSoft


        # get dimensions and volume of readout plane
        readPlaneDim = list(self.planeBldr.readPlaneDim)
        readPlane_lv = self.planeBldr.get_volume('volTPCPlane')


        # define TPC Active shape and volume
        tpcActiveDim = [ self.driftDistance, self.tpcDim[1], self.tpcDim[2] ]
        tpcActiveBox = geom.shapes.Box( 'TPCActive',            dx=0.5*tpcActiveDim[0], 
                                        dy=0.5*tpcActiveDim[1], dz=0.5*tpcActiveDim[2]  )
        tpcActive_lv = geom.structure.Volume('volTPCActive', material='LAr', shape=tpcActiveBox)



        # define tpc shape and volume, will be placed by CryostatBuilder
        tpcBox = geom.shapes.Box( 'TPC',                  dx=0.5*self.tpcDim[0], 
                                   dy=0.5*self.tpcDim[1], dz=0.5*self.tpcDim[2]  )
        tpc_lv = geom.structure.Volume('volTPC', material='LAr', shape=tpcBox)
        self.add_volume(tpc_lv)



        # Calculate volTPCPlane position assuming plane is centered in y and z.
        readPlane0Pos = [ -0.5*self.tpcDim[0] + 0.5*readPlaneDim[0], '0cm', '0cm' ]
        readPlane0_in_tpc = geom.structure.Position('readPlane0_in_TPC', 
                                                    readPlane0Pos[0], readPlane0Pos[1], readPlane0Pos[2])
        readPlane1Pos = [ -0.5*self.tpcDim[0] + 1.5*readPlaneDim[0], '0cm', '0cm' ]
        readPlane1_in_tpc = geom.structure.Position('readPlane1_in_TPC', 
                                                    readPlane1Pos[0], readPlane1Pos[1], readPlane1Pos[2])

        # Calculate volTPCActive position assuming plane is centered in y and z.
        tpcActivePos = [ 0.5*self.tpcDim[0] - 0.5*tpcActiveDim[0], '0cm', '0cm' ]
        tpcActive_in_tpc = geom.structure.Position('tpcActive_in_TPC', 
                                                   tpcActivePos[0], tpcActivePos[1], tpcActivePos[2])


        # place each plane and active volume in TPC volume
        pPlane0_in_TPC = geom.structure.Placement('placePlane0_in_TPC',
                                                 volume = readPlane_lv,
                                                 pos = readPlane0_in_tpc)
        pPlane1_in_TPC = geom.structure.Placement('placePlane1_in_TPC',
                                                 volume = readPlane_lv,
                                                 pos = readPlane1_in_tpc)
        pActive_in_TPC = geom.structure.Placement('placeActive_in_TPC',
                                                  volume = tpcActive_lv,
                                                  pos = tpcActive_in_tpc)
        tpc_lv.placements.append(pPlane0_in_TPC.name)
        tpc_lv.placements.append(pPlane1_in_TPC.name)
        tpc_lv.placements.append(pActive_in_TPC.name)
