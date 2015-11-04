#!/usr/bin/env python
'''
Example gegede builders for a trivial LAr geometry
'''

import gegede.builder

class STTBuilder(gegede.builder.Builder):

    def configure( self, foilThickness='0.004cm', spacerThickness='0.025cm', 
                   nFoilsPerRadiator=60, nRadiatorModules=46, nTargetModules=36,
                   radFoilMat='C3H6', spacerMat='Fabric', targetMat='Argon', sttMat='Air', **kwds):
        self.material    = sttMat
        self.stPlaneBldr = self.get_builder('STPlane')
        self.argonTargetBldr = self.get_builder('ArgonTargetPlane')
        self.nTargetModules  = nTargetModules

        self.foilThickness     = foilThickness
        self.spacerThickness   = spacerThickness
        self.nFoilsPerRadiator = nFoilsPerRadiator
        self.nRadiatorModules  = nRadiatorModules




    def construct(self, geom):

        argonTarget_lv = self.argonTargetBldr.get_volume('volArgonTargetPlane')
        self.targetDim = self.argonTargetBldr.targetPlaneDim

        self.sttDim = self.stPlaneBldr.stPlaneDim
        radThickness = self.nFoilsPerRadiator*( self.foilThickness + self.spacerThickness )
        self.sttDim[2] = (  self.nRadiatorModules*(      radThickness + self.stPlaneBldr.stPlaneDim[2] )
                          + self.nTargetModules  *( self.targetDim[2] + self.stPlaneBldr.stPlaneDim[2] ) )
        sttBox = geom.shapes.Box(self.name, dx=self.sttDim[0], dy=self.sttDim[1], dz=self.sttDim[2])
        stt_lv = geom.structure.Volume('vol'+self.name, material=self.material, shape=sttBox)
        self.add_volume(stt_lv)


        self.radFoilDim = self.stPlaneBldr.stPlaneDim
        self.radFoilDim[2] = self.foilThickness
        radFoilBox = geom.shapes.Box( 'RadiatorFoil',        dx=self.radFoilDim[0], 
                                      dy=self.radFoilDim[1], dz=self.radFoilDim[2])
        radFoil_lv = geom.structure.Volume('volRadiatorFoil', material=self.material, shape=radFoilBox)
        self.add_volume(radFoil_lv)
