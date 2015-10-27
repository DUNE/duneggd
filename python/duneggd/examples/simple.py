from gegede import construct

def airwaterboxes():
    g  = construct.Geometry()
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

    U235 = g.matter.Isotope("U235", z=92, ia=235, a="235.0439242 g/mole")
    U238 = g.matter.Isotope("U238", z=92, ia=238, a="238.0507847 g/mole")
    enriched_uranium = g.matter.Composition("enriched_U", symbol="U", 
                                            isotopes=(("U235",0.8), ("U238",0.2)))

    box1 = g.shapes.Box("box1",'1cm','2cm','3cm')    
    box2 = g.shapes.Box("box2",'1m','2m','3m')    
    pos = g.structure.Position(None, '1cm',z='2cm')
    rot = g.structure.Rotation('', x='90deg')
    lv1 = g.structure.Volume('a_box', material=water, shape=box1)
    lv1inlv2 = g.structure.Placement("lv1_in_lv2", volume=lv1, pos=pos, rot=rot)
    lv2 = g.structure.Volume('the_world', material = air, shape=box2,
                             placements = [lv1inlv2], params= (("foo",42), ("bar","baz")))
    g.set_world(lv2)
    return g

