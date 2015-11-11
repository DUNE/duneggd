#!/usr/bin/env python
'''
Subbuilder of Detector
'''

import gegede.builder

class MuIDEndBuilder(gegede.builder.Builder):
    '''
    Assemble configured number of RPC trays
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, muidDim=None, **kwds):
        if muidDim is None:
            raise ValueError("No value given for muidDim")

        self.material = "Steel"
        self.muidDim = muidDim

        #self.RPCTrayBldr = self.get_builder('RPCTray_End')
        


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        
        # Ccalculate the muidDim[2] (z dim) with other configured parameters: 
        #   number of planes, thicknesses...
        # If calculated different from configured, reset and print out a warning.



        # Make volume to be retrieved by DetectorBuilder
        muidEndBox = geom.shapes.Box( self.name,              dx=0.5*self.muidDim[0], 
                                      dy=0.5*self.muidDim[1], dz=0.5*self.muidDim[2]) 
        muidEnd_lv = geom.structure.Volume('vol'+self.name, material=self.material, shape=muidEndBox)
        self.add_volume(muidEnd_lv)


        # Get the RPC tray volume
        #tray_lv = self.RPCTrayBldr.get_volume('volRPCTray_End')



        
        # Place the RPC trays and steel sheets between in the configured way
        # Steel Sheets: just leave the default material of volMuID* steel 
        #   and leave spaces instead of placing explicit volumes



        return
