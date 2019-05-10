#!/usr/bin/env python
'''An example GeGeDe module.

This provides some builder classes to build a Rubik's cube.

Warning: any resemblance between the result and an actual Rubik's cube
is purely accidental.  It's really just a 3x3x3 stack of blocks less
one at the origin.
'''

import gegede.builder
from gegede import Quantity as Q

class WorldBuilder(gegede.builder.Builder):
    '''
    Build a simple box world of given material and size.
    '''
    def configure(self, material = 'Air', size = Q("1m"), **kwds):
        self.material, self.size = (material, size)
        pass

    def construct(self, geom):
        dim = (0.5*self.size,)*3
        shape = geom.shapes.Box(self.name + '_box_shape', *dim)
        lv = geom.structure.Volume(self.name+'_volume', material=self.material, shape=shape)
        self.add_volume(lv)

        # Note: this block adds all LVs of all sub builders at default
        # position/rotation which is probably not what is wanted in
        # general.
        for sbname, sbld in self.builders.items():
            for svname, svol in sbld.volumes.items():
                pname = '%s_in_%s' % (svol.name, self.name)
                p = geom.structure.Placement(pname, volume = svol)
                lv.placements.append(pname)  
