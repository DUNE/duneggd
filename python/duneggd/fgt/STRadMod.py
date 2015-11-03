#!/usr/bin/env python
'''
Example gegede builders for a trivial LAr geometry
'''

import gegede.builder

class STRadModBuilder(gegede.builder.Builder):

    def configure(self, stube_rmin, stube_rmax, stubeLength, stubeMaterial, **kwds):
        self.material   = stubeMaterial
        self.stube_rmin = stube_rmin
        self.stube_rmax = stube_rmax
        self.stubeLength = stubeLength

    def construct(self, geom):
        shape = geom.shapes.Tubs('StrawTube', rmin=self.stube_rmin, rmax=self.stube_rmax, dz=self.stubeLength)
        lv = geom.structure.Volume('vol'+self.name, material=self.material, shape=shape)
        self.add_volume(lv)
