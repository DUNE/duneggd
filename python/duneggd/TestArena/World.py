#!/usr/bin/env python
'''An example GeGeDe module.

This provides some builder classes to build a Rubik's cube.

Warning: any resemblance between the result and an actual Rubik's cube
is purely accidental.  It's really just a 3x3x3 stack of blocks less
one at the origin.
'''

import gegede.builder
from gegede import Quantity as Q

class WorldBuilder(gegede.builder.Builder):
    '''
    Build a simple box world of given material and size.
    '''
    def configure(self, material = 'Air', size = Q("100m"), **kwds):
        self.material, self.size = (material, size)
        pass

    def construct(self, geom):
        dim = (0.5*self.size,)*3
        shape = geom.shapes.Box(self.name + '_box_shape', *dim)
        lv = geom.structure.Volume('vol'+self.name, material=self.material, shape=shape)
        self.add_volume(lv)

        # Note: this block adds all LVs of all sub builders at default
        # position/rotation which is probably not what is wanted in
        # general.
        for sbname, sbld in self.builders.items():
            for svname, svol in sbld.volumes.items():
                pname = '%s_in_%s' % (svol.name, self.name)
                p = geom.structure.Placement(pname, volume = svol)
                lv.placements.append(pname)

        self.define_materials(geom)
        r90aboutX   = geom.structure.Rotation('r90aboutX',                   x='90deg',  y='0deg',   z='0deg'  )
        r90aboutY   = geom.structure.Rotation('r90aboutY',                   x='0deg',   y='90deg',  z='0deg'  )
        r90aboutZ   = geom.structure.Rotation('r90aboutZ',                   x='0deg',   y='0deg',   z='90deg' )
        r90aboutXZ  = geom.structure.Rotation('r90aboutX_90aboutZ',          x='90deg',  y='0deg',   z='90deg' )
        r90aboutXY  = geom.structure.Rotation('r90aboutX_90aboutY',          x='90deg',  y='90deg',  z='0deg'  )
        r90aboutXYZ = geom.structure.Rotation('r90aboutX_90aboutY_90aboutZ', x='90deg',  y='90deg',  z='90deg' )
        r180aboutX  = geom.structure.Rotation('r180aboutX',                  x='180deg', y='0deg',   z='0deg'  )
        r180aboutY  = geom.structure.Rotation('r180aboutY',                  x='0deg',   y='180deg', z='0deg'  )
        r180aboutXY = geom.structure.Rotation('r180aboutX_180aboutY',        x='180deg', y='180deg', z='0deg'  )
        
    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def define_materials(self, g):
        h  = g.matter.Element("hydrogen",   "H",  1,  "1.0791*g/mole" )
        be = g.matter.Element("beryllium",  "Be", 4,  "9.012182*g/mole" )
        c  = g.matter.Element("carbon",     "C",  6,  "12.0107*g/mole")
        n  = g.matter.Element("nitrogen",   "N",  7,  "14.0671*g/mole")
        o  = g.matter.Element("oxygen",     "O",  8,  "15.999*g/mole" )
        f  = g.matter.Element("fluorine",   "F",  9,  "18.9984*g/mole")
        na = g.matter.Element("sodium",     "Na", 11, "22.99*g/mole"  )
        mg = g.matter.Element("magnesium",  "Mg", 12, "24.305*g/mole" )
        al = g.matter.Element("aluminum",   "Al", 13, "26.9815*g/mole")
        si = g.matter.Element("silicon",    "Si", 14, "28.0855*g/mole")
        p  = g.matter.Element("phosphorus", "P",  15, "30.973*g/mole" )
        s  = g.matter.Element("sulfur",     "S",  16, "32.065*g/mole" )
        ar = g.matter.Element("argon",      "Ar", 18, "39.948*g/mole" )
        ar = g.matter.Element("potassium",  "K",  19, "39.0983*g/mole")
        ca = g.matter.Element("calcium",    "Ca", 20, "40.078*g/mole" )
        ti = g.matter.Element("titanium",   "Ti", 22, "47.867*g/mole" )
        cr = g.matter.Element("chromium",   "Cr", 24, "51.9961*g/mole")
        mn = g.matter.Element("manganese",  "Mn", 25, "54.9380*g/mole")
        fe = g.matter.Element("iron",       "Fe", 26, "55.8450*g/mole")
        ni = g.matter.Element("nickel",     "Ni", 28, "58.6934*g/mole")
        cu = g.matter.Element("copper",     "Cu", 29, "63.55*g/mole"  )
        br = g.matter.Element("bromine",    "Br", 35, "79.904*g/mole" )
        xe = g.matter.Element("xenon",      "Xe", 54, "131.293*g/mole")
        pb = g.matter.Element("lead",       "Pb", 82, "207.20*g/mole" )



        # Molecules for Rock and fibrous_glass Mixtures 
        SiO2  = g.matter.Molecule("SiO2",  density="2.2*g/cc",   elements=(("silicon",1),("oxygen",2)))
        FeO   = g.matter.Molecule("FeO",   density="5.745*g/cc", elements=(("iron",1),("oxygen",1)))
        Al2O3 = g.matter.Molecule("Al2O3", density="3.97*g/cc",  elements=(("aluminum",2),("oxygen",3)))
        MgO   = g.matter.Molecule("MgO",   density="3.58*g/cc",  elements=(("magnesium",1),("oxygen",1)))
        CO2   = g.matter.Molecule("CO2",   density="1.562*g/cc", elements=(("carbon",1),("oxygen",2)))
        CaO   = g.matter.Molecule("CaO",   density="3.35*g/cc",  elements=(("calcium",1),("oxygen",1)))
        Na2O  = g.matter.Molecule("Na2O",  density="2.27*g/cc",  elements=(("sodium",2),("oxygen",1)))
        P2O5  = g.matter.Molecule("P2O5",  density="1.562*g/cc", elements=(("phosphorus",2),("oxygen",5)))        
        Layer2Molecule = g.matter.Molecule("Layer2Molecule",
                                           density="545.91*kg*m^-3",
                                           elements=(("carbon",6),
                                                     ("oxygen",5),
                                                     ("hydrogen",10)))
        Layer3Molecule = g.matter.Molecule("Layer3Molecule",
                                           density="90*kg*m^-3",
                                           elements=(("carbon",17),
                                                     ("oxygen",4),
                                                     ("nitrogen",2),
                                                     ("hydrogen",16)))        
       
        rock  = g.matter.Mixture( "Rock", density = "2.82*g/cc", 
                                  components = (
                                      ("SiO2",   0.5267),
                                      ("FeO",    0.1174),
                                      ("Al2O3",  0.1025),
                                      ("oxygen", 0.0771),
                                      ("MgO",    0.0473),
                                      ("CO2",    0.0422),
                                      ("CaO",    0.0382),
                                      ("carbon", 0.0240),
                                      ("sulfur", 0.0186),
                                      ("Na2O",   0.0053),
                                      ("P2O5",   0.0007),
                                  ))


        dirt  = g.matter.Mixture( "Dirt", density = "1.7*g/cc", 
                                  components = (
                                      ("oxygen",    0.438),
                                      ("silicon",   0.257),
                                      ("sodium",    0.222),
                                      ("aluminum",  0.049),
                                      ("iron",      0.019),
                                      ("potassium", 0.015),
                                  ))

        air   = g.matter.Mixture( "Air", density = "0.001225*g/cc", 
                                  components = (
                                      ("nitrogen", 0.781154), 
                                      ("oxygen",   0.209476),
                                      ("argon",    0.00934)
                                  ))

        Steel    = g.matter.Mixture( "Steel", density = "7.9300*g/cc", 
                                     components = (
                                         ("iron",     0.7298),
                                         ("chromium", 0.1792),
                                         ("nickel",   0.0900),
                                         ("carbon",   0.0010)
                                     ))
        CuBe    = g.matter.Mixture( "CuBe", density = "8.25g/cc", 
                                      components = (
                                          ("copper",    0.98),
                                          ("beryllium", 0.02)
                                      ))
        S460ML    = g.matter.Mixture( "S460ML", density = "7.8*g/cc", 
                                      components = (
                                          ("iron",      0.96),
                                          ("manganese", 0.018),
                                          ("nickel",    0.0085),
                                          ("silicon",   0.0065),
                                          ("copper",    0.006),
                                          ("carbon",    0.0018)
                                      ))
        Acrylic = g.matter.Mixture( "Acrylic", density = "1.19*g/cc",
                                    components = (
                                        ("carbon"  , 0.600),
                                        ("oxygen"  , 0.320),
                                        ("hydrogen", 0.080)
                                    ))
        
        # Layer2Matter = g.matter.Mixture("Layer2Matter",
        #                                 density = "0.09*g/cc", 
        #                                 elements = (("Layer1Molecule",1)))
        # Layer3Matter = g.matter.Mixture("Layer3Matter",
        #                                 density = "0.5*g/cc", 
        #                                 elements = (("Layer2Molecule",1)))
        
        LArTarget = g.matter.Molecule("LAr", density="1.4*g/cc"    , elements=(("argon", 1),))
        ArGas     = g.matter.Molecule("GAr", density="0.00166*g/cc", elements=(("argon", 1),))
