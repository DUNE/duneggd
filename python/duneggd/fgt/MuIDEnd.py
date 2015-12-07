#!/usr/bin/env python
'''
Subbuilder of Detector
'''

import gegede.builder
from gegede import Quantity as Q


class MuIDEndBuilder(gegede.builder.Builder):
    '''
    Assemble configured number of RPC trays
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, 
                  muidDim = [ Q('600cm'), Q('600cm'), Q('107.5cm') ],
                  steelPlateDim = [ Q('600cm'), Q('600cm'), Q('20cm') ], 
                  nTraysPerPlane = 3, 
                  nPlanes = None,
                  muidMat = 'Steel', **kwds):

        self.muidMat        = muidMat
        self.muidDim        = muidDim
        self.steelPlateDim  = steelPlateDim
        self.nTraysPerPlane = nTraysPerPlane
        self.nPlanes        = nPlanes
        
        #print self.builders
        self.RPCTrayBldr = self.get_builder('RPCTray_End')


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Get the RPC tray volume and position
        rpcTray_lv = self.RPCTrayBldr.get_volume('volRPCTray_End')
        rpcTrayDim = self.RPCTrayBldr.rpcTrayDim
        
        # Calculate the muidDim[2] (z dim) with other configured parameters: 
        #   number of planes, thicknesses...


        # Make volume to be retrieved by DetectorBuilder
        muidBox = geom.shapes.Box( self.name,
                                   dx=0.5*self.muidDim[0],
                                   dy=0.5*self.muidDim[1],
                                   dz=0.5*self.muidDim[2])
        muid_lv = geom.structure.Volume('vol'+self.name, material=self.muidMat, shape=muidBox)
        self.add_volume(muid_lv)

        # Place the RPC trays and steel sheets between in the configured way
        # Steel Sheets: just leave the default material of volMuID* steel 
        #   and leave spaces instead of placing explicit volumes

        
        for i in range(self.nPlanes):
            zpos = -0.5*self.muidDim[2]+(i+0.5)*rpcTrayDim[2]+i*self.steelPlateDim[2]
            for j in range(self.nTraysPerPlane):

                xpos = Q('0cm')
                ypos = -0.5*self.muidDim[1]+(j+0.5)*rpcTrayDim[1]
        
                rpct_in_muid  = geom.structure.Position( 'rpct-'+str(self.nTraysPerPlane*i+j)+'_in_'+self.name,
                                                         xpos,  ypos,  zpos)
                prpct_in_muid = geom.structure.Placement( 'prpct-'+str(self.nTraysPerPlane*i+j)+'_in_'+self.name,
                                                          volume = rpcTray_lv, pos = rpct_in_muid )

                muid_lv.placements.append( prpct_in_muid.name )
        
        
        return
