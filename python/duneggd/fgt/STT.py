#!/usr/bin/env python
'''
Subbulder of DetEncBuilder
'''

import gegede.builder
from gegede import Quantity as Q

class STTBuilder(gegede.builder.Builder):

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure( self, config='cdr', 
                   nRadiatorModules=75,
                   FeTar_z = ('1mm'), CaTar_z = ('7mm'), 
                   CTar_z = ('4mm'), # this default bogus
                   radiatorMod_z=Q('76mm'), stt_z=Q('6.4m'), xxyyMod_z=Q('62mm'),
                   sttMat='Air', **kwds):
        self.config          = config
        self.sttMat          = sttMat
        self.stPlaneTarBldr  = self.get_builder('STPlaneTarget')
        self.stPlaneRadBldr  = self.get_builder('STPlaneRadiator')
        self.argonTargetBldr = self.get_builder('TargetPlaneArgon')
        self.emptyArTargetBldr = self.get_builder('EmptyTargetPlaneArgon')
        self.radiatorBldr    = self.get_builder('Radiator')

        self.nRadiatorModules  = nRadiatorModules
           # 4 radiators and 2 st planes per radiator module
        self.radiatorMod_z     = radiatorMod_z
        self.xxyyMod_z         = xxyyMod_z
        self.stt_z             = stt_z
        self.FeTar_z           = FeTar_z
        self.CaTar_z           = CaTar_z
        self.CTar_z            = CTar_z


        self.printZpos = False



    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Get subbuilder dimensions and volumes
        self.emptyArTarget_lv = self.emptyArTargetBldr.get_volume('volEmptyTargetPlaneArgon')
        self.argonTarget_lv   = self.argonTargetBldr.get_volume('volTargetPlaneArgon')
        self.targetArDim      = self.argonTargetBldr.targetPlaneDim
        self.radiator_lv      = self.radiatorBldr.get_volume('volRadiator')
        self.radiatorDim      = self.radiatorBldr.radiatorDim
        self.stPlaneTar_lv    = self.stPlaneTarBldr.get_volume('volSTPlaneTarget')
        self.stPlaneDim       = self.stPlaneTarBldr.stPlaneDim 
        # assume both types of planes have the same dimensions
        self.stPlaneRad_lv    = self.stPlaneRadBldr.get_volume('volSTPlaneRadiator')


        # Make various targets that are not Ar
        FeTarBox = geom.shapes.Box( 'FeTarget',                dx=0.5*self.stPlaneDim[0], 
                                    dy=0.5*self.stPlaneDim[1], dz=0.5*self.FeTar_z)
        CaTarBox = geom.shapes.Box( 'CaTarget',                dx=0.5*self.stPlaneDim[0], 
                                    dy=0.5*self.stPlaneDim[1], dz=0.5*self.CaTar_z)
        CTarBox  = geom.shapes.Box( 'CTarget',                 dx=0.5*self.stPlaneDim[0], 
                                    dy=0.5*self.stPlaneDim[1], dz=0.5*self.CTar_z)
        self.FeTarget_lv = geom.structure.Volume('volFeTarget', material='Iron',     shape=FeTarBox)
        self.CaTarget_lv = geom.structure.Volume('volCaTarget', material='Calcium',  shape=CaTarBox)
        self.CTarget_lv  = geom.structure.Volume('volCTarget',  material='Graphite', shape=CTarBox)


        # Calculate target module dimensions
        self.targetArMod_z = self.targetArDim[2] + self.xxyyMod_z
        self.targetFeMod_z = self.FeTar_z        + self.xxyyMod_z
        self.targetCaMod_z = self.CaTar_z        + self.xxyyMod_z
        self.targetCMod_z  = self.CTar_z         + self.xxyyMod_z


        # Make STT volume -- imaginary box containing STPlanes, Targets, and Radiators
        self.sttDim  = [ self.stPlaneDim[1], self.stPlaneDim[1], # assume stPlane larger in y than x
                         self.targetFeMod_z
                         + self.targetArMod_z 
                         + self.targetCaMod_z
                         + 2*self.targetCMod_z
                         + self.nRadiatorModules*self.radiatorMod_z ]

        print 'STTBuilder: set STT z dimension to '+str(self.sttDim[2])+' (configured as '+str(self.stt_z)+')'
        sttBox = geom.shapes.Box( self.name, 
                                  dx=0.5*self.sttDim[0], 
                                  dy=0.5*self.sttDim[1], 
                                  dz=0.5*self.sttDim[2])
        self.stt_lv = geom.structure.Volume('vol'+self.name, material=self.sttMat, shape=sttBox)
        self.add_volume(self.stt_lv)



        # Begin placing in STT, use zpos to zip through every position
        zpos = -0.5*self.sttDim[2]
        mod_i = 0


        if self.config=='cdr':
            # Fe target and subsequent XXYY planes
            zpos += 0.5*self.targetFeMod_z
            self.place_TargetModule(geom, mod_i, zpos, 'Iron')
            zpos += 0.5*self.targetFeMod_z
            mod_i+=1
            
            # Ar target
            zpos += 0.5*self.targetArMod_z
            self.place_TargetModule(geom, mod_i, zpos, 'Argon')
            zpos += 0.5*self.targetArMod_z
            mod_i+=1
            
            # Ca target and subsequent XXYY planes
            zpos += 0.5*self.targetCaMod_z
            self.place_TargetModule(geom, mod_i, zpos, 'Calcium')
            zpos += 0.5*self.targetCaMod_z
            mod_i+=1
            
            # 2 graphite targets and subsequent XXYY planes
            for i in range(2):
                zpos += 0.5*self.targetCMod_z
                self.place_TargetModule(geom, mod_i, zpos, 'Carbon')
                zpos += 0.5*self.targetCMod_z
                mod_i+=1

        elif self.config=='ArOptimized':
            self.nRadiatorModules -= 2
            print('STTBuilder: ArOptimized mode: subtracting 2 radiator modules to fit extra Ar targets')

            # Ca target and subsequent XXYY planes
            zpos += 0.5*self.targetCaMod_z
            self.place_TargetModule(geom, mod_i, zpos, 'Calcium')
            zpos += 0.5*self.targetCaMod_z
            mod_i+=1

            # 3 Ar targets
            for i in range(3):
                zpos += 0.5*self.targetArMod_z
                self.place_TargetModule(geom, mod_i, zpos, 'Argon')
                zpos += 0.5*self.targetArMod_z
                mod_i+=1
                
            # one empty Ar target for carbon subtraction
            zpos += 0.5*self.targetArMod_z
            self.place_TargetModule(geom, mod_i, zpos, 'EmptyArgon')
            zpos += 0.5*self.targetArMod_z
            mod_i+=1


        else:
            print('No configuration for string: '+self.config)

        # Place all of the subsequent radiator modules
        for i in range(self.nRadiatorModules):
            zpos += 0.5*self.radiatorMod_z
            self.place_RadiatorModule(geom, mod_i, zpos)
            zpos += 0.5*self.radiatorMod_z
            mod_i+=1

        return



    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def place_TargetModule(self, g, i, z, tarType):

        if(  tarType=='Iron' ): 
            tar_lv = self.FeTarget_lv
            tarMod_z  = self.targetFeMod_z
            tar_z     = self.FeTar_z
        elif(tarType=='Argon'): 
            tar_lv = self.argonTarget_lv
            tarMod_z  = self.targetArMod_z
            tar_z     = self.targetArDim[2]
        elif(tarType=='EmptyArgon'): 
            tar_lv = self.emptyArTarget_lv
            tarMod_z  = self.targetArMod_z
            tar_z     = self.targetArDim[2]
        elif(tarType=='Calcium'):
            tar_lv = self.CaTarget_lv
            tarMod_z  = self.targetCaMod_z
            tar_z     = self.CaTar_z
        elif(tarType=='Carbon'):
            tar_lv = self.CTarget_lv
            tarMod_z  = self.targetCMod_z
            tar_z     = self.CTar_z

        T_in_STT  = g.structure.Position(tarType+'Target-'+str(i)+'_in_STT', 
                                         '0cm', '0cm', 
                                         z - 0.5*tarMod_z + 0.5*tar_z )
        pT_in_STT = g.structure.Placement( 'place'+tarType+'Target-'+str(i)+'_in_STT',
                                           volume = tar_lv,
                                           pos = T_in_STT)
        self.stt_lv.placements.append( pT_in_STT.name )

        # Position the 2 stPlanes, 
        #   assume the downstream one is vertical (Y) and upstream horizontal (X)

        # each x and y plane has some amount of supporting material on both sides
        #  | |XX| || |YY| |
        #  | |XX| || |YY| |
        #  | |XX| || |YY| |
        #  | |XX| || |YY| |
        #   ^    ^  ^    ^  -- space (extra material)
        #      ^       ^    -- STPlanes
        space = 0.25*(self.xxyyMod_z - 2*self.stPlaneDim[2])

        z_up   = z + 0.5*tarMod_z - 1.5*self.stPlaneDim[2] - 3*space
        z_down = z + 0.5*tarMod_z - 0.5*self.stPlaneDim[2] - 1*space
        self.place_STPlanes_XXYY(g, 2*i, z_up, z_down, self.stPlaneTar_lv)

        return


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

        return


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

        if(self.printZpos):
            print "plane "+str(j)+": "+str(z_up)
            print "plane "+str(j+1)+": "+str(z_down)

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
        
        return
