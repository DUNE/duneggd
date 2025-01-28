#!/usr/bin/env python
'''
Cryostat builder for DUNE FD-VD
'''

import gegede.builder
from utils import *
import re

# helper function for making a volume object
def make_volume(geom, material, shape, name='', aux=False):
    name_lv = name
    if name == '':
        name_lv = 'vol'+shape.name

    lv = geom.structure.Volume(name_lv,
                               material = material,
                               shape = shape)
    if aux:
        lv.params.append(("SensDet","SimEnergyDeposit"))
        lv.params.append(("StepLimit","0.5208*cm"))
        lv.params.append(("Efield","0*V/cm"))
    return lv

class CryostatBuilder(gegede.builder.Builder):
    def configure(self, **kwds):
        if not set(kwds).issubset(globals.Cryostat): # no unknown keywords
            msg = 'Unknown parameter in: "%s"' % (', '.join(sorted(kwds.keys())), )
            raise ValueError(msg)

        # The builder hierarchy takes care of all the configuration parameters
        globals.Cryostat = kwds

    def construct(self, geom):
        globals.SetDerived()

        # get the shapes
        cryoBox = geom.shapes.Box(self.name,
                                  dx = 0.5*globals.get("Cryostat_x"),
                                  dy = 0.5*globals.get("Cryostat_y"),
                                  dz = 0.5*globals.get("Cryostat_z"))
        arInteriorBox = geom.shapes.Box('ArgonInterior',
                                        dx = 0.5*globals.get("Argon_x"),
                                        dy = 0.5*globals.get("Argon_y"),
                                        dz = 0.5*globals.get("Argon_z"))
        gasArBox = geom.shapes.Box('GaseousArgon',
                                   dx = 0.5*globals.get("HeightGaseousAr") - 0.5*globals.get("anodePlateWidth"),
                                   dy = 0.5*globals.get("Argon_y"),
                                   dz = 0.5*globals.get("Argon_z"))
        steelshellBox = geom.shapes.Boolean('SteelShell',
                                            type = 'subtraction',
                                            first = cryoBox,
                                            second = arInteriorBox)
        tpcencBox = geom.shapes.Box('TPCEnclosure',
                                    dx = 0.5*globals.get("TPCEnclosure_x"),
                                    dy = 0.5*globals.get("TPCEnclosure_y"),
                                    dz = 0.5*globals.get("TPCEnclosure_z"))
        anodePlateBox = geom.shapes.Box('AnodePlate',
                                        dx = 0.5*globals.get("anodePlateWidth"),
                                        dy = 0.5*globals.get("widthCathode"),
                                        dz = 0.5*globals.get("lengthCathode"))

        # define the logical volumes
        cryo_LV = make_volume(geom, "LAr", cryoBox, aux=True)
        self.add_volume(cryo_LV)

        # make the simple stuff
        anodePlate_LV = make_volume(geom, "vm2000", anodePlateBox)
        gasAr_LV = make_volume(geom, "ArGas", gasArBox)
        steelshell_LV = make_volume(geom, "STEEL_STAINLESS_Fe7Cr2Ni", steelshellBox)

        # arapucas
        arapuca = self.get_builder("Arapuca")
        arapuca_LV = [arapuca.get_volume("volArapuca")]
        if globals.get("nCRM_x") == 2:
            arapuca_LV.append(arapuca.get_volume("volArapucaDouble"))

        # field shapers
        fs = self.get_builder("FieldCage")
        fs_LV = fs.get_volume("volFieldShaper")
        fsslim_LV = fs.get_volume("volFieldShaperSlim")

        # start placing things
        gasar_x = 0.5*(globals.get("Argon_x")- globals.get("HeightGaseousAr") + globals.get("anodePlateWidth"))
        gasar_y = Q('0cm')
        gasar_z = Q('0cm')
        place_gasAr = geom.structure.Placement('place'+gasArBox.name,
                                               volume = gasAr_LV,
                                               pos = geom.structure.Position('pos'+gasArBox.name,
                                                                             x = gasar_x,
                                                                             y = gasar_y,
                                                                             z = gasar_z))
        cryo_LV.placements.append(place_gasAr.name)

        place_steelshell = geom.structure.Placement('place'+steelshellBox.name,
                                                    volume = steelshell_LV,
                                                    pos = geom.structure.Position('pos'+steelshellBox.name,
                                                                                  x = Q('0cm'),
                                                                                  y = Q('0cm'),
                                                                                  z = Q('0cm')))
        cryo_LV.placements.append(place_steelshell.name)

        # tpc enclosure
        if globals.get("tpc"):
            tpcenc_LV = make_volume(geom, "LAr", tpcencBox, name="volEnclosureTPC", aux=True)
            tpc = self.get_builder("TPC")
            tpc_LV = tpc.get_volume()
            cathode = self.get_builder("CathodeGrid")
            cathode_LV = cathode.get_volume()

            # place the volumes that go here
            tpcenc_LV = self.placeTPC(geom, tpc_LV, tpcenc_LV)
            tpcenc_LV = self.placeCathodeAndAnode(geom, cathode_LV, anodePlate_LV, tpcenc_LV)
            if globals.get("nCRM_x") != 2:
                tpcenc_LV = self.placeOpDetsCathode(geom, arapuca_LV[0], tpcenc_LV)
            else:
                tpcenc_LV = self.placeOpDetsCathode(geom, arapuca_LV[1], tpcenc_LV)

            # place it inside the cryostat
            tpcenc_x = 0.5*(globals.get("Argon_x") - globals.get("TPCEnclosure_x")) -                               \
                       globals.get("HeightGaseousAr") + globals.get("anodePlateWidth")
            tpcenc_y = Q('0cm')
            tpcenc_z = Q('0cm')
            place_tpcenc = geom.structure.Placement('place'+tpcencBox.name,
                                                    volume = tpcenc_LV,
                                                    pos = geom.structure.Position('pos'+tpcencBox.name,
                                                                                  x = tpcenc_x,
                                                                                  y = tpcenc_y,
                                                                                  z = tpcenc_z))
            cryo_LV.placements.append(place_tpcenc.name)
        # place the other optical components
        cryo_LV = self.placeOpDetsLateral(geom, arapuca_LV[0], cryo_LV)
        cryo_LV = self.placeOpDetsShortLateral(geom, arapuca_LV[0], cryo_LV)
        cryo_LV = self.placeOpDetsMembOnly(geom, arapuca_LV[0], cryo_LV)
        # place the field shaper
        cryo_LV = self.placeFieldShaper(geom, fs_LV, fsslim_LV, cryo_LV)
        return

    # a number of placement helpers for cryostat and other constituent volumes
    def placeTPC(self, geom, tpc_LV, tpcenc_LV):
        if not globals.get("tpc"):
            return tpcenc_LV

        pos_x = 0.5*globals.get("TPCEnclosure_x") - 0.5*globals.get("TPC_x") - globals.get("anodePlateWidth")
        posbottom_x = -pos_x
        pos_z = -0.5*globals.get("TPCEnclosure_z") + 0.5*globals.get("lengthCRM")

        idx = 0
        name = re.sub(r'vol', '', tpc_LV.name)
        for ii in range(globals.get("nCRM_z")):
            if ii % 2 == 0:
                pos_z += globals.get("borderCRP")*(1 + int(ii > 0))
            pos_y = -0.5*globals.get("TPCEnclosure_y") + 0.5*globals.get("widthCRM")
            for jj in range(globals.get("nCRM_y")):
                if jj % 2 == 0:
                    pos_y += globals.get("borderCRP")*(1 + int(jj > 0))

                place_top = geom.structure.Placement('placeTop%s-%d' % (name, idx),
                                                     volume = tpc_LV,
                                                     pos = geom.structure.Position('posTop%s-%d' % (name, idx),
                                                                                   x = pos_x,
                                                                                   y = pos_y,
                                                                                   z = pos_z))
                tpcenc_LV.placements.append(place_top.name)
                if globals.get("nCRM_x") == 2:
                    place_bot = geom.structure.Placement('placeBot%s-%d' % (name, idx),
                                                         volume = tpc_LV,
                                                         pos = geom.structure.Position('posBot%s-%d' % (name, idx),
                                                                                       x = posbottom_x,
                                                                                       y = pos_y,
                                                                                       z = pos_z))
                    tpcenc_LV.placements.append(place_bot.name)
                idx += 1
                pos_y += globals.get("widthCRM")
            pos_z += globals.get("lengthCRM")
        return tpcenc_LV

    def placeCathodeAndAnode(self, geom, c_LV, a_LV, tpcenc_LV):
        if not globals.get("Cathode_switch"):
            return tpcenc_LV

        cathode_x = 0.5*globals.get("TPCEnclosure_x") - globals.get("TPC_x") -                                      \
                    globals.get("anodePlateWidth") - 0.5*globals.get("heightCathode")
        cathode_y = -0.5*globals.get("TPCEnclosure_y") + 0.5*globals.get("widthCathode")
        cathode_z = -0.5*globals.get("TPCEnclosure_z") + 0.5*globals.get("lengthCathode")
        anode_toppos = 0.5*globals.get("TPCEnclosure_x") - 0.5*globals.get("anodePlateWidth")
        anode_botpos = -0.5*globals.get("TPCEnclosure_x") + 0.5*globals.get("anodePlateWidth")

        idx = 0
        for ii in range(globals.get("nCRM_z")//2):
            for jj in range(globals.get("nCRM_y")//2):
                name_c = re.sub(r'vol', '', c_LV.name)
                name_a = re.sub(r'vol', '', a_LV.name)
                place_c = geom.structure.Placement('place%s%d_inTPCEnc'%(c_LV.name, idx),
                                                   volume = c_LV,
                                                   pos = geom.structure.Position('pos%s-%d'%(name_c, idx),
                                                                                 x = cathode_x,
                                                                                 y = cathode_y,
                                                                                 z = cathode_z))
                place_a = geom.structure.Placement('place%s%d_inTPCEnc'%(a_LV.name, idx),
                                                   volume = a_LV,
                                                   pos = geom.structure.Position('pos%s-%d'%(name_a, idx),
                                                                                 x = anode_toppos,
                                                                                 y = cathode_y,
                                                                                 z = cathode_z),
                                                   rot = "rIdentity")
                tpcenc_LV.placements.append(place_c.name)
                tpcenc_LV.placements.append(place_a.name)

                if globals.get("nCRM_x") == 2:
                    place_ab = geom.structure.Placement('place%s%d_inTPCEncBottom'%(name_a, idx),
                                                        volume = a_LV,
                                                        pos = geom.structure.Position('pos%sBottom-%d' %            \
                                                                                            (name_a, idx),
                                                                                      x = anode_botpos,
                                                                                      y = cathode_y,
                                                                                      z = cathode_z),
                                                        rot = "rIdentity")
                    tpcenc_LV.placements.append(place_ab.name)

                idx += 1
                cathode_y += globals.get("widthCathode")
            cathode_z += globals.get("lengthCathode")
            cathode_y = -0.5*globals.get("TPCEnclosure_y") + 0.5*globals.get("widthCathode")
        return tpcenc_LV

    # upstream logic needed for arapuca vs arapurca double passed as argument
    def placeOpDetsCathode(self, geom, arapuca_LV, tpcenc_LV):
        if globals.get("pdsconfig"):
            return tpcenc_LV

        frCenter_x = 0.5*globals.get("TPCEnclosure_x") - globals.get("TPC_x") -                                     \
                     globals.get("anodePlateWidth") - 0.5*globals.get("heightCathode")
        frCenter_y = -0.5*globals.get("TPCEnclosure_y") + 0.5*globals.get("widthCathode")
        frCenter_z = -0.5*globals.get("TPCEnclosure_z") + 0.5*globals.get("lengthCathode")

        idx = 0
        for ii in range(globals.get("nCRM_y")//2):
            for jj in range(globals.get("nCRM_z")//2):
                for ara in range(4):
                    ara_x = frCenter_x
                    ara_y = frCenter_y + globals.get("list_posy_bot")[ara]
                    ara_z = frCenter_z + globals.get("list_posz_bot")[ara]

                    if jj == 0 and ara == 1:
                        ara_z = frCenter_z + globals.get("list_posz_bot")[0]
                    if jj == globals.get("nCRM_z")//2 - 1 and ara == 2:
                        ara_z = frCenter_z + globals.get("list_posz_bot")[3]
                    if ii == 0 and ara == 0:
                        ara_y = frCenter_y + globals.get("list_posy_bot")[2]
                    if ii == globals.get("nCRM_y")//2 - 1 and ara == 3:
                        ara_y = frCenter_y + globals.get("list_posy_bot")[1]

                    name = re.sub(r'vol', '', arapuca_LV.name)
                    place = geom.structure.Placement('place%sAra%d-%d_inTPCEnc'%(name, ara, idx),
                                                     volume = arapuca_LV,
                                                     pos = geom.structure.Position('pos%s%d-Frame-%d-%d' %          \
                                                                                    (name, ara, ii, jj),
                                                                                    x = ara_x,
                                                                                    y = ara_y,
                                                                                    z = ara_z),
                                                     rot = "rPlus90AboutXPlus90AboutZ")
                    tpcenc_LV.placements.append(place.name)
                idx += 1
                frCenter_z += globals.get("lengthCathode")
            frCenter_y += globals.get("widthCathode")
            frCenter_z = -0.5*globals.get("TPCEnclosure_z") + 0.5*globals.get("lengthCathode")
        return tpcenc_LV

    def placeFieldShaper(self, geom, fs_LV, fsslim_LV, cryo_LV):
        if not globals.get("FieldCage_switch"):
            return cryo_LV

        reversed = 0 if globals.get("nCRM_x") != 2 else 1
        pos_y = -0.5*globals.get("FieldShaperShortTubeLength") - globals.get("FieldShaperTorRad")
        pos_z = Q('0cm')

        for i in range(int(globals.get("NFieldShapers").magnitude) + 1):
            dist = i*globals.get("FieldShaperSeparation")
            pos_x = 0.5*globals.get("Argon_x") - globals.get("HeightGaseousAr") -                                   \
                    (globals.get("driftTPCActive") + globals.get("ReadoutPlane")) +                                 \
                    (i + 0.5)*globals.get("FieldShaperSeparation")
            if reversed:
                pos_x = 0.5*globals.get("Argon_x") - globals.get("HeightGaseousAr") -                               \
                        (globals.get("driftTPCActive") + globals.get("ReadoutPlane")) -                             \
                        globals.get("heightCathode") -                                                              \
                        (i + 0.5)*globals.get("FieldShaperSeparation")

            name = re.sub(r'vol', '', fs_LV.name)
            if (globals.get("pdsconfig") == 0 and dist <= Q('250cm')):
                place = geom.structure.Placement('place%s%d_inCryo' % (fs_LV.name, i),
                                                 volume = fs_LV,
                                                 pos = geom.structure.Position('pos%s_%d%d' %                       \
                                                                                 (name, int(reversed), i),
                                                                               x = pos_x,
                                                                               y = pos_y,
                                                                               z = pos_z),
                                                 rot = "rPlus90AboutZ")
                cryo_LV.placements.append(place.name)
            else:
                place_slim = geom.structure.Placement('place%s%d_inCryo' % (fsslim_LV.name, i),
                                                      volume = fsslim_LV,
                                                      pos = geom.structure.Position('pos%s_%d%d' %                  \
                                                                                      (name, int(reversed), i),
                                                                                    x = pos_x,
                                                                                    y = pos_y,
                                                                                    z = pos_z),
                                                      rot = "rPlus90AboutZ")
                cryo_LV.placements.append(place_slim.name)
        return cryo_LV

    def placeOpDetsLateral(self, geom, arapuca_LV, cryo_LV):
        if (globals.get("pdsconfig") != 0 or globals.get("nCRM_y") != 8):
            return cryo_LV

        frCenter_x = 0.5*globals.get("Argon_x") - globals.get("HeightGaseousAr") -                                  \
                     0.5*globals.get("padWidth")
        frCenter_z = -19*0.5*globals.get("lengthCathode") +                                                         \
                     (40 - globals.get("nCRM_z"))*0.25*globals.get("lengthCathode")

        name = re.sub(r'vol', '', arapuca_LV.name)
        for j in range(globals.get("nCRM_z")//2):
            ara_z = frCenter_z
            ara_x = frCenter_x - globals.get("FirstFrameVertDist")

            for ara in range(8*globals.get("nCRM_x")):
                if ara % 4 != 0:
                    ara_x -= globals.get("VerticalPDdist") if ara < 8 else -globals.get("VerticalPDdist")
                elif ara < 8:
                    ara_x = frCenter_x - globals.get("FirstFrameVertDist")
                else:
                    ara_x = -ara_x - globals.get("HeightGaseousAr") + globals.get("xLArBuffer")

                ara_y = 0.5*globals.get("Argon_y") - globals.get("FrameToArapucaSpaceLat")
                delta_sens = -0.5*globals.get("ArapucaOut_y") +                                                     \
                             0.5*globals.get("ArapucaAcceptanceWindow_y") + Q('0.01cm')
                ara_ysens = ara_y + delta_sens
                rotation = "rPlus180AboutX"

                if ara % 8 < 4:
                    ara_y = -ara_y
                    ara_ysens = ara_y - delta_sens
                    rotation = "rIdentity"

                place_lat = geom.structure.Placement('place%s%d-Lat%d' % (name, ara, j),
                                                     volume = arapuca_LV,
                                                     pos = geom.structure.Position('pos%s%d-Lat%d' %                \
                                                                                        (name, ara, j),
                                                                                   x = ara_x,
                                                                                   y = ara_y,
                                                                                   z = ara_z),
                                                     rot = rotation)
                cryo_LV.placements.append(place_lat.name)
            frCenter_z += globals.get("lengthCathode")
        return cryo_LV

    def placeOpDetsShortLateral(self, geom, arapuca_LV, cryo_LV):
        if (globals.get("pdsconfig") != 0 or globals.get("nCRM_y") != 8):
            return cryo_LV

        frCenter_x = 0.5*globals.get("Argon_x") - globals.get("HeightGaseousAr") -                                  \
                     0.5*globals.get("padWidth")
        frCenter_z = -19*0.5*globals.get("lengthCathode") +                                                         \
                     (40 - globals.get("nCRM_z"))*0.25*globals.get("lengthCathode")

        name = re.sub(r'vol', '', arapuca_LV.name)
        for j in range(2):
            frCenter_y = Q('220cm') if j else Q('-220cm')
            ara_x = frCenter_x - globals.get("FirstFrameVertDist")

            for ara in range(8*globals.get("nCRM_x")):
                if ara % 4 != 0:
                    ara_x -= globals.get("VerticalPDdist") if ara < 8 else -globals.get("VerticalPDdist")
                elif ara < 8:
                    ara_x = frCenter_x - globals.get("FirstFrameVertDist")
                else:
                    ara_x = -ara_x - globals.get("HeightGaseousAr") + globals.get("xLArBuffer")
                ara_y = frCenter_y

                ara_z = 0.5*globals.get("Argon_z") - globals.get("FrameToArapucaSpaceLat")
                delta_sens = -0.5*globals.get("ArapucaOut_z") +                                                     \
                             0.5*globals.get("ArapucaAcceptanceWindow_z") + Q('0.01cm')
                ara_zsens = ara_z + delta_sens
                rotation = "rPlus90AboutX"

                if ara % 8 < 4:
                    ara_z = -ara_z
                    ara_zsens = ara_z - delta_sens
                    rotation = "rMinus90AboutX"

                place_lat = geom.structure.Placement('place%s%d-ShortLat%d' % (name, ara, j),
                                                     volume = arapuca_LV,
                                                     pos = geom.structure.Position('pos%s%d-ShortLat%d' %           \
                                                                                        (name, ara, j),
                                                                                   x = ara_x,
                                                                                   y = ara_y,
                                                                                   z = ara_z),
                                                     rot = rotation)
                cryo_LV.placements.append(place_lat.name)
        return cryo_LV

    def placeOpDetsMembOnly(self, geom, arapuca_LV, cryo_LV):
        if (globals.get("pdsconfig") != 1 or globals.get("nCRM_y") != 8):
            return cryo_LV

        frCenter_x = 0.5*globals.get("TPC_x") - 0.5*globals.get("padWidth")
        frCenter_z = -19*0.5*globals.get("lengthCathode") +                                                         \
                     (40 - globals.get("nCRM_z"))*0.25*globals.get("lengthCathode")

        name = re.sub(r'vol', '', arapuca_LV.name)
        for j in range(globals.get("nCRM_z")//2):
            for ara in range(18):

                ara_z = frCenter_z
                ara_x = frCenter_x - 0.5*globals.get("ArapucaOut_x")
                if ara != 0 and ara != 9:
                    ara_x -= globals.get("ArapucaOut_x") - globals.get("FrameToArapucaSpace")

                ara_y = 0.5*globals.get("Argon_y") - globals.get("FrameToArapucaSpaceLat")
                delta_sens = -0.5*globals.get("ArapucaOut_y") +                                                     \
                             0.5*globals.get("ArapucaAcceptanceWindow_y") + Q('0.01cm')
                ara_ysens = ara_y + delta_sens
                rotation = "rPlus180AboutX"

                if ara < 9:
                    ara_y = -ara_y
                    ara_ysens = ara_y - delta_sens
                    rotation = "rIdentity"

                place_lat = geom.structure.Placement('place%s%d-Lat%d' % (name, ara, j),
                                                     volume = arapuca_LV,
                                                     pos = geom.structure.Position('pos%s%d-Lat%d' %                \
                                                                                        (name, ara, j),
                                                                                   x = ara_x,
                                                                                   y = ara_y,
                                                                                   z = ara_z),
                                                     rot = rotation)
                cryo_LV.placements.append(place_lat.name)
            frCenter_z += globals.get("lengthCathode")
        return cryo_LV
