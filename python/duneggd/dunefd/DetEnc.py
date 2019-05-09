#!/usr/bin/env python

import gegede.builder
from gegede import Quantity as Q

class DetEncBuilder(gegede.builder.Builder):

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self,
                  detEncDim       = None ,
                  encBoundToDet_z = None , 
                  detDim          = None ,
                  detEncMat       = 'Air',
                  **kwds):
        if detEncDim is None:
            raise ValueError("No value given for detEncDim")
        if encBoundToDet_z is None:
            raise ValueError("No value given for encBoundToDet_z")

        self.detEncMat       = detEncMat
        self.detEncDim       = detEncDim
        self.encBoundToDet_z = encBoundToDet_z
        self.detDim          = detDim


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):
        encBox    = geom.shapes.Box(self.name + "_box_shape",
                                    dx = 0.5*self.detEncDim[0],
                                    dy = 0.5*self.detEncDim[1],
                                    dz = 0.5*self.detEncDim[2])

        detEnc_lv = geom.structure.Volume(self.name + "_volume",
                                          material = self.detEncMat,
                                          shape    = encBox)
        self.add_volume(detEnc_lv)

        detBox = geom.shapes.Box('Detector_box_shape',
                                 dx = 0.5*self.detDim[0],
                                 dy = 0.5*self.detDim[1],
                                 dz = 0.5*self.detDim[2])
        det_lv = geom.structure.Volume('Detector_volume', material=self.detEncMat, shape=detBox)

        # Place the detector in the world
        self.encBoundToDet = [ 0.5*self.detEncDim[0] - 0.5*self.detDim[0], Q('0cm'), self.encBoundToDet_z ]

        detPos = [ -0.5*self.detEncDim[0] + self.encBoundToDet[0] + 0.5*self.detDim[0] ,
                   -0.5*self.detEncDim[1] + self.encBoundToDet[1] + 0.5*self.detDim[1] ,
                   -0.5*self.detEncDim[2] + self.encBoundToDet[2] + 0.5*self.detDim[2] ]
        det_in_enc = geom.structure.Position('Det_in_Enc', *detPos)
        pD_in_E    = geom.structure.Placement('placeDet_in_Enc', volume=det_lv, pos=det_in_enc)
        detEnc_lv.placements.append(pD_in_E.name)
