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


        # When naming things, keep in mind that self.name comes from
        #   the section name in the config file. So the names will be:
        #     RPCTray_BarBig
        #     RPCTray_BarSmall
        #     RPCTray_BarMid
        #     RPCTray_End
        # Each of these names comes from the configuration file, and each
        #   configurationsection corresponds to one instance of this builder.
        

        # get RPCMod volume and dim
        rpcMod_lv = self.RPCModBldr.get_volume('volRPCModule_')
        rpcModDim = self.RPCModBldr.rpcModDim


        # The size of the tray will depend on configuration, 
        #   and each instance of this builder will build
        #   this box once, with the unique self.name. 
        # So we only need to define it once here:

        # Define box and volume for RPC tray,
        #   to be retrieved by MuID*Builder.
        rpcTray = geom.shapes.Box(self.name,
                                  dx = 0.5*self.rpcTrayDim[0],
                                  dy = 0.5*self.rpcTrayDim[1],
                                  dz = 0.5*self.rpcTrayDim[2])
        rpcTray_lv = geom.structure.Volume('vol'+self.name, material=self.rpcTrayMat, shape=rpcTray)



        # ^ -----------> x (6m)
        # |
        # |
        # y (2m)
        nrpcCol = int(self.rpcTrayDim[0]/self.rpcModDim[0])
        nrpcRow = int(self.rpcTrayDim[1]/self.rpcModDim[1])
        
        for j in range(nrpcRow):
            for i in range(nrpcCol):

                # Position and place RPCMods in tray based off of configuration.
                # If the width is less than the number of modules times module width, 
                #   you will have to overlap them: z will differ for the center module
                # If not, then z is just zero.

               xpos = -0.5*self.rpcTrayDim[0]+(nrpcCol*j+i+0.5)*self.rpcModDim[0]
               ypos = -0.5*self.rpcTrayDim[1]+(j+0.5)*self.rpcModDim[1]
               zpos = '0cm'

               rpcm_in_t  = geom.structure.Position( 'RPCMod-'+str(nrpcCol*j+i)+'_in_'+self.name,
                                                     xpos,  ypos,  zpos)
               prpcm_in_t = geom.structure.Placement( 'placeRPCMod-'+str(nrpcCol*j+i)+'_in_'+self.name,
                                                      volume = rpcTray_lv,pos = rpcm_in_t,rot = "r90aboutX")
               rpcTray_lv.placements.append( prpcm_in_t.name )


        return
