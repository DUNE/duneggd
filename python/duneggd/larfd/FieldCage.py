#!/usr/bin/env python
'''
Subbiulder of the Field Cage
'''

import gegede.builder
from gegede import Quantity as Q
from gegede import units

class FieldCageBuilder(gegede.builder.Builder):
    def configure(self,
                  BarWidth         = None,
                  BarHeight        = None,
                  CryostatInnerDim = None,
                  DSSClearance     = None,
                  BarSpacing       = None,
                  *kwds):

        self.BarWidth         = BarWidth 
        self.BarHeight        = BarHeight
        self.CryostatInnerDim = CryostatInnerDim 
        self.DSSClearance     = DSSClearance     
        self.BarSpacing       = BarSpacing
        pass



    def construct(self, geom):

        #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
        FieldCageBox = geom.shapes.Box('FieldCageBox',
                                       dx = 0.5*(self.CryostatInnerDim[0] - 2*self.DSSClearance[0])
                                       dy = 0.5*(self.CryostatInnerDim[1] - 2*self.DSSClearance[1])
                                       dz = 0.5*(self.CryostatInnerDim[2] - 2*self.DSSClearance[2]))
        FieldCage_lv = geom.structure.Volume('volFieldCage',
                                             material = 'Air',
                                             shape    = FieldCageBox)
        self.add_volume(FieldCage_lv)

        # Defining the long and short bars in the field cage
        Bar_l = geom.shapes.box('FieldCageBar_l',
                                dx = 0.5*self.BarWidth,
                                dy = 0.5*self.BarHeight,
                                dz = 0.5*self.CryostatInnerDim[2] - self.DSSClearance[2])
        Bar_s = geom.shapes.box('FieldCageBar_s',
                                dx = 0.5*self.BarWidth,
                                dy = 0.5*self.CryostatInnerDim[1] - self.DSSClearance[1],
                                dz = 0.5*self.BarHeight)
        Bar_l_lv = geom.structure.Volume('volLongBar' , material='Copper', shape=Bar_l)
        Bar_s_lv = geom.structure.Volume('volShortBar', material='Copper', shape=Bar_s)

        self.add_volume(Bar_l_lv)
        self.add_volume(Bar_s_lv)
