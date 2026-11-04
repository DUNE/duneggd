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

# Returns the set of (myi, mzi) cells in a frame's 4x4 mesh grid that an arapuca
# occupies. Each arapuca uses list_posy_bot[ara] x list_posz_bot[ara] for its
# position; the relative ordering of those entries gives a fixed list-index to
# cell-index lookup independent of cathode size. Standard frame:
#
#              z direction (mzi) →
#          mzi=0   mzi=1   mzi=2   mzi=3
#        +-------+-------+-------+-------+
#     0  |       |       |  A3   |       |
#        +-------+-------+-------+-------+
#     1  |  A1   |       |       |       |
#        +-------+-------+-------+-------+
#     2  |       |       |       |  A2   |
#        +-------+-------+-------+-------+
#     3  |       |  A0   |       |       |
#        +-------+-------+-------+-------+
#
# Edge frames swap one arapuca to a neighboring list-index (mirroring the same
# edge corrections in placeOpDetsCathode) to avoid hanging off the cathode array.
# E.g. at the first y-row (ii=0), ara 0 shifts from row myi=3 to row myi=2:
#
#    non-edge frame              ii==0 edge frame
#
#    mzi: 0  1  2  3              mzi: 0  1  2  3
#      +--+--+--+--+                  +--+--+--+--+
#   0  |  |  |A3|  |               0  |  |  |A3|  |
#      +--+--+--+--+                  +--+--+--+--+
#   1  |A1|  |  |  |               1  |A1|  |  |  |
#      +--+--+--+--+                  +--+--+--+--+
#   2  |  |  |  |A2|               2  |  |A0|  |A2|    <- A0 here
#      +--+--+--+--+                  +--+--+--+--+
#   3  |  |A0|  |  |               3  |  |  |  |  |    <- row 3 empty
#      +--+--+--+--+                  +--+--+--+--+
#
# These 4 arapuca cells get the conductive cathode-arapuca mesh (placed in
# placeOpDetsCathode); the remaining 12 cells get the resistive mesh.
def arapucaCells(ii, jj, nii, njj):
    LIST_TO_MYI = [3, 1, 2, 0]
    LIST_TO_MZI = [1, 0, 3, 2]
    y_idx = [0, 1, 2, 3]
    z_idx = [0, 1, 2, 3]
    if ii == 0:       y_idx[0] = 2
    if ii == nii - 1: y_idx[3] = 1
    if jj == 0:       z_idx[1] = 0
    if jj == njj - 1: z_idx[2] = 3
    return {(LIST_TO_MYI[y_idx[a]], LIST_TO_MZI[z_idx[a]]) for a in range(4)}

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
        anodePlateBottomBox = geom.shapes.Box('AnodePlateBottom',
                                              dx = 0.5*globals.get("anodePlateWidth"),
                                              dy = 0.5*globals.get("widthCathode"),
                                              dz = 0.5*globals.get("lengthAnodeBottom"))

        # define the logical volumes
        cryo_LV = make_volume(geom, "LAr", cryoBox, aux=True)
        self.add_volume(cryo_LV)

        # make the simple stuff
        anodePlate_LV = make_volume(geom, "vm2000", anodePlateBox)
        anodePlateBottom_LV = make_volume(geom, "vm2000", anodePlateBottomBox)
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

            # fetch the cathode-arapuca conductive mesh and resistive mesh LVs
            mesh_cath_LV = arapuca.get_volume("volCathodeArapucaMesh") if globals.get("ArapucaMesh_switch") else None
            mesh_resist_LV = arapuca.get_volume("volCathodeMeshunion") if globals.get("ArapucaMesh_switch") else None

            # place the volumes that go here
            tpcenc_LV = self.placeTPC(geom, tpc_LV, tpcenc_LV)
            tpcenc_LV = self.placeCathodeAndAnode(geom, cathode_LV, anodePlate_LV, anodePlateBottom_LV, tpcenc_LV)
            if globals.get("nCRM_x") != 2:
                tpcenc_LV = self.placeOpDetsCathode(geom, arapuca_LV[0], tpcenc_LV, mesh_LV=mesh_cath_LV)
            else:
                tpcenc_LV = self.placeOpDetsCathode(geom, arapuca_LV[1], tpcenc_LV, mesh_LV=mesh_cath_LV)
            tpcenc_LV = self.placeResistiveMeshCathode(geom, mesh_resist_LV, tpcenc_LV)

            # place it inside the cryostat
            tpcenc_x = globals.get("posTPCEncInCryo_x")
            tpcenc_y = Q('0cm')
            tpcenc_z = Q('0cm')
            place_tpcenc = geom.structure.Placement('place'+tpcencBox.name,
                                                    volume = tpcenc_LV,
                                                    pos = geom.structure.Position('pos'+tpcencBox.name,
                                                                                  x = tpcenc_x,
                                                                                  y = tpcenc_y,
                                                                                  z = tpcenc_z))
            cryo_LV.placements.append(place_tpcenc.name)
        # fetch the membrane mesh LV (only added by Arapuca builder when switch is on)
        mesh_lat_LV = arapuca.get_volume("volArapucaMesh") if globals.get("ArapucaMesh_switch") else None

        # place the other optical components
        cryo_LV = self.placeOpDetsLateral(geom, arapuca_LV[0], cryo_LV, mesh_LV=mesh_lat_LV)
        cryo_LV = self.placeOpDetsShortLateral(geom, arapuca_LV[0], cryo_LV, mesh_LV=mesh_lat_LV)
        cryo_LV = self.placeOpDetsMembOnly(geom, arapuca_LV[0], cryo_LV)
        # place the field shaper
        nfs = [0] if globals.get("nCRM_x") != 2 else [0, 1]
        for reversed in nfs:
            cryo_LV = self.placeFieldShaper(geom, fs_LV, fsslim_LV, cryo_LV, reversed)
        return

    # a number of placement helpers for cryostat and other constituent volumes
    def placeTPC(self, geom, tpc_LV, tpcenc_LV):
        if not globals.get("tpc"):
            return tpcenc_LV

        pos_x = 0.5*globals.get("TPCEnclosure_x") - 0.5*globals.get("TPC_x") - globals.get("anodePlateWidth")
        posbottom_x = -pos_x
        pos_z = -0.5*globals.get("TPCEnclosure_z") + 0.5*globals.get("lengthCRM")
        pos_z_bot = -0.5*globals.get("TPCEnclosure_z") + 0.5*globals.get("lengthCRM")

        idx = 0
        name = re.sub(r'vol', '', tpc_LV.name)
        for ii in range(globals.get("nCRM_z")):
            if ii == 0:
                pos_z_bot += globals.get("borderCRUBottom1side_z")
            if ii > 0:
                pos_z_bot += 2 * globals.get("borderCRUBottom1side_z")
            if ii % 2 == 0:
                pos_z += globals.get("borderCRP")*(1 + int(ii > 0))
                if (globals.get("nSST2_z") == 0) and (ii % 6 == 0) and (ii > 0):
                    pos_z += globals.get("gapSST1_z")
                if (globals.get("nSST2_z") > 0) and (ii == 2):
                    pos_z += globals.get("gapSST2_z")
                if (globals.get("nSST2_z") > 0) and ((ii-2) % 6 == 0) and (ii > 2) and (ii < globals.get("nCRM_z") - 2):
                    pos_z += globals.get("gapSST1_z")
                if (globals.get("nSST2_z") > 0) and ((ii-2) % 6 == 0) and (ii >= globals.get("nCRM_z") - 2):
                    pos_z += globals.get("gapSST2_z")

            pos_y = -0.5*globals.get("TPCEnclosure_y") + 0.5*globals.get("widthCRM")
            pos_y_bot = -0.5*globals.get("TPCEnclosure_ybottom") + 0.5*globals.get("widthCRM")
            for jj in range(globals.get("nCRM_y")):
                if jj % 2 == 0:
                    pos_y += globals.get("borderCRP")*(1 + int(jj > 0))
                    pos_y_bot += globals.get("borderCRUBottom_y")*(1 + int(jj > 0))

                    if (jj % 4 == 0) and (jj > 0):
                        pos_y += globals.get("gapSST_y")
                        pos_y_bot += globals.get("gapSST_ybottom")

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
                                                                                       y = pos_y_bot,
                                                                                       z = pos_z_bot),
                                                         rot = "rPlus180AboutY")
                    tpcenc_LV.placements.append(place_bot.name)
                idx += 1
                pos_y += globals.get("widthCRM")
                pos_y_bot += globals.get("widthCRM")
            pos_z += globals.get("lengthCRM")
            pos_z_bot += globals.get("lengthCRM")
        return tpcenc_LV

    def placeCathodeAndAnode(self, geom, c_LV, a_LV, a_bot_LV, tpcenc_LV):
        if not globals.get("Cathode_switch"):
            return tpcenc_LV

        cathode_x = globals.get("posCathodeInTPCEnc_x")
        cathode_y = -0.5*globals.get("TPCEnclosure_y") + 0.5*globals.get("widthCathode")
        cathode_z = -0.5*globals.get("TPCEnclosure_z") + 0.5*globals.get("lengthCathode")
        anode_toppos = 0.5*globals.get("TPCEnclosure_x") - 0.5*globals.get("anodePlateWidth")
        anode_botpos = -0.5*globals.get("TPCEnclosure_x") + 0.5*globals.get("anodePlateWidth")
        cathode_z_bot = -0.5*globals.get("TPCEnclosure_z") + 0.5*globals.get("lengthCathodeBottom")
        cathode_y_bot = -0.5*globals.get("TPCEnclosure_ybottom") + 0.5*globals.get("widthCathodeBottom")
        anode_posz_bot = -0.5*globals.get("TPCEnclosure_z") + 0.5*globals.get("lengthCRM") + globals.get("borderCRUBottom1side_z")
        posz_bot = -0.5*globals.get("TPCEnclosure_z") + 0.5*globals.get("lengthCRM")


        idx = 0
        idx_bot = 0
        for ii in range(globals.get("nCRM_z")//2):
            for jj in range(globals.get("nCRM_y")//2):
                name_c = re.sub(r'vol', '', c_LV.name)
                name_a = re.sub(r'vol', '', a_LV.name)
                name_a_bot = re.sub(r'vol', '', a_bot_LV.name)
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
                    place_ab = geom.structure.Placement('place%s%d_inTPCEncBottom'%(name_a_bot, idx_bot),
                                                        volume = a_bot_LV,
                                                        pos = geom.structure.Position('pos%sBottom-%d' %            \
                                                                                            (name_a_bot, idx_bot),
                                                                                      x = anode_botpos,
                                                                                      y = cathode_y_bot,
                                                                                      z = anode_posz_bot),
                                                        rot = "rIdentity")
                    tpcenc_LV.placements.append(place_ab.name)
                    idx_bot += 1
                    # dead material on one side only
                    anode_posz_bot2 = anode_posz_bot + globals.get("lengthAnodeBottom") + (2 * globals.get("borderCRUBottom1side_z"))
                    place_ab2 = geom.structure.Placement('place%s%d_inTPCEncBottom'%(name_a_bot, idx_bot),
                                                        volume = a_bot_LV,
                                                        pos = geom.structure.Position('pos%sBottom-%d' %            \
                                                                                            (name_a_bot, idx_bot),
                                                                                      x = anode_botpos,
                                                                                      y = cathode_y_bot,
                                                                                      z = anode_posz_bot2),
                                                        rot = "rIdentity")
                    tpcenc_LV.placements.append(place_ab2.name)

                idx += 1
                idx_bot += 1
                cathode_y += globals.get("widthCathode")
                cathode_y_bot += globals.get("widthCathodeBottom")
                if ((jj+1) % 2 == 0) and (jj > 0):
                    cathode_y += globals.get("gapSST_y")
                    cathode_y_bot += globals.get("gapSST_ybottom")

            cathode_z += globals.get("lengthCathode")
            cathode_z_bot += globals.get("lengthCathodeBottom")
            anode_posz_bot += 2 * (globals.get("lengthAnodeBottom") + 2*globals.get("borderCRUBottom1side_z"))
            if (globals.get("nSST2_z") == 0) and ((ii+1) % 3 == 0) and (ii > 0):
                cathode_z += globals.get("gapSST1_z")
            if (globals.get("nSST2_z") > 0) and (ii == 0):
                cathode_z += globals.get("gapSST2_z")
            if (globals.get("nSST2_z") > 0) and (ii % 3 == 0) and (ii > 0) and (ii < globals.get("nCRM_z")/2 - 2):
                cathode_z += globals.get("gapSST1_z")
            if (globals.get("nSST2_z") > 0) and (ii % 3 == 0) and (ii >= globals.get("nCRM_z")/2 - 2):
                cathode_z += globals.get("gapSST2_z")

            cathode_y = -0.5*globals.get("TPCEnclosure_y") + 0.5*globals.get("widthCathode")
            cathode_y_bot = -0.5*globals.get("TPCEnclosure_ybottom") + 0.5*globals.get("widthCathodeBottom")

        return tpcenc_LV

    # upstream logic needed for arapuca vs arapurca double passed as argument
    def placeOpDetsCathode(self, geom, arapuca_LV, tpcenc_LV, mesh_LV=None):
        if globals.get("pdsconfig"):
            return tpcenc_LV

        frCenter_x = globals.get("posCathodeInTPCEnc_x")
        frCenter_y = -0.5*globals.get("TPCEnclosure_y") + 0.5*globals.get("widthCathode")
        frCenter_z = -0.5*globals.get("TPCEnclosure_z") + 0.5*globals.get("lengthCathode")

        # magnitude of the offset between arapuca center and cathode-void center along y
        # (matches perl literal 5.475cm for protodune values; sign per arapuca below)
        mesh_y_offset = 0.5*globals.get("widthCathodeVoid") - globals.get("GapPD") -                                \
                        0.5*globals.get("ArapucaOut_x")
        # face-to-face displacement of the mesh from the cathode block centre in x
        mesh_x_offset = 0.5*globals.get("heightCathode") - 2*globals.get("CathodeArapucaMeshRodRadious")
        mesh_name = re.sub(r'vol', '', mesh_LV.name) if mesh_LV is not None else None

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

                    # Place conductive mesh at the cathode-void center on top face (always) and
                    # bottom face (only when both drift volumes are active). Sign of mesh_y_offset
                    # depends on which list_posy_bot index this arapuca uses (which side of the
                    # void GapPD constrains it from): indices 0,1 -> +offset, indices 2,3 -> -offset.
                    if mesh_LV is not None:
                        mesh_y = ara_y + mesh_y_offset if ara < 2 else ara_y - mesh_y_offset
                        if ii == 0 and ara == 0:                            mesh_y = ara_y - mesh_y_offset
                        if ii == globals.get("nCRM_y")//2 - 1 and ara == 3: mesh_y = ara_y + mesh_y_offset
                        place_top = geom.structure.Placement('place%s0%d-%d_inTPCEnc' % (mesh_name, ara, idx),
                                                             volume = mesh_LV,
                                                             pos = geom.structure.Position('pos%s0%d-Frame-%d-%d' % \
                                                                                            (mesh_name, ara, ii, jj),
                                                                                            x = ara_x + mesh_x_offset,
                                                                                            y = mesh_y,
                                                                                            z = ara_z),
                                                             rot = "rPlus90AboutX")
                        tpcenc_LV.placements.append(place_top.name)
                        if globals.get("nCRM_x") == 2:
                            place_bot = geom.structure.Placement('place%s1%d-%d_inTPCEnc' % (mesh_name, ara, idx),
                                                                 volume = mesh_LV,
                                                                 pos = geom.structure.Position('pos%s1%d-Frame-%d-%d' % \
                                                                                                (mesh_name, ara, ii, jj),
                                                                                                x = ara_x - mesh_x_offset,
                                                                                                y = mesh_y,
                                                                                                z = ara_z),
                                                                 rot = "rPlus90AboutX")
                            tpcenc_LV.placements.append(place_bot.name)
                idx += 1
                frCenter_z += globals.get("lengthCathode")
                if (globals.get("nSST2_z") == 0) and ((jj+1) % 3 == 0) and (jj > 0):
                    frCenter_z += globals.get("gapSST1_z")
                if (globals.get("nSST2_z") > 0) and (jj == 0):
                    frCenter_z += globals.get("gapSST2_z")
                if (globals.get("nSST2_z") > 0) and (jj % 3 == 0) and (jj > 0) and (jj < globals.get("nCRM_z")/2 - 2):
                    frCenter_z += globals.get("gapSST1_z")
                if (globals.get("nSST2_z") > 0) and (jj % 3 == 0) and (jj >= globals.get("nCRM_z")/2 - 2):
                    frCenter_z += globals.get("gapSST2_z")

            frCenter_y += globals.get("widthCathode")
            if ((ii+1) % 2 == 0) and (ii > 0):
                frCenter_y += globals.get("gapSST_y")

            frCenter_z = -0.5*globals.get("TPCEnclosure_z") + 0.5*globals.get("lengthCathode")
        return tpcenc_LV

    def placeResistiveMeshCathode(self, geom, mesh_LV, tpcenc_LV):
        if mesh_LV is None or not globals.get("Cathode_switch") or globals.get("pdsconfig"):
            return tpcenc_LV

        nii = globals.get("nCRM_y") // 2
        njj = globals.get("nCRM_z") // 2
        wcv = globals.get("widthCathodeVoid")
        lcv = globals.get("lengthCathodeVoid")
        cb = globals.get("CathodeBorder")
        h = globals.get("heightCathode")
        t = globals.get("CathodeMeshInnerStructureThickness")
        offsetY = globals.get("CathodeMeshOffset_Y")

        # mesh sits flush with cathode top/bottom face (perl line 3200's
        # BotMesh_X formula is a typo; using the correct symmetric form here)
        x_face_offset = 0.5*(h - t)
        frCenter_x = 0.5*globals.get("TPCEnclosure_x") - globals.get("TPC_x") - \
                     globals.get("anodePlateWidth") - 0.5*h

        mesh_name = re.sub(r'vol', '', mesh_LV.name)

        idx = 0
        frCenter_y = -0.5*globals.get("TPCEnclosure_y") + 0.5*globals.get("widthCathode")
        for ii in range(nii):
            frCenter_z = -0.5*globals.get("TPCEnclosure_z") + 0.5*globals.get("lengthCathode")
            for jj in range(njj):
                skip_cells = arapucaCells(ii, jj, nii, njj)
                for myi in range(4):
                    for mzi in range(4):
                        if (myi, mzi) in skip_cells:
                            continue
                        Mesh_Y = frCenter_y + offsetY - myi*wcv - myi*cb
                        if myi > 1:
                            Mesh_Y -= cb
                        Mesh_Z = frCenter_z + (mzi - 1.5)*lcv + (mzi - 2.0)*cb
                        if mzi > 1:
                            Mesh_Z += cb

                        sides = [('top', frCenter_x + x_face_offset)]
                        if globals.get("nCRM_x") == 2:
                            sides.append(('bot', frCenter_x - x_face_offset))
                        for side, mesh_x in sides:
                            pos_name = 'pos%s_%s_%d_%d-Frame-%d-%d' % (mesh_name, side, myi, mzi, ii, jj)
                            place_name = 'place%s_%s_%d_%d-%d_inTPCEnc' % (mesh_name, side, myi, mzi, idx)
                            pos = geom.structure.Position(pos_name, x=mesh_x, y=Mesh_Y, z=Mesh_Z)
                            place = geom.structure.Placement(place_name, volume=mesh_LV, pos=pos)
                            tpcenc_LV.placements.append(place.name)

                idx += 1
                # advance z (mirror placeOpDetsCathode update logic)
                frCenter_z += globals.get("lengthCathode")
                if (globals.get("nSST2_z") == 0) and ((jj+1) % 3 == 0) and (jj > 0):
                    frCenter_z += globals.get("gapSST1_z")
                if (globals.get("nSST2_z") > 0) and (jj == 0):
                    frCenter_z += globals.get("gapSST2_z")
                if (globals.get("nSST2_z") > 0) and (jj % 3 == 0) and (jj > 0) and (jj < globals.get("nCRM_z")/2 - 2):
                    frCenter_z += globals.get("gapSST1_z")
                if (globals.get("nSST2_z") > 0) and (jj % 3 == 0) and (jj >= globals.get("nCRM_z")/2 - 2):
                    frCenter_z += globals.get("gapSST2_z")

            frCenter_y += globals.get("widthCathode")
            if ((ii+1) % 2 == 0) and (ii > 0):
                frCenter_y += globals.get("gapSST_y")
        return tpcenc_LV

    def placeFieldShaper(self, geom, fs_LV, fsslim_LV, cryo_LV, reversed):
        if not globals.get("FieldCage_switch"):
            return cryo_LV

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
                place = geom.structure.Placement('place%s_%d_%d_inCryo' % (fs_LV.name, int(reversed), i),
                                                 volume = fs_LV,
                                                 pos = geom.structure.Position('pos%s_%d_%d' %                       \
                                                                                 (name, int(reversed), i),
                                                                               x = pos_x,
                                                                               y = pos_y,
                                                                               z = pos_z),
                                                 rot = "rPlus90AboutZ")
                cryo_LV.placements.append(place.name)
            else:
                place_slim = geom.structure.Placement('place%s_%d_%d_inCryo' % (fsslim_LV.name, int(reversed), i),
                                                      volume = fsslim_LV,
                                                      pos = geom.structure.Position('pos%s_%d_%d' %                  \
                                                                                      (name, int(reversed), i),
                                                                                    x = pos_x,
                                                                                    y = pos_y,
                                                                                    z = pos_z),
                                                      rot = "rPlus90AboutZ")
                cryo_LV.placements.append(place_slim.name)
        return cryo_LV

    def placeOpDetsLateral(self, geom, arapuca_LV, cryo_LV, mesh_LV=None):
        if (globals.get("pdsconfig") != 0 or globals.get("nCRM_y") != 8):
            return cryo_LV

        frCenter_x = 0.5*globals.get("Argon_x") - globals.get("HeightGaseousAr") -                                  \
                     0.5*globals.get("padWidth")
        frCenter_z = -19*0.5*globals.get("lengthCathode") +                                                         \
                     (40 - globals.get("nCRM_z"))*0.25*globals.get("lengthCathode")

        name = re.sub(r'vol', '', arapuca_LV.name)
        mesh_name = re.sub(r'vol', '', mesh_LV.name) if mesh_LV is not None else None
        for j in range(globals.get("nCRM_z")//2):
            ara_z = frCenter_z
            ara_x = frCenter_x - globals.get("FirstFrameVertDist")

            for ara in range(8*globals.get("nCRM_x")):
                if ara % 4 != 0:
                    ara_x -= globals.get("VerticalPDdist") if ara < 8 else -globals.get("VerticalPDdist")
                elif ara < 8:
                    ara_x = frCenter_x - globals.get("FirstFrameVertDist")
                else:
                    ara_x = -frCenter_x - globals.get("HeightGaseousAr") + globals.get("xLArBuffer") +              \
                            globals.get("FirstFrameVertDist")

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

                # Place membrane mesh just inside the arapuca window, mirroring
                # perl place_MeshLateral (lines 3241-3280). Mesh world-x extent (76.7cm) is
                # slightly larger than VerticalPDdist (75.6cm), so adjacent meshes would
                # otherwise overlap. Shift each subsequent mesh in a column by 1.2cm toward
                # the cathode to leave a small gap between adjacent mesh containers; the
                # mesh tile is still much larger than the arapuca window so it still covers it.
                if mesh_LV is not None:
                    mesh_extra = (ara % 4) * Q('1.2cm')
                    mesh_x = ara_x - mesh_extra if ara < 8 else ara_x + mesh_extra
                    if ara % 8 < 4:
                        mesh_y = ara_y + 0.5*globals.get("ArapucaOut_y") +                                          \
                                 globals.get("Distance_Mesh_Arapuca_window")
                        mesh_rot = "rPlus90AboutY"
                    else:
                        mesh_y = ara_y - 0.5*globals.get("ArapucaOut_y") -                                          \
                                 globals.get("Distance_Mesh_Arapuca_window")
                        mesh_rot = "rPlus180AboutXPlus90AboutY"
                    place_mesh = geom.structure.Placement('place%s%d-Lat%d' % (mesh_name, ara, j),
                                                          volume = mesh_LV,
                                                          pos = geom.structure.Position('pos%s%d-Lat%d' %           \
                                                                                            (mesh_name, ara, j),
                                                                                        x = mesh_x,
                                                                                        y = mesh_y,
                                                                                        z = ara_z),
                                                          rot = mesh_rot)
                    cryo_LV.placements.append(place_mesh.name)
            frCenter_z += globals.get("lengthCathode")
        return cryo_LV

    def placeOpDetsShortLateral(self, geom, arapuca_LV, cryo_LV, mesh_LV=None):
        if (globals.get("pdsconfig") != 0 or globals.get("nCRM_y") != 8):
            return cryo_LV

        frCenter_x = 0.5*globals.get("Argon_x") - globals.get("HeightGaseousAr") -                                  \
                     0.5*globals.get("padWidth")
        frCenter_z = -19*0.5*globals.get("lengthCathode") +                                                         \
                     (40 - globals.get("nCRM_z"))*0.25*globals.get("lengthCathode")

        name = re.sub(r'vol', '', arapuca_LV.name)
        mesh_name = re.sub(r'vol', '', mesh_LV.name) if mesh_LV is not None else None
        for j in range(2):
            frCenter_y = Q('220cm') if j else Q('-220cm')
            ara_x = frCenter_x - globals.get("FirstFrameVertDist")

            for ara in range(8*globals.get("nCRM_x")):
                if ara % 4 != 0:
                    ara_x -= globals.get("VerticalPDdist") if ara < 8 else -globals.get("VerticalPDdist")
                elif ara < 8:
                    ara_x = frCenter_x - globals.get("FirstFrameVertDist")
                else:
                    ara_x = -frCenter_x - globals.get("HeightGaseousAr") + globals.get("xLArBuffer") +              \
                            globals.get("FirstFrameVertDist")
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

                if mesh_LV is not None:
                    mesh_extra = (ara % 4) * Q('1.2cm')
                    mesh_x = ara_x - mesh_extra if ara < 8 else ara_x + mesh_extra
                    if ara % 8 < 4:
                        mesh_z = ara_z + 0.5*globals.get("ArapucaOut_y") +                                          \
                                 globals.get("Distance_Mesh_Arapuca_window")
                        mesh_rot = "rMinus90AboutXPlus90AboutY"
                    else:
                        mesh_z = ara_z - 0.5*globals.get("ArapucaOut_y") -                                          \
                                 globals.get("Distance_Mesh_Arapuca_window")
                        mesh_rot = "rPlus90AboutXPlus90AboutY"
                    place_mesh = geom.structure.Placement('place%s%d-ShortLat%d' % (mesh_name, ara, j),
                                                          volume = mesh_LV,
                                                          pos = geom.structure.Position('pos%s%d-ShortLat%d' %      \
                                                                                            (mesh_name, ara, j),
                                                                                        x = mesh_x,
                                                                                        y = ara_y,
                                                                                        z = mesh_z),
                                                          rot = mesh_rot)
                    cryo_LV.placements.append(place_mesh.name)
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
