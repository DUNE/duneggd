#!/usr/bin/env python
'''An example GeGeDe module.

This provides some builder classes to build a Rubik's cube.

Warning: any resemblance between the result and an actual Rubik's cube
is purely accidental.  It's really just a 3x3x3 stack of blocks less
one at the origin.
'''

import gegede.builder
from gegede import Quantity as Q

class OuterBoxBiulder(gegede.builder.Builder):
    def configure(self, material='Air', size=Q('1m'), **kwds):
        self.material = material
        self.size     = size
        pass

    def construct(self, geom):

        # Construct the outer box
        outerBoxDim   = (0.5*self.size,)*3
        outerBoxShape = geom.shapes.Box(self.name + '_box_shape', *outerBoxDim)
        outerBox_lv   = geom.structure.Volume(self.name + '_volume', material=self.material, shape=outerBoxShape)
        self.add_volume(outerBox_lv)

        # build the sub structures
        block_volumes = []
        for key, value in self.builders.items():
            block_volumes.append(list(value.volumes.items())[0][1])

        lv = block_volumes[0]
        id = 'block0'
        pos = geom.structure.Position(id + '_pos', x=Q('0.5m'),y=Q('0.5m'),z=Q('0.5m'))
        placement = geom.structure.Placement(id+'_place', volume=lv, pos=pos)
        outerBox_lv.placements.append(id+'_place')

        lv = block_volumes[1]
        id = 'block1'
        pos = geom.structure.Position(id + '_pos', x=Q('0.5m'),y=Q('0.5m'),z=Q('0.5m'))
        placement = geom.structure.Placement(id+'_place', volume=lv, pos=pos)
        outerBox_lv.placements.append(id+'_place')

        lv = block_volumes[2]
        id = 'block2'
        pos = geom.structure.Position(id + '_pos', x=Q('0.5m'),y=Q('0.5m'),z=Q('0.5m'))
        placement = geom.structure.Placement(id+'_place', volume=lv, pos=pos)
        outerBox_lv.placements.append(id+'_place')

        return
        
