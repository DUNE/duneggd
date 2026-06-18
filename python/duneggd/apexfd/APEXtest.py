'''
Test to build APEX module
'''

from gegede import construct
from gegede import Quantity as Q
import gegede.export.gdml as gdml

ara_x = Q("0.5m")
ara_y = Q("0.5m")
ara_z = Q("0.007m")

ptp_width = Q("2um")


geom = construct.Geometry()


H = geom.matter.Element("H", "H", 1, "1.00794*g/mole")
C = geom.matter.Element("C", "C", 6, "12.0107*g/mole")
O = geom.matter.Element("O", "O", 8, "15.999*g/mole")


air = geom.matter.Mixture("Air", density="0.001225*g/cc")
acrylic = geom.matter.Mixture("Acrylic", density="1.18*g/cc", 
        components =  (("H", 5), ("C", 8), ("O", 2)))
ptp = geom.matter.Molecule("pTP", density="1.23*g/cc", 
        elements = (("C", 18), ("H", 14)))
mylar = geom.matter.Molecule("Mylar", density="1.40*g/cc",
        elements = (("C", 10), ("H", 8), ("O", 4)))


world_box = geom.shapes.Box("WorldBox", dx="3*m", dy="3*m", dz="3*m")
arapuca_box = geom.shapes.Box("AraBox", dx=ara_x/2, dy=ara_y/2, dz=ara_z/2)
ptp_box = geom.shapes.Box("pTPBox", dx=ara_x/2, dy=ara_y/2, dz=ptp_width/2)


world_lv = geom.structure.Volume("World", material="Air", shape=world_box)
arapuca_lv = geom.structure.Volume("Arapuca", material="Acrylic", shape=arapuca_box)
ptp_lv = geom.structure.Volume("pTP", material="pTP", shape=ptp_box)
back_lv = geom.structure.Volume("Backing", material="Mylar", shape=ptp_box)


ara_pos = geom.structure.Position("ara_pos", x="0*cm", y="0*cm", z="0*cm")
ara_rot = geom.structure.Rotation("ara_rot", x="0*deg", y="0*deg", z="0*deg")
ara_place = geom.structure.Placement("ara_place", volume=arapuca_lv, pos=ara_pos, rot=ara_rot)

ptp_pos = geom.structure.Position("ptp_pos", x="0*cm", y="0*cm", z= ara_z/2 + ptp_width/2)
ptp_place = geom.structure.Placement("ptp_place", volume=ptp_lv, pos=ptp_pos, rot=ara_rot)

back_pos = geom.structure.Position("back_pos", x="0*cm", y="0*cm", z= -ara_z/2 - ptp_width/2)
back_place = geom.structure.Placement("back_place", volume=back_lv, pos=back_pos, rot=ara_rot)

world_lv.placements.append(ara_place.name)
world_lv.placements.append(ptp_place.name)
world_lv.placements.append(back_place.name)

geom.set_world(world_lv)

xml = gdml.convert(geom)
gdml.output(xml, "test.gdml")
