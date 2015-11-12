#!/usr/bin/env python
'''
Subbuilder of Detector
'''

import gegede.builder

class MuIDBarrelBuilder(gegede.builder.Builder):
    '''
    Assemble RPC trays in the magnet yoke 
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, muidInDim=None, muidOutDim=None, **kwds):
        if muidOutDim is None:
            raise ValueError("No value given for muidOutDim")
        if muidInDim is None:
            raise ValueError("No value given for muidInDim")

        self.defMat = "Steel"
        self.muidInDim  = muidInDim
        self.muidOutDim = muidOutDim

        # Get RPC tray builders
        #self.RPCTraySmallBldr = self.get_builder('RPCTray_BarSmall')
        #self.RPCTrayMidBldr   = self.get_builder('RPCTray_BarMid')
        #self.RPCTrayBigBldr   = self.get_builder('RPCTray_BarBig')




    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):


        # Just like in the EndBuilder, calculate outer dimensions 
        #  using other configured parameters: number of planes, thicknesses...
        # If calculated different from configured, reset and print out a warning.


        # Define barrel as boolean, with hole to fit magnet inside
        #muidBarBox = geom.shapes.Box( 'MuIDOut',                 dx=0.5*self.muidOutDim[0], 
        #                               dy=0.5*self.muidOutDim[1], dz=0.5*self.muidOutDim[2]) 
        muidOut = geom.shapes.Box( 'MuIDOut',                 dx=0.5*self.muidOutDim[0], 
                                   dy=0.5*self.muidOutDim[1], dz=0.5*self.muidOutDim[2]) 
        muidIn = geom.shapes.Box(  'MuIDIn',                  dx=0.5*self.muidInDim[0], 
                                   dy=0.5*self.muidInDim[1],  dz=0.5*self.muidInDim[2]) 
        muidBarBox = geom.shapes.Boolean( self.name, type='subtraction', first=muidOut, second=muidIn )
        muidBar_lv = geom.structure.Volume('vol'+self.name, material=self.defMat, shape=muidBarBox)
        self.add_volume(muidBar_lv)


        # Get the RPC tray volumes
        #smallTray_lv = self.RPCTraySmallBldr.get_volume('volRPCTray_BarSmall')
        #midTray_lv   = self.RPCTrayMidBldr.get_volume('volRPCTray_BarMid')
        #bigTray_lv   = self.RPCTrayBigBldr.get_volume('volRPCTray_BarBig')


        
        # Place the RPC trays and steel sheets between, being mindful of rotation
        # Steel Sheets: just leave the default material of volMuID* steel 
        #   and leave spaces instead of placing explicit volumes

        return
