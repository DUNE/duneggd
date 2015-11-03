#!/usr/bin/env python
'''
Example gegede builders for a trivial LAr geometry
'''

import gegede.builder

class STTBuilder(gegede.builder.Builder):

    def configure(self, sttDim, sttMaterial = 'Air', **kwds):
        self.material   = sttMaterial
        self.dimensions = sttDim

    def construct(self, geom):
        shape = geom.shapes.Box('STT', dx=self.dimensions[0], dy=self.dimensions[1], dz=self.dimensions[2])
        lv = geom.structure.Volume('vol'+self.name, material=self.material, shape=shape)
        self.add_volume(lv)
