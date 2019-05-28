#!/usr/bin/env python
'''
Subbuilder of WorldBuilder
'''

import gegede.builder
from gegede import Quantity as Q


class DetEncLArBuilder(gegede.builder.Builder):
    '''
    Build the Detector Enclosure.
    '''


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, 
                  detEncDim            = None, 
                  magBarsDim           = None,
                  supportTubeThickness = None,
                  encBoundToDet_z      = None,
                  makeWaterShield      = False,
                  thickness            = Q('10cm'),
                  **kwds):
        if detEncDim is None:
            raise ValueError("No value given for detEncDim")
        if encBoundToDet_z is None:
            raise ValueError("No value given for encBoundToDet_z")

        self.detEncMat        = 'Air'
        self.detEncDim        = detEncDim
        self.makeWaterShield  = makeWaterShield
        self.thickness        = thickness   
        
        # Space from negative face of volDetEnc to closest face of detector
        #  This positions the detector in the enclosure
        self.encBoundToDet_z = encBoundToDet_z

        self.cryoBldr  = self.get_builder('Cryostat')
        

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):
        encBox = geom.shapes.Box( 'DetEnclosure',            dx=0.5*self.detEncDim[0], 
                                  dy=0.5*self.detEncDim[1],  dz=0.5*self.detEncDim[2])
        detEnc_lv = geom.structure.Volume('volDetEnclosure', material=self.detEncMat, shape=encBox)
        self.add_volume(detEnc_lv)

        cryoDim = list(self.cryoBldr.cryoDim)
        cryo_lv = self.cryoBldr.get_volume('volCryostat')
        self.detDim    = list(cryoDim) # this might be used by WorldBuilder for positioning


        # Calculate position of detector in the enclosure
        self.encBoundToDet = [ 0.5*self.detEncDim[0] - 0.5*self.detDim[0], # x: center it for now
                               Q('0cm'),                                   # y: det on floor
                               self.encBoundToDet_z ]                      # z: configure
        
        self.detCenter = [ -0.5*self.detEncDim[0] + self.encBoundToDet[0] + 0.5*self.detDim[0], 
                           -0.5*self.detEncDim[1] + self.encBoundToDet[1] + 0.5*self.detDim[1], 
                           -0.5*self.detEncDim[2] + self.encBoundToDet[2] + 0.5*self.detDim[2]  ]

        # Place Cryostat
        posName = 'Cryo_in_Enc'
        cryo_in_enc = geom.structure.Position(posName, self.detCenter[0], self.detCenter[1], self.detCenter[2])
        pC_in_E = geom.structure.Placement('place'+posName,
                                           volume = cryo_lv,
                                           pos = cryo_in_enc)
        detEnc_lv.placements.append(pC_in_E.name)

        if (self.makeWaterShield):
            
            # Build the water boxes
            waterBoxTop    = geom.shapes.Box('WaterBoxTop'   ,
                                             dx=0.5*self.detDim[0], dy=0.5*self.thickness, dz=0.5*self.detDim[2])
            waterBoxBottom = geom.shapes.Box('WaterBoxBottom',
                                             dx=0.5*self.detDim[0], dy=0.5*self.thickness, dz=0.5*self.detDim[2])
            waterBoxLeft   = geom.shapes.Box('WaterBoxLeft'  ,
                                             dx=0.5*self.thickness, dy=0.5*self.detDim[1], dz=0.5*self.detDim[2])
            waterBoxRight  = geom.shapes.Box('WaterBoxRight' ,
                                             dx=0.5*self.thickness, dy=0.5*self.detDim[1], dz=0.5*self.detDim[2]) 
            waterBoxFront  = geom.shapes.Box('WaterBoxFront' ,
                                             dx=0.5*self.detDim[0], dy=0.5*self.detDim[1], dz=0.5*self.thickness)
            waterBoxBack   = geom.shapes.Box('WaterBoxBack'  ,
                                             dx=0.5*self.detDim[0], dy=0.5*self.detDim[1], dz=0.5*self.thickness)
        
            # Define the logical volumes
            waterTop_lv    = geom.structure.Volume('volWaterBoxTop'   , material='Air', shape=waterBoxTop   )
            waterBottom_lv = geom.structure.Volume('volWaterBoxBottom', material='Air', shape=waterBoxBottom)
            waterLeft_lv   = geom.structure.Volume('volWaterBoxLeft'  , material='Air', shape=waterBoxLeft  )
            waterRight_lv  = geom.structure.Volume('volWaterBoxRight' , material='Air', shape=waterBoxRight )
            waterFront_lv  = geom.structure.Volume('volWaterBoxFront' , material='Air', shape=waterBoxFront )
            waterBack_lv   = geom.structure.Volume('volWaterBoxBack'  , material='Air', shape=waterBoxBack  ) 
            
            # Add all of the volumes to the detector
            self.add_volume(waterTop_lv   )
            self.add_volume(waterBottom_lv)
            self.add_volume(waterLeft_lv  )
            self.add_volume(waterRight_lv )
            self.add_volume(waterFront_lv )
            self.add_volume(waterBack_lv  )
            
            # Work out all of the positions of the water slabs
            posName_1 = 'Water_Top_around_Enc' 
            posName_2 = 'Water_Bot_around_Enc' 
            posName_3 = 'Water_Lef_around_Enc' 
            posName_4 = 'Water_Rig_around_Enc' 
            posName_5 = 'Water_Fro_around_Enc' 
            posName_6 = 'Water_Bac_around_Enc'
            
            # Define all of the centers to place the water slabs at
            posCenter_1 = geom.structure.Position(posName_1,
                                                  self.detCenter[0],
                                                  self.detCenter[1] + 0.5*(self.detDim[1]+self.thickness),
                                                  self.detCenter[2]) 
            posCenter_2 = geom.structure.Position(posName_2,
                                                  self.detCenter[0],
                                                  self.detCenter[1] - 0.5*(self.detDim[1]+self.thickness),
                                                  self.detCenter[2]) 
            posCenter_3 = geom.structure.Position(posName_3,
                                                  self.detCenter[0] + 0.5*(self.detDim[0]+self.thickness),
                                                  self.detCenter[1],
                                                  self.detCenter[2]) 
            posCenter_4 = geom.structure.Position(posName_4,
                                                  self.detCenter[0] - 0.5*(self.detDim[0]+self.thickness),
                                                  self.detCenter[1],
                                                  self.detCenter[2]) 
            posCenter_5 = geom.structure.Position(posName_5,
                                                  self.detCenter[0],
                                                  self.detCenter[1],
                                                  self.detCenter[2] + 0.5*(self.detDim[2]+self.thickness)) 
            posCenter_6 = geom.structure.Position(posName_6,
                                                  self.detCenter[0],
                                                  self.detCenter[1],
                                                  self.detCenter[2] - 0.5*(self.detDim[2]+self.thickness)) 
            
            pc_1 = geom.structure.Placement('place'+posName_1, volume=waterTop_lv   , pos=posCenter_1)
            pc_2 = geom.structure.Placement('place'+posName_2, volume=waterBottom_lv, pos=posCenter_2)
            pc_3 = geom.structure.Placement('place'+posName_3, volume=waterLeft_lv  , pos=posCenter_3)
            pc_4 = geom.structure.Placement('place'+posName_4, volume=waterRight_lv , pos=posCenter_4)
            pc_5 = geom.structure.Placement('place'+posName_5, volume=waterFront_lv , pos=posCenter_5)        
            pc_6 = geom.structure.Placement('place'+posName_6, volume=waterBack_lv  , pos=posCenter_6)
            
            detEnc_lv.placements.append(pc_1.name)
            detEnc_lv.placements.append(pc_2.name)
            detEnc_lv.placements.append(pc_3.name)
            detEnc_lv.placements.append(pc_4.name)
            detEnc_lv.placements.append(pc_5.name)
            detEnc_lv.placements.append(pc_6.name)
            
