import gegede.builder
from gegede import Quantity as Q
from utils import *

class CryostatEncBuilder(gegede.builder.Builder):
    def configure(self, **kwds):
        if not set(kwds).issubset(globals.Cryostat): # no unknown keywords
            msg = 'Unknown parameter in: "%s"' % (', '.join(sorted(kwds.keys())), )
            raise ValueError(msg)

        # The builder hierarchy takes care of all the configuration parameters
        globals.Cryostat = kwds
        self.fShieldThickness = globals.get("ShieldThickness")
        self.fColdSkinThickness = globals.get("ColdSkinThickness")
        self.fWoodThickness = globals.get("WoodThickness")
        self.fWarmSkinThickness = globals.get("WarmSkinThickness")
        self.Offset = Q('0.1cm')

    def construct(self, geom):
        globals.SetDerived()

        cryoencBox = geom.shapes.Box(self.name,
                                     dx = globals.get("Cryostat_x")/2 + self.fWarmSkinThickness + self.fWoodThickness + self.fShieldThickness + self.fColdSkinThickness + self.Offset,
                                     dy = globals.get("Cryostat_y")/2 + self.fWarmSkinThickness + self.fWoodThickness + self.fShieldThickness + self.fColdSkinThickness + self.Offset,
                                     dz = globals.get("Cryostat_z")/2 + self.fWarmSkinThickness + self.fWoodThickness + self.fShieldThickness + self.fColdSkinThickness + self.Offset)
        cryoencLV = geom.structure.Volume('volEnclosureCryostat', material="Air", shape=cryoencBox)
        self.add_volume(cryoencLV)

        cryostat = self.get_builder("Cryostat")
        cryostatLV = cryostat.get_volume()

        ###this is the start of Cryostat logical volume ###
        cryostat_place = geom.structure.Placement(cryostatLV.name+'_PV', pos = "posCenter", volume = cryostatLV)
        cryoencLV.placements.append(cryostat_place.name)

        fSolidCryostat = geom.get_shape(cryostatLV)
        ShellOut = geom.shapes.Box('ShellOut',
					dx = globals.get("Cryostat_x")/2 + self.fColdSkinThickness,
					dy = globals.get("Cryostat_y")/2 + self.fColdSkinThickness,
					dz = globals.get("Cryostat_z")/2 + self.fColdSkinThickness)
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
					dx = globals.get("Cryostat_x")/2 + self.fWoodThickness + self.fColdSkinThickness,
					dy = globals.get("Cryostat_y")/2 + self.fWoodThickness + self.fColdSkinThickness,
					dz = globals.get("Cryostat_z")/2 + self.fWoodThickness + self.fColdSkinThickness)
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
					dx = globals.get("Cryostat_x")/2 + self.fShieldThickness + self.fWoodThickness + self.fColdSkinThickness,
					dy = globals.get("Cryostat_y")/2 + self.fShieldThickness + self.fWoodThickness + self.fColdSkinThickness,
					dz = globals.get("Cryostat_z")/2 + self.fShieldThickness + self.fWoodThickness + self.fColdSkinThickness)
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
					dx = globals.get("Cryostat_x")/2 + self.fWarmSkinThickness + self.fWoodThickness + self.fShieldThickness + self.fColdSkinThickness,
					dy = globals.get("Cryostat_y")/2 + self.fWarmSkinThickness + self.fWoodThickness + self.fShieldThickness + self.fColdSkinThickness,
					dz = globals.get("Cryostat_z")/2 + self.fWarmSkinThickness + self.fWoodThickness + self.fShieldThickness + self.fColdSkinThickness)
        fShellW = geom.shapes.Boolean('WarmSkin', type = 'subtraction',
                                      first = ShellOutW,
                                      second = sOutShield)
        fLogicShellW = geom.structure.Volume('ShellOutLog', material='fDuneSteel',shape=fShellW)
        ShellOutPla = geom.structure.Placement('Warmskin',
                                               pos = "posCenter",
                                               volume = fLogicShellW)
        cryoencLV.placements.append(ShellOutPla.name)

        return
