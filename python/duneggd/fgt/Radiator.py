#!/usr/bin/env python
'''
Subbuilder of STTBuilder.
'''

import gegede.builder
from gegede import Quantity as Q


class RadiatorBuilder(gegede.builder.Builder):
    '''
    Puts foils and spacers into the radiator volume, which is passed 
    to the STT to be placed whenever building a radiator module.
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure( self, foilThickness=Q('25um'), spacerThickness=Q('125um'), 
                   nFoilsPerRadiator=60, radFoilDim = None, spacerDim = None,
                   radFoilMat='C3H6', spacerMat='Air', 
                   onlyOneBlock=False, **kwds):


        if radFoilDim is None:
            raise ValueError("No value given for radFoilDim")
        if spacerDim is None:
            raise ValueError("No value given for spacerDim")

        self.radFoilMat  = radFoilMat
        self.spacerMat   = spacerMat
        self.defaultMat  = 'RadiatorBlend'

        self.onlyOneBlock      = onlyOneBlock
        self.foilThickness     = foilThickness
        self.spacerThickness   = spacerThickness
        self.nFoilsPerRadiator = nFoilsPerRadiator
        self.radFoilDim        = radFoilDim
        self.spacerDim         = spacerDim
        

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Make radiator foil and spacer for foils
        radFoilBox = geom.shapes.Box( 'RadiatorFoil',            dx=0.5*self.radFoilDim[0], 
                                      dy=0.5*self.radFoilDim[1], dz=0.5*self.radFoilDim[2])
        spacerBox = geom.shapes.Box(  'RadiatorSpacer',          dx=0.5*self.spacerDim[0], 
                                      dy=0.5*self.spacerDim[1],  dz=0.5*self.spacerDim[2])
        radFoil_lv = geom.structure.Volume('volRadiatorFoil',   material=self.radFoilMat, shape=radFoilBox)
        spacer_lv  = geom.structure.Volume('volRadiatorSpacer', material=self.spacerMat,  shape=spacerBox)


        # Set the dimensions for and create the volume that this builder 
        # builds, to be passed to the STT builder for each ratiator module
        self.radiatorDim    = [ self.radFoilDim[0], self.radFoilDim[0],
                                self.nFoilsPerRadiator * ( self.radFoilDim[2] + self.spacerDim[2] ) ] 
        radiatorBox = geom.shapes.Box( 'Radiator',                 dx=0.5*self.radiatorDim[0], 
                                       dy=0.5*self.radiatorDim[1], dz=0.5*self.radiatorDim[2])
        radiator_lv = geom.structure.Volume('volRadiator', material=self.defaultMat, shape=radiatorBox)

    
        # Put the foils and spacers in the Radiator unless we want it blended into one volume
        if(not self.onlyOneBlock):
            zpos = -0.5*self.radiatorDim[2] # keep this one variable to zip through all z positions
            for i in range(self.nFoilsPerRadiator):
                
                # the foil
                zpos += 0.5*self.radFoilDim[2]
                foil_in_rad = geom.structure.Position('rad-'+str(i)+'_in_Rad', '0cm', '0cm', zpos)
                pF_in_R = geom.structure.Placement( 'placeFoil-'+str(i)+'_in_Rad',
                                                    volume = radFoil_lv,
                                                    pos = foil_in_rad)
                radiator_lv.placements.append( pF_in_R.name )
                
                # the spacer
                zpos += 0.5*(self.radFoilDim[2]+self.spacerDim[2])
                spacer_in_rad = geom.structure.Position('spacer-'+str(i)+'_in_Rad', '0cm', '0cm', zpos)
                pS_in_R = geom.structure.Placement( 'placeSpacer-'+str(i)+'_in_Rad',
                                                    volume = spacer_lv,
                                                    pos = spacer_in_rad)
                radiator_lv.placements.append( pS_in_R.name )
                zpos += 0.5*self.spacerDim[2]

        # add all of the volumes to this RadiatorBuilder
        self.add_volume(radFoil_lv, spacer_lv, radiator_lv)
