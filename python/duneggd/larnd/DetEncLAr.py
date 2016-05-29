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
                  detEncDim       = None, 
                  magBarsDim      = None,
                  encBoundToDet_z = None, 
                  **kwds):
        if detEncDim is None:
            raise ValueError("No value given for detEncDim")
        if magBarsDim is None:
            raise ValueError("No value given for magBarsDim")
        if encBoundToDet_z is None:
            raise ValueError("No value given for encBoundToDet_z")

        self.detEncMat     = 'Air'
        self.detEncDim     = detEncDim
        self.magBarsDim    = magBarsDim

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


        magBarsDim = self.magBarsDim
        magBarLong = geom.shapes.Box( 'magBarLong',
                                       dx=0.5*self.magBarsDim[0], 
                                       dy=0.5*self.magBarsDim[1], 
                                       dz=0.5*(cryoDim[2] + 2*self.magBarsDim[2]))
        magBarLong_lv = geom.structure.Volume('volMagBarLong', material='Aluminum', shape=magBarLong)
        magBarShort = geom.shapes.Box( 'magBarShort',
                                       dx=0.5*cryoDim[0],
                                       dy=0.5*self.magBarsDim[1], 
                                       dz=0.5*self.magBarsDim[2])
        magBarShort_lv = geom.structure.Volume('volMagBarShort', material='Aluminum', shape=magBarShort)



        # Calculate position of detector in the enclosure
        self.encBoundToDet = [ 0.5*self.detEncDim[0] - 0.5*self.detDim[0], # x: center it for now
                               self.magBarsDim[1],                         # y: magnet on floor, det on top
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


        # Place Magnet
        posName = 'magBarShort_bot_up_in_Enc' # bottom upstream
        magBar_in_enc = geom.structure.Position(posName, 
                                                self.detCenter[0], 
                                                self.detCenter[1] - 0.5*cryoDim[1] - 0.5*magBarsDim[1], 
                                                self.detCenter[2] - 0.5*cryoDim[2] - 0.5*magBarsDim[2])
        pMB_in_E = geom.structure.Placement('place'+posName,
                                            volume = magBarShort_lv,
                                            pos = magBar_in_enc)
        detEnc_lv.placements.append(pMB_in_E.name)

        posName = 'magBarShort_top_up_in_Enc' # top upstream
        magBar_in_enc = geom.structure.Position(posName, 
                                                self.detCenter[0], 
                                                self.detCenter[1] + 0.5*cryoDim[1] + 0.5*magBarsDim[1], 
                                                self.detCenter[2] - 0.5*cryoDim[2] - 0.5*magBarsDim[2])
        pMB_in_E = geom.structure.Placement('place'+posName,
                                            volume = magBarShort_lv,
                                            pos = magBar_in_enc)
        detEnc_lv.placements.append(pMB_in_E.name)

        posName = 'magBarShort_bot_down_in_Enc' # bottom downstream
        magBar_in_enc = geom.structure.Position(posName, 
                                                self.detCenter[0], 
                                                self.detCenter[1] - 0.5*cryoDim[1] - 0.5*magBarsDim[1], 
                                                self.detCenter[2] + 0.5*cryoDim[2] + 0.5*magBarsDim[2])
        pMB_in_E = geom.structure.Placement('place'+posName,
                                            volume = magBarShort_lv,
                                            pos = magBar_in_enc)
        detEnc_lv.placements.append(pMB_in_E.name)

        posName = 'magBarShort_top_down_in_Enc' # top downstream
        magBar_in_enc = geom.structure.Position(posName, 
                                                self.detCenter[0], 
                                                self.detCenter[1] + 0.5*cryoDim[1] + 0.5*magBarsDim[1], 
                                                self.detCenter[2] + 0.5*cryoDim[2] + 0.5*magBarsDim[2])
        pMB_in_E = geom.structure.Placement('place'+posName,
                                            volume = magBarShort_lv,
                                            pos = magBar_in_enc)
        detEnc_lv.placements.append(pMB_in_E.name)
      
        posName = 'magBarLong_bot_neg_in_Enc' # bottom negative x
        magBar_in_enc = geom.structure.Position(posName, 
                                                self.detCenter[0] - 0.5*cryoDim[0] - 0.5*magBarsDim[0], 
                                                self.detCenter[1] - 0.5*cryoDim[1] - 0.5*magBarsDim[1], 
                                                self.detCenter[2])
        pMB_in_E = geom.structure.Placement('place'+posName,
                                            volume = magBarLong_lv,
                                            pos = magBar_in_enc)
        detEnc_lv.placements.append(pMB_in_E.name)

        posName = 'magBarLong_top_neg_in_Enc' # top negative x
        magBar_in_enc = geom.structure.Position(posName, 
                                                self.detCenter[0] - 0.5*cryoDim[0] - 0.5*magBarsDim[0], 
                                                self.detCenter[1] + 0.5*cryoDim[1] + 0.5*magBarsDim[1], 
                                                self.detCenter[2])
        pMB_in_E = geom.structure.Placement('place'+posName,
                                            volume = magBarLong_lv,
                                            pos = magBar_in_enc)
        detEnc_lv.placements.append(pMB_in_E.name)

        posName = 'magBarLong_bot_pos_in_Enc' # bottom positive x
        magBar_in_enc = geom.structure.Position(posName, 
                                                self.detCenter[0] + 0.5*cryoDim[0] + 0.5*magBarsDim[0], 
                                                self.detCenter[1] - 0.5*cryoDim[1] - 0.5*magBarsDim[1], 
                                                self.detCenter[2])
        pMB_in_E = geom.structure.Placement('place'+posName,
                                            volume = magBarLong_lv,
                                            pos = magBar_in_enc)
        detEnc_lv.placements.append(pMB_in_E.name)

        posName = 'magBarLong_top_pos_in_Enc' # top positive x
        magBar_in_enc = geom.structure.Position(posName, 
                                                self.detCenter[0] + 0.5*cryoDim[0] + 0.5*magBarsDim[0], 
                                                self.detCenter[1] + 0.5*cryoDim[1] + 0.5*magBarsDim[1], 
                                                self.detCenter[2])
        pMB_in_E = geom.structure.Placement('place'+posName,
                                            volume = magBarLong_lv,
                                            pos = magBar_in_enc)
        detEnc_lv.placements.append(pMB_in_E.name)
