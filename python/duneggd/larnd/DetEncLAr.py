#!/usr/bin/env python
'''
Subbuilder of WorldBuilder
'''

import gegede.builder
from gegede import Quantity as Q


class DetEncLArBuilder(gegede.builder.Builder):
    '''
    Build the Detector Enclosure.
    '''


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, 
                  detEncDim       = None, 
                  encBoundToDet_z = None, 
                  nModules        = [2,1,3],
                  includeMagnet   = False,
                  magThickness    = Q('50cm'),
                  **kwds):
        if detEncDim is None:
            raise ValueError("No value given for detEncDim")
        if encBoundToDet_z is None:
            raise ValueError("No value given for encBoundToDet_z")

        self.detEncMat     = 'Air'
        self.detEncDim     = detEncDim
        self.nModules      = nModules
        self.includeMagnet = includeMagnet
        self.magThickness  = magThickness

        # Space from negative face of volDetEnc to closest face of detector
        #  This positions the detector in the enclosure
        self.encBoundToDet_z = encBoundToDet_z

        self.cryoBldr  = self.get_builder('Cryostat')



    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):
        encBox = geom.shapes.Box( 'DetEnclosure',            dx=0.5*self.detEncDim[0], 
                                  dy=0.5*self.detEncDim[1],  dz=0.5*self.detEncDim[2])
        detEnc_lv = geom.structure.Volume('volDetEnclosure', material=self.detEncMat, shape=encBox)
        self.add_volume(detEnc_lv)


        cryoDim = list(self.cryoBldr.cryoDim)
        cryo_lv = self.cryoBldr.get_volume('volCryostat')


        # Define dimensions of detector. note "detDim" is grabbed by WorldBuilder
        #   so dont change the name. it is the physical dimensions of entire detector.
        self.allModsDim = [ self.nModules[0]*cryoDim[0],
                            self.nModules[1]*cryoDim[1],
                            self.nModules[2]*cryoDim[2]  ]
        self.detDim    = list(self.allModsDim)

        # If incuding magnet, need to adjust entire det dim to include magnet thickness
        if self.includeMagnet:
            self.magInDim  = list(self.detDim)
            self.magOutDim = [ self.magInDim[0],
                               self.magInDim[1] + 2*self.magThickness, 
                               self.magInDim[2] + 2*self.magThickness  ]
            self.detDim    = list(self.magOutDim)
        

        # Calculate position of detector in the enclosure
        self.encBoundToDet = [ 0.5*self.detEncDim[0] - 0.5*self.detDim[0], # x: center it for now
                               Q('0cm'),                                   # y: sit detector on floor
                               self.encBoundToDet_z ]                      # z: configure
        
        self.detCenter = [ -0.5*self.detEncDim[0] + self.encBoundToDet[0] + 0.5*self.detDim[0], 
                           -0.5*self.detEncDim[1] + self.encBoundToDet[1] + 0.5*self.detDim[1], 
                           -0.5*self.detEncDim[2] + self.encBoundToDet[2] + 0.5*self.detDim[2]  ]


        moduleNum = 0
        for x_i in range(self.nModules[0]):
            for y_i in range(self.nModules[1]):
                for z_i in range(self.nModules[2]):

                    xpos = self.detCenter[0] - 0.5*self.allModsDim[0] + (x_i+0.5)*cryoDim[0]
                    ypos = self.detCenter[1] - 0.5*self.allModsDim[1] + (y_i+0.5)*cryoDim[1]
                    zpos = self.detCenter[2] - 0.5*self.allModsDim[2] + (z_i+0.5)*cryoDim[2]

                    posName = 'Cryo-'+str(moduleNum)+'_in_Enc'
                    cryo_in_enc = geom.structure.Position(posName, xpos, ypos, zpos)
                    pC_in_E = geom.structure.Placement('place'+posName,
                                                       volume = cryo_lv,
                                                       pos = cryo_in_enc)
                    detEnc_lv.placements.append(pC_in_E.name)

                    moduleNum += 1
        

        print "DetEncLAr: Built "+str(self.nModules[0])+" wide by "+str(self.nModules[1])+" high by "+str(self.nModules[2])+" long cryostats."


        # Center the magnet around all the cryostat modules
        if self.includeMagnet:        
            magOut = geom.shapes.Box( 'MagOut',                 dx=0.5*self.magOutDim[0], 
                                      dy=0.5*self.magOutDim[1], dz=0.5*self.magOutDim[2]) 
            magIn = geom.shapes.Box(  'MagIn',                  dx=0.5*self.magInDim[0], 
                                      dy=0.5*self.magInDim[1],  dz=0.5*self.magInDim[2]) 
            magBox = geom.shapes.Boolean( 'Magnet', type='subtraction', first=magOut, second=magIn ) 
            mag_lv = geom.structure.Volume('volMagnet', material='Steel', shape=magBox)
            mag_in_enc = geom.structure.Position('Mag_in_Enc', 
                                                 self.detCenter[0], 
                                                 self.detCenter[1], 
                                                 self.detCenter[2])
            pmag_in_E  = geom.structure.Placement('placeMag_in_Enc',
                                                  volume = mag_lv,
                                                  pos = mag_in_enc)
            detEnc_lv.placements.append(pmag_in_E.name)
            
