#!/usr/bin/env python
'''
Top level builder of the Fine-Grained Tracker (FGT)
'''

import gegede.builder
import math
#import gegede.Quantity as Q

class WorldBuilder(gegede.builder.Builder):
    '''
    Build a big box world volume.
    N.B. -- Global convention: index 0,1,2 = x,y,z
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, worldDim  =  ['100m','100m','100m'], 
                  servBuildingDim =  ['45ft','37.5ft','135.5ft'], 
                  secondHallDim   =  ['47ft','11ft','19ft'], 
                  encBackWallToHall_z = '46.25ft',
                  overburden          = '155.94ft', 
                  primaryShaft_r      = '11ft', 
                  secondaryShaft_r    = '8.5ft',
                  shaftToEndBuilding  = '79ft',
                  placeDetector       = True,
                  worldMat='Rock', **kwds):
        self.worldDim = worldDim
        self.material   = worldMat
        self.detEncBldr = self.get_builder("DetEnclosure")

        self.servBDim            = servBuildingDim
        self.overburden          = overburden
        self.primaryShaft_r      = primaryShaft_r
        self.secondaryShaft_r    = secondaryShaft_r
        self.secondHallDim       = secondHallDim
        self.encBackWallToHall_z = encBackWallToHall_z
        self.shaftToEndBuilding  = shaftToEndBuilding
        self.placeDet            = placeDetector

        self.secHallMat = 'Air'
        self.servBMat   = 'Air'
        self.shaftMat   = 'Air'


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Get relevant dimensions
        detEncDim     = list(self.detEncBldr.detEncDim)
        secShaft_y    = self.overburden + detEncDim[1] - self.secondHallDim[1]
        if self.placeDet:
            encBoundToDet = list(self.detEncBldr.encBoundToDet)
            detDim        = list(self.detEncBldr.detDim)
        else:
            encBoundToDet = [ 0*detEncDim[0], 0*detEncDim[1], 0*detEncDim[2]]
            detDim        = list(encBoundToDet)


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
        skyPos        = [ 0*servBPos[0],
                          0.5*self.worldDim[1] - 0.5*skyDim[1],
                          0*servBPos[0] ]


        ########################### Above is math, below is GGD ###########################

        self.define_materials(geom)
        r90aboutX = geom.structure.Rotation('r90aboutX', '90deg', '0deg', '0deg')

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
        na = g.matter.Element("sodium",     "Na", 11, "22.99*g/mole"  )
        mg = g.matter.Element("magnesium",  "Mg", 12, "24.305*g/mole" )
        al = g.matter.Element("aluminum",   "Al", 13, "26.9815*g/mole")
        si = g.matter.Element("silicon",    "Si", 14, "28.0855*g/mole")
        p  = g.matter.Element("phosphorus", "P",  15, "30.973*g/mole" )
        s  = g.matter.Element("sulfur",     "S",  16, "32.065*g/mole" )
        ar = g.matter.Element("argon",      "Ar", 18, "39.948*g/mole" )
        ca = g.matter.Element("calcium",    "Ca", 20, "40.078*g/mole" )
        ti = g.matter.Element("titanium",   "Ti", 22, "47.867*g/mole" )
        fe = g.matter.Element("iron",       "Fe", 26, "55.8450*g/mole")

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


        air   = g.matter.Mixture( "Air", density = "1.290*mg/cc", 
                                 components = (
                                     ("nitrogen", 0.781154), 
                                     ("oxygen",   0.209476),
                                     ("argon",    0.00934)
                                 ))


        fib_glass = g.matter.Mixture( "fibrous_glass", density = "0.1*g/cc", 
                                      components = (
                                          ("SiO2",   0.600),
                                          ("CaO",    0.224),
                                          ("Al2O3",  0.118),
                                          ("MgO",    0.034),
                                          ("TiO2",   0.013),
                                          ("Na2O",   0.010),
                                          ("Fe2O3",  0.001)
                                      ))

        # Materials for the radiators 
        # WARNING! densities not right!
        Fabric = g.matter.Molecule("Fabric", density="0.1*g/cc",   elements=(("carbon",3), ("hydrogen",6)))
        C3H6   = g.matter.Molecule("C3H6",   density="0.1*g/cc",   elements=(("carbon",16),("hydrogen",18),("oxygen",1)))

        # Materials for the targets
        H2O      = g.matter.Molecule("Water",       density="1.0*kg/l",   elements=(("oxygen",1),("hydrogen",2)))
        ArTarget = g.matter.Molecule("ArgonTarget", density="0.233*g/cc", elements=(("argon",1),))
        Aluminum = g.matter.Molecule("Aluminum",    density="2.70*g/cc",  elements=(("aluminum",1),))

    

