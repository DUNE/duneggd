#!/usr/bin/env python
'''
Top level builder of LAr FD modules at Homestake Mines
'''

import gegede.builder
import math
import pandas as pd
from gegede import Quantity as Q


class WorldBuilder(gegede.builder.Builder):
    '''
    Build a big box world volume.
    N.B. -- Global convention: index 0,1,2 = x,y,z
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self,
                  worldDim = [Q('100m'),Q('100m'),Q('100m')], 
                  worldMat = 'Rock',
                  **kwds):
        self.worldDim   = worldDim
        self.material   = worldMat
        self.detEncBldr = self.get_builder("DetEnclosure")
        self.cryoBldr   = self.detEncBldr.get_builder("Cryostat")


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Get relevant dimensions
        detEncDim      = list(self.detEncBldr.detEncDim)
        RadioRockThick = self.detEncBldr.RadioRockThickness
        encBoundToDet  = list(self.detEncBldr.ConcreteBeamGap)
        detDim         = list(self.detEncBldr.CryostatOuterDim)
        InsulationBeam = self.cryoBldr.TotalCryoLayer
        

        ########################### SET THE ORIGIN  #############################
        #                                                                       #
        # Position volDetEnclosure in the World Volume, displacing the world    #
        #  origin relative to the detector enclosure, thereby putting it        #
        #  anywhere in or around the detector we need.                          #
        #                                                                       #
        # Bring x=0 to -x of detEnc, then to det face, then to center of det    #
        setXCenter    =   0.5*detEncDim[0] - encBoundToDet[0] - 0.5*detDim[0]   #
        #                                                                       #
        # Bring y=0 to halfway between the top&bototm APAs                      #
        setYCenter    =   0.5*detEncDim[1] - encBoundToDet[1]                   #
        setYCenter    -=  InsulationBeam + self.cryoBldr.APAToFloor             #
        setYCenter    -=  self.cryoBldr.tpcDim[1]                               #
        setYCenter    -=  0.5*self.cryoBldr.APAGap_y                            #
        setYCenter    -=  0.5*RadioRockThick                                    #
        #                                                                       #        
        # Bring z=0 to back of detEnc, then to upstream face of detector.       #
        setZCenter    =   0.5*detEncDim[2] - encBoundToDet[2]                   #
        #  then through cryo steel and upstream dead LAr                        #
        setZCenter    -=  InsulationBeam                                        #
        setZCenter    -=  self.cryoBldr.APAToUpstreamWall                       #



        
        detEncPos     = [ setXCenter, setYCenter, setZCenter ]                  #
        #########################################################################


        ########################### Above is math, below is GGD ###########################
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


        worldBox = geom.shapes.Box( self.name,
                                    dx=0.5*self.worldDim[0], 
                                    dy=0.5*self.worldDim[1],
                                    dz=0.5*self.worldDim[2])
        
        world_lv = geom.structure.Volume('vol'+self.name, material=self.material, shape=worldBox)
        self.add_volume(world_lv)

        # Get volDetEnclosure and place it
        detEnc_lv       = self.detEncBldr.get_volume("volDetEnclosure")
        detEnc_in_world = geom.structure.Position('DetEnc_in_World', detEncPos[0], detEncPos[1], detEncPos[2])
        pD_in_W         = geom.structure.Placement('placeDetEnc_in_World',
                                                   volume = detEnc_lv,
                                                   pos    = detEnc_in_world)
        world_lv.placements.append(pD_in_W.name)
        return


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def define_materials(self, g):

        Elements  = pd.read_csv("MaterialDefinitions/Elements-Table 1.csv" )
        Molecules = pd.read_csv("MaterialDefinitions/Molecules-Table 1.csv")
        Mixtures  = pd.read_csv("MaterialDefinitions/Mixtures-Table 1.csv" )

        # Define all of the elements 
        for i in range(len(Elements)):
            density = str(Elements["AtomicDensity"][i]) + "*" + str(Elements["Units"][i])
            g.matter.Element(Elements["Name"      ][i],
                             Elements["Symbol"    ][i],
                             Elements["AtomicMass"][i],
                             density)
        
        # Define all of the molecules
        MoleculesNull = Molecules.isnull()
        columns       = list(Molecules.columns.values)        
        for i in range(len(Molecules)):
            density  = str(Molecules["Density"][i]) + "*" + str(Molecules["Unit"][i])
            elements = []
            counter  = 4
            while (counter < len(columns)):
                if (MoleculesNull[columns[counter]][i] == False):
                    elements.append((Molecules[columns[counter  ]][i],
                                     Molecules[columns[counter+1]][i]))
                counter += 2
            g.matter.Molecule(Molecules["Name"][i],
                              density  = density,
                              elements = tuple(elements))

        # Define all of the mixtures
        MixturesNull = Mixtures.isnull()
        columns      = list(Mixtures.columns.values)
        for i in range(len(Mixtures)):
            density    = str(Mixtures["Density"][i]) + "*" + str(Mixtures["Unit"][i])
            components = []
            counter    = 4

            while (counter < len(columns)):
                if (MixturesNull[columns[counter]][i] == False):
                    components.append((Mixtures[columns[counter]  ][i],
                                       Mixtures[columns[counter+1]][i]))
                counter += 2
            g.matter.Mixture(Mixtures["Name"][i],
                             density  = density,
                             components = tuple(components))
