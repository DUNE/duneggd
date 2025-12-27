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

        self.APAFrameDim  = list(self.planeBldrZ.APAFrameDim)
        # N.B. -- the names 'volTPCPlane*', 'volTPC*', and 'volTPCActive' are required by LArSoft
        # Add g10 plastic for mounting wires/gridplane and cover
        # get dimensions and volume of readout plane
        plane_x = self.planeBldrZ.planeDim[0]
        readPlaneZ_lv = self.planeBldrZ.get_volume('volTPCPlaneZ')
        readPlaneV_lv = self.planeBldrV.get_volume('volTPCPlaneV')
        readPlaneU_lv = self.planeBldrU.get_volume('volTPCPlaneU')
        
        self.tpcDim = [ self.driftDistance + 2*self.wirePlanePitch + plane_x,
                        self.APAFrameDim[1],
                        self.APAFrameDim[2] ]


        # define TPC Active shape and volume
        tpcActiveDim = [ self.driftDistance, self.tpcDim[1], self.tpcDim[2] ]
        #if self.name=='TPCOuter': tpcActiveDim[0] = Q('.1mm') # make active negligible on outside
        tpcActiveBox = geom.shapes.Box(self.name+'Active',
                                       dx=0.5*tpcActiveDim[0], 
                                       dy=0.5*tpcActiveDim[1],
                                       dz=0.5*tpcActiveDim[2])
        activename = 'volTPCActive'
        if self.name=='TPCOuter': activename = 'volTPCActiveOuter'
        tpcActive_lv = geom.structure.Volume(activename, material='LAr', shape=tpcActiveBox)


        # define tpc shape and volume, will be placed by CryostatBuilder
        tpcBox = geom.shapes.Box( self.name,             dx=0.5*self.tpcDim[0], 
                                  dy=0.5*self.tpcDim[1], dz=0.5*self.tpcDim[2]  )
        tpc_lv = geom.structure.Volume('vol'+self.name, material='LAr', shape=tpcBox)
        self.add_volume(tpc_lv)



        # Calculate volTPCPlane position assuming plane is centered in y and z.
        readPlaneZPos = [ 0.5*self.tpcDim[0] - 0.5*plane_x, 
                          Q('0cm'), Q('0cm') ]
        readPlaneZ_in_tpc = geom.structure.Position('readPlaneZ_in_'+self.name, 
                                                    readPlaneZPos[0], readPlaneZPos[1], readPlaneZPos[2])

        readPlaneVPos = [ 0.5*self.tpcDim[0] - 0.5*plane_x - 1*self.wirePlanePitch, 
                          Q('0cm'), Q('0cm') ]
        readPlaneV_in_tpc = geom.structure.Position('readPlaneV_in_'+self.name, 
                                                    readPlaneVPos[0], readPlaneVPos[1], readPlaneVPos[2])

        readPlaneUPos = [ 0.5*self.tpcDim[0] - 0.5*plane_x - 2*self.wirePlanePitch,
                          Q('0cm'), Q('0cm') ]
        readPlaneU_in_tpc = geom.structure.Position('readPlaneU_in_'+self.name, 
                                                    readPlaneUPos[0], readPlaneUPos[1], readPlaneUPos[2])

        # GRID PLANE?

        
        # Calculate volTPCActive position assuming plane is centered in y and z.
        tpcActivePos = [ 0.5*self.tpcDim[0] - plane_x - 2*self.wirePlanePitch - 0.5*tpcActiveDim[0], 
                         Q('0cm'), Q('0cm') ]
        tpcActive_in_tpc = geom.structure.Position('Active_in_'+self.name, 
                                                   tpcActivePos[0], tpcActivePos[1], tpcActivePos[2])


        # place each plane and active volume in TPC volume
        pPlaneZ_in_TPC = geom.structure.Placement('placePlaneZ_in_'+self.name,
                                                  volume = readPlaneZ_lv,
                                                  pos = readPlaneZ_in_tpc)
        
        pPlaneV_in_TPC = geom.structure.Placement('placePlaneV_in_'+self.name,
                                                  volume = readPlaneV_lv,
                                                  pos = readPlaneV_in_tpc)
        
        pPlaneU_in_TPC = geom.structure.Placement('placePlaneU_in_'+self.name,
                                                  volume = readPlaneU_lv,
                                                  pos = readPlaneU_in_tpc)
        
        pActive_in_TPC = geom.structure.Placement('placeActive_in_'+self.name,
                                                  volume = tpcActive_lv,
                                                  pos = tpcActive_in_tpc)

        tpc_lv.placements.append(pPlaneZ_in_TPC.name)
        tpc_lv.placements.append(pPlaneV_in_TPC.name)
        tpc_lv.placements.append(pPlaneU_in_TPC.name)
        tpc_lv.placements.append(pActive_in_TPC.name)
