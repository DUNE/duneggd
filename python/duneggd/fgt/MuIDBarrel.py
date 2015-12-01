#!/usr/bin/env python
'''
Subbuilder of Detector
'''

import gegede.builder
from gegede import Quantity as Q


class MuIDBarrelBuilder(gegede.builder.Builder):
    '''
    Assemble RPC trays in the magnet yoke 
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, muidInDim=None, magInDim=None, magThickness=Q('60cm'), **kwds):
        if muidInDim is None:
            raise ValueError("No value given for muidInDim")

        self.defMat = "Steel"
        self.muidInDim  = muidInDim
        self.magInDim   = magInDim
        self.magThickness = magThickness

        # Get RPC tray builders
        self.RPCTraySmallBldr = self.get_builder('RPCTray_BarSmall')
        self.RPCTrayMidFBldr   = self.get_builder('RPCTray_BarMidF')
        self.RPCTrayMidSBldr   = self.get_builder('RPCTray_BarMidS')
        self.RPCTrayBigBldr   = self.get_builder('RPCTray_BarBig')


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):


        # Just like in the EndBuilder, calculate outer dimensions 
        #  using other configured parameters: number of planes, thicknesses...
        # For now I'm using the CDR reported dimensions:
        self.muidOutDim = list(self.muidInDim)
        self.muidOutDim[0] = Q('9.6m')
        self.muidOutDim[1] = Q('7.5m')#4.5m')


        # Define barrel as boolean, with hole to fit magnet inside
        muidOut = geom.shapes.Box( 'MuIDOut',                 dx=0.5*self.muidOutDim[0], 
                                   dy=0.5*self.muidOutDim[1], dz=0.5*self.muidOutDim[2]) 
        muidIn = geom.shapes.Box(  'MuIDIn',                  dx=0.5*self.muidInDim[0], 
                                   dy=0.5*self.muidInDim[1],  dz=0.5*self.muidInDim[2]) 
        muidBarBox = geom.shapes.Boolean( self.name, type='subtraction', first=muidOut, second=muidIn )
        muidBar_lv = geom.structure.Volume('vol'+self.name, material=self.defMat, shape=muidBarBox)
        self.add_volume(muidBar_lv)


        # Get the RPC tray volumes and dimensions
        smallTray_lv = self.RPCTraySmallBldr.get_volume('volRPCTray_BarSmall')
        fmidTray_lv  = self.RPCTrayMidFBldr.get_volume('volRPCTray_BarMidF')
        smidTray_lv  = self.RPCTrayMidSBldr.get_volume('volRPCTray_BarMidS')
        bigTray_lv   = self.RPCTrayBigBldr.get_volume('volRPCTray_BarBig')
        rpcTrayDim_small = self.RPCTraySmallBldr.rpcTrayDim
        rpcTrayDim_midf = self.RPCTrayMidFBldr.rpcTrayDim
        rpcTrayDim_mids = self.RPCTrayMidSBldr.rpcTrayDim
        rpcTrayDim_big = self.RPCTrayBigBldr.rpcTrayDim


        # Place the RPC trays and steel sheets between, being mindful of rotation
        # Steel Sheets: just leave the default material of volMuID* steel 
        #   and leave spaces instead of placing explicit volumes
        # Placement of rpcTrays in vertical MuIDBarel
        for i in range(2):
           for j in range(2):
                xpos = -0.5*self.muidOutDim[0]+0.5*rpcTrayDim_big[2]+0.5*self.magThickness
                xpos_mids = -0.5*self.muidOutDim[0]+1.5*rpcTrayDim_big[2]+self.magThickness
                xpos_midf = -0.5*self.muidOutDim[0]+2.5*rpcTrayDim_big[2]+1.5*self.magThickness
            
                ypos = -0.5*self.muidOutDim[1]+0.5*self.magThickness+rpcTrayDim_big[2]+(j+0.5)*rpcTrayDim_big[1]
                ypos_mids = -0.5*self.muidOutDim[1]+1*self.magThickness+2*rpcTrayDim_big[2]+(j+0.5)*rpcTrayDim_mids[1]
                ypos_midf = -0.5*self.muidOutDim[1]+1.5*self.magThickness+3*rpcTrayDim_big[2]+(j+0.5)*rpcTrayDim_midf[1]
            
                zpos = -0.5*self.muidOutDim[2]+(i+0.5)*rpcTrayDim_big[0]

                brpct_in_muid  = geom.structure.Position( 'brpct-'+str(i*2+j)+'_in_'+self.name,
                                                         xpos,  ypos,  zpos)
                pbrpct_in_muid = geom.structure.Placement( 'pbrpct-'+str(i*2+j)+'_in_'+self.name,
                                                         volume = bigTray_lv, pos = brpct_in_muid, rot= "r90aboutY" )
                #print 'vbmuidbar: '+str(i)+' xpos:     '+str(xpos)+' ypos: '+str(ypos)+' zpos: '+str(zpos)
                smrpct_in_muid  = geom.structure.Position( 'smrpct-'+str(i*2+j)+'_in_'+self.name,
                                                         xpos_mids,  ypos_mids,  zpos)
                psmrpct_in_muid = geom.structure.Placement( 'psmrpct-'+str(i*2+j)+'_in_'+self.name,
                                                          volume = smidTray_lv, pos = smrpct_in_muid, rot= "r90aboutY" )
                #print 'vmsmuidbar: '+str(i)+' xpos_mids:  '+str(xpos_mids)+' ypos_mids: '+str(ypos_mids)+' zpos: '+str(zpos)
                fmrpct_in_muid  = geom.structure.Position( 'fmrpct-'+str(i*2+j)+'_in_'+self.name,
                                                         xpos_midf,  ypos_midf,  zpos)
                pfmrpct_in_muid = geom.structure.Placement( 'pfmrpct-'+str(i*2+j)+'_in_'+self.name,
                                                          volume = fmidTray_lv, pos = fmrpct_in_muid, rot= "r90aboutY" )
                #print 'vmfmuidbar: '+str(i)+' xpos_midf: '+str(xpos_midf)+' ypos_midf: '+str(ypos_midf)+' zpos: '+str(zpos)
                muidBar_lv.placements.append( pbrpct_in_muid.name )
                muidBar_lv.placements.append( psmrpct_in_muid.name )
                muidBar_lv.placements.append( pfmrpct_in_muid.name )

        # Placement of rpcTrays in Horizontal MuIDBarel
        for i in range(2):
            xpos_mids = -0.5*self.muidOutDim[0]+0.5*rpcTrayDim_mids[1]+0.5*self.magThickness
            xpos_midf = -0.5*self.muidOutDim[0]+0.5*rpcTrayDim_midf[1]+self.magThickness
            xpos_small = -0.5*self.muidOutDim[0]+0.5*rpcTrayDim_small[1]+1.5*self.magThickness

            zpos = -0.5*self.muidOutDim[2]+(i+0.5)*rpcTrayDim_mids[0]
            for j in range(2):
                if (j==0):
                        ypos_mids = -0.5*self.muidOutDim[1]+0.5*self.magThickness+0.5*rpcTrayDim_mids[2]
                        ypos_midf = -0.5*self.muidOutDim[1]+1*self.magThickness+0.5*rpcTrayDim_mids[2]
                        ypos_small= -0.5*self.muidOutDim[1]+1.5*self.magThickness+0.5*rpcTrayDim_mids[2]
                else :
                        ypos_mids = -(-0.5*self.muidOutDim[1]+0.5*self.magThickness+0.5*rpcTrayDim_mids[2])
                        ypos_midf = -(-0.5*self.muidOutDim[1]+1*self.magThickness+0.5*rpcTrayDim_mids[2])
                        ypos_small= -(-0.5*self.muidOutDim[1]+1.5*self.magThickness+0.5*rpcTrayDim_mids[2])

                smvrpct_in_muid  = geom.structure.Position( 'smvrpct-'+str(i*2+j)+'_in_'+self.name,
                                                          xpos_mids,  ypos_mids,  zpos)
                psmvrpct_in_muid = geom.structure.Placement( 'psmvrpct-'+str(i*2+j)+'_in_'+self.name,
                                                           volume = smidTray_lv, pos = smvrpct_in_muid, rot= "r90aboutXZ" )
                fmvrpct_in_muid  = geom.structure.Position( 'fmvrpct-'+str(i*2+j)+'_in_'+self.name,
                                                          xpos_midf,  ypos_midf,  zpos)
                pfmvrpct_in_muid = geom.structure.Placement( 'pfmvrpct-'+str(i*2+j)+'_in_'+self.name,
                                                           volume = fmidTray_lv, pos = fmvrpct_in_muid, rot= "r90aboutXZ" )
                svrpct_in_muid  = geom.structure.Position( 'svrpct-'+str(i*2+j)+'_in_'+self.name,
                                                          xpos_small,  ypos_small,  zpos)
                psvrpct_in_muid = geom.structure.Placement( 'psvrpct-'+str(i*2+j)+'_in_'+self.name,
                                                           volume = smallTray_lv, pos = svrpct_in_muid, rot= "r90aboutXZ" )

                muidBar_lv.placements.append( psmvrpct_in_muid.name )
                muidBar_lv.placements.append( pfmvrpct_in_muid.name )
                muidBar_lv.placements.append( psvrpct_in_muid.name )
                #print 'hmsmuidbar: '+str(i)+' xpos_mids:     '+str(xpos_mids)+' ypos_mids: '+str(ypos_mids)+' zpos: '+str(zpos)
                #print 'hmfmuidbar: '+str(i)+' xpos_midf:     '+str(xpos_midf)+' ypos_midf: '+str(ypos_midf)+' zpos: '+str(zpos)
                #print 'hsmuidbar: '+str(i)+' xpos_small:     '+str(xpos_small)+' ypos_small: '+str(ypos_small)+' zpos: '+str(zpos)
        return
