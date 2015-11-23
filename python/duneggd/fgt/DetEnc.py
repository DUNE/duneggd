#!/usr/bin/env python
'''
Subbuilder of WorldBuilder
'''

import gegede.builder
from gegede import Quantity as Q


class DetEncBuilder(gegede.builder.Builder):
    '''
    Build the Detector Enclosure.
    '''


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, 
                  detEncDim=None, 
                  encBoundToDet_z=None, 
                  detDim=None,
                  blankSite = False,
                  detEncMat = 'Air', **kwds):
        if detEncDim is None:
            raise ValueError("No value given for detEncDim")
        if encBoundToDet_z is None:
            raise ValueError("No value given for encBoundToDet_z")
        if detDim is None:
            self.configDetDim = False
        else: 
            self.configDetDim = True
            self.detDim       = detDim


        self.detEncMat     = detEncMat
        self.detEncDim     = detEncDim
        self.blankSite     = blankSite

        # Space from negative face of volDetEnc to closest face of volDet
        #  This positions the detector in the enclosure
        self.encBoundToDet_z = encBoundToDet_z


        # If not configuring the detector box, get it from the builder
        if (self.blankSite):
            if(not self.configDetDim):
                raise ValueError("Must configure detDim box for blank site")
        else: 
            self.detBldr  = self.get_builder('Detector')



    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):
        encBox = geom.shapes.Box( self.name,                 dx=0.5*self.detEncDim[0], 
                                  dy=0.5*self.detEncDim[1],  dz=0.5*self.detEncDim[2])
        detEnc_lv = geom.structure.Volume('vol'+self.name, material=self.detEncMat, shape=encBox)
        self.add_volume(detEnc_lv)


        #  Make or Get the box into which the physical detector volumes eventually go
        if (self.blankSite):
            detBox = geom.shapes.Box( 'Detector',              dx=0.5*self.detDim[0], 
                                      dy=0.5*self.detDim[1],  dz=0.5*self.detDim[2])
            det_lv = geom.structure.Volume('volDetector', material=self.detEncMat, shape=detBox)
            print "DetectorBuilder: Detector Enclosure has no detector volumes in it:"
        else:
            det_lv      = self.detBldr.get_volume('volDetector')


        # Get dimensions if not configured, print method
        if (self.configDetDim):
            print "DetectorBuilder: Detector box configured:"
        else:
            self.detDim = list(self.detBldr.detDim)
            print "DetectorBuilder: Detector box calculated:"
        print     "                 x="+str(self.detDim[0])+" y="+str(self.detDim[1])+" z="+str(self.detDim[2])
            
        
        self.encBoundToDet = [ 0.5*self.detEncDim[0] - 0.5*self.detDim[0], # x: center it for now
                               Q('0cm'),                                   # y: sit detector on floor
                               self.encBoundToDet_z ]                      # z: configure
        
        detPos = [ -0.5*self.detEncDim[0] + self.encBoundToDet[0] + 0.5*self.detDim[0], 
                   -0.5*self.detEncDim[1] + self.encBoundToDet[1] + 0.5*self.detDim[1], 
                   -0.5*self.detEncDim[2] + self.encBoundToDet[2] + 0.5*self.detDim[2]  ]
        det_in_enc = geom.structure.Position('Det_in_Enc', detPos[0], detPos[1], detPos[2])
        pD_in_E = geom.structure.Placement('placeDet_in_Enc',
                                           volume = det_lv,
                                           pos = det_in_enc)
        detEnc_lv.placements.append(pD_in_E.name)
        

