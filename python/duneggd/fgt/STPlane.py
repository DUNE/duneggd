#!/usr/bin/env python
'''
Subbulder of STTBuilder
'''

import gegede.builder
import math

class STPlaneBuilder(gegede.builder.Builder):

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, sTube_rmin='0.95cm', sTube_rmax='0.9565cm', sTube_length='350cm', 
                  stPlaneMat='Air', strawMat='fibrous_glass', stGas='stGas_Ar', **kwds):
        self.material   = stPlaneMat
        self.strawMat   = strawMat
        self.stGas      = stGas
        self.sTube_rmin = sTube_rmin
        self.sTube_rmax = sTube_rmax
        self.sTube_length = sTube_length


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Make the straw tube shape and volume
        sTube = geom.shapes.Tubs('StrawTube_'+self.name, rmin=self.sTube_rmin, rmax=self.sTube_rmax, dz=self.sTube_length)
        sTube_lv = geom.structure.Volume('volStrawTube_'+self.name, material=self.stGas, shape=sTube)
        self.add_volume(sTube_lv)

        # Make the double-layer of straw tubes, used for both orientations
        self.stPlaneDim = [ self.sTube_length, 
                            self.sTube_length, 
                            2*self.sTube_rmax + 2*self.sTube_rmax*math.sin( math.radians(60) ) ]
        stPlaneBox = geom.shapes.Box(    self.name,          dx=self.stPlaneDim[0], 
                                      dy=self.stPlaneDim[1], dz=self.stPlaneDim[2])
        stPlane_lv = geom.structure.Volume('vol'+self.name, material=self.material, shape=stPlaneBox)
        self.add_volume(stPlane_lv)
