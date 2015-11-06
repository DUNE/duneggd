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
    def configure(self, detEncDim=['50m','50m','50m'], detEncMat = 'Air', **kwds):
        self.material   = detEncMat
        self.dimensions = detEncDim
        self.sttBldr = self.get_builder('STT')

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):
        encBox = geom.shapes.Box(   self.name,          dx=self.dimensions[0], 
                                 dy=self.dimensions[1], dz=self.dimensions[2])
        detEnc_lv = geom.structure.Volume('vol'+self.name, material=self.material, shape=encBox)
        self.add_volume(detEnc_lv)

        # Position volSTT in volDetEnclosure
        sttDim = self.sttBldr.sttDim
        sttPos = ['0cm', '0cm', 0.5*sttDim[2] ]
        stt_lv = self.sttBldr.get_volume('volSTT')
        stt_in_detenc = geom.structure.Position('STT_in_DetEnc', sttPos[0], sttPos[1], sttPos[2])
        pSTT_in_DE = geom.structure.Placement('placeSTT_in_DetEnc',
                                              volume = stt_lv,
                                              pos = stt_in_detenc)
        detEnc_lv.placements.append(pSTT_in_DE.name)
