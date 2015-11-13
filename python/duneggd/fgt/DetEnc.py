#!/usr/bin/env python
'''
Subbuilder of WorldBuilder
'''

import gegede.builder

class DetEncBuilder(gegede.builder.Builder):
    '''
    Build the Detector Enclosure.
    '''


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, detEncDim=None, encBoundToDet_z=None, 
                  placeDetector=True, detEncMat = 'Air', **kwds):
        if detEncDim is None:
            raise ValueError("No value given for detEncDim")
        if encBoundToDet_z is None:
            raise ValueError("No value given for encBoundToDet_z")


        self.material      = detEncMat
        self.detEncDim     = detEncDim

        # Space from negative face of volDetEnc to closest face of volDet
        #  This positions the detector in the enclosure
        self.encBoundToDet_z = encBoundToDet_z

        self.placeDet = placeDetector
        if self.placeDet:
            self.detBldr  = self.get_builder('Detector')



    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):
        encBox = geom.shapes.Box( self.name,                 dx=0.5*self.detEncDim[0], 
                                  dy=0.5*self.detEncDim[1],  dz=0.5*self.detEncDim[2])
        detEnc_lv = geom.structure.Volume('vol'+self.name, material=self.material, shape=encBox)
        self.add_volume(detEnc_lv)


        # Position detector in enclosure
        if self.placeDet:
            det_lv      = self.detBldr.get_volume('volDetector')
            self.detDim = list(self.detBldr.detDim)

            self.encBoundToDet = [ 0.5*self.detEncDim[0] - 0.5*self.detDim[0], # x: center it for now
                                   0*self.detDim[1],                           # y: sit detector on floor
                                   self.encBoundToDet_z ]                      # z: configure

            detPos = [ -0.5*self.detEncDim[0] + self.encBoundToDet[0] + 0.5*self.detDim[0], 
                       -0.5*self.detEncDim[1] + self.encBoundToDet[1] + 0.5*self.detDim[1], 
                       -0.5*self.detEncDim[2] + self.encBoundToDet[2] + 0.5*self.detDim[2]  ]
            det_lv = self.detBldr.get_volume('volDetector')
            det_in_enc = geom.structure.Position('Det_in_Enc', detPos[0], detPos[1], detPos[2])
            pD_in_E = geom.structure.Placement('placeDet_in_Enc',
                                               volume = det_lv,
                                               pos = det_in_enc)
            detEnc_lv.placements.append(pD_in_E.name)
        

