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


        # Get the ECAL Module volumes
        #ecalMod_lv = self.ECALModBldr.get_volume('volecalMod')

                
        # Place the ECAL Modules, being mindful of rotation

        return
