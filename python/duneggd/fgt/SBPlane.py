#!/usr/bin/env python
'''
Subbuilder of ECALBuilder
'''

import gegede.builder
from gegede import Quantity as Q
import math

class SBPlaneBuilder(gegede.builder.Builder):
 
    # define builder data here
    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, ScintBarDim = [Q('3.2m'), Q('2.5cm'), Q('1cm')],
                        SBPlaneMat  = "epoxy_resin",
                        ScintBarMat = "Scintillator", **kwds):
        self.SBPlaneMat  = SBPlaneMat
        self.ScintBarMat = ScintBarMat
        self.ScintBarDim = ScintBarDim
     

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Make the scint bar shape and volume
        ScintBarBox = geom.shapes.Box( 'ScintBarBox',            dx=0.5*self.ScintBarDim[0], 
                                     dy=0.5*self.ScintBarDim[1], dz=0.5*self.ScintBarDim[2])
        ScintBar_lv = geom.structure.Volume('volScintBar', material=self.ScintBarMat, shape=ScintBarBox)
        self.add_volume(ScintBar_lv)

        # define material in World Builder
        # Make the scint bar plane, used for both orientations
        self.SBPlaneDim = [Q('3.2m'), Q('3.2m'), Q('1cm')]
        SBPlaneBox = geom.shapes.Box( 'SBPlaneBox',               dx=0.5*self.SBPlaneDim[0], 
                                      dy=0.5*self.SBPlaneDim[1], dz=0.5*self.SBPlaneDim[2])
        SBPlane_lv = geom.structure.Volume('volSBPlane', material=self.SBPlaneMat, shape=SBPlaneBox)
        self.add_volume(SBPlane_lv)
        # make default material glue -- search 'epoxy' in gdmlMaterials.py
	# This volume will be retrieved by ECAL*Builder


        # Place the bars in the plane
        nScintBarsPerPlane = int(math.floor((self.SBPlaneDim[1]/self.ScintBarDim[1])))
        for i in range(nScintBarsPerPlane):
            xpos = -0.5*self.SBPlaneDim[0] + 0.5*(2*i+1)*self.ScintBarDim[1]
            sb_in_sp      = geom.structure.Position( 'SB-'+str(i)+'_in_'+self.name, 
                                                     xpos, '0cm', '0cm')
            psb_in_sp     = geom.structure.Placement( 'placeSB-'+str(i)+'_in_'+self.name, 
                                                      volume = ScintBar_lv, pos = sb_in_sp)
            SBPlane_lv.placements.append(psb_in_sp.name)
