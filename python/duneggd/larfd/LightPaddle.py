#!/usr/bin/env python
'''
Subbuilder of DetEncBuilder
'''

import gegede.builder
import math
from gegede import Quantity as Q
from pint import UnitRegistry
import pandas as pd
ureg = UnitRegistry()

class LightPaddleBuilder(gegede.builder.Builder):

    def configure(self,
                  APAFrameZSide_y     = Q('4in'),
                  APAFrameZSide_z     = Q('4in'),                  
                  LightPaddle_x       = Q('0.476cm'),
                  LightPaddle_y       = Q('10.16cm'),
                  LightPaddle_z       = Q('219.8425cm'),
                  **kwds):
        self.LightPaddle_x   = LightPaddle_x
        self.LightPaddle_y   = LightPaddle_y
        self.LightPaddle_z   = LightPaddle_z
        self.APAFrameZSide_y = APAFrameZSide_y
        self.APAFrameZSide_z = APAFrameZSide_z
        
    def construct(self, geom):

        LightPaddleBox = geom.shapes.Box('LightPaddle',
                                         dx=0.5*self.LightPaddle_x,
                                         dy=0.5*self.LightPaddle_y,
                                         dz=0.5*self.LightPaddle_z)
        LightPaddle_lv = geom.structure.Volume('volLightPaddle',
                                               material = 'Acrylic',
                                               shape = LightPaddleBox)
        self.add_volume(LightPaddle_lv)
