#!/usr/bin/env python
'''
Example gegede builders for a trivial LAr geometry
'''

import gegede.builder

class WorldBuilder(gegede.builder.Builder):
    '''
    Build a big box world volume.
    '''

    def configure(self, size='50m', material='Rock', **kwds):
        self.size = size
        self.material = material
        
    def construct(self, geom):

        g  = geom
        h  = g.matter.Element("Hydrogen",   "H",  1,  "1.0791*g/mole" )
        c  = g.matter.Element("Carbon",     "C",  6,  "12.0107*g/mole")
        n  = g.matter.Element("Nitrogen",   "N",  7,  "14.0671*g/mole")
        o  = g.matter.Element("Oxygen",     "O",  8,  "15.999*g/mole" )
        na = g.matter.Element("Sodium",     "Na", 11, "22.99*g/mole"  )
        mg = g.matter.Element("Magnesium",  "Mg", 12, "24.305*g/mole" )
        al = g.matter.Element("Aluminum",   "Al", 13, "26.9815*g/mole")
        si = g.matter.Element("Silicon",    "Si", 14, "28.0855*g/mole")
        p  = g.matter.Element("Phosphorus", "P",  15, "30.973*g/mole" )
        s  = g.matter.Element("Sulfur",     "S",  16, "32.065*g/mole" )
        ar = g.matter.Element("Argon",      "Ar", 18, "39.948*g/mole" )
        ca = g.matter.Element("Calcium",    "Ca", 20, "40.078*g/mole" )
        fe = g.matter.Element("Iron",       "Fe", 26, "55.8450*g/mole")
        
        
        SiO2  = g.matter.Molecule("SiO2",  density="2.2*g/cc",   elements=(("Silicon",1),("Oxygen",2)))
        FeO   = g.matter.Molecule("FeO",   density="5.745*g/cc", elements=(("Iron",1),("Oxygen",1)))
        Al2O3 = g.matter.Molecule("Al2O3", density="3.97*g/cc",  elements=(("Aluminum",2),("Oxygen",3)))
        MgO   = g.matter.Molecule("MgO",   density="3.58*g/cc",  elements=(("Magnesium",1),("Oxygen",1)))
        CO2   = g.matter.Molecule("CO2",   density="1.562*g/cc", elements=(("Carbon",1),("Oxygen",2)))
        CaO   = g.matter.Molecule("CaO",   density="3.35*g/cc",  elements=(("Calcium",1),("Oxygen",1)))
        Na2O  = g.matter.Molecule("Na2O",  density="2.27*g/cc",  elements=(("Sodium",2),("Oxygen",1)))
        P2O5  = g.matter.Molecule("P2O5",  density="1.562*g/cc", elements=(("Phosphorus",2),("Oxygen",5)))
        
        water = g.matter.Molecule("Water", density="1.0*kg/l",   elements=(("Oxygen",1),("Hydrogen",2)))
        air   = g.matter.Mixture("Air", density = "1.290*mg/cc", 
                                 components = (("Nitrogen", 0.7), ("Oxygen",0.3)))
        
        rock  = g.matter.Mixture("Rock", density = "2.82*g/cc", 
                                 components = (
                                     ("SiO2",   0.5267),
                                     ("FeO",    0.1174),
                                     ("Al2O3",  0.1025),
                                     ("Oxygen", 0.0771),
                                     ("MgO",    0.0473),
                                     ("CO2",    0.0422),
                                     ("CaO",    0.0382),
                                     ("Carbon", 0.0240),
                                     ("Sulfur", 0.0186),
                                     ("Na2O",   0.0053),
                                     ("P2O5",   0.0007),
                                 ))

        shape = geom.shapes.Box(self.name + '_box_shape', dx=self.size, dy=self.size, dz=self.size)
        lv = geom.structure.Volume(self.name+'_volume', material=self.material, shape=shape)
        self.add_volume(lv)

        site_lv = self.builders.values()[0].volumes.values()[0] # expect one sub-builder with one logical volume
        geom.structure.Placement('%s_in_%s' % (site_lv.name, self.name), volume = site_lv)
        return

class SiteBuilder(gegede.builder.Builder):
    def configure(self, site='homestake', material = 'Air', **kwds):
        self.site = site.lower()
        self.material = material

    def construct(self, geom):
        if self.site == 'homestake':
            shape = geom.shapes.Box('homestake site box', dx='10m', dy='10m', dz='10m')
        elif self.site == '35t':
            shape = geom.shapes.Box('35t site box', dx='5m', dy='5m', dz='5m')
        else:
            raise ValueError, 'Unknown site: "%s"' % self.site
        lv = geom.structure.Volume(self.site + '_volume', material=self.material, shape=shape)
        self.add_volume(lv)
