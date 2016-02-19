#!/usr/bin/env python
'''
Subbuilder of DetEncBuilder
'''

import gegede.builder
from gegede import Quantity as Q


class CryostatBuilder(gegede.builder.Builder):
    '''
    Build the Cryostat.
    '''


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, 
                  membraneThickness   = Q('0.5in'),  # <-- just default values,
                  readPlaneToModWall  = Q('10cm'),   #     they really come from 
                  G10Thickness        = Q('2mm'),    #     the cfg file 
                  cathodeThickness    = Q('0.016cm'),
                  nModules            = [2,1,3],
                  **kwds):

        self.membraneThickness    = membraneThickness
        self.cathodeThickness     = cathodeThickness
        self.G10Thickness         = G10Thickness
        self.readPlaneToModWall   = readPlaneToModWall
        self.nModules             = nModules

        self.tpcBldr = self.get_builder('TPC')


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):


        # Using volTPC dimensions, calculate module dimensions
        tpcDim = list(self.tpcBldr.tpcDim)
        modDim = [ 2*tpcDim[0] + 2*self.readPlaneToModWall 
                               + self.cathodeThickness
                               + 2*self.G10Thickness, 
                   tpcDim[1] + 2*self.G10Thickness,
                   tpcDim[2] + 2*self.G10Thickness  ]
        g10CageOutDim = list(modDim)
        g10CageInDim  = [ g10CageOutDim[0] - 2*self.G10Thickness, 
                          g10CageOutDim[1] - 2*self.G10Thickness,
                          g10CageOutDim[2] - 2*self.G10Thickness]

        # Using module dimensions, calculate cryostat dimensions
        allModsDim      = [ self.nModules[0]*modDim[0], 
                            self.nModules[1]*modDim[1],
                            self.nModules[2]*modDim[2]  ]
        membraneInDim   = list(allModsDim)
        membraneOutDim  = [ membraneInDim[0] + 2*self.membraneThickness, 
                            membraneInDim[1] + 2*self.membraneThickness,
                            membraneInDim[2] + 2*self.membraneThickness]
        self.cryoDim    = list(membraneOutDim) 


        # define cryostat shape and volume, will be placed by a builder owning this builder
        cryoBox = geom.shapes.Box( 'Cryostat',              dx=0.5*self.cryoDim[0], 
                                   dy=0.5*self.cryoDim[1],  dz=0.5*self.cryoDim[2]  )
        cryo_lv = geom.structure.Volume('volCryostat', material='LAr', shape=cryoBox)
        self.add_volume(cryo_lv)


        # define the g10 module cage volume
        g10CageOut = geom.shapes.Box( 'G10CageOut',                 dx=0.5*g10CageOutDim[0], 
                                  dy=0.5*g10CageOutDim[1], dz=0.5*g10CageOutDim[2]) 
        g10CageIn = geom.shapes.Box(  'G10CageIn',                  dx=0.5*g10CageInDim[0], 
                                  dy=0.5*g10CageInDim[1],  dz=0.5*g10CageInDim[2]) 
        g10CageBox = geom.shapes.Boolean( 'G10Cage', type='subtraction', first=g10CageOut, second=g10CageIn ) 
        g10Cage_lv = geom.structure.Volume('volG10Cage', material='Steel', shape=g10CageBox)


        # define the cathode volume 
        # TODO -- material?
        cathodeBox = geom.shapes.Box( 'Cathode',               dx=0.5*self.cathodeThickness, 
                                      dy=0.5*g10CageInDim[1],  dz=0.5*g10CageInDim[2]  )
        cathode_lv = geom.structure.Volume('volCathode', material='Steel', shape=cathodeBox)
        self.add_volume(cathode_lv)


        # Get the TPC volume from its builder so we can position and place it
        tpc_lv = self.tpcBldr.get_volume('volTPC')


        # Position both TPCs, G10 cage, and cathode for each module
        moduleNum = 0
        for x_i in range(self.nModules[0]):
            for y_i in range(self.nModules[1]):
                for z_i in range(self.nModules[2]):

                    # Calculate module positions
                    xpos = - 0.5*allModsDim[0] + (x_i+0.5)*modDim[0]
                    ypos = - 0.5*allModsDim[1] + (y_i+0.5)*modDim[1]
                    zpos = - 0.5*allModsDim[2] + (z_i+0.5)*modDim[2]


                    modCenter = geom.structure.Position('Module-'+str(moduleNum)+'_in_Cryo', 
                                                        xpos,ypos,zpos )
                    
                    
                    # Calculate volTPC positions around module center
                    tpc0Pos = [ xpos - 0.5*self.cathodeThickness - 0.5*tpcDim[0], ypos, zpos ]
                    tpc1Pos = [ xpos + 0.5*self.cathodeThickness + 0.5*tpcDim[0], ypos, zpos ]
                    pos0Name = 'Mod-'+str(moduleNum)+'_TPC-0_in_Cryo'
                    pos1Name = 'Mod-'+str(moduleNum)+'_TPC-1_in_Cryo'
                    tpc0_in_cryo = geom.structure.Position(pos0Name, tpc0Pos[0], tpc0Pos[1], tpc0Pos[2])
                    tpc1_in_cryo = geom.structure.Position(pos1Name, tpc1Pos[0], tpc1Pos[1], tpc1Pos[2])

                    # Place the TPCs, making sure to rotate the right one
                    pTPC0_in_C = geom.structure.Placement('place'+pos0Name,
                                                          volume = tpc_lv,
                                                          pos = tpc0_in_cryo)
                    pTPC1_in_C = geom.structure.Placement('place'+pos1Name,
                                                          volume = tpc_lv,
                                                          pos = tpc1_in_cryo,
                                                          rot = 'r180aboutY')
                    cryo_lv.placements.append(pTPC0_in_C.name)
                    cryo_lv.placements.append(pTPC1_in_C.name)


                    # place the G10 cage and cathode, both centered at module center
                    pG10Cage_in_C  = geom.structure.Placement('placeG10Cage-'+str(moduleNum)+'_in_Cryo',
                                                              volume = g10Cage_lv,
                                                              pos = modCenter)
                    pCathode_in_C  = geom.structure.Placement('placeCathode-'+str(moduleNum)+'_in_Cryo',
                                                              volume = cathode_lv,
                                                              pos = modCenter)
                    cryo_lv.placements.append(pG10Cage_in_C.name)
                    cryo_lv.placements.append(pCathode_in_C.name)


                    moduleNum += 1
        

        print "Cryostat: Built "+str(self.nModules[0])+" wide by "+str(self.nModules[1])+" high by "+str(self.nModules[2])+" long modules."



        # make and place the steel membrane
        membraneOut = geom.shapes.Box( 'MembraneOut',                 dx=0.5*membraneOutDim[0], 
                                  dy=0.5*membraneOutDim[1], dz=0.5*membraneOutDim[2]) 
        membraneIn = geom.shapes.Box(  'MembraneIn',                  dx=0.5*membraneInDim[0], 
                                  dy=0.5*membraneInDim[1],  dz=0.5*membraneInDim[2]) 
        membraneBox = geom.shapes.Boolean( 'Membrane', type='subtraction', first=membraneOut, second=membraneIn ) 
        membrane_lv = geom.structure.Volume('volMembrane', material='Steel', shape=membraneBox)
        membrane_in_cryo = geom.structure.Position('Membrane_in_Cryo', 
                                                  '0cm','0cm','0cm')
        pMembrane_in_C  = geom.structure.Placement('placeMembrane_in_Cryo',
                                                   volume = membrane_lv,
                                                   pos = membrane_in_cryo)
        cryo_lv.placements.append(pMembrane_in_C.name)
