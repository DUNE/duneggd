#!/usr/bin/env python
'''
Subbulder of STTBuilder
'''

import gegede.builder
import math

class STPlaneBuilder(gegede.builder.Builder):

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, sTube_innerDia='0.95cm', sTube_outerDia='0.9565cm', sTube_length='350cm', 
                  stPlaneMat='Air', strawMat='fibrous_glass', stGas='stGas_Ar', **kwds):
        self.material   = stPlaneMat
        self.strawMat   = strawMat
        self.stGas      = stGas
        self.sTube_innerDia = sTube_innerDia
        self.sTube_outerDia = sTube_outerDia
        self.sTube_length = sTube_length


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # Make the straw tube shape and volume, and add straw into it
        # rmin=0, else material at 0 would be default of STPlane
        sTube      = geom.shapes.Tubs('StrawTube_'+self.name, 
                                      rmin = '0cm',                   
                                      rmax = self.sTube_outerDia, 
                                      dz   = self.sTube_length)
        sTube_lv   = geom.structure.Volume('volStrawTube_'+self.name, material=self.stGas, shape=sTube)
        straw      = geom.shapes.Tubs('Straw_'+self.name, 
                                      rmin = self.sTube_innerDia, 
                                      rmax = self.sTube_outerDia, 
                                      dz   = self.sTube_length)
        straw_lv   = geom.structure.Volume('volStraw_'+self.name, material=self.strawMat, shape=straw)
        pS_in_Tube = geom.structure.Placement( 'placeS_in_Tube_'+self.name, volume = straw_lv )
        sTube_lv.placements.append( pS_in_Tube.name )
        self.add_volume(sTube_lv)

        # Make the double-layer of straw tubes, used for both orientations
        self.stPlaneDim = [ self.sTube_length, 
                            self.sTube_length, 
                            2*self.sTube_outerDia*( 1 + math.sin( math.radians(60) ) ) ]
        stPlaneBox = geom.shapes.Box(    self.name,          dx=self.stPlaneDim[0], 
                                      dy=self.stPlaneDim[1], dz=self.stPlaneDim[2])
        stPlane_lv = geom.structure.Volume('vol'+self.name, material=self.material, shape=stPlaneBox)
        self.add_volume(stPlane_lv)

        print ""
        print " From SubBuilder named "+self.name+", dimensions are:"
        print self.stPlaneDim
        print ""

        
        nTubesPerPlane = int( math.floor((self.stPlaneDim[0] - 0.5*self.sTube_outerDia) / self.sTube_outerDia) )

        r90AboutX = geom.structure.Rotation('r90aboutX_'+self.name, '90deg', '0deg', '0deg')
        for i in range(nTubesPerPlane):

            #     <--- O O O O O O    ^      <--B_i+n    For each i, place ith A at (x,y,z) and
            #      +x   O O O O O O   | +z   <--A_i       place (i+n)th B at (x_next,y,-z),
            #                         |                   where n is number of tubes per plane

            xpos      = -0.5*self.stPlaneDim[0] + (i+0.5)*self.sTube_outerDia
            xpos_next =  xpos + 0.5*self.sTube_outerDia
            ypos      =  '0cm'
            zpos      = -0.5*self.stPlaneDim[2] + self.sTube_outerDia


            # define positions, append placements
            st_in_p      = geom.structure.Position( 'Tube-'+str(i)+'_in_STPlane_'+self.name, 
                                                    xpos,      ypos,  zpos)
            stnext_in_p  = geom.structure.Position( 'Tube-'+str(i+nTubesPerPlane)+'_in_STPlane_'+self.name, 
                                                    xpos_next, ypos, -zpos)

            pst_in_p     = geom.structure.Placement( 'placeTube-'+str(i)+'_in_STPlane_'+self.name,
                                                     volume = sTube_lv,
                                                     pos = st_in_p,
                                                     rot = r90AboutX)
            pstnext_in_p = geom.structure.Placement( 'placeTube-'+str(i+nTubesPerPlane)+'_in_STPlane_'+self.name,
                                                     volume = sTube_lv,
                                                     pos = stnext_in_p,
                                                     rot = r90AboutX)

            stPlane_lv.placements.append( pst_in_p.name     )
            stPlane_lv.placements.append( pstnext_in_p.name )
        
