#!/usr/bin/env python
'''
Subbuilder of Detector
'''

import gegede.builder
from gegede import Quantity as Q


class MuIDBarrelBuilder(gegede.builder.Builder):
    '''
    Assemble RPC trays in the magnet yoke 
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, muidInDim=None, **kwds):
        if muidInDim is None:
            raise ValueError("No value given for muidInDim")

        self.defMat = "Steel"
        self.muidInDim  = muidInDim

        # Get RPC tray builders
        #self.RPCTraySmallBldr = self.get_builder('RPCTray_BarSmall')
        #self.RPCTrayMidBldr   = self.get_builder('RPCTray_BarMid')
        #self.RPCTrayBigBldr   = self.get_builder('RPCTray_BarBig')




    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):


        # Just like in the EndBuilder, calculate outer dimensions 
        #  using other configured parameters: number of planes, thicknesses...
        # For now I'm using the CDR reported dimensions:
        self.muidOutDim = list(self.muidInDim)
        self.muidOutDim[0] = Q('6.7m')
        self.muidOutDim[1] = Q('6.7m')


        # Define barrel as boolean, with hole to fit magnet inside
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
