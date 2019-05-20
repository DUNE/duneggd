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
                  driftDistance  = Q('1m'),             # <-- just default values,
                  APAGap_y       = Q('0.4cm'),
                  APAGap_z       = Q('0.8cm'),
                  wirePlanePitch = Q('0.476cm'),
                  **kwds):
        
        self.driftDistance      = driftDistance
        self.APAGap_y           = APAGap_y     
        self.APAGap_z           = APAGap_z
        self.wirePlanePitch     = wirePlanePitch
        
        self.planeBldrZ  =      self.get_builder('TPCPlaneZ')
        self.planeBldrV  =      self.get_builder('TPCPlaneV')
        self.planeBldrU  =      self.get_builder('TPCPlaneU')



    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        self.apaPhysicalDim  = list(self.planeBldrZ.apaPhysicalDim)
        self.apaFrameDim  = list(self.planeBldrZ.apaFrameDim)
        self.apaPhysicalDim[0] += 2*3*self.wirePlanePitch
        self.g10Thickness = self.planeBldrZ.g10Thickness
        self.wrapCover    = self.planeBldrZ.wrapCover
             
        
        # N.B. -- the names 'volTPCPlane*', 'volTPC*', and 'volTPCActive' are required by LArSoft

        # Add g10 plastic for mounting wires/gridplane and cover

        # get dimensions and volume of readout plane
        plane_x = self.planeBldrZ.planeDim[0]
        readPlaneZ_lv = self.planeBldrZ.get_volume('volTPCPlaneZ')
        readPlaneV_lv = self.planeBldrV.get_volume('volTPCPlaneV')
        readPlaneU_lv = self.planeBldrU.get_volume('volTPCPlaneU')


        self.tpcDim = [ self.driftDistance + 2*self.wirePlanePitch + 0.5*plane_x,
                        self.apaPhysicalDim[1]+self.APAGap_y,
                        self.apaPhysicalDim[2]+self.APAGap_z ]


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
        readPlaneZPos = [ -0.5*self.tpcDim[0] + 0.5*plane_x, Q('0cm'), Q('0cm') ]
        readPlaneZ_in_tpc = geom.structure.Position('readPlaneZ_in_TPC', 
                                                    readPlaneZPos[0], readPlaneZPos[1], readPlaneZPos[2])

        readPlaneVPos = [ -0.5*self.tpcDim[0] + 1.5*plane_x, Q('0cm'), Q('0cm') ]
        readPlaneV_in_tpc = geom.structure.Position('readPlaneV_in_TPC', 
                                                    readPlaneVPos[0], readPlaneVPos[1], readPlaneVPos[2])

        readPlaneUPos = [ -0.5*self.tpcDim[0] + 2.5*plane_x, Q('0cm'), Q('0cm') ]
        readPlaneU_in_tpc = geom.structure.Position('readPlaneU_in_TPC', 
                                                    readPlaneUPos[0], readPlaneUPos[1], readPlaneUPos[2])

        # GRID PLANE?

        
        # Calculate volTPCActive position assuming plane is centered in y and z.
        tpcActivePos = [ 0.5*self.tpcDim[0] - 0.5*tpcActiveDim[0], Q('0cm'), Q('0cm') ]
        tpcActive_in_tpc = geom.structure.Position('tpcActive_in_TPC', 
                                                   tpcActivePos[0], tpcActivePos[1], tpcActivePos[2])


        # place each plane and active volume in TPC volume
        pPlaneZ_in_TPC = geom.structure.Placement('placePlaneZ_in_TPC',
                                                  volume = readPlaneZ_lv,
                                                  pos = readPlaneZ_in_tpc)
        
        pPlaneV_in_TPC = geom.structure.Placement('placePlaneV_in_TPC',
                                                  volume = readPlaneV_lv,
                                                  pos = readPlaneV_in_tpc)
        
        pPlaneU_in_TPC = geom.structure.Placement('placePlaneU_in_TPC',
                                                  volume = readPlaneU_lv,
                                                  pos = readPlaneU_in_tpc)
        
        pActive_in_TPC = geom.structure.Placement('placeActive_in_TPC',
                                                  volume = tpcActive_lv,
                                                  pos = tpcActive_in_tpc)

        tpc_lv.placements.append(pPlaneZ_in_TPC.name)
        tpc_lv.placements.append(pPlaneV_in_TPC.name)
        tpc_lv.placements.append(pPlaneU_in_TPC.name)
        tpc_lv.placements.append(pActive_in_TPC.name)
