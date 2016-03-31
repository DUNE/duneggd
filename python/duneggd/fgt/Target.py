#!/usr/bin/env python
'''
Subbuilder of STTBuilder
'''

import gegede.builder
from gegede import Quantity as Q

class TargetPlaneBuilder(gegede.builder.Builder):

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure( self, tTube_innerDia=None, tTube_outerDia=None, tTube_length=None, 
                   tTube_interval=Q('0.505in'), nTubesPerTarget=275, 
                   targetMat='ArgonTarget', **kwds ):

        if tTube_innerDia is None:
            raise ValueError("No value given for tTube_innerDia")
        if tTube_outerDia is None:
            raise ValueError("No value given for tTube_outerDia")
        if tTube_length is None:
            raise ValueError("No value given for tTube_length")

        self.targetMat   = targetMat
        self.defaultMat  = 'Air'
        self.tubeMat     = 'CarbonFiber'

        self.tTube_innerDia  = tTube_innerDia
        self.tTube_outerDia  = tTube_outerDia
        self.tTube_length    = tTube_length
        self.tTube_interval  = tTube_interval
        self.nTubesPerTarget = nTubesPerTarget


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):


        # Make the tubes of target material, with aluminum tube on the outer boundary
        # rmin=0, else material at 0 would be default of target plane
        targetTube    = geom.shapes.Tubs(self.name+'Tube', 
                                         rmin = '0cm',              
                                         rmax = 0.5*self.tTube_outerDia, 
                                         dz   = 0.5*self.tTube_length)
        targetTube_lv = geom.structure.Volume('vol'+self.name+'Tube', material=self.targetMat, shape=targetTube)
        alumTube      = geom.shapes.Tubs(self.name+'AlumTube', 
                                         rmin = 0.5*self.tTube_innerDia, 
                                         rmax = 0.5*self.tTube_outerDia, 
                                         dz   = 0.5*self.tTube_length)
        alumTube_lv   = geom.structure.Volume('vol'+self.name+'AlumTube', material=self.tubeMat, shape=targetTube)
        pAlum_in_Tube = geom.structure.Placement( 'placeAlum_in_Tube', volume = alumTube_lv )
        targetTube_lv.placements.append( pAlum_in_Tube.name )
        self.add_volume(targetTube_lv)


        # Make a box of target tubes found in the STT
        self.targetPlaneDim = [ self.tTube_length,    # this assumes a square crossection, tubes are vertical
                                self.tTube_length, 
                                self.tTube_outerDia ] # is there more space than just outerDia?
        targetPlane = geom.shapes.Box( self.name,                     dx=0.5*self.targetPlaneDim[0], 
                                       dy=0.5*self.targetPlaneDim[1], dz=0.5*self.targetPlaneDim[2])
        targetPlane_lv = geom.structure.Volume('vol'+self.name, material=self.defaultMat, shape=targetPlane)
        self.add_volume(targetPlane_lv)


        # Check parameter consistency
        calculatedWidth = ( (self.nTubesPerTarget-1) * self.tTube_interval ) + self.tTube_outerDia
        if( calculatedWidth > self.targetPlaneDim[0] ):
            # TODO: Make a set of warning string templates for printing things like this
            # parameters would be (builder name, iterated volume name, # of iterations, interval, mother volume)
            print "TargetBuilder: "+str(self.nTubesPerTarget)+" target tubes at a "+str(self.tTube_interval)+" interval don't fit in Target Plane"
            self.tTube_interval = ( self.targetPlaneDim[0] - self.tTube_outerDia )/(self.nTubesPerTarget-1)
            print "TargetBuilder: Reset interval to "+str(self.tTube_interval)
            if( self.tTube_interval < self.tTube_outerDia ):
                print " WARNING: target tube interval "+str(self.tTube_interval)+", diameter "+str(self.tTube_outerDia);



        # Place tubes
        xstart = -0.5*self.targetPlaneDim[0] + 0.5*self.tTube_outerDia
        for i in range(self.nTubesPerTarget):

            xpos =  xstart + i*(self.tTube_interval)
            
            T_in_Tar  = geom.structure.Position('Tube-'+str(i)+'_in_TargetPlane', xpos, '0cm', '0cm')
            pT_in_Tar = geom.structure.Placement( 'placeTube-'+str(i)+'_in_TargetPlane',
                                                  volume = targetTube_lv,
                                                  pos = T_in_Tar,
                                                  rot = 'r90aboutX')
            targetPlane_lv.placements.append( pT_in_Tar.name )
