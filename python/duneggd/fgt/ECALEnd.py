#!/usr/bin/env python
'''
Subbuilder of Detector
'''

import gegede.builder
from gegede import Quantity as Q
import math

class ECALEndBuilder(gegede.builder.Builder):
    '''
    Piece together SBPlanes, worry about rotations in DetectorBuilder,
    assuring that lead layer on outside is closest to tracker
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, ECALEndDim=None, **kwds):
        if ECALEndDim is None:
            raise ValueError("No value given for ECALEndDim")

        self.defMat     = "Lead"
        self.ECALEndDim = ECALEndDim
        
        #print self builders
        self.SBPlaneBldr = self.get_builder('SBPlane')


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Get the SB Plane volume and dimensions
        SBPlane_lv = self.SBPlaneBldr.get_volume('volSBPlane')
        SBPlaneDim = list(self.SBPlaneBldr.SBPlaneDim)
        
        # self.name == configuration section name
        self.leadThickness = leadThickness
        self.nSBPlanes     = nSBPlanes  

        # Calculate ECAL dimensions 
        print "The values of the ECAL dimensions are not based on the CDR values and are calculated such that the SBPlanes fit in to the ECAL detector"  
        self.ECALEndDim    = list(SBPlaneDim) # get the right x and y dimension
        self.ECALEndDim[2] = self.nSBPlanes*(self.leadThickness + self.SBPlaneDim[2])
      
        # make box into which those dimensions go
        # Make volume into which the ensuing placements go and which will be retrieved by DetectorBuilder
        ECALEndBox = geom.shapes.Box('ECALEndBox',
                                       dx=0.5*self.ECALEndDim[0],
                                       dy=0.5*self.ECALEndDim[1],
                                       dz=0.5*self.ECALEndDim[2])
        ECALEnd_lv = geom.structure.Volume('volECALEnd', material=self.ECALEndMat, shape=ECALEndBox)

  

        #Place the SB Planes in the ECAL

        for i in range(self.nSBPlanes):
            zpos = -0.5*self.ECALEndDim[2]+ (i+0.5)*self.SBPlaneDim[2]+i*self.leadThickness

            rsbp_in_ecalend  = geom.structure.Position('SBPlane-'+str(i)+'_in_ECALEnd', 
                                                       '0cm', '0cm', zpos)
            prsbp_in_ecalend = geom.structure.Placement('placeSBPlane-'+str(i)+'_in_ECALEnd',
                                                        volume = ECALEnd_lv, 
                                                        pos = rsbp_in_ecalend,rot = "r90aboutZ")

            ECALEnd_lv.placements.append( prsbp_in_ecalend.name )
        return
