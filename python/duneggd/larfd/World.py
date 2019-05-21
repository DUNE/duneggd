#!/usr/bin/env python
'''
Top level builder of LAr FD modules at Homestake Mines
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
                  
                  worldMat='Rock', **kwds):
        self.worldDim = worldDim
        self.material   = worldMat
        self.detEncBldr = self.get_builder("DetEnclosure")
        self.cryoBldr   = self.detEncBldr.get_builder("Cryostat")


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Get relevant dimensions
        detEncDim     = list(self.detEncBldr.detEncDim)

        encBoundToDet = list(self.detEncBldr.encBoundToDet)
        detDim        = list(self.detEncBldr.detDim)
        steelShell    = self.cryoBldr.membraneThickness
        

        ########################### SET THE ORIGIN  #############################
        #                                                                       #
        # Position volDetEnclosure in the World Volume, displacing the world    #
        #  origin relative to the detector enclosure, thereby putting it        #
        #  anywhere in or around the detector we need.                          #
        #                                                                       #
        # Bring x=0 to -x of detEnc, then to det face, then to center of det    #
        setXCenter    =   0.5*detEncDim[0] - encBoundToDet[0] - 0.5*detDim[0]   #
                                                                                #
        # Bring y=0 to halfway between the top&bototm APAs                      #
        setYCenter    =   0.5*detEncDim[1] - encBoundToDet[1]                   #
        setYCenter    -=  steelShell + self.cryoBldr.APAToFloor                 #
        setYCenter    -=  self.cryoBldr.apaPhysicalDim[1]                       #
        setYCenter    -=  0.5*self.cryoBldr.APAGap_y                            #
                                                                                #
        # Bring z=0 to back of detEnc, then to upstream face of detector.       #
        setZCenter    =   0.5*detEncDim[2] - encBoundToDet[2]                   #
        #  then through cryo steel and upstream dead LAr                        #
        setZCenter    -=  self.cryoBldr.membraneThickness                       #
        setZCenter    -=  self.cryoBldr.APAToUpstreamWall                       #
                                                                                #
        detEncPos     = [ setXCenter, setYCenter, setZCenter ]                  #
        #########################################################################


        ########################### Above is math, below is GGD ###########################
        self.define_materials(geom)
        r90aboutX      = geom.structure.Rotation( 'r90aboutX',      '90deg',  '0deg',  '0deg'  )
        r180aboutY     = geom.structure.Rotation( 'r180aboutY',     '0deg',   '180deg','0deg'  )
        # rminus90aboutX = geom.structure.Rotation( 'rminus90aboutX', '-90deg', '0deg',  '0deg'  )
        # r90aboutY      = geom.structure.Rotation( 'r90aboutY',      '0deg',   '90deg', '0deg'  )
        # rminus90aboutY = geom.structure.Rotation( 'rminus90aboutY', '0deg', '-90deg',  '0deg'  )
        # r90aboutZ      = geom.structure.Rotation( 'r90aboutZ',      '0deg',   '0deg',  '90deg' )
        # r90aboutXZ     = geom.structure.Rotation( 'r90aboutXZ', '90deg',  '0deg', '90deg'  )


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



        LArTarget = g.matter.Molecule("LAr", density="1.4*g/cc", elements=(("argon",1),))
