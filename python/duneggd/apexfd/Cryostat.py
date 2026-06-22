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
        apex = self.get_builder("Apex")
        apex_LV = [apex.get_volume()]

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
            tpcenc_LV = self.placeCathodeAndAnode(geom, cathode_LV, anodePlate_LV, anodePlateBottom_LV, tpcenc_LV)

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
        cryo_LV = self.placeApex(geom, apex_LV, cryo_LV)

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
                                                                                       z = pos_z_bot))
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

        cathode_x = 0.5*globals.get("TPCEnclosure_x") - globals.get("TPC_x") -                                      \
                    globals.get("anodePlateWidth") - 0.5*globals.get("heightCathode")
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

    def placeApex(self, geom, apex_LV, cryo_LV) :
        if globals.get("pdsconfig"):
            return cryo_LV

        ara_dep = globals.get("Arapuca_z")
        ara_len = globals.get("Arapuca_y")  
        ptp_dep = globals.get("ptpWidth")

        vert_space = globals.get("AraVertSpacing")
        long_space = globals.get("AraLongWallSpace")
        short_space = globals.get("AraShortWallSpace")

        cryo_x = globals.get("Cryostat_x")
        cryo_y = globals.get("Cryostat_y")
        cryo_z = globals.get("Cryostat_z")
        
        FC_x = 2*globals.get("FieldCageSizeX")
        FC_y = globals.get("FieldCageSizeY")
        FC_z = globals.get("FieldCageSizeZ")
        
        cathode_x = 0.5*globals.get("TPCEnclosure_x") - globals.get("TPC_x") -                                      \
                    globals.get("anodePlateWidth") - 0.5*globals.get("heightCathode")
        
        tpcenc_x = 0.5*(globals.get("Argon_x") - globals.get("TPCEnclosure_x")) -                               \
                       globals.get("HeightGaseousAr") + globals.get("anodePlateWidth")
        
        longwall_y = 2*globals.get("widthCathode")# + globals.get("gapSST_y")
        
        shortwall_z = 10*globals.get("lengthCathode") + 2.5*globals.get("gapSST1_z")# + globals.get("gapSST2_z") 

        # Long sides
        ncols=120
        nrows=12 
        
        zpos = -shortwall_z + 0.5*ara_len
        for i in range(1, ncols+1):
            xpos = tpcenc_x + cathode_x + 0.5*(ara_len+vert_space) + globals.get('heightCathode')
            for j in range(1, nrows+1):
                araL = geom.structure.Position('LeftAraP%d_%d' % (i,j), x=xpos, y=-longwall_y, z=zpos)
                araR = geom.structure.Position('RightAraP%d_%d' % (i,j), x=xpos, y=longwall_y, z=zpos)
                
                placeLeft = geom.structure.Placement('ArapucaLeft%d_%d' % (i,j), 
                                                 volume = "volArapucaEnc",
                                                 pos = 'LeftAraP%d_%d' % (i,j),
                                                 rot = "rPlus90AboutX")
                placeRight = geom.structure.Placement('ArapucaRight%d_%d' % (i,j),  
                                                 volume = "volArapucaEnc",
                                                 pos = 'RightAraP%d_%d' % (i,j),
                                                 rot = "rMinus90AboutX")
                
                cryo_LV.placements.append(placeRight.name)
                cryo_LV.placements.append(placeLeft.name)
                
                xpos += (ara_len + vert_space)
                if (j % 6 == 0):
                    xpos += globals.get('LargeVertSpacing')


            xpos = tpcenc_x + cathode_x - 0.5*(ara_len+vert_space) - globals.get('heightCathode')
            for j in range(nrows+1 ,2*nrows+1):
                araL = geom.structure.Position('LeftAraP%d_%d' % (i,j), x=xpos, y=-longwall_y, z=zpos)
                araR = geom.structure.Position('RightAraP%d_%d' % (i,j), x=xpos, y=longwall_y, z=zpos)

                placeLeft = geom.structure.Placement('ArapucaLeft%d_%d' % (i,j),
                                                 volume = "volArapucaEnc",
                                                 pos = 'LeftAraP%d_%d' % (i,j),
                                                 rot = "rPlus90AboutX")
                placeRight = geom.structure.Placement('ArapucaRight%d_%d' % (i,j),
                                                 volume = "volArapucaEnc",
                                                 pos = 'RightAraP%d_%d' % (i,j),
                                                 rot = "rMinus90AboutX")
                
                cryo_LV.placements.append(placeRight.name)
                cryo_LV.placements.append(placeLeft.name)
                
                xpos -= (ara_len + vert_space)
                if (j % 6 == 0):
                    xpos -= globals.get('LargeVertSpacing')
            
            if (i % 6 == 0):
                zpos += (ara_len + long_space)
            else:
                zpos += (ara_len)


        # Short sides
        ncols=24
        nrows=12
        ypos=0.0
        
        ypos = -longwall_y + 0.5*ara_len
        for i in range(1, ncols+1):
            xpos = tpcenc_x + cathode_x + 0.5*(ara_len+vert_space) + globals.get('heightCathode')
            for j in range(1, nrows+1):
                araF = geom.structure.Position('FrontAraP%d_%d' % (i,j), x=xpos, y=ypos, z=shortwall_z)
                araB = geom.structure.Position('BackAraP%d_%d' % (i,j), x=xpos, y=ypos, z=-shortwall_z)

                placeFront = geom.structure.Placement('ArapucaFront%d_%d' % (i,j),
                                                 volume = "volArapucaEnc",
                                                 pos = 'FrontAraP%d_%d' % (i,j),
                                                 rot = "rPlus180AboutX")
                placeBack = geom.structure.Placement('ArapucaBack%d_%d' % (i,j),
                                                 volume = "volArapucaEnc",
                                                 pos = 'BackAraP%d_%d' % (i,j),
                                                 rot = "rIdentity")
                
                cryo_LV.placements.append(placeFront.name)
                cryo_LV.placements.append(placeBack.name)
                
                xpos += (ara_len + vert_space)
                if (j % 6 == 0):
                    xpos += globals.get('LargeVertSpacing')

            xpos = tpcenc_x + cathode_x - 0.5*(ara_len+vert_space) - globals.get('heightCathode')
            for j in range(nrows+1, 2*nrows+1):
                araF = geom.structure.Position('FrontAraP%d_%d' % (i,j), x=xpos, y=ypos, z=shortwall_z)
                araB = geom.structure.Position('BackAraP%d_%d' % (i,j), x=xpos, y=ypos, z=-shortwall_z)

                placeFront = geom.structure.Placement('ArapucaFront%d_%d' % (i,j),                                                
                                                 volume = "volArapucaEnc",
                                                 pos = 'FrontAraP%d_%d' % (i,j),
                                                 rot = "rPlus180AboutX")
                placeBack = geom.structure.Placement('ArapucaBack%d_%d' % (i,j),                                                
                                                 volume = "volArapucaEnc",
                                                 pos = 'BackAraP%d_%d' % (i,j),
                                                 rot = "rIdentity")
                
                cryo_LV.placements.append(placeFront.name)
                cryo_LV.placements.append(placeBack.name)
                
                xpos -= (ara_len + vert_space)
                if (j % 6 == 0):
                    xpos -= globals.get('LargeVertSpacing')
            
            if (i % 6 == 0):
                ypos += (ara_len + short_space)
            else:
                ypos += (ara_len)

        # Vertical bars for longer laterals
        BarDepth = globals.get('VerticalBar_y')
        vertBar = geom.shapes.Box('VerticalBar', dx=globals.get('VerticalBar_x')/2, dy=globals.get('VerticalBar_y')/2, dz=globals.get('VerticalBar_z')/2)
        vertBarLV = make_volume(geom, "G10", vertBar)
        
        ncols = 60
        zpos = -shortwall_z + ara_len
        for i in range(1, ncols+1):
            LBpos = geom.structure.Position('LBpos%d' % (i),
                                                      x = -FC_x/4+tpcenc_x+cathode_x,
                                                      y = -longwall_y + BarDepth,
                                                      z = zpos)
            LTpos = geom.structure.Position('LTpos%d' % (i),
                                                      x = FC_x/4+tpcenc_x+cathode_x,
                                                      y = -longwall_y + BarDepth,
                                                      z = zpos)
            RBpos = geom.structure.Position('RBpos%d' % (i),
                                                      x = -FC_x/4+tpcenc_x+cathode_x,
                                                      y = longwall_y - BarDepth,
                                                      z = zpos)
            RTpos = geom.structure.Position('RTpos%d' % (i),
                                                      x = FC_x/4+tpcenc_x+cathode_x,
                                                      y = longwall_y - BarDepth,
                                                      z = zpos)

            LeftBottom = geom.structure.Placement('LeftBottom%d' % (i),
                                                  volume = vertBarLV.name,
                                                  pos = LBpos)
            LeftTop = geom.structure.Placement('LeftTop%d' % (i),
                                               volume = vertBarLV.name,
                                               pos = LTpos)
            RightBottom = geom.structure.Placement('RightBottom%d' % (i),
                                                   volume = vertBarLV.name,
                                                   pos = RBpos)
            RightTop = geom.structure.Placement('RightTop%d' % (i),
                                                volume = vertBarLV.name,
                                                pos = RTpos)
            
            cryo_LV.placements.append(LeftBottom.name)
            cryo_LV.placements.append(LeftTop.name)
            cryo_LV.placements.append(RightBottom.name)
            cryo_LV.placements.append(RightTop.name)
            
            zpos += 2*ara_len

            if (i % 3 == 0):
                zpos += long_space
        
        # Vertical bars for shorter laterals
        ncols = 12
        ypos = -longwall_y + ara_len
        for i in range(1, ncols+1):
            FBpos = geom.structure.Position('FBpos%d' % (i),
                                                      x = -FC_x/4+tpcenc_x+cathode_x,
                                                      y = ypos,
                                                      z = shortwall_z - BarDepth)
            FTpos = geom.structure.Position('FTpos%d' % (i),
                                                      x = FC_x/4+tpcenc_x+cathode_x,
                                                      y = ypos,
                                                      z = shortwall_z - BarDepth)
            BBpos = geom.structure.Position('BBpos%d' % (i),
                                                      x = -FC_x/4+tpcenc_x+cathode_x,
                                                      y = ypos,
                                                      z = -shortwall_z + BarDepth)
            BTpos = geom.structure.Position('BTpos%d' % (i),
                                                      x = FC_x/4+tpcenc_x+cathode_x,
                                                      y = ypos,
                                                      z = -shortwall_z + BarDepth)

            FrontBottom = geom.structure.Placement('FrontBottom%d' % (i),
                                                  volume = vertBarLV.name,
                                                  pos = FBpos)
            FrontTop = geom.structure.Placement('FrontTop%d' % (i),
                                               volume = vertBarLV.name,
                                               pos = FTpos)
            BackBottom = geom.structure.Placement('BackBottom%d' % (i),
                                                   volume = vertBarLV.name,
                                                   pos = BBpos)
            BackTop = geom.structure.Placement('BackTop%d' % (i),
                                                volume = vertBarLV.name,
                                                pos = BTpos)

            cryo_LV.placements.append(FrontBottom.name)
            cryo_LV.placements.append(FrontTop.name)
            cryo_LV.placements.append(BackBottom.name)
            cryo_LV.placements.append(BackTop.name)

            ypos += 2*ara_len

            if (i % 3 == 0):
                ypos += short_space

        return cryo_LV

