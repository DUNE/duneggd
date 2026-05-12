#!/usr/bin/env python
'''
DetEnclosure builder for DUNE FD-VD
'''

import gegede.builder
from utils import *
import math as m

class DetEnclosureBuilder(gegede.builder.Builder):
    def configure(self, **kwds):
        if not set(kwds).issubset(globals.Enclosure): # no unknown keywords
            msg = 'Unknown parameter in: "%s"' % (', '.join(sorted(kwds.keys())), )
            raise ValueError(msg)

        # The builder hierarchy takes care of all the configuration parameters
        globals.Enclosure = kwds

    def construct_simplified(self, geom):

        detencBox = geom.shapes.Box(self.name,
                                    dx=0.5*globals.get("DetEncX"),
                                    dy=0.5*globals.get("DetEncY"),
                                    dz=0.5*globals.get("DetEncZ"))
        detencLV = geom.structure.Volume('vol'+self.name, material="Air", shape=detencBox)
        self.add_volume(detencLV)

        # get the cryostat volume from the subbuilder and place it
        cryostat = self.get_builder("Cryostat")
        cryostatLV = cryostat.get_volume()
        posCryoInDetEnc = geom.structure.Position("posCryoInDetEnc", x=globals.get("posCryoInDetEnc_x"),
                                                                     y=globals.get("posCryoInDetEnc_y"),
                                                                     z=globals.get("posCryoInDetEnc_z"))
        cryostat_place = geom.structure.Placement(cryostatLV.name+'_PV_InDetEnc',
                                                  volume = cryostatLV,
                                                  pos = posCryoInDetEnc)
        detencLV.placements.append(cryostat_place.name)

        # get the outer structure volumes
        foampadblockBox = geom.shapes.Box('FoamPadBlock',
                                          dx=0.5*globals.get("Cryostat_x") + globals.get("FoamPadding"),
                                          dy=0.5*globals.get("Cryostat_y") + globals.get("FoamPadding"),
                                          dz=0.5*globals.get("Cryostat_z") + globals.get("FoamPadding"))
        foampaddingBox = geom.shapes.Boolean('FoamPadding',
                                             type = 'subtraction',
                                             first = foampadblockBox,
                                             second = geom.get_shape(cryostatLV),
                                             pos = "posCenter")
        steelsupportblockBox = geom.shapes.Box('SteelSupportBlock',
                                               dx=0.5*globals.get("Cryostat_x") +   \
                                                  globals.get("FoamPadding") +      \
                                                  globals.get("SteelSupport_x"),
                                               dy=0.5*globals.get("Cryostat_y") +   \
                                                  globals.get("FoamPadding") +      \
                                                  globals.get("SteelSupport_y"),
                                               dz=0.5*globals.get("Cryostat_z") +   \
                                                  globals.get("FoamPadding") +      \
                                                  globals.get("SteelSupport_z"))
        steelsupportBox = geom.shapes.Boolean('SteelSupport',
                                              type = 'subtraction',
                                              first = steelsupportblockBox,
                                              second = foampadblockBox,
                                              pos = "posCenter")

        foampaddingLV = geom.structure.Volume('vol'+foampaddingBox.name,
                                              material = "fibrous_glass",
                                              shape = foampaddingBox)
        steelsupportLV = geom.structure.Volume('vol'+steelsupportBox.name,
                                              material = "AirSteelMixture",
                                              shape = steelsupportBox)

        # define the placements and put it inside the detector enclosure
        foampadding_place = geom.structure.Placement('place'+foampaddingBox.name,
                                                     volume = foampaddingLV,
                                                     pos = "posCryoInDetEnc")
        steelsupport_place = geom.structure.Placement('place'+steelsupportBox.name,
                                                     volume = steelsupportLV,
                                                     pos = "posCryoInDetEnc")
        detencLV.placements.append(foampadding_place.name)
        detencLV.placements.append(steelsupport_place.name)

    def construct_cavern(self, geom):

        r = globals.get("archRadius")
        theta = globals.get("archHalfAngle")

        # Define the box for the detector enclosure
        detencBox = geom.shapes.Box(self.name,
                                    dx=0.5*globals.get("DetEncX"),
                                    dy=0.5*globals.get("DetEncY"),
                                    dz=0.5*globals.get("DetEncZ"))
        encArch   = geom.shapes.Tubs(self.name+'Arch',
                                     rmin = Q('0cm'),
                                     rmax = r,
                                     dz   = 0.5*globals.get("DetEncZ"),
                                     sphi = -theta,
                                     dphi = 2*theta)

        elevation = globals.get("DetEncX")/2. - m.cos(theta.to('radians')) * r
        arch_pos       = geom.structure.Position(self.name+'_ArchPos', elevation, Q('0m'), Q('0m'))
        encTotal  = geom.shapes.Boolean(self.name+"Total",
                                        type   = 'union',
                                        first  = detencBox,
                                        second = encArch,
                                        pos    = arch_pos)

        # Place RadioRock shell around the detector enclosure
        rock_t = globals.get("RadioRockThickness")
        RockBox   = geom.shapes.Box('RadioRockBox',
                                    dx=0.5*(globals.get("DetEncX"))+0.5*rock_t,
                                    dy=0.5*(globals.get("DetEncY"))+rock_t,
                                    dz=0.5*(globals.get("DetEncZ"))+rock_t)

        y         = globals.get("DetEncY") + 2*rock_t
        rplus     = r + rock_t
        RockAngle = m.degrees(m.asin(y/(2*rplus)))
        elevation = globals.get("DetEncX")/2. - m.cos(m.radians(RockAngle)) * rplus + 0.5*rock_t
        Tube_pos  = geom.structure.Position('posTube', elevation, Q('0m'), Q('0m'))

        RockTup = geom.shapes.Tubs('RockArch',
                                   rmin = Q('0cm'),
                                   rmax = rplus,
                                   dz   = 0.5*globals.get("DetEncZ") + rock_t,
                                   sphi = -Q(RockAngle, 'deg'),
                                   dphi = 2*Q(RockAngle, 'deg'))

        RockBox = geom.shapes.Boolean('RockAddition',
                                      type   = 'union',
                                      first  = RockBox,
                                      second = RockTup,
                                      pos    = Tube_pos)

        detencLV = geom.structure.Volume('volDetEnclosure', material='Air', shape=RockBox)
        self.add_volume(detencLV)

        pos       = geom.structure.Position('posFirstSub', 0.5*rock_t, Q('0m'), Q('0m'))
        RockBox   = geom.shapes.Boolean('FirstSub',
                                        type   = 'subtraction',
                                        first  = RockBox,
                                        second = encTotal,
                                        pos    = pos)

        rockLV   = geom.structure.Volume('volRadioRockShell', material='RadioAverageDuneRock', shape=RockBox)
        rock_pos  = geom.structure.Position('posRock', Q('0m'), Q('0m'), Q('0m'))
        placeRock = geom.structure.Placement('placeRock', volume=rockLV, pos=rock_pos)
        detencLV.placements.append(placeRock.name)

        # Place Concrete on the floor
        conc_t = globals.get("ConcreteThickness")
        grout_t = globals.get("GroutThickness")
        ConcreteBox   = geom.shapes.Box('ConcreteBox',
                                        dx=0.5*conc_t,
                                        dy=0.5*globals.get("DetEncY"),
                                        dz=0.5*globals.get("DetEncZ"))
        GroutBox   = geom.shapes.Box('GroutBox',
                                     dx=0.5*grout_t,
                                     dy=0.5*globals.get("DetEncY"),
                                     dz=0.5*globals.get("DetEncZ"))

        ConcreteLV   = geom.structure.Volume('volConcrete', material='RadioConcretePeteLein', shape=ConcreteBox)
        GroutLV      = geom.structure.Volume('volGrout', material='RadioConcretePeteLein', shape=GroutBox)

        conc_x = -0.5*globals.get("DetEncX") + 0.5*rock_t + 0.5*conc_t
        grout_x = -0.5*globals.get("DetEncX") + 0.5*rock_t + conc_t + 0.5*grout_t
        ConcretePos   = geom.structure.Position ('posConcrete', conc_x, Q('0m'), Q('0m'))
        GroutPos      = geom.structure.Position ('posGrout', grout_x, Q('0m'), Q('0m'))

        placeConcrete = geom.structure.Placement('placeConcreteInDetEnc', volume=ConcreteLV, pos=ConcretePos)
        placeGrout    = geom.structure.Placement('placeGroutInDetEnc', volume=GroutLV, pos=GroutPos)
        detencLV.placements.append(placeConcrete.name)
        detencLV.placements.append(placeGrout.name)

        # Place shotcrete shell on walls and ceiling
        shot_t = globals.get("ShotCreteThickness")
        ShotOuterBox    = geom.shapes.Box('ShotOuterBox',
                                          dx=0.5*globals.get("DetEncX"),
                                          dy=0.5*globals.get("DetEncY"),
                                          dz=0.5*globals.get("DetEncZ"))
        ShotOuterArch   = geom.shapes.Tubs('ShotOuterArch',
                                     rmin = Q('0cm'),
                                     rmax = r,
                                     dz   = 0.5*globals.get("DetEncZ"),
                                     sphi = -theta,
                                     dphi = 2*theta)
        elevation     = globals.get("DetEncX")/2 - m.cos(theta.to('radians')) * r
        Pos           = geom.structure.Position('ShotOuterArchPos', elevation, Q('0m'), Q('0m'))
        ShotOuterBox  = geom.shapes.Boolean("ShotOuterBoolAdd",
                                        type   = 'union',
                                        first  = ShotOuterBox,
                                        second = ShotOuterArch,
                                        pos    = Pos)

        ShotInnerBox    = geom.shapes.Box('ShotInnerBox',
                                          dx=0.5*globals.get("DetEncX"),
                                          dy=0.5*globals.get("DetEncY") - shot_t,
                                          dz=0.5*globals.get("DetEncZ") - shot_t)
        ShotInnerBoxPos = geom.structure.Position("ShotInnerBoxPos", Q('0m'), Q('0m'), Q('0m'))
        ShotOuterBox    = geom.shapes.Boolean("ShotInnerBoxSub",
                                              type   = 'subtraction',
                                              first  = ShotOuterBox,
                                              second = ShotInnerBox,
                                              pos    = ShotInnerBoxPos)

        y         = globals.get("DetEncY") - 2*shot_t
        rminus     = r - shot_t
        RockAngle = m.degrees(m.asin(y/(2*rminus)))
        elevation = 0.5*globals.get("DetEncX") - (m.cos(m.radians(RockAngle)) * rminus) - 0.5*shot_t
        ShotInnerArch   = geom.shapes.Tubs('ShotInnerArch',
                                     rmin = Q('0cm'),
                                     rmax = rminus,
                                     dz   = 0.5*globals.get("DetEncZ") - shot_t,
                                     sphi = -Q(RockAngle, 'deg'),
                                     dphi = Q(RockAngle, 'deg')*2)
        Pos           = geom.structure.Position('ShotInnerArchPos', elevation, Q('0m'), Q('0m'))
        ShotOuterBox  = geom.shapes.Boolean("ShotInnerArchSub",
                                            type   = 'subtraction',
                                            first  = ShotOuterBox,
                                            second = ShotInnerArch,
                                            pos    = Pos)

        ConcSubBox = geom.shapes.Box('ConcSubBox',
                                     dx=0.5*(conc_t + grout_t),
                                     dy=0.5*globals.get("DetEncY"),
                                     dz=0.5*globals.get("DetEncZ"))
        ConcSubPos = geom.structure.Position('ConcSubPos',
                                             -0.5*(globals.get("DetEncX") - conc_t - grout_t),
                                             Q('0m'),
                                             Q('0m'))
        ShotOuterBox  = geom.shapes.Boolean('ShotOuterMinusBox',
                                            type   = 'subtraction',
                                            first  = ShotOuterBox,
                                            second = ConcSubBox,
                                            pos    = ConcSubPos)

        ShotLV = geom.structure.Volume('volShotbox', shape=ShotOuterBox, material='RadioShotcretePeteLein')
        ShotPos = geom.structure.Position('posShotBox', 0.5*rock_t, Q('0m'), Q('0m'))
        ShotPla = geom.structure.Placement('placeShotBox', volume=ShotLV, pos=ShotPos)
        detencLV.placements.append(ShotPla.name)

        posCryoInDetEnc = geom.structure.Position("posCryoInDetEnc", x=globals.get("posCryoInDetEnc_x"),
                                                                     y=globals.get("posCryoInDetEnc_y"),
                                                                     z=globals.get("posCryoInDetEnc_z"))
        # get outer support structure + cryostat
        supportenc = self.get_builder("SupportEnc")
        supportencLV = supportenc.get_volume()
        supportPla = geom.structure.Placement('SupportStructurePlace', pos=posCryoInDetEnc, volume=supportencLV)
        detencLV.placements.append(supportPla.name)

    def construct(self, geom):
        # for leaf builders, get the rest of the derived global parameters
        globals.SetDerived()
        if globals.get("simple"):
            self.construct_simplified(geom)
        else:
            self.construct_cavern(geom)

        return
