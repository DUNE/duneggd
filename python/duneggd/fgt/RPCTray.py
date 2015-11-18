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
    def configure(self,  rpcTrayDim = [ Q('600cm'), Q('200cm'), Q('1.5cm') ], rpcTrayMat = 'Air',
                  nrpcCol = 3, nrpcRow = 2, **kwds):

      self.rpcTrayMat = rpcTrayMat
      self.rpcTrayDim = rpcTrayDim
      self.nrpcCol = nrpcCol
      self.nrpcRow = nrpcRow

      #print self.builders
      self.RPCModBldr = self.get_builder('RPCMod')

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):


        # get RPCMod volume and dim
        rpcMod_lv = self.RPCModBldr.get_volume('volRPCMod')
        rpcModDim = self.RPCModBldr.rpcModDim


        # define box and volume for RPC tray,
        # to be retrieved by MuID*Builder.
        # size will depend on configuration
        rpcTray = geom.shapes.Box(self.name,
                                 dx = 0.5*self.rpcTrayDim[0],
                                 dy = 0.5*self.rpcTrayDim[1],
                                 dz = 0.5*self.rpcTrayDim[2])
        rpcTray_lv = geom.structure.Volume('vol'+self.name, material=self.rpcTrayMat, shape=rpcTray)
        self.add_volume(rpcTray_lv)
        
        
        # position and place RPCMods
        for i in range(self.nrpcRow):
            for j in range(self.nrpcCol):
                xpos = -0.5*self.rpcTrayDim[0]+(self.nrpcCol*i+j+0.5)*rpcModDim[0]
                ypos = -0.5*self.rpcTrayDim[1]+(i+0.5)*rpcModDim[1]
                if (self.rpcTrayDim[1] < self.nrpcRow*rpcModDim[1]):
                    if i==1:
                        zpos = 0.5*self.rpcTrayDim[2]
                    else:
                        zpos = Q('0cm')
                else:
                    zpos = Q('0cm')

                rpcm_in_t  = geom.structure.Position( 'RPCMod-'+str(self.nrpcCol*i+j)+'_in_'+self.name,
                                                      xpos,  ypos,  zpos)
                prpcm_in_t = geom.structure.Placement( 'placeRPCMod-'+str(self.nrpcCol*i+j)+'_in_'+self.name,
                                                       volume = rpcMod_lv, pos = rpcm_in_t)
                rpcTray_lv.placements.append( prpcm_in_t.name )
        
        
        return
