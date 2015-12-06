#!/usr/bin/env python
'''
Subbuilder of Detector
'''

import gegede.builder
from gegede import Quantity as Q
import math

class ECALModBuilder(gegede.builder.Builder):
    '''
    Piece together SBPlanes, worry about rotations in DetectorBuilder,
    assuring that lead layer on outside is closest to tracker
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, 
                  ecalThickness = None, 
                  leadThickness = None, 
                  nSBPlanes = None,
		  altPlaneOrient = True,
                  **kwds):
        if ecalThickness is None:
            raise ValueError("No value given for ecalThickness")
        if leadThickness is None:
            raise ValueError("No value given for leadThickness")
        if nSBPlanes is None:
            raise ValueError("No value given for nSBPlanes")

        self.ecalMat        = "Lead"
        self.ecalThickness  = ecalThickness
        self.leadThickness  = leadThickness
        self.nSBPlanes      = nSBPlanes  
        self.altPlaneOrient = altPlaneOrient
        self.SBPlaneBldr = self.get_builder('SBPlane')


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Get the SB Plane volume and dimensions
        SBPlane_lv = self.SBPlaneBldr.get_volume('volSBPlane')
        SBPlaneDim = list(self.SBPlaneBldr.SBPlaneDim)
        

        # Calculate ECAL dimensions 
        self.ecalModDim    = list(SBPlaneDim) # get the right x and y dimension
        self.ecalModDim[2] = self.nSBPlanes*(self.leadThickness + SBPlaneDim[2])
        print 'ECALModBuilder: set ECAL z dimension to '+str(self.ecalModDim[2])+' (configured as '+str(self.ecalThickness)+')'
      
        # Make main shape/volume for this builder
        ecalModBox = geom.shapes.Box( self.name,
                                      dx=0.5*self.ecalModDim[0],
                                      dy=0.5*self.ecalModDim[1],
                                      dz=0.5*self.ecalModDim[2])
        ecalMod_lv = geom.structure.Volume('vol'+self.name, material=self.ecalMat, shape=ecalModBox)
        self.add_volume(ecalMod_lv)
  

        #Place the SB Planes in the ECAL

        n1 = 0 
        n2 = 0
        for i in range(self.nSBPlanes):
            zpos = -0.5*self.ecalModDim[2]+ (i+0.5)*SBPlaneDim[2]+(i+1)*self.leadThickness

	    rotPlane = 'identity'
	    if(self.altPlaneOrient): rotPlane = 'r90aboutZ'

            if i%2==0:
               rsbp_in_ecalend  = geom.structure.Position('SBPlane-'+str(i)+'_in_'+self.name, 
                                                          '0cm', '0cm', zpos)
               prsbp_in_ecalend = geom.structure.Placement('placeSBPlane-'+str(i)+'_in_'+self.name,
                                                           volume = SBPlane_lv, 
                                                           pos = rsbp_in_ecalend)
               ecalMod_lv.placements.append( prsbp_in_ecalend.name )
               n1=n1+1
            else:
                rsbp_in_ecalend  = geom.structure.Position('SBPlane-'+str(i)+'_in_'+self.name, 
                                                           '0cm', '0cm', zpos)
                prsbp_in_ecalend = geom.structure.Placement('placeSBPlane-'+str(i)+'_in_'+self.name,
                                                            volume = SBPlane_lv, 
                                                            pos = rsbp_in_ecalend, rot=rotPlane)
                ecalMod_lv.placements.append( prsbp_in_ecalend.name )
                n2=n2+1
                
        #print 'ECALModBuilder:',i+1 ,'SBPlanes', 'in '+str(self.name)
        #print n1, 'SBPlanes have scint. bars oriented along X direction and', n2, 'SBPlanes have scint. bars oriented along Y direction for '+str(self.name) 
        return



































