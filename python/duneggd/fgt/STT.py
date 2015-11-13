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

        self.printZpos = False



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
        self.sttDim = list(self.stPlaneTarBldr.stPlaneDim) # get the right x and y dimensions
        self.sttDim[2] = (  self.nRadiatorModules*( self.radiatorDim[2] + self.stPlaneDim[2] )
                          + self.nTargetModules  *( self.targetDim[2]   + self.stPlaneDim[2] ) )
        sttBox = geom.shapes.Box( self.name, 
                                  dx=0.5*self.sttDim[0], 
                                  dy=0.5*self.sttDim[1], 
                                  dz=0.5*self.sttDim[2])
        stt_lv = geom.structure.Volume('vol'+self.name, material=self.sttMat, shape=sttBox)
        self.add_volume(stt_lv)


        # Place all of the STPlanes, Targets, and Radiators
        nModules = self.nRadiatorModules + self.nTargetModules

        # For now arbitrarily order the module type, later do in cfg
        ModuleType = []
        for i in range(nModules):
            if( i % 2 == 0 and 2*i<self.nTargetModules ): ModuleType.append('ArgonTarget')
            else: ModuleType.append('Radiator')

        zpos = -0.5*self.sttDim[2]
        for i in range(nModules):

            if(self.printZpos): print "Module "+str(i)+": "+ModuleType[i]

            if  ( ModuleType[i]=='ArgonTarget' ): 
                zpos += 0.5*self.targetDim[2]
                if(self.printZpos): print "  Target Plane z: "+str(zpos)
                stplanevol = stPlaneTar_lv
                T_in_STT  = geom.structure.Position('ArgonTarget-'+str(i)+'_in_STT', '0cm', '0cm', zpos)
                pT_in_STT = geom.structure.Placement( 'placeArgonTarget-'+str(i)+'_in_STT',
                                                      volume = argonTarget_lv,
                                                      pos = T_in_STT)
                stt_lv.placements.append( pT_in_STT.name )
                if(self.printZpos): print "    shifting "+str(0.5*( self.targetDim[2]   + self.stPlaneDim[2] ))
                zpos += 0.5*( self.targetDim[2]   + self.stPlaneDim[2] ) # move it to STPlane center
                if(self.printZpos): print "      ST Plane z: "+str(zpos)

    
            elif( ModuleType[i]=='Radiator'    ): 
                zpos += 0.5*self.radiatorDim[2]
                if(self.printZpos): print "  Rad Plane z: "+str(zpos)
                stplanevol = stPlaneRad_lv
                R_in_STT  = geom.structure.Position('Radiator-'+str(i)+'_in_STT', '0cm', '0cm', zpos)
                pR_in_STT = geom.structure.Placement( 'placeRadiator-'+str(i)+'_in_STT',
                                                      volume = radiator_lv,
                                                      pos = R_in_STT)
                stt_lv.placements.append( pR_in_STT.name )
                if(self.printZpos): print "    shifting "+str(0.5*( self.radiatorDim[2] + self.stPlaneDim[2] ))
                zpos += 0.5*( self.radiatorDim[2] + self.stPlaneDim[2] ) # move it to STPlane center
                if(self.printZpos): print "   ST Plane z: "+str(zpos)

            stP_in_STT   = geom.structure.Position('stPlane-'+str(i)+'_in_STT', '0cm', '0cm', zpos)
            p_stP_in_STT = geom.structure.Placement( 'place_stP-'+str(i)+'_in_STT',
                                                     volume = stplanevol,
                                                     pos = stP_in_STT)
            stt_lv.placements.append( p_stP_in_STT.name )
