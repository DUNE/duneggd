#!/usr/bin/env python
'''
Arapuca builder for DUNE FD-VD
'''

import gegede.builder
from utils import *

class ArapucaBuilder(gegede.builder.Builder):
    def configure(self, **kwds):
        if not set(kwds).issubset(globals.Arapuca): # no unknown keywords
            msg = 'Unknown parameter in: "%s"' % (', '.join(sorted(kwds.keys())), )
            raise ValueError(msg)

        # The builder hierarchy takes care of all the configuration parameters
        globals.Arapuca = kwds

    def construct(self, geom):
        # for leaf builders, get the rest of the derived global parameters
        globals.SetDerived()
        # define all the shapes
        a_out = (globals.get("ArapucaOut_x"), globals.get("ArapucaOut_y"), globals.get("ArapucaOut_z"))
        a_acc = (globals.get("ArapucaAcceptanceWindow_x"),
                 globals.get("ArapucaAcceptanceWindow_y"),
                 globals.get("ArapucaAcceptanceWindow_z"))

        arapucaEnclosureBox = geom.shapes.Box('ArapucaEnclosure',
                                              dx = 0.5*a_out[0],
                                              dy = 0.5*a_out[1],
                                              dz = 0.5*a_out[2])
        arapucaOutBox = geom.shapes.Box('ArapucaOut',
                                        dx = 0.5*a_out[0] - Q('0.025cm'),
                                        dy = 0.5*a_out[1] - Q('0.025cm'),
                                        dz = 0.5*a_out[2] - Q('0.025cm'))
        arapucaInBox = geom.shapes.Box('ArapucaIn',
                                       dx = 0.5*globals.get("ArapucaIn_x"),
                                       dy = 0.5*a_out[1],
                                       dz = 0.5*globals.get("ArapucaIn_z"))
        arapucaWallsBox = geom.shapes.Boolean('ArapucaWalls',
                                              type = 'subtraction',
                                              first = arapucaOutBox,
                                              second = arapucaInBox,
                                              pos = geom.structure.Position('posArapucaSub',
                                                                            x = Q('0cm'),
                                                                            y = 0.5*a_out[1],
                                                                            z = Q('0cm'))
                                              )

        arapucaAccBox = geom.shapes.Box('ArapucaAcceptanceWindow',
                                        dx = 0.5*a_acc[0],
                                        dy = 0.5*a_acc[1],
                                        dz = 0.5*a_acc[2])
        arapucaDoubleInBox = geom.shapes.Box('ArapucaDoubleIn',
                                             dx = 0.5*globals.get("ArapucaIn_x"),
                                             dy = 0.5*a_out[1] + Q('0.5cm'),
                                             dz = 0.5*globals.get("ArapucaIn_z"))
        arapucaDoubleWallsBox = geom.shapes.Boolean('ArapucaDoubleWalls',
                                                    type = 'subtraction',
                                                    first = arapucaOutBox,
                                                    second = arapucaDoubleInBox,
                                                    pos = geom.structure.Position('posArapucaDoubleSub',
                                                                                  x = Q('0cm'),
                                                                                  y = Q('0cm'),
                                                                                  z = Q('0cm'))
                                                    )
        arapucaDoubleAccBox = geom.shapes.Box('ArapucaDoubleAcceptanceWindow',
                                              dx = 0.5*a_acc[0],
                                              dy = 0.5*a_out[1] - Q('0.01cm'),
                                              dz = 0.5*a_acc[2])

        # define all the sub-volumes
        opdetsens_LV = geom.structure.Volume('volOpDetSensitive',
                                             material = "LAr",
                                             shape = arapucaAccBox)
        arapuca_LV = geom.structure.Volume('Arapuca',
                                           material = "G10",
                                           shape = arapucaWallsBox)
        # define the larger volumes
        arapucaenc_LV = geom.structure.Volume('volArapuca',
                                              material = "LAr",
                                              shape = arapucaEnclosureBox)
        # add it to the builder
        self.add_volume(arapucaenc_LV)

        # now do the placements for each
        arapucaenc_LV     = self.placeArapuca(geom, arapucaenc_LV, arapuca_LV, opdetsens_LV,
                                              opdet_pos = geom.structure.Position('opdetshift',
                                                                                  x = Q('0cm'),
                                                                                  y = 0.5*a_acc[1],
                                                                                  z = Q('0cm')))
        # Deal with double-sided cathode arapucas, for the case of 2 drift volumes
        if globals.get("nCRM_x") == 2:
            # define all the sub-volumes
            opdetsens2_LV = geom.structure.Volume('volOpDetSensitiveDouble',
                                                 material = "LAr",
                                                 shape = arapucaDoubleAccBox)
            arapuca2_LV = geom.structure.Volume('ArapucaDouble',
                                                material = "G10",
                                                shape = arapucaDoubleWallsBox)
            # define the larger volumes
            arapucaenc2_LV = geom.structure.Volume('volArapucaDouble',
                                                   material = "LAr",
                                                   shape = arapucaEnclosureBox)
            # add it to the builder
            self.add_volume(arapucaenc2_LV)

            # now do the placements for each
            arapucaenc2_LV     = self.placeArapuca(geom, arapucaenc2_LV, arapuca2_LV, opdetsens2_LV,
                                                   opdet_pos="posCenter")
        return

    # helper for arapuca placements
    def placeArapuca(self, geom, arapucaenc_LV, arapuca_LV, opdet_LV, opdet_pos, rotArapuca="rIdentity"):
        place1 = geom.structure.Placement('placearapuca_in'+arapucaenc_LV.name,
                                          volume = arapuca_LV,
                                          pos = "posCenter",
                                          rot = rotArapuca
                                          )
        place2 = geom.structure.Placement('placeopdet_in'+arapucaenc_LV.name,
                                          volume = opdet_LV,
                                          pos = opdet_pos,
                                          )
        arapucaenc_LV.placements.append(place1.name)
        arapucaenc_LV.placements.append(place2.name)
        return arapucaenc_LV
