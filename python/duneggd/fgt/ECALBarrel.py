#!/usr/bin/env python
'''
Subbuilder of Detector
'''

import gegede.builder
from gegede import Quantity as Q


class ECALBarrelBuilder(gegede.builder.Builder):

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, ecalInDim=None, **kwds):
        if ecalInDim is None:
            raise ValueError("No value given for ecalInDim")

        self.defMat    = "Air"
        self.ecalInDim  = ecalInDim
        self.ECALBarModBldr = self.get_builder('ECALBarMod')


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):


        # Just like in the ECALEndBuilder, calculate outer dimensions 
        #  using other configured parameters: number of planes, thicknesses...
        # For now I'm using the CDR reported dimensions:
        self.ecalOutDim    = list(self.ecalInDim)
        # For now I am hard-coding the values of the ecalOutDim[0] and ecalOutDim[1]. Need to calculate it more thorughly.
        self.ecalOutDim[0] = Q('3.932m') 
        self.ecalOutDim[1] = Q('3.932m')


        # Define barrel as boolean, with hole to fit magnet inside
        ecalOut = geom.shapes.Box( 'ECALOut',                 dx=0.5*self.ecalOutDim[0], 
                                   dy=0.5*self.ecalOutDim[1], dz=0.5*self.ecalOutDim[2]) 
        ecalIn = geom.shapes.Box(  'ECALIn',                  dx=0.5*self.ecalInDim[0], 
                                   dy=0.5*self.ecalInDim[1],  dz=0.5*self.ecalInDim[2]) 
        ecalBarBox = geom.shapes.Boolean( self.name, type='subtraction', first=ecalOut, second=ecalIn )
        ecalBar_lv = geom.structure.Volume('vol'+self.name, material=self.defMat, shape=ecalBarBox)
        self.add_volume(ecalBar_lv)


        # Get the ECAL Barrel  Module volumes
        ecalMod_lv = self.ECALBarModBldr.get_volume('ECALBarMod')
                
        # Place the ECAL Modules, being mindful of rotation
        rtopup_in_ecalbarrel   = geom.structure.Position('ECALTopUp_in_'+self.name, 
                                                         '0m', '1.858m', '-1.6m') # y: (3.5m + 21.6cm)/2 z: -(3.2m)/2 
        prtopup_in_ecalbarrel  = geom.structure.Placement('placeECALTopUp_in_'+self.name,
                                                          volume = ecalMod_lv, 
                                                          pos = rtopup_in_ecalbarrel, rot='r90aboutX')
        ecalBar_lv.placements.append( prtopup_in_ecalbarrel.name )
 
        rtopdown_in_ecalbarrel   = geom.structure.Position('ECALTopDown_in_'+self.name, 
                                                           '0m', '1.858m', '1.6m')
        prtopdown_in_ecalbarrel  = geom.structure.Placement('placeECALTopDown_in_'+self.name,
                                                            volume = ecalMod_lv, 
                                                            pos = rtopdown_in_ecalbarrel, rot='r90aboutX')
        ecalBar_lv.placements.append( prtopdown_in_ecalbarrel.name )
        
        rleftup_in_ecalbarrel   = geom.structure.Position('ECALLeftUp_in_'+self.name, 
                                                          '-1.858m', '0m', '-1.6m')
        prleftup_in_ecalbarrel  = geom.structure.Placement('placeECALLeftUp_in_'+self.name,
                                                          volume = ecalMod_lv, 
                                                          pos = rleftup_in_ecalbarrel, rot='r90aboutY')
        ecalBar_lv.placements.append( prleftup_in_ecalbarrel.name )
 
        rleftdown_in_ecalbarrel   = geom.structure.Position('ECALLeftDown_in_'+self.name, 
                                                            '-1.858m', '0m', '1.6m')
        prleftdown_in_ecalbarrel  = geom.structure.Placement('placeECALLeftDown_in_'+self.name,
                                                            volume = ecalMod_lv, 
                                                            pos = rleftdown_in_ecalbarrel, rot='r90aboutY')
        ecalBar_lv.placements.append( prleftdown_in_ecalbarrel.name )
        
        rdownup_in_ecalbarrel   = geom.structure.Position('ECALDownUp_in_'+self.name, 
                                                         '0m', '-1.858m', '-1.6m')
        prdownup_in_ecalbarrel  = geom.structure.Placement('placeECALDownUp_in_'+self.name,
                                                          volume = ecalMod_lv, 
                                                          pos = rdownup_in_ecalbarrel, rot='rminus90aboutX')
        ecalBar_lv.placements.append( prdownup_in_ecalbarrel.name )
 
        rdowndown_in_ecalbarrel   = geom.structure.Position('ECALDownDown_in_'+self.name, 
                                                           '0m', '-1.858m', '1.6m')
        prdowndown_in_ecalbarrel  = geom.structure.Placement('placeECALDownDown_in_'+self.name,
                                                            volume = ecalMod_lv, 
                                                            pos = rdowndown_in_ecalbarrel, rot='rminus90aboutX')
        ecalBar_lv.placements.append( prdowndown_in_ecalbarrel.name )
        
        rrightup_in_ecalbarrel   = geom.structure.Position('ECALRightUp_in_'+self.name, 
                                                          '1.858m', '0m', '-1.6m')
        prrightup_in_ecalbarrel  = geom.structure.Placement('placeECALRightUp_in_'+self.name,
                                                          volume = ecalMod_lv, 
                                                          pos = rrightup_in_ecalbarrel, rot='rminus90aboutY')
        ecalBar_lv.placements.append( prrightup_in_ecalbarrel.name )
 
        rrightdown_in_ecalbarrel   = geom.structure.Position('ECALRightDown_in_'+self.name, 
                                                            '1.858m', '0m', '1.6m')
        prrightdown_in_ecalbarrel  = geom.structure.Placement('placeECALRightDown_in_'+self.name,
                                                            volume = ecalMod_lv, 
                                                            pos = rrightdown_in_ecalbarrel, rot='rminus90aboutY')
        ecalBar_lv.placements.append( prrightdown_in_ecalbarrel.name )
        return
