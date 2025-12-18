import gegede.builder
from gegede import Quantity as Q
from utils import *

#Globals
#--------------------#
#  # these are nominal numbers
#  fShieldThickness = Q('77.6cm')
#  fColdSkinThickness = Q('0.18cm')
#  fWoodThickness = Q('4.8cm')
#  fWarmSkinThickness = Q('2.4cm')
# these are numbers just for testing
Offset = Q('0.1cm')
fShieldThickness = Q('77.48cm')
fColdSkinThickness = Q('0.1cm')
fWoodThickness = Q('2.4cm')
fWarmSkinThickness = Q('0.1cm')

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
                                     dx = globals.get("Cryostat_x")/2 +fWarmSkinThickness+ fWoodThickness +fShieldThickness+ fColdSkinThickness + Offset,
                                     dy = globals.get("Cryostat_y")/2 +fWarmSkinThickness+ fWoodThickness +fShieldThickness+ fColdSkinThickness + Offset,
                                     dz = globals.get("Cryostat_z")/2 +fWarmSkinThickness+ fWoodThickness +fShieldThickness+ fColdSkinThickness + Offset)
        cryoencLV = geom.structure.Volume('vol'+self.name, material="Air", shape=cryoencBox)
        self.add_volume(cryoencLV)

        #  posCryoInDetEnc = geom.structure.Position("posCryoInDetEnc", x = Q("-100cm"),
        #                                                               y=globals.get("posCryoInDetEnc_y"),
        #                                                               z= Q("-4000cm"))
        cryostat = self.get_builder("Cryostat")
        cryostatLV = cryostat.get_volume()

        ###this is the start of Cryostat logical volume ###
        cryostat_place = geom.structure.Placement('Cryostat_Place', pos = "posCenter", volume = cryostatLV)
        cryoencLV.placements.append(cryostat_place.name)

        fSolidCryostat = geom.get_shape(cryostatLV)
        ShellOut = geom.shapes.Box('ShellOut',
					dx = globals.get("Cryostat_x")/2 + fColdSkinThickness,
					dy = globals.get("Cryostat_y")/2 + fColdSkinThickness,
					dz = globals.get("Cryostat_z")/2 + fColdSkinThickness)
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

        ###this is start of wood logical volume###
        sOutWood = geom.shapes.Box('InWood',
					dx = globals.get("Cryostat_x")/2 + fWoodThickness + fColdSkinThickness,
					dy = globals.get("Cryostat_y")/2 + fWoodThickness + fColdSkinThickness,
					dz = globals.get("Cryostat_z")/2 + fWoodThickness + fColdSkinThickness)
        sWood = geom.shapes.Boolean('Wood', type = 'subtraction',
						first = sOutWood,
						second = ShellOut)
        fLogicWood = geom.structure.Volume('WoodLog', material='Wood', shape=sWood)
        WoodPla = geom.structure.Placement('WoodPlacement',
                                           pos = "posCenter",
                                           volume = fLogicWood)
        cryoencLV.placements.append(WoodPla.name)

        ###this is the start of foam logical volume###
        sOutShield = geom.shapes.Box('InShield',
					dx = globals.get("Cryostat_x")/2 + fShieldThickness + fWoodThickness + fColdSkinThickness,
					dy = globals.get("Cryostat_y")/2 + fShieldThickness + fWoodThickness + fColdSkinThickness,
					dz = globals.get("Cryostat_z")/2 + fShieldThickness + fWoodThickness + fColdSkinThickness)
        sShield = geom.shapes.Boolean('Foam', type = 'subtraction',
						first = sOutShield,
						second = sOutWood)
        fLogicShield = geom.structure.Volume('FoamLog', material='foam_protoDUNE_RPUF_assayedSample', shape=sShield)
        FoamPla = geom.structure.Placement('FoamPlacement',
                                           pos = "posCenter",
                                           volume = fLogicShield)

        cryoencLV.placements.append(FoamPla.name)


        ###this is the start of warmskin Logical volume###
        ShellOutW = geom.shapes.Box('ShellOutW',
					dx = globals.get("Cryostat_x")/2 + fWarmSkinThickness + fWoodThickness + fShieldThickness + fColdSkinThickness,
					dy = globals.get("Cryostat_y")/2 + fWarmSkinThickness + fWoodThickness + fShieldThickness + fColdSkinThickness,
					dz = globals.get("Cryostat_z")/2 + fWarmSkinThickness + fWoodThickness + fShieldThickness + fColdSkinThickness)
        fShellW = geom.shapes.Boolean('WarmSkin', type = 'subtraction',
                                      first = ShellOutW,
                                      second = sOutShield)
        fLogicShellW = geom.structure.Volume('ShellOutLog', material='fDuneSteel',shape=fShellW)
        ShellOutPla = geom.structure.Placement('Warmskin',
                                               pos = "posCenter",
                                               volume = fLogicShellW)

        cryoencLV.placements.append(ShellOutPla.name)

        return
