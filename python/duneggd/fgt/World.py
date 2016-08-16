#!/usr/bin/env python
'''
Top level builder of the Fine-Grained Tracker (FGT)
'''

import gegede.builder
import math
from gegede import Quantity as Q


class WorldBuilder(gegede.builder.Builder):
    '''
    Build a big box world volume.
    N.B. -- Global convention: index 0,1,2 = x,y,z
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, worldDim  =  [Q('100m'),Q('100m'),Q('100m')], 
                  servBuildingDim =  [Q('45ft'),Q('37.5ft'),Q('135.5ft')], 
                  secondHallDim   =  [Q('47ft'),Q('11ft'),Q('19ft')], 
                  encBackWallToHall_z = Q('46.25ft'),
                  overburden          = Q('155.94ft'),
                  dirtDepth           = Q('50ft'),
                  primaryShaft_r      = Q('11ft'), 
                  secondaryShaft_r    = Q('8.5ft'),
                  shaftToEndBuilding  = Q('79ft'),
                  worldMat='Rock', **kwds):
        self.worldDim = worldDim
        self.material   = worldMat
        self.detEncBldr = self.get_builder("DetEnclosure")

        self.servBDim            = servBuildingDim
        self.overburden          = overburden
        self.dirtDepth           = dirtDepth
        self.primaryShaft_r      = primaryShaft_r
        self.secondaryShaft_r    = secondaryShaft_r
        self.secondHallDim       = secondHallDim
        self.encBackWallToHall_z = encBackWallToHall_z
        self.shaftToEndBuilding  = shaftToEndBuilding

        self.secHallMat = 'Air'
        self.servBMat   = 'Air'
        self.shaftMat   = 'Air'


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Get relevant dimensions
        detEncDim     = list(self.detEncBldr.detEncDim)
        secShaft_y    = self.overburden + detEncDim[1] - self.secondHallDim[1]

        encBoundToDet = list(self.detEncBldr.encBoundToDet)
        detDim        = list(self.detEncBldr.detDim)
        

        ########################### SET THE ORIGIN  #############################
        #                                                                       #
        # Position volDetEnclosure in the World Volume, displacing the world    #
        #  origin relative to the detector enclosure, thereby putting it        #
        #  anywhere in or around the detector we need.                          #
        #                                                                       #
        # Bring x=0 to -x of detEnc, then to det face, then to center of det    #
        setXCenter    =   0.5*detEncDim[0] - encBoundToDet[0] - 0.5*detDim[0]   #
                                                                                #
        # Bring y=0 to bottom of detEnc, then to center of detector             #
        setYCenter    =   0.5*detEncDim[1] - encBoundToDet[1] - 0.5*detDim[1]   #
                                                                                #
        # Bring z=0 to back of detEnc, then to upstream face of detector.       #
        setZCenter    =   0.5*detEncDim[2] - encBoundToDet[2]                   #
        #  should we leave this at the back of the enclosure?:                  #
        #setZCenter    =  -0.5*detEncDim[2]                                     #
                                                                                #
        detEncPos     = [ setXCenter, setYCenter, setZCenter ]                  #
        #########################################################################




        # Position shafts and secondary hall around DetEnclosure
        primShaftPos  = [ detEncPos[0],  # center for now
                          detEncPos[1] + 0.5*detEncDim[1] + 0.5*self.overburden,
                          detEncPos[2] - 0.5*detEncDim[2] + self.primaryShaft_r ]

        secHallPos    = [ detEncPos[0] - 0.5*detEncDim[0] - 0.5*self.secondHallDim[0],
                          detEncPos[1] - 0.5*detEncDim[1] + 0.5*self.secondHallDim[1],
                          detEncPos[2] - 0.5*detEncDim[2] + self.encBackWallToHall_z + 0.5*self.secondHallDim[2] ]

        secShaftPos   = [ secHallPos[0] - 0.5*self.secondHallDim[0] + self.secondaryShaft_r,
                          secHallPos[1] + 0.5*self.secondHallDim[1] + 0.5*secShaft_y,
                          secHallPos[2] ]
                          


        # Determine rotation around y bassed off of shaft positions
        #   In local coordinates of service building, assume the
        #    primary shaft is centered in x (blatantly wrong), 
        #    and positive x boundary bisects secondary shaft
        primToSec_aboutX_worldC = math.atan( (secShaftPos[0] - primShaftPos[0]) / (secShaftPos[2] - primShaftPos[2]) )

        secToPrim_aboutX_servBC = math.atan( 0.5*self.servBDim[0] / (self.shaftToEndBuilding - self.secondaryShaft_r) )
        
        servBRot_aboutY         = secToPrim_aboutX_servBC - primToSec_aboutX_worldC

        shaftCent_to_servBCent  = 0.5*self.secondaryShaft_r + self.shaftToEndBuilding - 0.5*self.servBDim[2]



        # Position sevice building on top of primary shaft
        servBPos      = [ primShaftPos[0] - shaftCent_to_servBCent*math.sin(servBRot_aboutY),
                          primShaftPos[1] + 0.5*self.overburden + 0.5*self.servBDim[1],
                          primShaftPos[2] + shaftCent_to_servBCent*math.cos(servBRot_aboutY) ]


        # Put Sky around Building
        skyDim        = [ self.worldDim[0],
                          0.5*self.worldDim[1] - (servBPos[1] - 0.5*self.servBDim[1]),
                          self.worldDim[2] ]
        skyPos        = [ Q('0cm'),
                          0.5*self.worldDim[1] - 0.5*skyDim[1],
                          Q('0cm') ]

        # Put dirt layer around shafts
        dirtLayerPos  = [ Q('0cm'),
                          detEncPos[1] + 0.5*detEncDim[1] + self.overburden - 0.5*self.dirtDepth,
                          Q('0cm') ]


        ########################### Above is math, below is GGD ###########################

        self.define_materials(geom)
        r90aboutX      = geom.structure.Rotation( 'r90aboutX',      '90deg',  '0deg',  '0deg'  )
        rminus90aboutX = geom.structure.Rotation( 'rminus90aboutX', '-90deg', '0deg',  '0deg'  )
        r90aboutY      = geom.structure.Rotation( 'r90aboutY',      '0deg',   '90deg', '0deg'  )
        r180aboutY     = geom.structure.Rotation( 'r180aboutY',     '0deg',   '180deg','0deg'  )
        rminus90aboutY = geom.structure.Rotation( 'rminus90aboutY', '0deg', '-90deg',  '0deg'  )
        r90aboutZ      = geom.structure.Rotation( 'r90aboutZ',      '0deg',   '0deg',  '90deg' )
        r90aboutXZ = geom.structure.Rotation( 'r90aboutXZ', '90deg',  '0deg', '90deg'  )



        worldBox = geom.shapes.Box( self.name,               dx=0.5*self.worldDim[0], 
                                    dy=0.5*self.worldDim[1], dz=0.5*self.worldDim[2])
        world_lv = geom.structure.Volume('vol'+self.name, material=self.material, shape=worldBox)
        self.add_volume(world_lv)

        # Get volDetEnclosure and place it
        detEnc_lv = self.detEncBldr.get_volume("volDetEnclosure")
        detEnc_in_world = geom.structure.Position('DetEnc_in_World', detEncPos[0], detEncPos[1], detEncPos[2])
        pD_in_W = geom.structure.Placement('placeDetEnc_in_World',
                                           volume = detEnc_lv,
                                           pos = detEnc_in_world)
        world_lv.placements.append(pD_in_W.name)


        # Hall from DetEnc to Secondary Shaft
        secHallBox = geom.shapes.Box( 'SecondaryHall',              dx=0.5*self.secondHallDim[0], 
                                      dy=0.5*self.secondHallDim[1], dz=0.5*self.secondHallDim[2])
        secHall_lv = geom.structure.Volume('volSecondaryHall', material=self.secHallMat, shape=secHallBox)
        secHall_in_world = geom.structure.Position('secHall_in_World', secHallPos[0], secHallPos[1], secHallPos[2])
        p_secHall_in_W = geom.structure.Placement('place_secHall_in_World',
                                                  volume = secHall_lv,
                                                  pos = secHall_in_world)
        world_lv.placements.append(p_secHall_in_W.name)



        # Primary Shaft
        pShaftTube    = geom.shapes.Tubs('PrimaryShaft', 
                                         rmin = '0cm',              
                                         rmax = self.primaryShaft_r, 
                                         dz   = 0.5*self.overburden)
        pShaft_lv = geom.structure.Volume('volPrimaryShaft', material=self.shaftMat, shape=pShaftTube)
        pShaft_in_world = geom.structure.Position('pShaft_in_World', primShaftPos[0], primShaftPos[1], primShaftPos[2])
        pS_in_W = geom.structure.Placement('placePrimShaft_in_World',
                                           volume = pShaft_lv,
                                           pos = pShaft_in_world, rot='r90aboutX')
        world_lv.placements.append(pS_in_W.name)


        # Secondary Shaft
        sShaftTube    = geom.shapes.Tubs('SecondaryShaft', 
                                         rmin = '0cm',              
                                         rmax = self.secondaryShaft_r, 
                                         dz   = 0.5*secShaft_y)
        sShaft_lv = geom.structure.Volume('volSecondaryShaft', material=self.shaftMat, shape=sShaftTube)
        sShaft_in_world = geom.structure.Position('sShaft_in_World', secShaftPos[0], secShaftPos[1], secShaftPos[2])
        sS_in_W = geom.structure.Placement('placeSecShaft_in_World',
                                           volume = sShaft_lv,
                                           pos = sShaft_in_world, rot='r90aboutX')
        world_lv.placements.append(sS_in_W.name)



        # Dirt layer
        DirtLayerBox = geom.shapes.Box(     'DirtLayerBox',          dx=0.5*self.worldDim[0], 
                                            dy=0.5*self.dirtDepth,   dz=0.5*self.worldDim[2])
        pShaft_in_dLayer = geom.structure.Position('pShaft_in_dLayer', primShaftPos[0], Q('0cm'), primShaftPos[2])
        sShaft_in_dLayer = geom.structure.Position('sShaft_in_dLayer', secShaftPos[0],  Q('0cm'), secShaftPos[2] )
        DirtLayer1   = geom.shapes.Boolean( 'DirtLayer1', type='subtraction', 
                                            first=DirtLayerBox, second=pShaftTube,
                                            pos = pShaft_in_dLayer, rot='r90aboutX') 
        DirtLayer    = geom.shapes.Boolean( 'DirtLayer',  type='subtraction', 
                                            first=DirtLayer1, second=sShaftTube,
                                            pos = sShaft_in_dLayer, rot='r90aboutX') 
        dirtLayer_lv = geom.structure.Volume('volDirtLayer', material='Dirt', shape=DirtLayer)
        dLayer_in_world = geom.structure.Position('dLayer_in_World', dirtLayerPos[0], dirtLayerPos[1], dirtLayerPos[2])
        pdl_in_W = geom.structure.Placement('placeDLayer_in_World',
                                            volume = dirtLayer_lv,
                                            pos = dLayer_in_world )
        world_lv.placements.append(pdl_in_W.name)



        # Sky with building
        skyBox = geom.shapes.Box( 'Sky',            dx=0.5*skyDim[0], 
                                  dy=0.5*skyDim[1], dz=0.5*skyDim[2])
        sky_lv = geom.structure.Volume('volSky', material='Air', shape=skyBox)
        sky_in_world = geom.structure.Position('sky_in_World', skyPos[0], skyPos[1], skyPos[2])
        p_sky_in_W = geom.structure.Placement('place_sky_in_World',
                                              volume = sky_lv,
                                              pos = sky_in_world)
        world_lv.placements.append(p_sky_in_W.name)


        # Sevice Building
        servBBox = geom.shapes.Box( 'ServiceBuilding',       dx=0.5*self.servBDim[0], 
                                    dy=0.5*self.servBDim[1], dz=0.5*self.servBDim[2])
        servB_lv = geom.structure.Volume('volServiceBuilding', material=self.servBMat, shape=servBBox)
        yrot = str(servBRot_aboutY)+'rad'
        rServB_aboutY = geom.structure.Rotation('rSevBuilding_aboutY', '0deg', yrot, '0deg')
        #servB_in_world = geom.structure.Position('servB_in_World', servBPos[0], servBPos[1], servBPos[2])
        servB_in_sky = geom.structure.Position('servB_in_Sky', 
                                               servBPos[0], 
                                               -0.5*skyDim[1] + 0.5*self.servBDim[1], 
                                               servBPos[2])
        p_servB_in_S = geom.structure.Placement('place_servB_in_Sky',
                                                volume = servB_lv,
                                                pos = servB_in_sky, rot = rServB_aboutY)
        sky_lv.placements.append(p_servB_in_S.name)

        return


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def define_materials(self, g):
        h  = g.matter.Element("hydrogen",   "H",  1,  "1.0791*g/mole" )
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
        fe = g.matter.Element("iron",       "Fe", 26, "55.8450*g/mole")
        ni = g.matter.Element("nickel",     "Ni", 28, "58.6934*g/mole")
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
        TiO2  = g.matter.Molecule("TiO2",  density="4.23*g/cc",  elements=(("titanium",1),("oxygen",2)))
        Fe2O3 = g.matter.Molecule("Fe2O3", density="5.24*g/cc",  elements=(("iron",2),("oxygen",3)))

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


        bakelite = g.matter.Mixture( "Bakelite", density = "1.25*g/cc", 
                                      components = (
                                          ("hydrogen", 0.057441),
                                          ("carbon",   0.774591),
                                          ("oxygen",   0.167968)
                                      ))


        honeycomb = g.matter.Mixture( "Honeycomb", density = "0.94*g/cc", 
                                      components = (
                                          ("hydrogen", 0.143711),
                                          ("carbon",   0.856289)
                                      ))

        # Materials for the radiators and st planes following
        # WARNING! densities not right!
        C3H6   = g.matter.Molecule("C3H6",   density="0.946*g/cc",   elements=(("carbon",3), ("hydrogen",6)))
        fracC3H6 = (25*0.946)/(25*0.946+125*0.001225) # TODO get from spacing in RadiatorBldr cfg
        #densRad = fracC3H6*0.946 + (1-fracC3H6)*0.001225
        #dRad = str(densRad)+"*g/cc"
        dRad = "0.1586875*g/cc"
        print "Radiator dens: " + dRad
        RadBlend = g.matter.Mixture( "RadiatorBlend", density = dRad, 
                                     components = (
                                         ("Air",  1-fracC3H6),
                                         ("C3H6", fracC3H6)
                                     ))
        densCO2 = 44.01/22.4*0.001 # molar mass / STP molar volume * conversion to g/cm3 from L
        densAr  = 39.95/22.4*0.001
        densXe  = 131.3/22.4*0.001
        fracCO2 = .3
        densArCO2 = fracCO2 * densCO2 + (1-fracCO2) * densAr
        densXeCO2 = fracCO2 * densCO2 + (1-fracCO2) * densXe
        dArCO2 = str(densArCO2)+"*g/cc"
        dXeCO2 = str(densXeCO2)+"*g/cc"

        print "ArC02 dens: " + dArCO2
        print "XeC02 dens: " + dXeCO2

        stGas_Xe = g.matter.Mixture( "stGas_Xe", density = dXeCO2, 
                                      components = (
                                          ("CO2",    fracCO2),
                                          ("argon",  1-fracCO2)
                                          #("xenon",  1-fracCO2)   #GENIE XSec spline having trouble with xenon 
                                      ))

        # Materials for the targets and st planes following
        H2O      = g.matter.Molecule("Water",       density="1.0*kg/l",   elements=(("oxygen",1),("hydrogen",2)))
        ArTarget = g.matter.Molecule("ArgonTarget", density="0.2297*g/cc", elements=(("argon",1),))
        #ArTarget = g.matter.Molecule("ArgonTarget", density="10.2297*g/cc", elements=(("argon",1),))
        Aluminum = g.matter.Molecule("Aluminum",    density="2.70*g/cc",  elements=(("aluminum",1),))
        CarFiber = g.matter.Molecule("CarbonFiber", density="1.6*g/cc",  elements=(("carbon",1),))
        stGas_Ar = g.matter.Mixture( "stGas_Ar", density = dArCO2, 
                                      components = (
                                          ("CO2",    fracCO2),
                                          ("argon",  1-fracCO2)
                                      ))


        Kapton   = g.matter.Molecule("Kapton",   density="1.4*g/cc",   elements=(("carbon",22), ("oxygen",5), ("nitrogen",2)))


        Iron     = g.matter.Molecule("Iron",     density="7.874*g/cc", elements=(("iron",1),))
        Graphite = g.matter.Molecule("Graphite", density="2.23*g/cc",  elements=(("carbon",1),))
        Calcium  = g.matter.Molecule("Calcium",  density="1.55*g/cc",  elements=(("calcium",1),))

        Steel    = g.matter.Mixture( "Steel", density = "7.9300*g/cc", 
                                     components = (
                                         ("iron",     0.7298),
                                         ("chromium", 0.1792),
                                         ("nickel",   0.0900),
                                         ("carbon",   0.0010)
                                     ))


        Polycarbonate = g.matter.Molecule("polycarbonate", density="1.6*g/cc",  
                                          elements=(
                                              ("carbon",16),
                                              ("hydrogen",6),
                                              ("oxygen",3)
                                          ))

        # make up a dumb but not crazy density for the STT framing just inside of the ECAL
        sttFrameMix = g.matter.Mixture( "sttFrameMix", density = "0.235*g/cc", 
                                        components = (
                                            ("carbon",        3.9/5.1),
                                            ("polycarbonate", 1.2/5.1)
                                        ))
        
        
        # for the straws -- density??
        fib_glass = g.matter.Mixture( "fibrous_glass", density = "1.0*g/cc", 
                                      components = (
                                          ("SiO2",   0.600),
                                          ("CaO",    0.224),
                                          ("Al2O3",  0.118),
                                          ("MgO",    0.034),
                                          ("TiO2",   0.013),
                                          ("Na2O",   0.010),
                                          ("Fe2O3",  0.001)
                                      ))

        #   Materials for the RPCs
        # tetraflouroethane:
        CH2FCF3 = g.matter.Molecule( "CH2FCF3",  density="0.00425*g/cc",   
                                     elements=( ("carbon",2), ("hydrogen",2), ("fluorine",4) ))
        # isobutane:
        C4H10   = g.matter.Molecule( "C4H10",    density="0.00251*g/cc",   
                                     elements=( ("carbon",4), ("hydrogen",10) ))
        # sulphurhexaflouride:
        SF6     = g.matter.Molecule( "SF6",      density="6.17*g/L",   
                                     elements=( ("sulfur",4), ("fluorine",6)  ))

        # use argon density at stp for now. has very little effect.
        rpcGas   = g.matter.Mixture( "rpcGas", density = "1.784*g/L", 
                                     components = (
                                         ("argon",   0.75),
                                         ("CH2FCF3", 0.20),
                                         ("C4H10",   0.04),
                                         ("SF6",     0.01)
                                     ))


        # Materials for the ECAL
        # Epoxy Resin (Glue that will hold the scintillator bars and the lead sheets together):
        # probably won't show up, just the default material of SBPlane
        epoxy_resin   = g.matter.Molecule("epoxy_resin",   density="1.1250*g/cc",   
                                          elements=(
                                              ("carbon",38), 
                                              ("hydrogen",40), 
                                              ("oxygen",6) 
                                              #("bromine",4) GENIE having trouble with Br 
                                              ))
        
        # Scintillator:
        Scintillator  = g.matter.Mixture("Scintillator",   density="1.05*g/cc",   
                                         components = (
                                             ("carbon",   0.916), 
                                             ("hydrogen", 0.084)
                                         ))          
        # Lead:
        Lead  = g.matter.Molecule("Lead",   density="11.342*g/cc",   elements=(("lead",1),))


        # for LAr otion using this world:
        LArTarget = g.matter.Molecule("LAr", density="1.4*g/cc", elements=(("argon",1),))
