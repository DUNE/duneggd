#!/usr/bin/env python
'''
Subbuilder of STTBuilder.
'''

import gegede.builder

class RadiatorBuilder(gegede.builder.Builder):
    '''
    Puts foils and spacers into the radiator volume, which is passed 
    to the STT to be placed whenever building a radiator module.
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure( self, foilThickness='0.004cm', spacerThickness='0.025cm', 
                   nFoilsPerRadiator=60, radFoilDim = None, spacerDim = None,
                   radFoilMat='C3H6', spacerMat='Fabric', **kwds):


        if radFoilDim is None:
            raise ValueError("No value given for radFoilDim")
        if spacerDim is None:
            raise ValueError("No value given for spacerDim")

        self.radFoilMat  = radFoilMat
        self.spacerMat   = spacerMat
        self.defaultMat  = 'Air'

        self.foilThickness     = foilThickness
        self.spacerThickness   = spacerThickness
        self.nFoilsPerRadiator = nFoilsPerRadiator
        self.radFoilDim        = radFoilDim
        self.spacerDim         = spacerDim
        

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Make radiator foil and spacer for foils
        radFoilBox = geom.shapes.Box( 'RadiatorFoil',        dx=self.radFoilDim[0], 
                                      dy=self.radFoilDim[1], dz=self.radFoilDim[2])
        spacerBox = geom.shapes.Box(  'RadiatorSpacer',      dx=self.spacerDim[0], 
                                      dy=self.spacerDim[1],  dz=self.spacerDim[2])
        radFoil_lv = geom.structure.Volume('volRadiatorFoil',   material=self.radFoilMat, shape=radFoilBox)
        spacer_lv  = geom.structure.Volume('volRadiatorSpacer', material=self.spacerMat,  shape=spacerBox)


        # Set the dimensions for and create the volume that this builder 
        # builds, to be passed to the STT builder for each ratiator module
        self.radiatorDim    = self.radFoilDim
        self.radiatorDim[2] = self.nFoilsPerRadiator * ( self.radFoilDim[2] + self.spacerDim[2] ) 
        radiatorBox = geom.shapes.Box( 'Radiator',             dx=self.radiatorDim[0], 
                                       dy=self.radiatorDim[1], dz=self.radiatorDim[2])
        radiator_lv = geom.structure.Volume('volRadiator', material=self.defaultMat, shape=radiatorBox)

    
        # Put the foils and spacers in the Radiator
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
            zpos += 0.5*self.spacerDim[2]
            spacer_in_rad = geom.structure.Position('spacer-'+str(i)+'_in_Rad', '0cm', '0cm', zpos)
            pS_in_R = geom.structure.Placement( 'placeSpacer-'+str(i)+'_in_Rad',
                                                volume = spacer_lv,
                                                pos = spacer_in_rad)
            radiator_lv.placements.append( pS_in_R.name )


        # add all of the volumes to this RadiatorBuilder
        self.add_volume(radFoil_lv, spacer_lv, radiator_lv)
