#!/usr/bin/env python
'''
Example gegede builders for a trivial LAr geometry
'''

import gegede.builder

class DetEncBuilder(gegede.builder.Builder):

    def configure(self, detEncDim, detEncMaterial = 'Air', **kwds):
        self.material   = detEncMaterial
        self.dimensions = detEncDim

    def construct(self, geom):
        encBox = geom.shapes.Box('DetEnclosure', dx=self.dimensions[0], dy=self.dimensions[1], dz=self.dimensions[2])
        lv = geom.structure.Volume('vol'+self.name, material=self.material, shape=encBox)
        self.add_volume(lv)
