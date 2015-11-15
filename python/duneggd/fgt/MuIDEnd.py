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
    def configure(self, muidUpDim = [ Q('600cm'), Q('600cm'), Q('64.5cm') ], muidDownDim = [ Q('600cm'), Q('600cm'), Q('107.5cm') ],
                  magDim = [ Q('600cm'), Q('600cm'), Q('20cm') ], nTraysPerPlane = 3, nUpPlanes = 3, nDownPlanes = 5,
                  muidMat = 'Steel', **kwds):

        self.muidMat = muidMat
        self.muidUpDim   = muidUpDim
        self.muidDownDim = muidDownDim
        self.magDim      = magDim
        self.nTraysPerPlane = nTraysPerPlane
        self.nUpPlanes      = nUpPlanes
        self.nDownPlanes    = nDownPlanes
        
        #print self.builders
        self.RPCTrayBldr = self.get_builder('RPCTray_End')


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Get the RPC tray volume and position
        rpcTray_lv = self.RPCTrayBldr.get_volume('volRPCTray_')
        rpcTrayDim = self.RPCMTrayBldr.rpcTrayDim
        
        # Ccalculate the muidDim[2] (z dim) with other configured parameters: 
        #   number of planes, thicknesses...


        # Make volume to be retrieved by DetectorBuilder
        muidUpEndBox = geom.shapes.Box('MuIdUpEnd_'+self.name,
                                       dx=0.5*self.muidUpDim[0],
                                       dy=0.5*self.muidUpDim[1],
                                       dz=0.5*self.muidUpDim[2])
        muidDownEndBox = geom.shapes.Box('MuIdDownEnd_'+self.name,
                                       dx=0.5*self.muidDownDim[0],
                                       dy=0.5*self.muidDownDim[1],
                                       dz=0.5*self.muidDownDim[2])
        muidUpEnd_lv   = geom.structure.Volume('volMuIdUpEnd_'+self.name, material=self.muidMat, shape=muidUpEndBox)
        muidDownEnd_lv = geom.structure.Volume('volMuIdDownEnd_'+self.name, material=self.muidMat, shape=muidDownEndBox)

        pRPCT_in_UpEnd   = geom.structure.Placement( 'placeRPCTray_in_UpEnd_'+self.name, volume = rpcTray_lv )
        pRPCT_in_DownEnd = geom.structure.Placement( 'placeRPCTray_in_DownEnd_'+self.name, volume = rpcTray_lv )
        muidUpEnd_lv.placements.append( pRPCT_in_UpEnd.name )
        muidDownEnd_lv.placements.append( pRPCT_in_DownEnd.name )
        self.add_volume(muidUpEnd_lv)
        self.add_volume(muidDownEnd_lv)

        # Place the RPC trays and steel sheets between in the configured way
        # Steel Sheets: just leave the default material of volMuID* steel 
        #   and leave spaces instead of placing explicit volumes

        #Planes for MuIDUpEnd
        for i in range(self.nUpPlanes):
            zpos = -0.5*self.muidUpDim[2]+(i+0.5)*self.rpcTrayDim[2]+i*self.magDim[2]
        for j in range(self.nTraysPerPlane):
            xpos = '0cm'
            ypos = -0.5*self.muidUpDim[1]+(j+0.5)*self.rpcTrayDim[1]

        rpct_in_uend  = geom.structure.Position( 'RPCTray-'+str(self.nTraysPerPlane*i+j)+'_in_MuIDUpEnd_'+self.name,
                                                       xpos,  ypos,  zpos)
        prpct_in_uend = geom.structure.Placement( 'placeRPCTray-'+str(self.nTraysPerPlane*i+j)+'_in_MuIDUpEnd_'+self.name,volume = muidUpEnd_lv,                                         pos = rpct_in_uend,rot = "r90aboutX")

        #Planes for MuIDDownEnd
        for i in range(self.nDownPlanes):
            zpos = -0.5*self.muidDownDim[2]+(i+0.5)*self.rpcTrayDim[2]+i*self.magDim[2]
        for j in range(self.nTraysPerPlane):
            xpos = '0cm'
            ypos = -0.5*self.muidDownDim[1]+(j+0.5)*self.rpcTrayDim[1]

        rpct_in_dend  = geom.structure.Position( 'RPCTray-'+str(self.nTraysPerPlane*i+j)+'_in_MuIDDownEnd_'+self.name,
                                                       xpos,  ypos,  zpos)
        prpct_in_dend = geom.structure.Placement( 'placeRPCTray-'+str(self.nTraysPerPlane*i+j)+'_in_MuIDDownEnd_'+self.name,
                                                 volume = muidDownEnd_lv,pos = rpct_in_dend,rot = "r90aboutX")


        muidUpEnd_lv.placements.append( prpct_in_uend.name )
        muidDownEnd_lv.placements.append( prpct_in_dend.name )
        
        return
