#!/usr/bin/env python
'''
Subbuilder of Detector
'''

import gegede.builder
from gegede import Quantity as Q


class ECALEndBuilder(gegede.builder.Builder):
    '''
    Piece together SBPlanes, worry about rotations in DetectorBuilder,
    assuring that lead layer on outside is closest to tracker
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, **kwds):

        #self.parameter = parameter
        
        self.sbPlaneBldr = self.get_builder('SBPlane')


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Get the SB Plane volume and dimensions
        sbPlane_lv = self.sbPlaneBldr.get_volume('volSBPlane')
        sbPlaneDim = list(self.sbPlaneBldr.SBPlaneDim)
        

        # using configurations and sbPlaneDim, calculate ECAL* dimensions 


        # make box into which those dimensions go
        # make volume into which ensuing placements go
  

        # for loop, 
        #for i in range(nSBPlanes):
        #    place at interval leadThickness+SBPlaneDim[2]

        
        return
