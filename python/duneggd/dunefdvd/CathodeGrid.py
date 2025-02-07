#!/usr/bin/env python
'''
CathodeGrid builder for DUNE FD-VD
'''

import gegede.builder
from utils import *

class CathodeGridBuilder(gegede.builder.Builder):
    def configure(self, **kwds):
        if not set(kwds).issubset(globals.Cathode): # no unknown keywords
            msg = 'Unknown parameter in: "%s"' % (', '.join(sorted(kwds.keys())), )
            raise ValueError(msg)

        # The builder hierarchy takes care of all the configuration parameters
        globals.Cathode = kwds

    def constructGrid(self, geom, cblock, cvoid, ny=4, nz=4):
        # recursively step through a 4x4 grid
        py = (2.5-ny)*globals.get("widthCathodeVoid") + (2.0-ny + (ny<=2))*globals.get("CathodeBorder")
        pz = (2.5-nz)*globals.get("lengthCathodeVoid") + (2.0-nz + (nz<=2))*globals.get("CathodeBorder")
        posij = geom.structure.Position('posCathodeSub'+str((4-ny)*4 + (5-nz)),
                                        x = Q('0cm'),
                                        y = py,
                                        z = pz)
        name = 'Cathode'+str((4-ny)*4 + (5-nz))
        if ny == 1 and nz == 1:
            name = 'CathodeGrid'
        cij = geom.shapes.Boolean(name,
                                  type = 'subtraction',
                                  first = cblock,
                                  second = cvoid,
                                  pos = posij)
        if ny == 1 and nz == 1:
            return cij
        elif nz == 1:
            return self.constructGrid(geom, cij, cvoid, ny-1, 4)
        else:
            return self.constructGrid(geom, cij, cvoid, ny, nz-1)

    def construct(self, geom):
        # for leaf builders, get the rest of the derived global parameters
        globals.SetDerived()
        # construction begins
        cathodeblockBox = geom.shapes.Box('CathodeBlock',
                                          dx=0.5*globals.get("heightCathode"),
                                          dy=0.5*globals.get("widthCathode"),
                                          dz=0.5*globals.get("lengthCathode"))
        cathodevoidBox = geom.shapes.Box('CathodeVoid',
                                          dx=0.5*globals.get("heightCathode") + Q('0.5cm'),
                                          dy=0.5*globals.get("widthCathodeVoid"),
                                          dz=0.5*globals.get("lengthCathodeVoid"))

        cathodegridBox = self.constructGrid(geom, cathodeblockBox, cathodevoidBox)
        cathodegridLV = geom.structure.Volume('vol'+cathodegridBox.name,
                                              material = "G10",
                                              shape = cathodegridBox)
        self.add_volume(cathodegridLV)
        return
