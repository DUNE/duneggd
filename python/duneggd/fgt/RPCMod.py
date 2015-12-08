#!/usr/bin/env python
'''
Subbuilder of RPCTray*Builder
'''

import gegede.builder
from gegede import Quantity as Q

class RPCModBuilder(gegede.builder.Builder):
    '''
    Build the RPC modules, the effective unit of the MuID, 
    constituting an X and Y plane of RPC strips 
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, 
                  rpcModDim    = [ Q('200cm'),   Q('100cm'),  Q('1.5cm')  ], 
                  resiplateDim = [ Q('196cm'),   Q('96cm'),   Q('0.3cm')  ], 
                  stripxDim    = [ Q('0.765cm'), Q('96cm'), Q('0.35cm') ],
                  stripyDim    = [ Q('196cm'), Q('0.75cm'), Q('0.35cm') ],
                  gas_gap      = Q('0.2cm'),
                  rpcModMat='Air', resiplateMat='bakelite', 
                  gasMat='rpcGas', rpcReadoutMat='honeycomb', **kwds):
         self.rpcModMat     = rpcModMat
         self.rpcReadoutMat = rpcReadoutMat
         self.resiplateMat  = resiplateMat
         self.gasMat        = gasMat
         self.rpcModDim     = rpcModDim
         self.resiplateDim  = resiplateDim
         self.stripxDim      = stripxDim
         self.stripyDim      = stripyDim
         self.gas_gap       = gas_gap


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # define box and volume for whole RPCMod,
        # to be retrieved by RPCTray*Builder
        rpcMod = geom.shapes.Box( self.name,
                                  dx = 0.5*self.rpcModDim[0],
                                  dy = 0.5*self.rpcModDim[1],
                                  dz = 0.5*self.rpcModDim[2])
        rpcMod_lv = geom.structure.Volume('vol'+self.name, material=self.rpcModMat, shape=rpcMod)
        # define box and volume for RPC strip
        rpcStripx = geom.shapes.Box( 'RPCStripx',
                                    dx = 0.5*self.stripxDim[0],
                                    dy = 0.5*self.stripxDim[1],
                                    dz = 0.5*self.stripxDim[2])
        rpcStripx_lv = geom.structure.Volume('volRPCStripx', material=self.rpcReadoutMat, shape=rpcStripx)
        rpcStripy = geom.shapes.Box( 'RPCStripy',
                                    dx = 0.5*self.stripyDim[0],
                                    dy = 0.5*self.stripyDim[1],
                                    dz = 0.5*self.stripyDim[2])
        rpcStripy_lv = geom.structure.Volume('volRPCStripy', material=self.rpcReadoutMat, shape=rpcStripy)
        # define box and volume for resistive plate (maybe the same volume for anode and cathode?)
        resiplate = geom.shapes.Box( 'ResistivePlate',
                                     dx = 0.5*self.resiplateDim[0],
                                     dy = 0.5*self.resiplateDim[1],
                                     dz = 0.5*self.resiplateDim[2])
        resiplate_lv = geom.structure.Volume('volResistivePlate', material=self.resiplateMat, shape=resiplate)
        # define box and volume for gas in rpc
        rpcGas = geom.shapes.Box( 'RPCGas',
                                  dx = 0.5*self.resiplateDim[0],
                                  dy = 0.5*self.resiplateDim[1],
                                  dz = 0.5*self.gas_gap)
        rpcGas_lv = geom.structure.Volume('volRPCGas', material=self.gasMat, shape=rpcGas)

        # position and place resistive plates in RPCMod
        #pRP_in_Module = geom.structure.Placement( 'placeRP_in_'+self.name, volume = resiplate_lv )
        pG_in_Module  = geom.structure.Placement( 'placeG_in_'+self.name, volume = rpcGas_lv )
        #rpcMod_lv.placements.append( pRP_in_Module.name )
        rpcMod_lv.placements.append( pG_in_Module.name )
        self.add_volume(rpcMod_lv)

        # total nu of X and Y strips
        nXStrips = int(self.resiplateDim[0]/self.stripxDim[0])
        nYStrips = int(self.resiplateDim[1]/self.stripyDim[1])

        #print 'RPCModBuilder: '+ str(nXStrips) +' X-Strips per RPC '
        #print 'RPCModBuilder: '+ str(nYStrips) +' Y-Strips per RPC '

        # for loop to position and place X strips in RPCMod
        for i in range(nXStrips):

            xpos  = -0.5*self.resiplateDim[0]+(i+0.5)*self.stripxDim[0]
            ypos  = '0cm'
            zpos  = 0.5*self.rpcModDim[2]-0.5*self.stripxDim[2]
            
            xS_in_m  = geom.structure.Position( 'XStrip-'+str(i)+'_in_'+self.name,
                                                xpos,  ypos,  zpos)
            pxS_in_m = geom.structure.Placement( 'placeXStrip-'+str(i)+'_in_'+self.name,
                                                 volume = rpcStripx_lv,pos = xS_in_m)#,rot = "r90aboutX" )
            rpcMod_lv.placements.append( pxS_in_m.name )
            #print str(i)+' x-strip pos: '+str(xpos)+str(ypos)+str(zpos)


        # for loop to position and place Y strips in RPCMod
        for j in range(nYStrips):

            xpos  = '0cm'
            ypos  = -0.5*self.resiplateDim[1]+(j+0.5)*self.stripyDim[1]
            zpos  = -0.5*self.rpcModDim[2]+0.5*self.stripyDim[2]
            yS_in_m  = geom.structure.Position( 'YStrip-'+str(j)+'_in_'+self.name,
                                                xpos,  ypos,  zpos)
            pyS_in_m = geom.structure.Placement( 'placeYStrip-'+str(j)+'_in_'+self.name,
                                                 volume = rpcStripy_lv,pos = yS_in_m)#,rot = "r90aboutX")
            rpcMod_lv.placements.append( pyS_in_m.name )
            #print str(j)+' y-strip pos: '+str(xpos)+str(ypos)+str(zpos)


        for k in range(2):

            xpos = '0cm'
            ypos = '0cm'
            zpos = -(0.5*self.gas_gap+0.5*self.resiplateDim[2])
            if (k==1):
                    zpos = -zpos
            RP_in_m  = geom.structure.Position( 'RP-'+str(k)+'_in_'+self.name,
                                                xpos,  ypos,  zpos)
            pRP_in_m = geom.structure.Placement( 'placeRP-'+str(k)+'_in_'+self.name,
                                                 volume = resiplate_lv,pos = RP_in_m)
            rpcMod_lv.placements.append( pRP_in_m.name )


        return
