#!/usr/bin/env python
'''
Subbuilder of CryostatBuilder
'''

import gegede.builder
from gegede import Quantity as Q

inch = 2.54
APAFrame_z = 231.59 - 2*(2*0.3175 + 0.15875) = 230.0025
APAFrameYSide_z = 5.08

class TPCBuilder(gegede.builder.Builder):


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self,
                  LightPaddle_x = Q('0.476cm'),
                  LightPaddle_y = Q('10.16cm'),
                  LightPaddle_z = Q('219.8425cm'),
                  **kwds):
        
        self.LightPaddle_x = LightPaddle_x
        self.LightPaddle_y = LightPaddle_y
        self.LightPaddle_z = LightPaddle_z
        
    def construct(self, geom):
        LightPaddleBox = geom.shapes.Box(self.name,
                                         dx=LightPaddle_x,
                                         dy=LightPaddle_y,
                                         dz=LightPaddle_z)
        LightPaddle_lv = geom.structure.Volume('vol'+self.name,
                                               material = 'Acrylic',
                                               shape    = LightPaddleBox)
        
