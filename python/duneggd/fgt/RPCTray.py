#!/usr/bin/env python
'''
Subbuilder of MuID*Builder
'''

import gegede.builder
from gegede import Quantity as Q

class RPCTrayBuilder(gegede.builder.Builder):
    '''
    Arrange the RPC modules in configured way 
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self,  rpcTrayDim = [ Q('600cm'), Q('200cm'), Q('1.5cm') ], rpcTrayMat='Air', **kwds):
      self.rpcTrayMat = rpcTrayMat
      self.rpcTrayDim = rpcTrayDim

      #print self.builders
      self.RPCModBldr = self.get_builder('RPCMod')

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):


        # get RPCMod volume and dim
        rpcMod_lv = self.RPCModBldr.get_volume('volRPCModule_')
        rpcModDim = self.RPCModBldr.rpcModDim


        # define box and volume for RPC tray,
        # to be retrieved by MuID*Builder.
        # size will depend on configuration
        rpcTray = geom.shapes.Box('RPCTray_'+self.name,
                                 dx = 0.5*self.rpcTrayDim[0],
                                 dy = 0.5*self.rpcTrayDim[1],
                                 dz = 0.5*self.rpcTrayDim[2])
        rpcTray_lv = geom.structure.Volume('volRPCTray_'+self.name, material=self.rpcTrayMat, shape=rpcTray)


        # position and place RPCMods in tray based off of configuration
        pRPCM_in_Tray  = geom.structure.Placement( 'placeRPCModule_in_Tray_'+self.name, volume = rpcMod_lv )
        rpcTray_lv.placements.append( pRPCMS_in_Tray.name )
        self.add_volume(rpcTray_lv)

        # ^ -----------> x (6m)
        # |
        # |
        # y (2m)
        nrpcCol = int(self.rpcTrayDim[0]/self.rpcModDim[0])
        nrpcRow = int(self.rpcTrayDim[1]/self.rpcModDim[1])
        
        for j in range(nrpcRow):
            for i in range(nrpcCol):
               xpos = -0.5*self.rpcTrayDim[0]+(nrpcCol*j+i+0.5)*self.rpcModDim[0]
               ypos = -0.5*self.rpcTrayDim[1]+(j+0.5)*self.rpcModDim[1]
               zpos = '0cm'

        rpcm_in_t  = geom.structure.Position( 'RPCMod-'+str(nrpcCol*j+i)+'_in_RPCTray_'+self.name,
                                                       xpos,  ypos,  zpos)
        prpcm_in_t = geom.structure.Placement( 'placeRPCMod-'+str(nrpcCol*j+i)+'_in_RPCTray_'+self.name,volume = rpcTray_lv,pos = rpcm_in_t,rot = "r90aboutX")


        rpcTray_lv.placements.append( prpcm_in_t.name )
        return
