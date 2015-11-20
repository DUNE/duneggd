#!/usr/bin/env python
'''
Subbulder of DetEncBuilder
'''

import gegede.builder
from gegede import Quantity as Q

class STTBuilder(gegede.builder.Builder):

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure( self, nRadiatorModules=46, nTargetModules=36, 
                   radiatorMod_z=Q("76mm"), sttMat='Air', **kwds):
        self.sttMat          = sttMat
        self.stPlaneTarBldr  = self.get_builder('STPlaneTarget')
        self.stPlaneRadBldr  = self.get_builder('STPlaneRadiator')
        self.argonTargetBldr = self.get_builder('TargetPlaneArgon')
        self.radiatorBldr    = self.get_builder('Radiator')

        self.nTargetModules    = nTargetModules
        self.nRadiatorModules  = nRadiatorModules
        # There are 4 radiators and 2 st planes per mod
        self.radiatorMod_z     = radiatorMod_z

        self.printZpos = False



    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Get subbuilder dimensions and volumes
        self.argonTarget_lv  = self.argonTargetBldr.get_volume('volTargetPlaneArgon')
        self.targetDim       = self.argonTargetBldr.targetPlaneDim
        self.radiator_lv     = self.radiatorBldr.get_volume('volRadiator')
        self.radiatorDim     = self.radiatorBldr.radiatorDim
        self.stPlaneTar_lv   = self.stPlaneTarBldr.get_volume('volSTPlaneTarget')
        self.stPlaneDim      = self.stPlaneTarBldr.stPlaneDim 
        # assume both types of planes have the same dimensions
        self.stPlaneRad_lv   = self.stPlaneRadBldr.get_volume('volSTPlaneRadiator')


        # Make STT volume -- imaginary box containing STPlanes, Targets, and Radiators
        self.targetMod_z = self.targetDim[2] + 2*self.stPlaneDim[2]
        self.sttDim      = [ self.stPlaneDim[1], self.stPlaneDim[1], # assume stPlane larger in y than x
                             self.nRadiatorModules*self.radiatorMod_z + self.nTargetModules*self.targetMod_z ]
        print 'STTBuilder: set STT z dimension to '+str(self.sttDim[2])
        sttBox = geom.shapes.Box( self.name, 
                                  dx=0.5*self.sttDim[0], 
                                  dy=0.5*self.sttDim[1], 
                                  dz=0.5*self.sttDim[2])
        self.stt_lv = geom.structure.Volume('vol'+self.name, material=self.sttMat, shape=sttBox)
        self.add_volume(self.stt_lv)


        # Place all of the STPlanes, Targets, and Radiators
        nModules = self.nRadiatorModules + self.nTargetModules

        # For now arbitrarily order the module type, later do in cfg
        ModuleType = []
        for i in range(nModules):
            if( i % 2 == 0 and 0.5*i<self.nTargetModules ): ModuleType.append('ArgonTarget')
            else: ModuleType.append('Radiator')

        zpos = -0.5*self.sttDim[2]
        for i in range(nModules):

            #if(self.printZpos): print "Module "+str(i)+": "+ModuleType[i]

            if  ( ModuleType[i]=='ArgonTarget' ): 
                zpos += 0.5*self.targetMod_z
                self.place_TargetModule(geom, i, zpos, 'Argon')
                zpos += 0.5*self.targetMod_z
            elif( ModuleType[i]=='Radiator'    ): 
                zpos += 0.5*self.radiatorMod_z
                self.place_RadiatorModule(geom, i, zpos)
                zpos += 0.5*self.radiatorMod_z



    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def place_TargetModule(self, g, i, z, tarType):

        if(tarType=='Argon'): tar_lv = self.argonTarget_lv

        T_in_STT  = g.structure.Position(tarType+'Target-'+str(i)+'_in_STT', 
                                         '0cm', '0cm', 
                                         z - 0.5*self.targetMod_z + 0.5*self.targetDim[2] )
        pT_in_STT = g.structure.Placement( 'place'+tarType+'Target-'+str(i)+'_in_STT',
                                           volume = tar_lv,
                                           pos = T_in_STT)
        self.stt_lv.placements.append( pT_in_STT.name )

        # Position the 2 stPlanes, 
        #   assume the downstream one is vertical (Y) and upstream horizontal (X)

        z_up   = z + 0.5*self.targetMod_z - 1.5*self.stPlaneDim[2]
        z_down = z + 0.5*self.targetMod_z - 0.5*self.stPlaneDim[2]
        self.place_STPlanes_XXYY(g, 2*i, z_up, z_down, self.stPlaneTar_lv)



    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def place_RadiatorModule(self, g, i, z):
        
        upstream_z   = z - 0.5*self.radiatorMod_z
        downstream_z = z + 0.5*self.radiatorMod_z

        # Position the 4 radiators around radiator module z center
        R0_in_STT  = g.structure.Position('Radiator-'+str(2*i)+'-0_in_STT', 
                                          '0cm', '0cm', 
                                          upstream_z + 0.5*self.radiatorDim[2] )
        R1_in_STT  = g.structure.Position('Radiator-'+str(2*i)+'-1_in_STT', 
                                          '0cm', '0cm', 
                                          upstream_z + 1.5*self.radiatorDim[2] + self.stPlaneDim[2] )
        R2_in_STT  = g.structure.Position('Radiator-'+str(2*i+1)+'-2_in_STT', 
                                          '0cm', '0cm', 
                                          downstream_z - 0.5*self.radiatorDim[2])
        R3_in_STT  = g.structure.Position('Radiator-'+str(2*i+1)+'-3_in_STT', 
                                          '0cm', '0cm', 
                                          downstream_z - 1.5*self.radiatorDim[2] - self.stPlaneDim[2] )


        # Position the X (up) and Y (down) st planes
        z_up   = upstream_z   + self.radiatorDim[2] + 0.5*self.stPlaneDim[2]
        z_down = downstream_z - self.radiatorDim[2] - 0.5*self.stPlaneDim[2]
        self.place_STPlanes_XXYY(g, 2*i, z_up, z_down, self.stPlaneRad_lv)


        # Place everything in the STT 
        pR0_in_STT = g.structure.Placement( 'placeRadiator-'+str(2*i)+'-0_in_STT',
                                            volume = self.radiator_lv, pos = R0_in_STT)

        pR1_in_STT = g.structure.Placement( 'placeRadiator-'+str(2*i)+'-1_in_STT',
                                            volume = self.radiator_lv, pos = R1_in_STT)
        
        pR2_in_STT = g.structure.Placement( 'placeRadiator-'+str(2*i+1)+'-2_in_STT',
                                            volume = self.radiator_lv, pos = R2_in_STT)

        pR3_in_STT = g.structure.Placement( 'placeRadiator-'+str(2*i+1)+'-3_in_STT',
                                            volume = self.radiator_lv, pos = R3_in_STT)
        self.stt_lv.placements.append( pR0_in_STT.name )
        self.stt_lv.placements.append( pR1_in_STT.name )
        self.stt_lv.placements.append( pR2_in_STT.name )
        self.stt_lv.placements.append( pR3_in_STT.name )




    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def place_STPlanes_XXYY(self, g, j, z_up, z_down, stPlane_lv):

        # Position the 2 stPlanes, 
        #   assume the downstream one is vertical (Y) and upstream horizontal (X)
        stPX_in_STT   = g.structure.Position('stPlane-'+str(j)+'-X_in_STT', 
                                             '0cm', '0cm', 
                                             z_up)
        stPY_in_STT   = g.structure.Position('stPlane-'+str(j+1)+'-Y_in_STT', 
                                             '0cm', '0cm', 
                                             z_down)
        
        #print "plane "+str(j)+": "+str(z_up)
        #print "plane "+str(j+1)+": "+str(z_down)

        # stPlane defined with tubes vertical by default. 
        # Rotate X plany around z to get horizontal tubes
        p_stPX_in_STT = g.structure.Placement( 'place_stP-'+str(j)+'-X_in_STT',
                                               volume = stPlane_lv,
                                               pos = stPX_in_STT, 
                                               rot = "r90aboutZ")
        p_stPY_in_STT = g.structure.Placement( 'place_stP-'+str(j+1)+'-Y_in_STT',
                                               volume = stPlane_lv,
                                               pos = stPY_in_STT)
        self.stt_lv.placements.append( p_stPX_in_STT.name )
        self.stt_lv.placements.append( p_stPY_in_STT.name )
