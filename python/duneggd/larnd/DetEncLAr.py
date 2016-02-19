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
                  encBoundToDet_z = None, 
                  **kwds):
        if detEncDim is None:
            raise ValueError("No value given for detEncDim")
        if encBoundToDet_z is None:
            raise ValueError("No value given for encBoundToDet_z")

        self.detEncMat     = 'Air'
        self.detEncDim     = detEncDim

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
                               Q('0cm'),                                   # y: sit detector on floor
                               self.encBoundToDet_z ]                      # z: configure
        
        self.detCenter = [ -0.5*self.detEncDim[0] + self.encBoundToDet[0] + 0.5*self.detDim[0], 
                           -0.5*self.detEncDim[1] + self.encBoundToDet[1] + 0.5*self.detDim[1], 
                           -0.5*self.detEncDim[2] + self.encBoundToDet[2] + 0.5*self.detDim[2]  ]


        # Place it
        posName = 'Cryo_in_Enc'
        cryo_in_enc = geom.structure.Position(posName, self.detCenter[0], self.detCenter[1], self.detCenter[2])
        pC_in_E = geom.structure.Placement('place'+posName,
                                           volume = cryo_lv,
                                           pos = cryo_in_enc)
        detEnc_lv.placements.append(pC_in_E.name)

      
