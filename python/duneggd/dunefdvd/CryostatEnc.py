import gegede.builder
from gegede import Quantity as Q
from utils import *

#Globals
#--------------------#
fColdSkinThickness = Q('0.18cm')
Offset = Q('10cm')
fShieldThickness = Q('77.6cm')
fWoodThickness = Q('4.8cm')
fWarmSkinThickness = Q('2.4cm')
fht = Q('841.1cm')
fst = Q('896.4cm') + Q('3.1cm')
fzpl = Q('6473.2cm') + Q('0.1cm')

class CryostatEncBuilder(gegede.builder.Builder):
    def configure(self, **kwds):
        if not set(kwds).issubset(globals.Cryostat): # no unknown keywords
            msg = 'Unknown parameter in: "%s"' % (', '.join(sorted(kwds.keys())), )
            raise ValueError(msg)

        # The builder hierarchy takes care of all the configuration parameters
        globals.Cryostat = kwds

    def construct(self, geom):
        globals.SetDerived()

        cryoencBox = geom.shapes.Box(self.name,
                                     dx=0.5*globals.get("Cavern_x") - Q('100cm'),
                                     dy=0.5*globals.get("Cavern_y") - Q('10cm'),
                                     dz=0.5*globals.get("Cavern_z") - Q('10cm'))
        cryoencLV = geom.structure.Volume('vol'+self.name, material="Air", shape=cryoencBox)
        self.add_volume(cryoencLV)

        cryostat = self.get_builder("Cryostat")
        cryostatLV = cryostat.get_volume()

        ###this is the start of Cryostat logical volume ###
        cryostat_place = geom.structure.Placement('Cryostat_Place', pos = "posCenter", volume = cryostatLV)
        cryoencLV.placements.append(cryostat_place.name)

        fSolidCryostat = geom.get_shape(cryostatLV)
        ShellOut = geom.shapes.Box('ShellOut',
					dy = globals.get("Cryostat_x")/2 +fColdSkinThickness + Offset,
					dx = globals.get("Cryostat_y")/2 +fColdSkinThickness + Offset,
					dz = globals.get("Cryostat_z")/2 +fColdSkinThickness + Offset)
        fShell = geom.shapes.Boolean('fShell', type = 'subtraction',
                                     first = ShellOut,
                                     second = fSolidCryostat)
        fLogicShell = geom.structure.Volume('fShellLog',
                                            material = 'fDuneSteel',
                                            shape = fShell)
        fPhysShell = geom.structure.Placement('fPhysShell',
                                              pos = "posCenter",
                                              volume = fLogicShell)

        cryoencLV.placements.append(fPhysShell.name)

        ###this is the start of foam logical volume###
        sOutShield = geom.shapes.Box('InShield',
					dy = globals.get("Cryostat_x")/2 + fShieldThickness + fColdSkinThickness + Offset,
					dx = globals.get("Cryostat_y")/2 + fShieldThickness + fColdSkinThickness + Offset,
					dz = globals.get("Cryostat_z")/2 + fShieldThickness + fColdSkinThickness + Offset)
        sShield = geom.shapes.Boolean('Foam', type = 'subtraction',
						first = sOutShield,
						second = ShellOut)
        fLogicShield = geom.structure.Volume('FoamLog', material='Foam', shape=sShield)
        FoamPla = geom.structure.Placement('FoamPlacement',
                                           pos = "posCenter",
                                           volume = fLogicShield)

        cryoencLV.placements.append(FoamPla.name)

        ###this is start of wood logical volume###
        sOutWood = geom.shapes.Box('InWood',
					dy = globals.get("Cryostat_x")/2 + fWoodThickness + fShieldThickness+ fColdSkinThickness + Offset,
					dx = globals.get("Cryostat_y")/2 + fWoodThickness +fShieldThickness+ fColdSkinThickness + Offset,
					dz = globals.get("Cryostat_z")/2 + fWoodThickness +fShieldThickness+ fColdSkinThickness + Offset)
        sWood = geom.shapes.Boolean('Wood', type = 'subtraction',
						first = sOutWood,
						second = sOutShield)
        fLogicWood = geom.structure.Volume('WoodLog', material='Wood', shape=sWood)
        WoodPla = geom.structure.Placement('WoodPlacement',
                                           pos = "posCenter",
                                           volume = fLogicWood)
        cryoencLV.placements.append(WoodPla.name)

        ###this is the start of warmskin Logical volume###
        ShellOutW = geom.shapes.Box('ShellOutW',
					dy = globals.get("Cryostat_x")/2 +fWarmSkinThickness+ fWoodThickness +fShieldThickness+ fColdSkinThickness + Offset,
					dx = globals.get("Cryostat_y")/2 +fWarmSkinThickness+ fWoodThickness +fShieldThickness+ fColdSkinThickness + Offset,
					dz = globals.get("Cryostat_z")/2 +fWarmSkinThickness+ fWoodThickness +fShieldThickness+ fColdSkinThickness + Offset)
        fShellW = geom.shapes.Boolean('WarmSkin', type = 'subtraction',
                                      first = ShellOutW,
                                      second = sOutWood)
        fLogicShellW = geom.structure.Volume('ShellOutLog', material='fDuneSteel',shape=fShellW)
        ShellOutPla = geom.structure.Placement('Warmskin',
                                               pos = "posCenter",
                                               volume = fLogicShellW)

        cryoencLV.placements.append(ShellOutPla.name)

        # get outer support structure
        supportenc = self.get_builder("SupportEnc")
        supportencLV = supportenc.get_volume()
        supportPla = geom.structure.Placement('SupportStructurePlace', pos="posCenter", volume=supportencLV)
        cryoencLV.placements.append(supportPla.name)

        return
