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
        readPlanePos = [ -0.5*self.tpcDim[0] + 0.5*readPlaneDim[0], '0cm', '0cm' ]
        readPlane_in_tpc = geom.structure.Position('readPlane_in_TPC', 
                                                   readPlanePos[0], readPlanePos[1], readPlanePos[2])

        # Calculate volTPCActive position assuming plane is centered in y and z.
        tpcActivePos = [ 0.5*self.tpcDim[0] - 0.5*tpcActiveDim[0], '0cm', '0cm' ]
        tpcActive_in_tpc = geom.structure.Position('tpcActive_in_TPC', 
                                                   tpcActivePos[0], tpcActivePos[1], tpcActivePos[2])


        # place each plane and active volume in TPC volume
        pPlane_in_TPC = geom.structure.Placement('placePlane_in_TPC',
                                                 volume = readPlane_lv,
                                                 pos = readPlane_in_tpc)
        pActive_in_TPC = geom.structure.Placement('placeActive_in_TPC',
                                                  volume = tpcActive_lv,
                                                  pos = tpcActive_in_tpc)
        tpc_lv.placements.append(pPlane_in_TPC.name)
        tpc_lv.placements.append(pActive_in_TPC.name)
