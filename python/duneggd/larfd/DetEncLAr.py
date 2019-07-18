#!/usr/bin/env python
'''
Subbuilder of WorldBuilder
'''

# Water Brick website https://practicalpreppers.com/product/10-pack-of-waterbrick-standard-3-5-gallon-tan/
# Water Brich dimensions 9" W x 18" L x 6" H
# Recomended stacking height is 4' so that is 8 height
# Assing the Super structure of these blocks will be 18" by 36" by 48"

import gegede.builder
from gegede import Quantity as Q
import math as m

# for the cavern dimensions, I used the 60% CF for the FD Submission drawings
#http://docs.dunescience.org/cgi-bin/RetrieveFile?docid=11239&filename=EXC%2060PCT%20FD%20Page%20Turn%20Presentation.pdf&version=2

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
                  waterBlocks          = False,
                  waterBoxDim          = None,
                  archRadius           = None,
                  archHalfAngle        = None,
                  blockSpacing         = Q('30cm'),
                  thickness            = Q('10cm'),
                  **kwds):
        
        if detEncDim is None:
            raise ValueError("No value given for detEncDim")
        if encBoundToDet_z is None:
            raise ValueError("No value given for encBoundToDet_z")
        if makeWaterShield and waterBoxDim is None:
            raise ValueError("No value given for waterBoxDim")

        self.detEncMat        = 'Air'
        self.detEncDim        = detEncDim
        self.archRadius       = archRadius    
        self.archHalfAngle    = archHalfAngle
        
        self.makeWaterShield  = makeWaterShield
        self.waterBlocks      = waterBlocks
        self.waterBoxDim      = waterBoxDim
        self.blockSpacing     = blockSpacing
        self.thickness        = thickness   
        
        # Space from negative face of volDetEnc to closest face of detector
        #  This positions the detector in the enclosure
        self.encBoundToDet_z = encBoundToDet_z

        self.cryoBldr  = self.get_builder('Cryostat')



    

    def MakeWaterShield(self, geom, detEnc_lv):
        # Build the water boxes
        waterBoxTop    = geom.shapes.Box('WaterBoxTop'   ,
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
        waterTop_lv    = geom.structure.Volume('volWaterBoxTop'   , material='Water', shape=waterBoxTop   )
        waterLeft_lv   = geom.structure.Volume('volWaterBoxLeft'  , material='Water', shape=waterBoxLeft  )
        waterRight_lv  = geom.structure.Volume('volWaterBoxRight' , material='Water', shape=waterBoxRight )
        waterFront_lv  = geom.structure.Volume('volWaterBoxFront' , material='Water', shape=waterBoxFront )
        waterBack_lv   = geom.structure.Volume('volWaterBoxBack'  , material='Water', shape=waterBoxBack  ) 
        
            # Add all of the volumes to the detector
        self.add_volume(waterTop_lv   )
        self.add_volume(waterLeft_lv  )
        self.add_volume(waterRight_lv )
        self.add_volume(waterFront_lv )
        self.add_volume(waterBack_lv  )
        
            # Work out all of the positions of the water slabs
        posName_1 = 'Water_Top_around_Enc' 
        posName_3 = 'Water_Lef_around_Enc' 
        posName_4 = 'Water_Rig_around_Enc' 
        posName_5 = 'Water_Fro_around_Enc' 
        posName_6 = 'Water_Bac_around_Enc'
            
            # Define all of the centers to place the water slabs at
        posCenter_1 = geom.structure.Position(posName_1,
                                              self.detCenter[0],
                                              self.detCenter[1] + 0.5*(self.detDim[1]+self.thickness),
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
        pc_3 = geom.structure.Placement('place'+posName_3, volume=waterLeft_lv  , pos=posCenter_3)
        pc_4 = geom.structure.Placement('place'+posName_4, volume=waterRight_lv , pos=posCenter_4)
        pc_5 = geom.structure.Placement('place'+posName_5, volume=waterFront_lv , pos=posCenter_5)        
        pc_6 = geom.structure.Placement('place'+posName_6, volume=waterBack_lv  , pos=posCenter_6)
        
        detEnc_lv.placements.append(pc_1.name)
        detEnc_lv.placements.append(pc_3.name)
        detEnc_lv.placements.append(pc_4.name)
        detEnc_lv.placements.append(pc_5.name)
        detEnc_lv.placements.append(pc_6.name)

        if (self.waterBlocks):

            container_cost   = 178.00
            num_boxes_placed = 0
            LRBoxIndex       = [0, 0]
            TBBoxIndex       = [0, 0]
            FBBoxIndex       = [0, 0]

            # ^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
            # Front and back planes

            # Define the initial position, bottom middle of the front/back planes
            posX   = self.detCenter[0]
            posY   = self.detCenter[1] - (0.5 * self.detDim[1]) + self.waterBoxDim[1]
            posZ_f = self.detCenter[2] + (0.5 * self.detDim[2]) + self.waterBoxDim[0]
            posZ_b = self.detCenter[2] - (0.5 * self.detDim[2]) - self.waterBoxDim[0]

            init_posX   = self.detCenter[0]
            init_posY   = self.detCenter[1] - (0.5 * self.detDim[1]) + (self.waterBoxDim[1])
            init_posZ_f = self.detCenter[2] + (0.5 * self.detDim[2]) + (0.5 * self.waterBoxDim[0])
            init_posZ_b = self.detCenter[2] - (0.5 * self.detDim[2]) - (0.5 * self.waterBoxDim[0])



            while (posY + (0.5 * self.waterBoxDim[1]) + self.blockSpacing - init_posY < (self.detDim[1])):
                num_boxes_placed += 2
                # Place the initial boxes
                waterBoxFB_f = geom.shapes.Box(('WaterBoxFB_f_') + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                               dx = self.waterBoxDim[2],
                                               dy = self.waterBoxDim[1],
                                               dz = self.waterBoxDim[0])
                waterBoxFB_b = geom.shapes.Box(('WaterBoxFB_b_') + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                               dx = self.waterBoxDim[2],
                                               dy = self.waterBoxDim[1],
                                               dz = self.waterBoxDim[0])
                # Define the logical volumes
                waterBoxFB_lv_f = geom.structure.Volume('volWaterBoxFB_f_' + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                        material = 'Water',
                                                        shape    = waterBoxFB_f)
                waterBoxFB_lv_b = geom.structure.Volume('volWaterBoxFB_b_' + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                        material = 'Water',
                                                        shape    = waterBoxFB_b)
                # Name the positions
                posName_f   = 'Water_Box_FB_f_' + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1])
                posName_b   = 'Water_Box_FB_b_' + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1])
                # Define the positions
                posCenter_f = geom.structure.Position(posName_f, posX, posY, posZ_f)
                posCenter_b = geom.structure.Position(posName_b, posX, posY, posZ_b)
                # Define the placements
                pc_f        = geom.structure.Placement('place' + posName_f, volume=waterBoxFB_lv_f, pos=posCenter_f)
                pc_b        = geom.structure.Placement('place' + posName_b, volume=waterBoxFB_lv_b, pos=posCenter_b)
                # Add them to the placements in the detector enclosure
                detEnc_lv.placements.append(pc_f.name)
                detEnc_lv.placements.append(pc_b.name)
                # incriment the position of the box in the y-axis
                FBBoxIndex[0] += 1
                posX          += self.blockSpacing + self.waterBoxDim[2]
                
                
                while (posX - init_posX < (0.5 * self.detDim[0])):
                    num_boxes_placed += 4
                    waterBoxFB_fl = geom.shapes.Box(('WaterBoxFB_fl_') + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                    dx = self.waterBoxDim[2],
                                                    dy = self.waterBoxDim[1],
                                                    dz = self.waterBoxDim[0])
                    waterBoxFB_fr = geom.shapes.Box(('WaterBoxFB_fr_') + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                    dx = self.waterBoxDim[2],
                                                    dy = self.waterBoxDim[1],
                    dz = self.waterBoxDim[0])
                    waterBoxFB_bl = geom.shapes.Box(('WaterBoxFB_bl_') + str(-FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                    dx = self.waterBoxDim[2],
                                                    dy = self.waterBoxDim[1],
                                                    dz = self.waterBoxDim[0])                
                    waterBoxFB_br = geom.shapes.Box(('WaterBoxFB_br_') + str(-FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                    dx = self.waterBoxDim[2],
                                                    dy = self.waterBoxDim[1],
                                                    dz = self.waterBoxDim[0])
                    
                    waterBoxFB_lv_fl = geom.structure.Volume('volWaterBoxFB_fl_' + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxFB_fl)
                    waterBoxFB_lv_fr = geom.structure.Volume('volWaterBoxFB_fr_' + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxFB_fr)
                    waterBoxFB_lv_bl = geom.structure.Volume('volWaterBoxFB_bl_' + str(-FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxFB_bl)
                    waterBoxFB_lv_br = geom.structure.Volume('volWaterBoxFB_br_' + str(-FBBoxIndex[0]) + "_" + str(FBBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxFB_br)
                    
                    posName_fl   = 'Water_Box_FB_fl_' + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1])
                    posName_fr   = 'Water_Box_FB_fr_' + str(FBBoxIndex[0]) + "_" + str(FBBoxIndex[1])
                    posName_bl   = 'Water_Box_FB_bl_' + str(FBBoxIndex[0]) + "_" + str(-FBBoxIndex[1])
                    posName_br   = 'Water_Box_FB_br_' + str(FBBoxIndex[0]) + "_" + str(-FBBoxIndex[1])
                    
                    posCenter_fl = geom.structure.Position(posName_fl,  posX, posY, posZ_f)
                    posCenter_fr = geom.structure.Position(posName_fr, -posX, posY, posZ_f)
                    posCenter_bl = geom.structure.Position(posName_bl,  posX, posY, posZ_b)
                    posCenter_br = geom.structure.Position(posName_br, -posX, posY, posZ_b)
                    
                    pc_fl        = geom.structure.Placement('place' + posName_fl, volume=waterBoxFB_lv_fl, pos=posCenter_fl)
                    pc_fr        = geom.structure.Placement('place' + posName_fr, volume=waterBoxFB_lv_fr, pos=posCenter_fr)
                    pc_bl        = geom.structure.Placement('place' + posName_bl, volume=waterBoxFB_lv_bl, pos=posCenter_bl)
                    pc_br        = geom.structure.Placement('place' + posName_br, volume=waterBoxFB_lv_br, pos=posCenter_br)
                    
                    detEnc_lv.placements.append(pc_fl.name)
                    detEnc_lv.placements.append(pc_fr.name)
                    detEnc_lv.placements.append(pc_bl.name)
                    detEnc_lv.placements.append(pc_br.name)
                    
                    posX          += self.blockSpacing + self.waterBoxDim[2]
                    FBBoxIndex[0] += 1

                FBBoxIndex[1] += 1
                posY          += self.blockSpacing + self.waterBoxDim[1]
                posX           = init_posX


            # ^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
            # Left and right planes

            # Define the initial position, bottom middle of the left/right planes
            posX_l = self.detCenter[0] - (0.5 * self.detDim[0]) - self.waterBoxDim[0]
            posX_r = self.detCenter[0] + (0.5 * self.detDim[0]) + self.waterBoxDim[0]
            posY   = self.detCenter[1] - (0.5 * self.detDim[1]) + self.waterBoxDim[1]
            posZ   = self.detCenter[2]
            posZ_f = self.detCenter[2]
            posZ_b = self.detCenter[2]
            
            init_posX_l = self.detCenter[0] - (0.5 * self.detDim[0]) + (0.5 * self.waterBoxDim[0])
            init_posX_r = self.detCenter[0] + (0.5 * self.detDim[0]) + (0.5 * self.waterBoxDim[0])
            init_posY   = self.detCenter[1] - (0.5 * self.detDim[1]) + (self.waterBoxDim[1])
            init_posZ   = self.detCenter[2]


            while (posY + (0.5 * self.waterBoxDim[1]) + self.blockSpacing - init_posY < (self.detDim[1])):
                num_boxes_placed += 2
                # Place the initial boxes
                waterBoxLR_l = geom.shapes.Box(('WaterBoxLR_l_') + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                               dx = self.waterBoxDim[0],
                                               dy = self.waterBoxDim[1],
                                               dz = self.waterBoxDim[2])
                waterBoxLR_r = geom.shapes.Box(('WaterBoxLR_r_') + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                               dx = self.waterBoxDim[0],
                                               dy = self.waterBoxDim[1],
                                               dz = self.waterBoxDim[2])
                # Define the logical volumes
                waterBoxLR_lv_l = geom.structure.Volume('volWaterBoxLR_l_' + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                        material = 'Water',
                                                        shape    = waterBoxLR_l)
                waterBoxLR_lv_r = geom.structure.Volume('volWaterBoxLR_r_' + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                        material = 'Water',
                                                        shape    = waterBoxLR_r)
                # Name the positions
                posName_l   = 'Water_Box_LR_l_' + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1])
                posName_r   = 'Water_Box_LR_r_' + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1])
                # Define the positions
                posCenter_l = geom.structure.Position(posName_l, posX_l, posY, posZ)
                posCenter_r = geom.structure.Position(posName_r, posX_r, posY, posZ)
                # Define the placements
                pc_l        = geom.structure.Placement('place' + posName_l, volume=waterBoxLR_lv_l, pos=posCenter_l)
                pc_r        = geom.structure.Placement('place' + posName_r, volume=waterBoxLR_lv_r, pos=posCenter_r)
                # Add them to the placements in the detector enclosure
                detEnc_lv.placements.append(pc_l.name)
                detEnc_lv.placements.append(pc_r.name)
                # incriment the position of the box in the y-axis
                LRBoxIndex[0] += 1
                posZ_f        += (self.blockSpacing + self.waterBoxDim[2])
                posZ_b        -= (self.blockSpacing + self.waterBoxDim[2])
                
                while (posZ_f - init_posZ < (0.5 * self.detDim[2])):
                    num_boxes_placed += 4
                    waterBoxLR_lb = geom.shapes.Box(('WaterBoxLR_lb_') + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                    dx = self.waterBoxDim[0],
                                                    dy = self.waterBoxDim[1],
                                                    dz = self.waterBoxDim[2])
                    waterBoxLR_lf = geom.shapes.Box(('WaterBoxLR_lf_') + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                    dx = self.waterBoxDim[0],
                                                    dy = self.waterBoxDim[1],
                                                    dz = self.waterBoxDim[2])
                    waterBoxLR_rb = geom.shapes.Box(('WaterBoxLR_rb_') + str(-LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                    dx = self.waterBoxDim[0],
                                                    dy = self.waterBoxDim[1],
                                                    dz = self.waterBoxDim[2])                
                    waterBoxLR_rf = geom.shapes.Box(('WaterBoxLR_rf_') + str(-LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                    dx = self.waterBoxDim[0],
                                                    dy = self.waterBoxDim[1],
                                                    dz = self.waterBoxDim[2])
                                    
                    waterBoxLR_lv_lb = geom.structure.Volume('volWaterBoxLR_lb_' + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxLR_lb)
                    waterBoxLR_lv_lf = geom.structure.Volume('volWaterBoxLR_lf_' + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxLR_lf)
                    waterBoxLR_lv_rb = geom.structure.Volume('volWaterBoxLR_rb_' + str(-LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxLR_rb)
                    waterBoxLR_lv_rf = geom.structure.Volume('volWaterBoxLR_fr_' + str(-LRBoxIndex[0]) + "_" + str(LRBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxLR_rf)
                    
                    posName_lb   = 'Water_Box_LR_lb_' + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1])
                    posName_lf   = 'Water_Box_LR_lf_' + str(LRBoxIndex[0]) + "_" + str(LRBoxIndex[1])
                    posName_rb   = 'Water_Box_LR_rb_' + str(LRBoxIndex[0]) + "_" + str(-LRBoxIndex[1])
                    posName_rf   = 'Water_Box_LR_rf_' + str(LRBoxIndex[0]) + "_" + str(-LRBoxIndex[1])
                    
                    posCenter_lb = geom.structure.Position(posName_lb, posX_l, posY,  posZ_f)
                    posCenter_lf = geom.structure.Position(posName_lf, posX_l, posY,  posZ_b)
                    posCenter_rb = geom.structure.Position(posName_rb, posX_r, posY,  posZ_f)
                    posCenter_rf = geom.structure.Position(posName_rf, posX_r, posY,  posZ_b)
                    
                    pc_lb        = geom.structure.Placement('place' + posName_lb, volume=waterBoxLR_lv_lb, pos=posCenter_lb)
                    pc_lf        = geom.structure.Placement('place' + posName_lf, volume=waterBoxLR_lv_lf, pos=posCenter_lf)
                    pc_rb        = geom.structure.Placement('place' + posName_rb, volume=waterBoxLR_lv_rb, pos=posCenter_rb)
                    pc_rf        = geom.structure.Placement('place' + posName_rf, volume=waterBoxLR_lv_rf, pos=posCenter_rf)
                    
                    detEnc_lv.placements.append(pc_lb.name)
                    detEnc_lv.placements.append(pc_lf.name)
                    detEnc_lv.placements.append(pc_rb.name)
                    detEnc_lv.placements.append(pc_rf.name)
                    
                    posZ_f        += (self.blockSpacing + self.waterBoxDim[2])
                    posZ_b        -= (self.blockSpacing + self.waterBoxDim[2]) 
                    LRBoxIndex[0] += 1

                LRBoxIndex[1] += 1
                posY          += self.blockSpacing + self.waterBoxDim[1]
                posZ_f        = init_posZ 
                posZ_b        = init_posZ                  
                
            # ^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
            # Top plane
            
            # Define the initial position, bottom middle of the front/back planes
            posX   = self.detCenter[0]
            posY   = self.detCenter[1] + (0.5 * self.detDim[1]) + self.waterBoxDim[0]
            posZ_b = self.detCenter[2]
            posZ_f = self.detCenter[2]
            
            init_posX = self.detCenter[0]
            init_posY = self.detCenter[1] + (0.5 * self.detDim[1]) + (0.5 * self.waterBoxDim[0])
            init_posZ = self.detCenter[2]

            num_boxes_placed += 1
            # Place the initial box
            waterBoxTB = geom.shapes.Box(('WaterBoxTB_') + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                          dx = self.waterBoxDim[2],
                                          dy = self.waterBoxDim[0],
                                          dz = self.waterBoxDim[1])
            # Define the logical volumes
            waterBoxTB_lv = geom.structure.Volume('volWaterBoxTB_' + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                                   material = 'Water',
                                                   shape    = waterBoxTB)
            # Name the position
            posName   = 'Water_Box_TB_' + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1])
            # Define the position
            posCenter = geom.structure.Position(posName, posX, posY, posZ)
            # Define the placement
            pc        = geom.structure.Placement('place' + posName, volume=waterBoxTB_lv, pos=posCenter)
            # Add them to the placements in the detector enclosure
            detEnc_lv.placements.append(pc.name)

            # incriment the position of the box in the y-axis
            TBBoxIndex[0] += 1
            posX += self.waterBoxDim[2] + self.blockSpacing
            
            while (posX - init_posX < (0.5 * self.detDim[0])):
                num_boxes_placed += 2
                waterBoxTB_l = geom.shapes.Box(('WaterBoxTB_l_') + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                             dx = self.waterBoxDim[2],
                                             dy = self.waterBoxDim[0],
                                             dz = self.waterBoxDim[1])
                waterBoxTB_r = geom.shapes.Box(('WaterBoxTB_r') + str(-TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                             dx = self.waterBoxDim[2],
                                             dy = self.waterBoxDim[0],
                                             dz = self.waterBoxDim[1])
                waterBoxTB_lv_l = geom.structure.Volume('volWaterBoxTB_' + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                                        material = 'Water',
                                                        shape    = waterBoxTB_l)
                waterBoxTB_lv_r = geom.structure.Volume('volWaterBoxTB_' + str(-TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                                        material = 'Water',
                                                        shape    = waterBoxTB_r)
                posName_l   = 'Water_Box_TB_l_' + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1])
                posName_r   = 'Water_Box_TB_r_' + str(-TBBoxIndex[0]) + "_" + str(TBBoxIndex[1])
                posCenter_l = geom.structure.Position(posName_l,  posX, posY, posZ_f)
                posCenter_r = geom.structure.Position(posName_r, -posX, posY, posZ_f)
                pc_l        = geom.structure.Placement('place' + posName_l, volume=waterBoxTB_lv_l, pos=posCenter_l)
                pc_r        = geom.structure.Placement('place' + posName_r, volume=waterBoxTB_lv_r, pos=posCenter_r)
                detEnc_lv.placements.append(pc_l.name)
                detEnc_lv.placements.append(pc_r.name)

                posX += self.waterBoxDim[2] + self.blockSpacing
                TBBoxIndex[0] += 1

            posZ_b        += (self.waterBoxDim[1] + self.blockSpacing)
            posZ_f        -= (self.waterBoxDim[1] + self.blockSpacing)
            posX           = init_posX
            TBBoxIndex[1] += 1
            TBBoxIndex[0]  = 1            
            
            while (posZ_f - init_posZ < (0.5 * self.detDim[2])):
                num_boxes_placed += 2
                waterBoxTB_b = geom.shapes.Box(('WaterBoxTB_b_') + str(TBBoxIndex[0]) + "_" + str(-TBBoxIndex[1]),
                                             dx = self.waterBoxDim[2],
                                             dy = self.waterBoxDim[0],
                                             dz = self.waterBoxDim[1])
                waterBoxTB_f = geom.shapes.Box(('WaterBoxTB_f') + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                             dx = self.waterBoxDim[2],
                                             dy = self.waterBoxDim[0],
                                             dz = self.waterBoxDim[1])
                waterBoxTB_lv_b = geom.structure.Volume('volWaterBoxTB_b_' + str(TBBoxIndex[0]) + "_" + str(-TBBoxIndex[1]),
                                                        material = 'Water',
                                                        shape    = waterBoxTB_b)
                waterBoxTB_lv_f = geom.structure.Volume('volWaterBoxTB_f_' + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                                        material = 'Water',
                                                        shape    = waterBoxTB_f)
                posName_b   = 'Water_Box_TB_b_' + str(TBBoxIndex[0]) + "_" + str(-TBBoxIndex[1])
                posName_f   = 'Water_Box_TB_f_' + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1])
                posCenter_b = geom.structure.Position(posName_b, posX, posY, posZ_b)
                posCenter_f = geom.structure.Position(posName_f, posX, posY, posZ_f)
                pc_b        = geom.structure.Placement('place' + posName_b, volume=waterBoxTB_lv_b, pos=posCenter_b)
                pc_f        = geom.structure.Placement('place' + posName_f, volume=waterBoxTB_lv_f, pos=posCenter_f)
                detEnc_lv.placements.append(pc_b.name)
                detEnc_lv.placements.append(pc_f.name)


                # incriment the position of the box in the y-axis
                TBBoxIndex[0] = 1
                posX += self.waterBoxDim[2] + self.blockSpacing
                while (posX - init_posX < (0.5 * self.detDim[0])):
                    num_boxes_placed += 4
                    waterBoxTB_lb = geom.shapes.Box(('WaterBoxTB_lb_') + str(-TBBoxIndex[0]) + "_" + str(-TBBoxIndex[1]),
                                                   dx = self.waterBoxDim[2],
                                                   dy = self.waterBoxDim[0],
                                                   dz = self.waterBoxDim[1])
                    waterBoxTB_lf = geom.shapes.Box(('WaterBoxTB_lf_') + str(-TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                                   dx = self.waterBoxDim[2],
                                                   dy = self.waterBoxDim[0],
                                                   dz = self.waterBoxDim[1])
                    waterBoxTB_rb = geom.shapes.Box(('WaterBoxTB_rb') + str(TBBoxIndex[0]) + "_" + str(-TBBoxIndex[1]),
                                                   dx = self.waterBoxDim[2],
                                                   dy = self.waterBoxDim[0],
                                                   dz = self.waterBoxDim[1])
                    waterBoxTB_rf = geom.shapes.Box(('WaterBoxTB_rf') + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                                   dx = self.waterBoxDim[2],
                                                   dy = self.waterBoxDim[0],
                                                   dz = self.waterBoxDim[1])
                    waterBoxTB_lv_lb = geom.structure.Volume('volWaterBoxTB_lb_' + str(-TBBoxIndex[0]) + "_" + str(-TBBoxIndex[1]),
                                                            material = 'Water',
                                                            shape    = waterBoxTB_lb)
                    waterBoxTB_lv_lf = geom.structure.Volume('volWaterBoxTB_lf_' + str(-TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                                            material = 'Water',
                                                            shape    = waterBoxTB_lf)
                    waterBoxTB_lv_rb = geom.structure.Volume('volWaterBoxTB_rb_' + str(TBBoxIndex[0]) + "_" + str(-TBBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxTB_rb)
                    waterBoxTB_lv_rf = geom.structure.Volume('volWaterBoxTB_rf_' + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1]),
                                                             material = 'Water',
                                                             shape    = waterBoxTB_rf)
                    posName_lb   = 'Water_Box_TB_lb_' + str(-TBBoxIndex[0]) + "_" + str(-TBBoxIndex[1])
                    posName_lf   = 'Water_Box_TB_lf_' + str(-TBBoxIndex[0]) + "_" + str(TBBoxIndex[1])
                    posName_rb   = 'Water_Box_TB_rb_' + str(TBBoxIndex[0]) + "_" + str(-TBBoxIndex[1])
                    posName_rf   = 'Water_Box_TB_rf_' + str(TBBoxIndex[0]) + "_" + str(TBBoxIndex[1])
                    posCenter_lb = geom.structure.Position(posName_lb, -posX, posY, posZ_b)
                    posCenter_lf = geom.structure.Position(posName_lf, -posX, posY, posZ_f)
                    posCenter_rb = geom.structure.Position(posName_rb, posX, posY, posZ_b)
                    posCenter_rf = geom.structure.Position(posName_rf, posX, posY, posZ_f)
                    pc_lb        = geom.structure.Placement('place' + posName_lb, volume=waterBoxTB_lv_lb, pos=posCenter_lb)
                    pc_lf        = geom.structure.Placement('place' + posName_lf, volume=waterBoxTB_lv_lf, pos=posCenter_lf)
                    pc_rb        = geom.structure.Placement('place' + posName_rb, volume=waterBoxTB_lv_rb, pos=posCenter_rb)
                    pc_rf        = geom.structure.Placement('place' + posName_rf, volume=waterBoxTB_lv_rf, pos=posCenter_rf)
                    detEnc_lv.placements.append(pc_lb.name)
                    detEnc_lv.placements.append(pc_lf.name)
                    detEnc_lv.placements.append(pc_rb.name)
                    detEnc_lv.placements.append(pc_rf.name)

                    posX += self.waterBoxDim[2]+ self.blockSpacing
                    TBBoxIndex[0] += 1

                posX = self.detCenter[0]
                posZ_f += (self.waterBoxDim[1] + self.blockSpacing)
                posZ_b -= (self.waterBoxDim[1] + self.blockSpacing)
                TBBoxIndex[1] += 1



            print('='*80)
            words = 'number of boxes placed: ' + str(num_boxes_placed)
            if (len(words)%2 == 0):
                space = (80 - len(words)) / 2
            else:
                space = (81 - len(words)) / 2
            print(' '*space + str(words) + ' '*space)
            # print(' '*space + 'Cost of boxes: $' + str(container_cost * num_boxes_placed / 1000000) + "M")
            print('='*80)

    def MakeBeamStructure(self, geom, detEnc_lv):
        #self.get_builder("BeamStructure").IPEBeamLength = detDim[1]
        posX_beam_lv = self.get_builder("BeamStructure").get_volume('volBeamPlanePosX')
        posName = 'BeamPlanePosX_in_Enc'
        print(str(self.detCenter[1]))
        posX_beam_in_enc = geom.structure.Position(posName,
                                                   self.detCenter[0]+self.detDim[0]/2,
                                                   self.detCenter[1],
                                                   self.detCenter[2])
        p_posX_beam_in_E  = geom.structure.Placement('place'+posName,
                                                     volume = posX_beam_lv,
                                                     pos = posX_beam_in_enc)
        detEnc_lv.placements.append(p_posX_beam_in_E.name)

        

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):
        encBox = geom.shapes.Box('DetEnclosureBox',
                                 dx=0.5*self.detEncDim[0], 
                                 dy=0.5*self.detEncDim[1],
                                 dz=0.5*self.detEncDim[2])
        encArch = geom.shapes.Tubs('DetEnclosureArch',  rmin=Q('0cm'), rmax=self.archRadius,
                                   dz=0.5*self.detEncDim[2],
                                   sphi=Q('90deg')-self.archHalfAngle, dphi=self.archHalfAngle*2)
        elevation = self.detEncDim[1]/2 - m.cos(self.archHalfAngle.to('radians')) * self.archRadius
        
        Pos = geom.structure.Position(self.name+'_ArchPos',
                                      Q('0m'),elevation, Q('0m'))
        
        encTotal = geom.shapes.Boolean(self.name+"BoolAdd",
                                       type='union', first=encBox,
                                       second=encArch, pos=Pos)
        
        detEnc_lv = geom.structure.Volume('volDetEnclosure', material=self.detEncMat, shape=encTotal)
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
        posName = 'Cryostat_in_Enc'
        cryo_in_enc = geom.structure.Position(posName, self.detCenter[0], self.detCenter[1], self.detCenter[2])
        pCryo_in_E  = geom.structure.Placement('place'+posName,
                                               volume = cryo_lv,
                                               pos = cryo_in_enc)
        detEnc_lv.placements.append(pCryo_in_E.name)

        builders = self.get_builders()
        print (type(builders[0]))
        if (self.makeWaterShield):
            self.MakeWaterShield(geom, detEnc_lv)

        self.MakeBeamStructure(geom, detEnc_lv)








