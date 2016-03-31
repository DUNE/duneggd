#!/usr/bin/env python
'''
Subbuilder of Detector
'''

import gegede.builder
from gegede import Quantity as Q


class ECALBarrelBuilder(gegede.builder.Builder):

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, sTubeEndsToLead=Q('10cm'), **kwds):
        self.defMat    = "Air"
        self.sTubeEndsToLead  = sTubeEndsToLead
        self.ECALBarModBldr = self.get_builder('ECALBarrelMod')


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        #self.ecalOutDim    = list(self.ecalInDim)
        #self.ecalOutDim[0] = Q('3.932m') 
        #self.ecalOutDim[1] = Q('3.932m')

        # Get the ECAL Barrel Module volume and dimensions
        ecalMod_lv = self.ECALBarModBldr.get_volume('ECALBarrelMod')
        ecalModDim = list(self.ECALBarModBldr.ecalModDim)
        ecalModThick = ecalModDim[2]
        ecalModWide = ecalModDim[1]

        # Define inner barrel dimensions with stt dim and thickness
        sttBldr = self.get_builder('STT')
        sttDim = sttBldr.sttDim
        self.ecalInDim  = [ sttDim[0] + 2*self.sTubeEndsToLead,
                            sttDim[1] + 2*self.sTubeEndsToLead,
                            2*ecalModWide ]
        self.ecalOutDim = [ self.ecalInDim[0] + 2*ecalModThick, # add thickness of ecal module
                            self.ecalInDim[1] + 2*ecalModThick,
                            self.ecalInDim[2] ]


        # Define barrel as boolean, with hole to fit magnet inside
        ecalOut = geom.shapes.Box( 'ECALOut',                 dx=0.5*self.ecalOutDim[0], 
                                   dy=0.5*self.ecalOutDim[1], dz=0.5*self.ecalOutDim[2]) 
        ecalIn = geom.shapes.Box(  'ECALIn',                  dx=0.5*self.ecalInDim[0], 
                                   dy=0.5*self.ecalInDim[1],  dz=0.5*self.ecalInDim[2]) 
        ecalBarBox = geom.shapes.Boolean( self.name, type='subtraction', first=ecalOut, second=ecalIn )
        ecalBar_lv = geom.structure.Volume('vol'+self.name, material=self.defMat, shape=ecalBarBox)
        self.add_volume(ecalBar_lv)


        # Place the ECAL Modules, being mindful of rotation
        rtopup_in_ecalbarrel   = geom.structure.Position('ECALTopUp_in_'+self.name, 
                                                         '0m', 
                                                         0.5*sttDim[1] + 0.5*ecalModThick + self.sTubeEndsToLead,
                                                         -0.5*ecalModWide )
        prtopup_in_ecalbarrel  = geom.structure.Placement('placeECALTopUp_in_'+self.name,
                                                          volume = ecalMod_lv, 
                                                          pos = rtopup_in_ecalbarrel, 
                                                          rot='r90aboutX')

 
        rtopdown_in_ecalbarrel   = geom.structure.Position('ECALTopDown_in_'+self.name, 
                                                           '0m', 
                                                           0.5*sttDim[1] + 0.5*ecalModThick + self.sTubeEndsToLead, 
                                                           0.5*ecalModWide)
        prtopdown_in_ecalbarrel  = geom.structure.Placement('placeECALTopDown_in_'+self.name,
                                                            volume = ecalMod_lv, 
                                                            pos = rtopdown_in_ecalbarrel, 
                                                            rot='r90aboutX')

        
        rleftup_in_ecalbarrel   = geom.structure.Position('ECALLeftUp_in_'+self.name, 
                                                          -0.5*sttDim[0] - 0.5*ecalModThick - self.sTubeEndsToLead, 
                                                          '0m', 
                                                          -0.5*ecalModWide)
        prleftup_in_ecalbarrel  = geom.structure.Placement('placeECALLeftUp_in_'+self.name,
                                                           volume = ecalMod_lv, 
                                                           pos = rleftup_in_ecalbarrel, 
                                                           rot='r90aboutY')

 
        rleftdown_in_ecalbarrel   = geom.structure.Position('ECALLeftDown_in_'+self.name, 
                                                            -0.5*sttDim[0] - 0.5*ecalModThick - self.sTubeEndsToLead, 
                                                            '0m', 
                                                            0.5*ecalModWide)
        prleftdown_in_ecalbarrel  = geom.structure.Placement('placeECALLeftDown_in_'+self.name,
                                                             volume = ecalMod_lv, 
                                                             pos = rleftdown_in_ecalbarrel, 
                                                             rot='r90aboutY')

        
        rdownup_in_ecalbarrel   = geom.structure.Position('ECALDownUp_in_'+self.name, 
                                                          '0m', 
                                                          -0.5*sttDim[1] - 0.5*ecalModThick - self.sTubeEndsToLead, 
                                                          -0.5*ecalModWide)
        prdownup_in_ecalbarrel  = geom.structure.Placement('placeECALDownUp_in_'+self.name,
                                                           volume = ecalMod_lv, 
                                                           pos = rdownup_in_ecalbarrel, 
                                                           rot='rminus90aboutX')

 
        rdowndown_in_ecalbarrel   = geom.structure.Position('ECALDownDown_in_'+self.name, 
                                                            '0m', 
                                                            -0.5*sttDim[1] - 0.5*ecalModThick - self.sTubeEndsToLead, 
                                                            0.5*ecalModWide)
        prdowndown_in_ecalbarrel  = geom.structure.Placement('placeECALDownDown_in_'+self.name,
                                                             volume = ecalMod_lv, 
                                                             pos = rdowndown_in_ecalbarrel, 
                                                             rot='rminus90aboutX')

        
        rrightup_in_ecalbarrel   = geom.structure.Position('ECALRightUp_in_'+self.name, 
                                                           0.5*sttDim[0] + 0.5*ecalModThick + self.sTubeEndsToLead, 
                                                           '0m', 
                                                           -0.5*ecalModWide)
        prrightup_in_ecalbarrel  = geom.structure.Placement('placeECALRightUp_in_'+self.name,
                                                            volume = ecalMod_lv, 
                                                            pos = rrightup_in_ecalbarrel, 
                                                            rot='rminus90aboutY')

 
        rrightdown_in_ecalbarrel   = geom.structure.Position('ECALRightDown_in_'+self.name, 
                                                             0.5*sttDim[0] + 0.5*ecalModThick + self.sTubeEndsToLead, 
                                                             '0m', 
                                                             0.5*ecalModWide)
        prrightdown_in_ecalbarrel  = geom.structure.Placement('placeECALRightDown_in_'+self.name,
                                                              volume = ecalMod_lv, 
                                                              pos = rrightdown_in_ecalbarrel, 
                                                              rot='rminus90aboutY')


        ecalBar_lv.placements.append( prtopup_in_ecalbarrel.name )
        ecalBar_lv.placements.append( prtopdown_in_ecalbarrel.name )
        ecalBar_lv.placements.append( prleftup_in_ecalbarrel.name )
        ecalBar_lv.placements.append( prleftdown_in_ecalbarrel.name )
        ecalBar_lv.placements.append( prdownup_in_ecalbarrel.name )
        ecalBar_lv.placements.append( prdowndown_in_ecalbarrel.name )
        ecalBar_lv.placements.append( prrightup_in_ecalbarrel.name )
        ecalBar_lv.placements.append( prrightdown_in_ecalbarrel.name )

        return
