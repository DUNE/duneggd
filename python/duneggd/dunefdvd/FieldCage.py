#!/usr/bin/env python
'''
FieldCage builder for DUNE FD-VD
'''

import gegede.builder
from utils import *

class FieldCageBuilder(gegede.builder.Builder):
    def configure(self, **kwds):
        if not set(kwds).issubset(globals.FieldCage): # no unknown keywords
            msg = 'Unknown parameter in: "%s"' % (', '.join(sorted(kwds.keys())), )
            raise ValueError(msg)

        # The builder hierarchy takes care of all the configuration parameters
        globals.FieldCage = kwds

    def constructShortTubeSlim(self, geom):
        # construction begins
        fsshorttubeL = globals.get("FieldShaperShortTubeLength")
        if globals.get("nCRM_y") != 8:
            fieldshapershortTubeSlim = geom.shapes.Tubs("FieldShaperShorttubeSlim",
                                                        rmin = globals.get("FieldShaperInnerRadius"),
                                                        rmax = globals.get("FieldShaperOuterRadiusSlim"),
                                                        dz   = 0.5*fsshorttubeL,
                                                        sphi = Q("0deg"),
                                                        dphi = Q("360deg"))
            return fieldshapershortTubeSlim
        else:

            fcarapucaWL = globals.get("FieldCageArapucaWindowLength")


            fieldshapershortTubeWindowSlim = geom.shapes.Tubs("FieldShaperShorttubeWindowSlim",
                                                              rmin = globals.get("FieldShaperInnerRadius"),
                                                              rmax = globals.get("FieldShaperOuterRadiusSlim"),
                                                              dz   = 0.5*fcarapucaWL,
                                                              sphi = Q("0deg"),
                                                              dphi = Q("360deg"))
            fieldshapershortTubeWindowNotSlim = geom.shapes.Tubs("FieldShaperShorttubeWindowNotSlim",
                                                                  rmin = globals.get("FieldShaperInnerRadius"),
                                                                  rmax = globals.get("FieldShaperOuterRadius"),
                                                                  dz   = 0.25*(fsshorttubeL - fcarapucaWL),
                                                                  sphi = Q("0deg"),
                                                                  dphi = Q("360deg"))
            fsunionWindow1 = geom.shapes.Boolean("FSunionWindow1",
                                                 type = "union",
                                                 first = fieldshapershortTubeWindowSlim,
                                                 second = fieldshapershortTubeWindowNotSlim,
                                                 pos = geom.structure.Position("posFieldShaperShortTube_shift1",
                                                                               x = Q('0cm'),
                                                                               y = Q('0cm'),
                                                                               z = 0.25*(fcarapucaWL+fsshorttubeL)))
            fieldshapershortTubeSlim = geom.shapes.Boolean("FieldShaperShorttubeSlim",
                                                           type = "union",
                                                           first = fsunionWindow1,
                                                           second = fieldshapershortTubeWindowNotSlim,
                                                           pos = geom.structure.Position("posFieldShaperShortTube_shift2",
                                                                                         x = Q('0cm'),
                                                                                         y = Q('0cm'),
                                                                                         z = -0.25*(fcarapucaWL+fsshorttubeL)))
            return fieldshapershortTubeSlim



    def construct(self, geom):
        # for leaf builders, get the rest of the derived global parameters
        globals.SetDerived()

        fieldshapercornerTorus = geom.shapes.Torus("FieldShaperCorner",
                                                   rmin = globals.get("FieldShaperInnerRadius"),
                                                   rmax = globals.get("FieldShaperOuterRadius"),
                                                   rtor = globals.get("FieldShaperTorRad"),
                                                   deltaphi = Q("90deg"),
                                                   startphi = Q("0deg"))
        fieldshaperlongTube = geom.shapes.Tubs("FieldShaperLongtube",
                                               rmin = globals.get("FieldShaperInnerRadius"),
                                               rmax = globals.get("FieldShaperOuterRadius"),
                                               dz = 0.5*globals.get("FieldShaperLongTubeLength"),
                                               sphi = Q("0deg"),
                                               dphi = Q("360deg"))
        fieldshapershortTube = geom.shapes.Tubs("FieldShaperShorttube",
                                                rmin = globals.get("FieldShaperInnerRadius"),
                                                rmax = globals.get("FieldShaperOuterRadius"),
                                                dz = 0.5*globals.get("FieldShaperShortTubeLength"),
                                                sphi = Q("0deg"),
                                                dphi = Q("360deg"))
        fieldshaperlongTubeSlim = geom.shapes.Tubs("FieldShaperLongtubeSlim",
                                                   rmin = globals.get("FieldShaperInnerRadius"),
                                                   rmax = globals.get("FieldShaperOuterRadiusSlim"),
                                                   dz = 0.5*globals.get("FieldShaperLongTubeLength"),
                                                   sphi = Q("0deg"),
                                                   dphi = Q("360deg"))
        fieldshapershortTubeSlim = self.constructShortTubeSlim(geom)

        stlength = globals.get("FieldShaperShortTubeLength")
        ltlength = globals.get("FieldShaperLongTubeLength")
        torrad   = globals.get("FieldShaperTorRad")

        xz_positions = [(-torrad, 0.5*ltlength),
                        (-torrad - 0.5*stlength, 0.5*ltlength + torrad),
                        (-torrad -stlength, 0.5*ltlength),
                        (-stlength - 2*torrad, Q('0cm')),
                        (-torrad -stlength, -0.5*ltlength),
                        (-torrad - 0.5*stlength, -0.5*ltlength - torrad),
                        (-torrad, -0.5*ltlength)
                        ]
        rotations = ["rPlus90AboutX",
                     "rPlus90AboutY",
                     "rPlus90AboutXMinux90AboutY",
                     "rIdentity",
                     "rPlus90AboutXPlus180AboutY",
                     "rPlus90AboutY",
                     "rPlus90AboutXPlus90AboutY"
                    ]

        unionShape = fieldshaperlongTube
        unionShapeSlim = fieldshaperlongTubeSlim
        for ui in range(1, 8):
            secondShape = fieldshapercornerTorus
            secondShapeSlim = fieldshapercornerTorus
            if ui % 2 == 0 and ui % 4 != 0:
                secondShape = fieldshapershortTube
                secondShapeSlim = fieldshapershortTubeSlim
            elif ui % 2 == 0:
                secondShape = fieldshaperlongTube
                secondShapeSlim = fieldshaperlongTubeSlim

            # follow perl-script naming convention
            fs_name = "FSunion"+str(ui)
            fs_slim_name = "FSunionSlim"+str(ui)
            if ui == 7:
                fs_name = "FieldShaperSolid"
                fs_slim_name = "FieldShaperSolidSlim"
            pos_name = "esquinapos"+str(ui)
            pos_slim_name = "esquinapos"+str(ui+7) if ui < 4 else "esquinapos"+str(ui+6)
            if ui == 4:
                pos_slim_name = "esquinapos4Slim"

            unionShape = geom.shapes.Boolean(fs_name,
                                             type = 'union',
                                             first = unionShape,
                                             second = secondShape,
                                             pos = geom.structure.Position(pos_name,
                                                                           x = xz_positions[ui-1][0],
                                                                           y = Q('0cm'),
                                                                           z = xz_positions[ui-1][1]),
                                             rot = rotations[ui-1]
                                             )
            unionShapeSlim = geom.shapes.Boolean(fs_slim_name,
                                                 type = 'union',
                                                 first = unionShapeSlim,
                                                 second = secondShapeSlim,
                                                 pos = geom.structure.Position(pos_slim_name,
                                                                               x = xz_positions[ui-1][0],
                                                                               y = Q('0cm'),
                                                                               z = xz_positions[ui-1][1]),
                                                 rot = rotations[ui-1]
                                                 )

        # define the logical volumes
        fieldshaper_LV = geom.structure.Volume('volFieldShaper',
                                               material = "ALUMINIUM_Al",
                                               shape = unionShape)
        fieldshaperSlim_LV = geom.structure.Volume('volFieldShaperSlim',
                                                   material = "ALUMINIUM_Al",
                                                   shape = unionShapeSlim)

        # add the volumes
        self.add_volume(fieldshaper_LV, fieldshaperSlim_LV)
        return
