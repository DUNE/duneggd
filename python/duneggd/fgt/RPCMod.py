#!/usr/bin/env python
'''
Subbuilder of RPCTray*Builder
'''

import gegede.builder

class RPCModBuilder(gegede.builder.Builder):
    '''
    Build the RPC modules, the effective unit of the MuID, 
    constituting an X and Y plane of RPC strips 
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, rpcModDim=['200cm','100cm','1.5cm'], resiplateDim=['196cm','96cm','0.8cm'], stripDim=['0.765cm','0.75cm','0.35cm'],
                 gas_thicknes='0.2cm', rpcModMat='Air', resiplateMat='fib_glass', gasMat='stGas_Ar', rpcReadoutMat='fib_glass', **kwds):
         self.rpcModMat     = rpcModMat
         self.rpcReadoutMat = rpcReadoutMat
         self.resiplateMat  = resiplateMat
         self.gasMat        = gasMat
         self.rpcModDim     = rpcModDim
         self.resiplateDim  = resiplateDim
         self.stripDim      = stripDim
         self.gas_thickness = gas_thickness



    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # define box and volume for whole RPCMod,
        # to be retrieved by RPCTray*Builder
        rpcMod = geom.shapes.Box('RPCModule_'+self.name,
                                 dx = 0.5*self.rpcModDim[0],
                                 dy = 0.5*self.rpcModDim[1],
                                 dz = 0.5*self.rpcModDim[2])
        rpcMod_lv = geom.structure.Volume('volRPCModule_'+self.name, material=self.rpcModMat, shape=rpcMod)
        # define box and volume for RPC strip
        rpcStrip = geom.shapes.Box('RPCStrip_'+self.name,
                                  dx = 0.5*self.resiplateDim[0],
                                  dy = 0.5*self.resiplateDim[1],
                                  dz = 0.5*self.rpcModDim[2])
        rpcStrip_lv = geom.structure.Volume('volRPCStrip_'+self.name, material=self.rpcreadoutMat, shape=rpcStrip)
        # define box and volume for resistive plate (maybe the same volume for anode and cathode?)
        resiplate = geom.shapes.Box('ResistivePlate_'+self.name,
                                    dx = 0.5*self.resiplateDim[0],
                                    dy = 0.5*self.resiplateDim[1],
                                    dz = 0.5*self.resiplateDim[2])
        resiplate_lv = geom.structure.Volume('volResistivePlate_'+self.name, material=self.resiplateMat, shape=resiplate)
        # define box and volume for gas in rpc
        rpcGas = geom.shape.Box('RPCGas_'+self.name,
                                dx = 0.5*self.resiplateDim[0],
                                dy = 0.5*self.resiplateDim[0],
                                dz = 0.5*gas_thickness)
        rpcGas_lv = geom.structure.Volume('volRPCGas_'+self.name, material=self.self.gasMat, shape=rpcGas)

        # position and place resistive plates in RPCMod
        pS_in_Module  = geom.structure.Placement( 'placeS_in_Module_'+self.name, volume = rpcStrip_lv )
        pRP_in_Module = geom.structure.Placement( 'placeRP_in_Module_'+self.name, volume = resiplate_lv )
        pG_in_Module  = geom.structure.Placement( 'placeG_in_Module_'+self.name, volume = rpcGas_lv )
        rpcMod_lv.placements.append( pS_in_Module.name )
        rpcMod_lv.placements.append( pRP_in_Module.name )
        rpcMod_lv.placements.append( pG_in_Module.name )
        self.add_volume(rpcMod_lv)

        # total nu of X and Y strips
        nXStrips = int(self.resiplateDim[0]/self.stripDim[0])
        nYStrips = int(self.resiplateDim[1]/self.stripDim[1])

        # for loop to position and place X strips in RPCMod
        for i in range(nXStrips):


                    xpos  = -0.5*self.rpcMod[0]+(i+0.5)*self.stripDim[0]
                    ypos  = '0cm'
                    zpos  = 0.5*self.rpcModDim[2]-0.5*self.stripDim[2]

                    xS_in_m  = geom.structure.Position( 'XStrip-'+str(i)+'_in_RPCModule_'+self.name,
                                                       xpos,  ypos,  zpos)
                    pxS_in_m = geom.structure.Placement( 'placeXStrip-'+str(i)+'_in_RPCModule_'+self.name,volume = rpcMod_lv,pos = xS_in_m,rot = "r90aboutX" )

        # for loop to position and place Y strips in RPCMod
        for j in range(nYStrips):


                    xpos  = '0cm'
                    ypos  = -0.5*self.rpcMod[1]+(j+0.5)*self.stripDim[1]
                    zpos  = -(0.5*self.rpcModDim[2]-0.5*self.stripDim[2])
                    yS_in_m  = geom.structure.Position( 'YStrip-'+str(j)+'_in_RPCModule_'+self.name,
                                                       xpos,  ypos,  zpos)
                    pyS_in_m = geom.structure.Placement( 'placeYStrip-'+str(j)+'_in_RPCModule_'+self.name,volume = rpcMod_lv,pos = yS_in_m,rot = "r90aboutX")


        rpcMod_lv.placements.append( pxS_in_m.name )
        rpcMod_lv.placements.append( pyS_in_m.name )

        return
