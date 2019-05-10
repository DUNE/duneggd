#!/usr/bin/env python
'''An example GeGeDe module.

This provides some builder classes to build a Rubik's cube.

Warning: any resemblance between the result and an actual Rubik's cube
is purely accidental.  It's really just a 3x3x3 stack of blocks less
one at the origin.
'''

import gegede.builder
from gegede import Quantity as Q

class RubikBlockBuilder(gegede.builder.Builder):
    '''
    Build a corner, edge or center Rubik's cube block.
    '''
    def configure(self, location = "center", material = 'Plastic', size = Q("20cm"), **kwds):
        self.material, self.size = (material, size)
        pass

    def construct(self, geom):
        dim = (0.5*self.size,)*3
        shape = geom.shapes.Box(self.name + '_box_shape', *dim)
        lv = geom.structure.Volume(self.name+'_volume', material=self.material, shape=shape)
        self.add_volume(lv)
