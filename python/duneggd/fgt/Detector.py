#!/usr/bin/env python
'''
Subbuilder of DetEncBuilder
'''

import gegede.builder

class DetectorBuilder(gegede.builder.Builder):
    '''
    Assemble all the subsystems into one bounding box.
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, defMat = 'Air',
                  magInDim=None, magThickness='60cm', **kwds):
        if magInDim is None:
            raise ValueError("No value given for magInDim")

        self.defMat      = defMat
        self.magMat      = 'Steel'

        # dimensions of bounding box are calculated in construct

        # Get all of the detector subsystems to position and place
        self.sttBldr      = self.get_builder('STT')
        #self.ecalUpBldr   = self.get_builder('ECALUpstream')
        #self.ecalDownBldr = self.get_builder('ECALDownstream')
        #self.ecalBarBldr  = self.get_builder('ECALBarrel')
        self.muidUpBldr   = self.get_builder('MuIDUpstream')
        self.muidDownBldr = self.get_builder('MuIDDownstream')
        self.muidBarBldr  = self.get_builder('MuIDBarrel')

        # set the inner and outer magnet dimensions
        self.magInDim  = magInDim
        self.magOutDim = [  self.magInDim[0], 
                            self.magInDim[0] + 2*magThickness, 
                            self.magInDim[0] + 2*magThickness  ]

        # Set inner MuID dimensions to outer magned dimensions
        #self.muidBarBldr.muidInDim = list(self.ecalBarBldr.ecalOutDim)



    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Define magnet as boolean, with hole to fit ECAL inside
        #magBox = geom.shapes.Box( 'Magnet',                 dx=0.5*self.magOutDim[0], 
        #                          dy=0.5*self.magOutDim[1], dz=0.5*self.magOutDim[2]) 
        magOut = geom.shapes.Box( 'MagOut',                 dx=0.5*self.magOutDim[0], 
                                  dy=0.5*self.magOutDim[1], dz=0.5*self.magOutDim[2]) 
        magIn = geom.shapes.Box(  'MagIn',                  dx=0.5*self.magInDim[0], 
                                  dy=0.5*self.magInDim[1],  dz=0.5*self.magInDim[2]) 
        magBox = geom.shapes.Boolean( 'Magnet', type='Subtraction', first=magOut, second=magIn ) 
        mag_lv = geom.structure.Volume('volMagnet', material=self.magMat, shape=magBox)
        self.add_volume(mag_lv)

        
        # Get subsystem dimensions, give warnings concerning following assumptions
        sttDim      = list(self.sttBldr.sttDim)
        muidDownDim = list(self.muidDownBldr.muidDim)
        muidUpDim   = list(self.muidUpBldr.muidDim)
        muidBarOutDim  = list(self.muidBarBldr.muidOutDim)
        muidBarInDim   = list(self.muidBarBldr.muidInDim)
        muidBarDim = muidBarOutDim
        #ecalDownDim = list(self.ecalDownBldr.ecalDim)
        #ecalUpDim   = list(self.ecalUpBldr.ecalDim)
        #ecalBarDim  = list(self.ecalBarBldr.ecalDim)
        if( muidDownDim[2] == muidUpDim[2] ): 
            print "DetEncBuilder: Up and Downstream MuIDs the same thickness in beam direction"
        if(       muidDownDim[1] > muidBarDim[1] 
               or muidDownDim[2] > muidBarDim[2]
               or muidUpDim[1]   > muidBarDim[1]
               or muidUpDim[2]   > muidBarDim[2]  ): 
            print "DetEncBuilder: MuID Ends have larger xy dimensions than Barrel"


        # vol is a bounding box ~ not corresponding to physical volume.
        #  assume Barrel biggest in x and y
        #  assume no space between the z boundaries of Barrel and Ends
        self.detDim = [ muidBarDim[0], muidBarDim[1], 
                        muidUpDim[2] + muidBarDim[2] + muidDownDim[2] ]


        # Position MuID Barrel and ends.
        # Since the MuID is the outermost part of the detector... assume Barrel 
        #  is centered, with the z boundaries of the Barrel and ends touching
        muidBarPos  = [ '0cm','0cm', 
                        -0.5*self.detDim[2] + muidUpDim[2] + 0.5*muidBarDim[2] ]
        muidDownPos = [ muidBarPos[0], muidBarPos[1], # add shift parameter if there is any xy shift rel to Barrel
                        muidBarPos[2] + 0.5*muidBarDim[2] + 0.5*muidDownDim[2] ]
        muidUpPos   = [ muidBarPos[0], muidBarPos[1],
                        muidBarPos[2] - 0.5*muidBarDim[2] - 0.5*muidUpDim[2] ]


        # Position Magnet, assuming it is concentric with the MuID Barrel
        magPos      = list(muidBarPos) 


        # Position ECAL Barrel and Ends
        ecalBarPos  = list(muidBarPos)
        #ecalDownPos = [ ecalBarPos[0], ecalBarPos[1], # add shift parameter if there is any relative shift  
        #                0.5*ecalBarPos[1] + 0.5*ecalBarDim[2] + 0.5*ecalDownDim[2] ]
        #ecalUpPos   = [ ecalBarPos[0], ecalBarPos[1],
        #                0.5*ecalBarPos[1] + 0.5*ecalBarDim[2] + 0.5*ecalUpDim[2] ]


        # Position volSTT 
        sttPos = [ ecalBarPos[0], 
                   ecalBarPos[1],
                   ecalBarPos[2]  ] # need to adjust z as soon as ECAL dimensions avaliable.



        # Make detector box and place STT inside
        detBox = geom.shapes.Box( self.name,              dx=0.5*self.detDim[0], 
                                  dy=0.5*self.detDim[1],  dz=0.5*self.detDim[2])
        det_lv = geom.structure.Volume('vol'+self.name, material=self.defMat, shape=detBox)
        self.add_volume(det_lv)
        stt_lv = self.sttBldr.get_volume('volSTT')
        stt_in_det = geom.structure.Position('STT_in_Det', sttPos[0], sttPos[1], sttPos[2])
        pSTT_in_D = geom.structure.Placement('placeSTT_in_Det',
                                             volume = stt_lv,
                                             pos = stt_in_det)
        det_lv.placements.append(pSTT_in_D.name)




        # Get volMuIDDownstream, volMuIDUpstream, volMuIDBarrel,
        # and volMagnet volumes and place in volDetector
        muidDown_lv = self.muidDownBldr.get_volume('volMuIDDownstream')
        muidDown_in_det = geom.structure.Position('MuIDDown_in_Det', muidDownPos[0], muidDownPos[1], muidDownPos[2])
        pmuidDown_in_D = geom.structure.Placement('placeMuIDDown_in_Det',
                                                  volume = muidDown_lv,
                                                  pos = muidDown_in_det)
        det_lv.placements.append(pmuidDown_in_D.name)
        muidUp_lv = self.muidUpBldr.get_volume('volMuIDUpstream')
        muidUp_in_det = geom.structure.Position('MuIDUp_in_Det', muidUpPos[0], muidUpPos[1], muidUpPos[2])
        pmuidUp_in_D = geom.structure.Placement('placeMuIDUp_in_Det',
                                                volume = muidUp_lv,
                                                pos = muidUp_in_det)
        det_lv.placements.append(pmuidUp_in_D.name)
        muidBar_lv = self.muidBarBldr.get_volume('volMuIDBarrel')
        muidBar_in_det = geom.structure.Position('MuIDBar_in_Det', muidBarPos[0], muidBarPos[1], muidBarPos[2])
        pmuidBar_in_D = geom.structure.Placement('placeMuIDBar_in_Det',
                                                 volume = muidBar_lv,
                                                 pos = muidBar_in_det)
        det_lv.placements.append(pmuidBar_in_D.name)
        mag_in_det = geom.structure.Position('Mag_in_Det', magPos[0], magPos[1], magPos[2])
        pmag_in_D  = geom.structure.Placement('placeMag_in_Det',
                                              volume = mag_lv,
                                              pos = mag_in_det)
        det_lv.placements.append(pmag_in_D.name)
