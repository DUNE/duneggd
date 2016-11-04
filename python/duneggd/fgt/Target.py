#!/usr/bin/env python
'''
Subbuilder of STTBuilder
'''

import gegede.builder
from gegede import Quantity as Q

class TargetPlaneBuilder(gegede.builder.Builder):

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure( self, empty=False, 
                   tTube_innerDia=None, tTube_outerDia=None, tTube_length=None, 
                   nTubesPerTarget=68, 
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
        self.nTubesPerTarget = nTubesPerTarget


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):


        # Make the tubes of target material, with aluminum tube on the outer boundary
        # rmin=0, else material at 0 would be default of target plane
        targetTube    = geom.shapes.Tubs(self.name+'_Tube', 
                                         rmin = '0cm',              
                                         rmax = 0.5*self.tTube_outerDia, 
                                         dz   = 0.5*self.tTube_length)
        targetTube_lv = geom.structure.Volume('vol'+self.name+'Tube', material=self.tubeMat, shape=targetTube)
        #CarbonTube    = geom.shapes.Tubs(self.name+'_CarbonTube', 
        #                                 rmin = 0.5*self.tTube_innerDia, 
        #                                 rmax = 0.5*self.tTube_outerDia, 
        #                                 dz   = 0.5*self.tTube_length)
        GasTube    = geom.shapes.Tubs(self.name+'_ArgonTarget', 
                                         rmin = '0cm', 
                                         rmax = 0.5*self.tTube_innerDia, 
                                         dz   = 0.5*self.tTube_length)
        #CarbonTube_lv   = geom.structure.Volume('vol'+self.name+'CarbonTube', material=self.tubeMat, shape=CarbonTube)
        GasTube_lv   = geom.structure.Volume('vol'+self.name+'GasTube', material=self.targetMat, shape=GasTube)
        #GasTube_lv   = geom.structure.Volume('vol'+self.name+'GasTube', material='Air', shape=GasTube)
        pGas_in_Tube = geom.structure.Placement( 'placeGas_in_Tube_'+self.name, volume = GasTube_lv )
        targetTube_lv.placements.append( pGas_in_Tube.name )
        self.add_volume(targetTube_lv)


        # Make a box of target tubes found in the STT
        self.targetPlaneDim = [ self.tTube_length,    # this assumes a square crossection, tubes are vertical
                                self.tTube_length, 
                                self.tTube_outerDia ] # is there more space than just outerDia?
        targetPlane = geom.shapes.Box( self.name,                     dx=0.5*self.targetPlaneDim[0], 
                                       dy=0.5*self.targetPlaneDim[1], dz=0.5*self.targetPlaneDim[2])
        targetPlane_lv = geom.structure.Volume('vol'+self.name, material=self.defaultMat, shape=targetPlane)
        self.add_volume(targetPlane_lv)


        # Calculate spaceing based off of number of target tubes
        self.tTube_interval = (self.targetPlaneDim[0] - self.tTube_outerDia) / self.nTubesPerTarget
        if( self.tTube_interval <= self.tTube_outerDia ):
            print " WARNING: target tube interval "+str(self.tTube_interval)+", diameter "+str(self.tTube_outerDia);


        # Check parameter consistency in case interval is asserted
        calculatedWidth = ( (self.nTubesPerTarget-1) * self.tTube_interval ) + self.tTube_outerDia
        if( calculatedWidth > self.targetPlaneDim[0] ):
            # TODO: Make a set of warning string templates for printing things like this
            # parameters would be (builder name, iterated volume name, # of iterations, interval, mother volume)
            print "TargetBuilder: "+str(self.nTubesPerTarget)+" target tubes at a "+str(self.tTube_interval)+" interval don't fit in Target Plane"
            self.tTube_interval = ( self.targetPlaneDim[0] - self.tTube_outerDia )/(self.nTubesPerTarget-1)
            print "TargetBuilder: Reset interval to "+str(self.tTube_interval)


        # Place tubes
        xstart = -0.5*self.targetPlaneDim[0] + 0.5*self.tTube_outerDia
        for i in range(self.nTubesPerTarget):

            xpos =  xstart + i*(self.tTube_interval)
            
            T_in_Tar  = geom.structure.Position('Tube-'+str(i)+'_in_'+self.name, xpos, '0cm', '0cm')
            pT_in_Tar = geom.structure.Placement( 'placeTube-'+str(i)+'_in_'+self.name,
                                                  volume = targetTube_lv,
                                                  pos = T_in_Tar,
                                                  rot = 'r90aboutX')
            targetPlane_lv.placements.append( pT_in_Tar.name )
