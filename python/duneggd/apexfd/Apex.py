#!/usr/bin/env python
'''
APEX builder for DUNE FD-VD
'''

import gegede.builder
from utils import *

class ApexBuilder(gegede.builder.Builder):
    def configure(self, **kwds):
        if not set(kwds).issubset(globals.Apex): # no unknown keywords
            msg = 'Unknown parameter in: "%s"' % (', '.join(sorted(kwds.keys())), )
            raise ValueError(msg)

        # The builder hierarchy takes care of all the configuration parameters
        globals.Apex = kwds

    def construct(self, geom):
        # for leaf builders, get the rest of the derived global parameters
        globals.SetDerived()
        # define all the shapes
        ara = (globals.get("Arapuca_x"), globals.get("Arapuca_y"), globals.get("Arapuca_z"))
        ptp_width = globals.get("ptpWidth")


        arapuca = geom.shapes.Box('Arapuca', dx=0.5*ara[0], dy=0.5*ara[1], dz=0.5*ara[2])
        ptp = geom.shapes.Box('pTP', dx=0.5*ara[0], dy=0.5*ara[1], dz=0.5*ptp_width)
        backing = geom.shapes.Box('Backing', dx=0.5*ara[0], dy=0.5*ara[1], dz=0.5*ptp_width)
        arapucaEnc = geom.shapes.Box('ArapucaEnc', dx=0.5*ara[0], dy=0.5*ara[1], dz=0.5*ara[2]+ptp_width)

        # define all the sub-volumes
        arapuca_LV = geom.structure.Volume('volArapuca',
                                           material = "Acrylic",
                                           shape = arapuca)
        ptp_LV = geom.structure.Volume('volPTP', 
                                       material = "pTP",
                                       shape = ptp)
        backing_LV = geom.structure.Volume('volBacking',
                                           material = "Mylar",
                                           shape = backing)
        backing_OS = geom.surfaces.SkinSurface("AraBackingSurface",
                                                surface="MylarSurface",
                                                volume=backing_LV.name)

        # define the larger volume
        arapucaEnc_LV = geom.structure.Volume('ArapucaEnc',
                                              material = "LAr",
                                              shape = arapucaEnc)
        # place volumes
        ptp_pos = geom.structure.Position('pTP_pos', x=Q('0cm'), y=Q('0cm'), z=0.5*ara[2] + 0.5*ptp_width)
        backing_pos = geom.structure.Position('Backing_pos', x=Q('0cm'), y=Q('0cm'), z=-(0.5*ara[2] + 0.5*ptp_width))

        arapuca_place = geom.structure.Placement('Arapuca_place',
                                                 volume = arapuca_LV,
                                                 pos = "posCenter")
        ptp_place = geom.structure.Placement('pTP_place', 
                                             volume = ptp_LV,
                                             pos = ptp_pos)
        backing_place = geom.structure.Placement('Backing_place', 
                                                 volume = backing_LV,
                                                 pos = backing_pos)

        # add it to the builder
        arapucaEnc_LV.placements.append(arapuca_place.name)
        arapucaEnc_LV.placements.append(ptp_place.name)
        arapucaEnc_LV.placements.append(backing_place.name)
        
        arapucaEnc_LV.params.append(("vis", "invisible"))

        self.add_volume(arapucaEnc_LV)
