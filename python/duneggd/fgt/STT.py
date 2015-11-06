#!/usr/bin/env python
'''
Subbulder of DetEncBuilder
'''

import gegede.builder

class STTBuilder(gegede.builder.Builder):

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure( self, nRadiatorModules=46, nTargetModules=36, sttMat='Air', **kwds):
        self.sttMat          = sttMat
        self.stPlaneTarBldr  = self.get_builder('STPlaneTarget')
        self.stPlaneRadBldr  = self.get_builder('STPlaneRadiator')
        self.argonTargetBldr = self.get_builder('TargetPlaneArgon')
        self.radiatorBldr    = self.get_builder('Radiator')

        self.nTargetModules    = nTargetModules
        self.nRadiatorModules  = nRadiatorModules



    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Get subbuilder dimensions and volumes
        argonTarget_lv   = self.argonTargetBldr.get_volume('volTargetPlaneArgon')
        self.targetDim   = self.argonTargetBldr.targetPlaneDim
        radiator_lv      = self.radiatorBldr.get_volume('volRadiator')
        self.radiatorDim = self.radiatorBldr.radiatorDim
        stPlaneTar_lv    = self.stPlaneTarBldr.get_volume('volSTPlaneTarget')
        self.stPlaneDim  = self.stPlaneTarBldr.stPlaneDim 
        # assume both types of planes have the same dimensions
        stPlaneRad_lv    = self.stPlaneRadBldr.get_volume('volSTPlaneRadiator')

        # Make STT volume -- imaginary box containing STPlanes, Targets, and Radiators
        self.sttDim = self.stPlaneTarBldr.stPlaneDim # get the right x and y dimensions
        self.sttDim[2] = (  self.nRadiatorModules*( self.radiatorDim[2] + self.stPlaneDim[2] )
                          + self.nTargetModules  *( self.targetDim[2]   + self.stPlaneDim[2] ) )
        sttBox = geom.shapes.Box(self.name, dx=self.sttDim[0], dy=self.sttDim[1], dz=self.sttDim[2])
        stt_lv = geom.structure.Volume('vol'+self.name, material=self.sttMat, shape=sttBox)
        self.add_volume(stt_lv)




        # Place all of the STPlanes, Targets, and Radiators
        nModules = self.nRadiatorModules + self.nTargetModules

        ModuleType = []
        for i in range(nModules):
            if( i % 2 == 0 and 2*i<self.nTargetModules ): ModuleType.append('ArgonTarget')
            else: ModuleType.append('Radiator')

        zpos = -0.5*self.sttDim[2]
        for i in range(nModules):

            if  ( ModuleType[i]=='ArgonTarget' ): 
                zpos += 0.5*self.targetDim[2]
                stplanevol = stPlaneTar_lv
            elif( ModuleType[i]=='Radiator'    ): 
                zpos += 0.5*self.radiatorDim[2]
                stplanevol = stPlaneRad_lv

            stP_in_STT = geom.structure.Position('stPlane-'+str(i)+'_in_STT', '0cm', '0cm', zpos)
            p_stP_in_STT = geom.structure.Placement( 'place_stP-'+str(i)+'_in_STT',
                                                     volume = stplanevol,
                                                     pos = stP_in_STT)
            stt_lv.placements.append( p_stP_in_STT.name )
            
