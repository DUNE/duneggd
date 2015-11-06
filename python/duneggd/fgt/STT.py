#!/usr/bin/env python
'''
Subbulder of DetEncBuilder
'''

import gegede.builder

class STTBuilder(gegede.builder.Builder):

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure( self, foilThickness='0.004cm', spacerThickness='0.025cm', 
                   nFoilsPerRadiator=60, nRadiatorModules=46, nTargetModules=36,
                   radFoilMat='C3H6', spacerMat='Fabric', targetMat='Argon', sttMat='Air', **kwds):
        self.material        = sttMat
        self.stPlaneBldr     = self.get_builder('STPlane')
        self.argonTargetBldr = self.get_builder('ArgonTargetPlane')
        self.radiatorBldr    = self.get_builder('Radiator')

        self.nTargetModules    = nTargetModules
        self.nRadiatorModules  = nRadiatorModules



    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Get subbuilder dimensions and volumes
        argonTarget_lv = self.argonTargetBldr.get_volume('volArgonTargetPlane')
        self.targetDim = self.argonTargetBldr.targetPlaneDim
        radiator_lv = self.radiatorBldr.get_volume('volRadiator')
        self.radiatorDim = self.radiatorBldr.radiatorDim
        stPlane_lv = self.stPlaneBldr.get_volume('volSTPlane')
        self.stPlaneDim = self.stPlaneBldr.stPlaneDim

        # Make STT volume -- imaginary box containing STPlanes, Targets, and Radiators
        self.sttDim = self.stPlaneBldr.stPlaneDim # get the right x and y dimensions
        self.sttDim[2] = (  self.nRadiatorModules*( self.radiatorDim[2] + self.stPlaneBldr.stPlaneDim[2] )
                          + self.nTargetModules  *( self.targetDim[2]   + self.stPlaneBldr.stPlaneDim[2] ) )
        sttBox = geom.shapes.Box(self.name, dx=self.sttDim[0], dy=self.sttDim[1], dz=self.sttDim[2])
        stt_lv = geom.structure.Volume('vol'+self.name, material=self.material, shape=sttBox)
        self.add_volume(stt_lv)




        # Place all of the STPlanes, Targets, and Radiators
        nModules = self.nRadiatorModules + self.nTargetModules

        ModuleType = []
        for i in range(nModules):
            if( i % 2 == 0 and 2*i<self.nTargetModules ): ModuleType.append('ArgonTarget')
            else: ModuleType.append('Radiator')

        zpos = -0.5*self.sttDim[2]
        for i in range(nModules):

            if  ( ModuleType[i]=='ArgonTarget' ): zpos += 0.5*self.targetDim[2]
            elif( ModuleType[i]=='Radiator'    ): zpos += 0.5*self.radiatorDim[2]

            stP_in_STT = geom.structure.Position('stPlane-'+str(i)+'_in_STT', '0cm', '0cm', zpos)
            p_stP_in_STT = geom.structure.Placement( 'place_stP-'+str(i)+'_in_STT',
                                                     volume = stPlane_lv,
                                                     pos = stP_in_STT)
            stt_lv.placements.append( p_stP_in_STT.name )
            
