#!/usr/bin/env python
'''
Example gegede builders for a trivial LAr geometry
'''

import gegede.builder

class TargetPlaneBuilder(gegede.builder.Builder):

    def configure( self, tTube_rmin, tTube_rmax, tTube_length, nTubesPerTarget, 
                   targetMat='Argon', **kwds ):
        self.targetMat   = targetMat
        self.defaultMat  = 'Air'
        self.tubeMat     = 'Aluminum'

        self.tTube_rmin   = tTube_rmin
        self.tTube_rmax   = tTube_rmax
        self.tTube_length = tTube_length
        self.nTubesPerTarget = nTubesPerTarget


    def construct(self, geom):

        # Make the tubes of target material
        targetTube = geom.shapes.Tubs(self.name+'Tube', rmin=self.tTube_rmin, rmax=self.tTube_rmax, dz=self.tTube_length)
        targetTube_lv = geom.structure.Volume('vol'+self.name+'Tube', material=self.targetMat, shape=targetTube)
        self.add_volume(targetTube_lv)
        # need to do the subtraction

        # Make a box of target tubes found in the STT
        self.targetPlaneDim = [ self.tTube_length, self.tTube_length, self.tTube_rmax ] # is there more space than just rmax?
        targetPlane = geom.shapes.Box(    self.name,              dx=self.targetPlaneDim[0], 
                                       dy=self.targetPlaneDim[1], dz=self.targetPlaneDim[2])
        targetPlane_lv = geom.structure.Volume('vol'+self.name, material=self.defaultMat, shape=targetPlane)
        self.add_volume(targetPlane_lv)

        # Place tubes


