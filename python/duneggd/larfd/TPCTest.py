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
                  driftDistance    = Q('1m'),             # <-- just default values,
                  APAGap_y         = Q('0.4cm'),
                  APAGap_z         = Q('0.8cm'),
                  wirePlanePitch   = Q('0.476cm'),
                  cryoInnerDim     = None,
                  APAFrameDim      = None,
                  cathodeThickness = None,
                  nAPAs            = None,
                  **kwds):
        
        self.driftDistance      = driftDistance
        self.APAGap_y           = APAGap_y     
        self.APAGap_z           = APAGap_z
        self.wirePlanePitch     = wirePlanePitch
        self.cryoInnerDim       = cryoInnerDim
        self.APAFrameDim        = APAFrameDim
        self.cathodeThickness   = cathodeThickness
        self.nAPAs              = nAPAs
        self.APAFrameDim        = APAFrameDim
        
        self.planeBldrZ   =      self.get_builder('TPCPlaneZ')
        self.planeBldrV   =      self.get_builder('TPCPlaneV')
        self.planeBldrU   =      self.get_builder('TPCPlaneU')




    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        plane_x           = self.planeBldrZ.frameDim[0]

        self.tpcDim       = [ self.driftDistance , # + 2*self.wirePlanePitch + plane_x,
                              self.APAFrameDim[1],
                              self.APAFrameDim[2] ]

        # Define the shape that will be placed in the cryostat
        tpcBox = geom.shapes.Box(self.name,
                                 dx=0.5*self.tpcDim[0], 
                                 dy=0.5*self.tpcDim[1],
                                 dz=0.5*self.tpcDim[2]  )
        tpc_lv = geom.structure.Volume('vol'+self.name, material='LAr', shape=tpcBox)
        self.add_volume(tpc_lv)

        # Place the read out planes
        readPlaneZ_lv = self.planeBldrZ.get_volume('volTPCPlaneZ')
        readPlaneV_lv = self.planeBldrV.get_volume('volTPCPlaneV')
        readPlaneU_lv = self.planeBldrU.get_volume('volTPCPlaneU')

        readPlaneZ_in_tpc = geom.structure.Position('readPlaneZ_in_'+self.name, 
                                                    0.5*(self.tpcDim[0]-plane_x), Q('0m'), Q('0m'))
        readPlaneV_in_tpc = geom.structure.Position('readPlaneV_in_'+self.name, 
                                                    0.5*(self.tpcDim[0]-plane_x-self.wirePlanePitch), Q('0m'), Q('0m'))
        readPlaneU_in_tpc = geom.structure.Position('readPlaneU_in_'+self.name, 
                                                    0.5*(self.tpcDim[0]-plane_x-(2*self.wirePlanePitch)), Q('0m'), Q('0m'))

        pPlaneZ_in_TPC = geom.structure.Placement('placePlaneZ_in_'+self.name,
                                                  volume = readPlaneZ_lv,
                                                  pos    = readPlaneZ_in_tpc)
        pPlaneV_in_TPC = geom.structure.Placement('placePlaneV_in_'+self.name,
                                                  volume = readPlaneV_lv,
                                                  pos    = readPlaneV_in_tpc)
        pPlaneU_in_TPC = geom.structure.Placement('placePlaneU_in_'+self.name,
                                                  volume = readPlaneU_lv,
                                                  pos    = readPlaneU_in_tpc)

        tpc_lv.placements.append(pPlaneZ_in_TPC.name)
        tpc_lv.placements.append(pPlaneV_in_TPC.name)
        tpc_lv.placements.append(pPlaneU_in_TPC.name)

        # Construct and place the TPC Active volume
        self.tpcActiveDim = [self.driftDistance - plane_x - (2.0*self.wirePlanePitch), self.tpcDim[1], self.tpcDim[2]]
        if self.name=='TPCOuter': self.tpcActiveDim[0] = Q('0.1mm') # make active negligible on outside
        activename = 'volTPCActive'
        if self.name=='TPCOuter': activename = 'volTPCActiveOuter'

        # Construct and place the TPC Active volume
        tpcActiveBox = geom.shapes.Box(self.name+'Active',
                                       dx=0.5*self.tpcActiveDim[0], 
                                       dy=0.5*self.tpcActiveDim[1],
                                       dz=0.5*self.tpcActiveDim[2])
        tpcActive_lv = geom.structure.Volume(activename, material='LAr', shape=tpcActiveBox)
        
        tpcActive_in_tpc = geom.structure.Position('Active_in_'+self.name, 
                                                   -0.5*(plane_x + (2.0*self.wirePlanePitch)),
                                                   Q('0m'),
                                                   Q('0m'))
        
        pActive_in_TPC = geom.structure.Placement('placeActive_in_'+self.name,
                                                  volume = tpcActive_lv,
                                                  pos    = tpcActive_in_tpc)

        tpc_lv.placements.append(pActive_in_TPC.name)
