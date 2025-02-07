#!/usr/bin/env python
'''
World builder for DUNE FD-VD

                                  |--> FieldCage
World -> DetEnclosure -> Cryostat |--> TPC -> Wires
                                  |--> Arapuca
                                  |--> CathodeGrid
'''

import gegede.builder
from utils import *

class WorldBuilder(gegede.builder.Builder):
    def configure(self, **kwds):
        if not set(kwds).issubset(globals.World): # no unknown keywords
            msg = 'Unknown parameter in: "%s"' % (', '.join(sorted(kwds.keys())), )
            raise ValueError(msg)

        # The builder hierarchy takes care of all the configuration parameters
        globals.World = kwds

    def construct(self, geom):
        # get all the relevant stuff here
        globals.SetDerived()
        construct_materials(geom)
        construct_definitions(geom)

        # create the world box
        worldBox = geom.shapes.Box(self.name,
                                   dx=0.5*globals.get("DetEncX")+globals.get("RockThickness"),
                                   dy=0.5*globals.get("DetEncY")+globals.get("RockThickness"),
                                   dz=0.5*globals.get("DetEncZ")+globals.get("RockThickness"))

        # put it in the world volume
        worldLV = geom.structure.Volume('vol'+self.name, material="DUSEL_Rock", shape=worldBox)
        self.add_volume(worldLV)

        # get the detector enclosure sub-builder
        detenc = self.get_builder("DetEnclosure")
        detencLV = detenc.get_volume()

        # define where it goes inside the world volume
        detenc_pos = geom.structure.Position('pos'+detenc.name,
                                             x = globals.get("OriginXSet"),
                                             y = globals.get("OriginYSet"),
                                             z = globals.get("OriginZSet"))
        detenc_place = geom.structure.Placement('place'+detenc.name,
                                                volume = detencLV,
                                                pos = detenc_pos)

        # place it inside the world volume
        worldLV.placements.append(detenc_place.name)
        return
