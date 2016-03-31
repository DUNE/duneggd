#!/usr/bin/env python
'''
Subbuilder of DetEncBuilder
'''

import gegede.builder
from gegede import Quantity as Q

class DetectorBuilder(gegede.builder.Builder):
    '''
    Assemble all the subsystems into one bounding box.
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, defMat = 'Air',
                  magInDim=None, magThickness=Q('60cm'), 
                  downMuIDtoMagnet = Q('0.8m'), upMuIDtoMagnet = Q('1.15m'), **kwds):
        if magInDim is None:
            raise ValueError("No value given for magInDim")

        self.defMat      = defMat
        self.magMat      = 'Steel'

        # dimensions of bounding box are calculated in construct

        # Get all of the detector subsystems to position and place
        self.sttBldr      = self.get_builder('STT')
        self.ecalUpBldr   = self.get_builder('ECALUpstream')
        self.ecalDownBldr = self.get_builder('ECALDownstream')
        self.ecalBarBldr  = self.get_builder('BarrelECAL')
        self.muidUpBldr   = self.get_builder('MuIDUpstream')
        self.muidDownBldr = self.get_builder('MuIDDownstream')
        self.muidBarBldr  = self.get_builder('MuIDBarrel')

        # set the inner and outer magnet dimensions
        self.magInDim  = magInDim
        self.magOutDim = list(magInDim)
        self.magOutDim[1] += 2*magThickness
        self.magOutDim[2] += 2*magThickness
        self.magThickness = magThickness

        self.upMuIDtoMagnet   = upMuIDtoMagnet
        self.downMuIDtoMagnet = downMuIDtoMagnet


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):
        
        # Get subsystem dimensions, 
        sttDim      = list(self.sttBldr.sttDim)
        muidDownDim = list(self.muidDownBldr.muidDim)
        muidUpDim   = list(self.muidUpBldr.muidDim)
        muidBarOutDim  = list(self.muidBarBldr.muidOutDim)
        muidBarInDim   = list(self.muidBarBldr.muidInDim)
        muidBarDim = muidBarOutDim
        ecalDownDim = list(self.ecalDownBldr.ecalModDim)
        ecalUpDim   = list(self.ecalUpBldr.ecalModDim)
        ecalBarOutDim  = list(self.ecalBarBldr.ecalOutDim)
        ecalBarInDim   = list(self.ecalBarBldr.ecalInDim)
        ecalBarDim  = ecalBarOutDim

        # first check to see if ecal barrel fits in magnet, otherwise nudge it to fit
        # need to do this before using and magnet dimensions for positioning
        if( self.magInDim[1] < ecalBarDim[1] ):
             print "DetectorBuilder: Barrel ECAL ("+str(ecalBarDim[1])+" high) does not fit inside magnet ("+str(self.magInDim[1])+")"
             self.magInDim[1]  = ecalBarDim[1]
             self.magOutDim[1] = self.magInDim[1] + 2*self.magThickness
             print "       ... nudging magnet inner and outer height dimensions to "+str(self.magInDim[1])+" and "+str(self.magOutDim[1])
             print "       ... this affects PRC placements, which fit tightly around magnet"

        # vol is a bounding box ~ not corresponding to physical volume.
        #  assume Barrel biggest in x and y
        self.detDim    = list(muidBarDim)
        self.detDim[2] = ( muidUpDim[2] + self.upMuIDtoMagnet 
                           + muidBarDim[2] 
                           + self.downMuIDtoMagnet + muidDownDim[2] )


        # Position MuID Barrel
        # Since the MuID is the outermost part of the detector, 
        #  assume Barrel is centered in xy
        muidBarPos  = [ Q('0cm'),Q('0cm'), 
                        -0.5*self.detDim[2] + muidUpDim[2] + self.upMuIDtoMagnet + 0.5*muidBarDim[2] ]


        # Position Magnet, assuming it is concentric with the MuID Barrel
        magPos      = list(muidBarPos) 


        # Position MuID Ends around magnet
        muidDownPos = [ muidBarPos[0], muidBarPos[1], # assume centered in xy
                        magPos[2] + 0.5*self.magOutDim[2] + self.downMuIDtoMagnet + 0.5*muidDownDim[2] ]
        muidUpPos   = [ muidBarPos[0], muidBarPos[1],
                        muidBarPos[2] - 0.5*self.magOutDim[2] - self.upMuIDtoMagnet - 0.5*muidUpDim[2] ]



        # Calculate bounding box dimensions of ECAL so that ECAL/STT unit can 
        #  be centered inside of the Magnet, until spacings are better known.
        # Assume barrel is larger in x,y, while z dim is sum of stt and ECAL ends, with gap
        sttToEcal = self.ecalBarBldr.sTubeEndsToLead
        ecalBounds = [ ecalBarDim[0], 
                       ecalBarDim[1], 
                       ecalUpDim[2] + sttDim[2] + ecalDownDim[2] + 2*sttToEcal ]


        # Position volSTT
        sttPos = [ magPos[0], 
                   magPos[1],
                   magPos[2] - 0.5*ecalBounds[2] + ecalUpDim[2] + sttToEcal + 0.5*sttDim[2] ]


        # Position ECAL Barrel
        ecalBarPos    = list(sttPos)


        # Position ECAL Ends
        ecalDownPos = [ ecalBarPos[0], ecalBarPos[1], # assume centered in xy
                        sttPos[2] + 0.5*sttDim[2] + sttToEcal + 0.5*ecalDownDim[2] ]
        ecalUpPos   = [ ecalBarPos[0], ecalBarPos[1],
                        sttPos[2] - 0.5*sttDim[2] - sttToEcal - 0.5*ecalUpDim[2] ]




       #########################################################################
       ########################### Check Assumptions ###########################
        
        if( muidDownDim[2] == muidUpDim[2] ):
            print "DetectorBuilder: Up and Downstream MuIDs the same thickness in beam direction"

        # For the Boolean shapes, make sure the inner/outer dimensions match 
        #  where they should -- barrel is a "tube" in z and magnet a "tube" in x
        if( muidBarInDim[2] != muidBarOutDim[2] ):
            print "DetectorBuilder: MuID barrel not same length in z on inside and outside"
            print "     inner barrel is "+str(muidBarInDim[2])+" and outer barrel is "+str(muidBarOutDim[2])+" in z"
        if( self.magInDim[0] != self.magOutDim[0] ):
            print "DetectorBuilder: Magnet not same length in x on inside and outside"
            print "     inner magnet is "+str(self.magInDim[0])+" and outer magnet is "+str(self.magOutDim[0])+" in x"

        # The MuID barrel should tightly hug the magnet,
        #   and be the same dimension in z
        if( muidBarInDim[0] != self.magOutDim[0] ):
            print "DetectorBuilder: MuID barrel not touching magnet in x"
            print "     inner barrel is "+str(muidBarInDim[0])+" and magnet is "+str(self.magOutDim[0])+" in x"
        if( muidBarInDim[1] != self.magOutDim[1] ):
            print "DetectorBuilder: MuID barrel not touching magnet in y"
            print "     inner barrel is "+str(muidBarInDim[1])+" and outer magnet is "+str(self.magOutDim[1])+" in y"
        if( muidBarInDim[2] != self.magOutDim[2] ):
            print "DetectorBuilder: MuID barrel not same length in z as magnet"
            print "     barrel is "+str(muidBarInDim[2])+" and outer magnet is "+str(self.magOutDim[2])+" in z"

        # Check that the ECAL, positioned tightly around the STT, fits
        #   inside the inner dimensions of the magnet.
        if( (ecalUpPos[2] - 0.5*ecalUpDim[2]) < (magPos[2] - 0.5*self.magInDim[2]) ):
            print "DetectorBuilder: Upstream ECAL upstream z face ("+str(ecalUpPos[2] - 0.5*ecalUpDim[2])+") overlaps magnet ("+str(magPos[2] - 0.5*self.magInDim[2])+")"
            print "      ... downstream ECAL downstream face is "+str(magPos[2] + 0.5*self.magInDim[2] - (ecalDownPos[2] + 0.5*ecalDownDim[2]))+" away from magnet"
        if( (ecalDownPos[2] + 0.5*ecalDownDim[2]) > (magPos[2] + 0.5*self.magInDim[2]) ):
            print "DetectorBuilder: Downstream ECAL downstream z face ("+str(ecalDownPos[2] + 0.5*ecalDownDim[2])+") overlaps magnet ("+str(magPos[2] + 0.5*self.magInDim[2])+")"
            print "      ... upstream ECAL upstream face is "+str(ecalUpPos[2] - 0.5*ecalUpDim[2] - (magPos[2] - 0.5*self.magInDim[2]))+" away from magnet"
        if( self.magInDim[2] < ecalUpDim[2] + sttDim[2] + ecalDownDim[2] ):
            print "DetectorBuilder: STT+ECAL ends ("+str(ecalUpDim[2] + sttDim[2] + ecalDownDim[2])+") do not fit inside magnet ("+str(self.magInDim[2])+")"
 
        if(       muidDownDim[1] > muidBarDim[1] 
               or muidDownDim[2] > muidBarDim[2]
               or muidUpDim[1]   > muidBarDim[1]
               or muidUpDim[2]   > muidBarDim[2]  ):
            print "DetectorBuilder: MuID Ends have larger xy dimensions than Barrel"

        ############################ Finish Checking ############################
        #########################################################################




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
        #   volumes and place in volDetector
        muidDown_lv = self.muidDownBldr.get_volume('volMuIDDownstream')
        muidDown_in_det = geom.structure.Position('MuIDDown_in_Det', muidDownPos[0], muidDownPos[1], muidDownPos[2])
        pmuidDown_in_D = geom.structure.Placement('placeMuIDDown_in_Det',
                                                  volume = muidDown_lv,
                                                  pos = muidDown_in_det,
                                                  rot = "r180aboutY")
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



        # Define magnet as boolean, with hole to fit ECAL inside, place it
        magOut = geom.shapes.Box( 'MagOut',                 dx=0.5*self.magOutDim[0], 
                                  dy=0.5*self.magOutDim[1], dz=0.5*self.magOutDim[2]) 
        magIn = geom.shapes.Box(  'MagIn',                  dx=0.5*self.magInDim[0], 
                                  dy=0.5*self.magInDim[1],  dz=0.5*self.magInDim[2]) 
        magBox = geom.shapes.Boolean( 'Magnet', type='subtraction', first=magOut, second=magIn ) 
        mag_lv = geom.structure.Volume('volMagnet', material=self.magMat, shape=magBox)
        self.add_volume(mag_lv)
        mag_in_det = geom.structure.Position('Mag_in_Det', magPos[0], magPos[1], magPos[2])
        pmag_in_D  = geom.structure.Placement('placeMag_in_Det',
                                              volume = mag_lv,
                                              pos = mag_in_det)
        det_lv.placements.append(pmag_in_D.name)



        # Get volECALDownstream, volECALUpstream, volECALBarrel volumes and place in volDetector
        ecalDown_lv = self.ecalDownBldr.get_volume('volECALDownstream')
        ecalDown_in_det = geom.structure.Position('ECALDown_in_Det', ecalDownPos[0], ecalDownPos[1], ecalDownPos[2])
        pecalDown_in_D = geom.structure.Placement('placeECALDown_in_Det',
                                                  volume = ecalDown_lv,
                                                  pos = ecalDown_in_det)
        det_lv.placements.append(pecalDown_in_D.name)
        ecalUp_lv = self.ecalUpBldr.get_volume('volECALUpstream')
        ecalUp_in_det = geom.structure.Position('ECALUp_in_Det', ecalUpPos[0], ecalUpPos[1], ecalUpPos[2])
        pecalUp_in_D = geom.structure.Placement('placeECALUp_in_Det',
                                                volume = ecalUp_lv,
                                                pos = ecalUp_in_det,
                                                rot='r180aboutY')
        det_lv.placements.append(pecalUp_in_D.name)
        
        ecalBar_lv = self.ecalBarBldr.get_volume('volBarrelECAL')
        ecalBar_in_det = geom.structure.Position('ECALBar_in_Det', ecalBarPos[0], ecalBarPos[1], ecalBarPos[2])
        pecalBar_in_D = geom.structure.Placement('placeECALBar_in_Det',
                                                 volume = ecalBar_lv,
                                                 pos = ecalBar_in_det)
        det_lv.placements.append(pecalBar_in_D.name)
       


        return
