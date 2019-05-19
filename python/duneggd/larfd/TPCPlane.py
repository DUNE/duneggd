#!/usr/bin/env python
'''
Subbuilder of TPCBuilder
'''

import gegede.builder
from gegede import Quantity as Q


class TPCPlaneBuilder(gegede.builder.Builder):
    '''
    Build the Cryostat.
    '''


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, 
                  wireDiam            = Q('150um'), # <-- just default values,
                  wirePitch           = Q('5mm'),   #     they really come from
                  wireLength          = Q('2.5m'),  #     the cfg file 
                  readPlaneDim  = [Q('150um'), Q('3m'), Q('2m')], 
                  nWires              = 399,
                  nowires             = False,
                  apaFrameDim         = None,
                  G10Thickness        = Q('0.125in'),
                  wrapCover           = Q('0.0625in'),
                  view                = None,
                  **kwds):

        if view is None:
            raise ValueError("No value given for view")
        

        self.wireDiam           = wireDiam
        self.wirePitch          = wirePitch
        self.wireLength         = wireLength
        self.readPlaneDim       = readPlaneDim
        self.nWires             = nWires
        self.nowires            = nowires
        self.apaFrameDim        = apaFrameDim
        self.G10Thickness       = G10Thickness 
        self.wrapCover          = wrapCover
        self.view               = view

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # N.B. -- the names 'volTPCPlane*' and 'volTPCWire*' are required by LArSoft

        # Define wire shape and volume
        #
        # TODO: fix material
        #

        planeDim = list(self.apaFrameDim)
        
        # 4x comes from is from Z, V, U, gridplane
        self.apaFrameDim[1] = self.apaFrameDim[1] + (4 * self.G10Thickness) + self.wrapCover

        # add something to deal with the type of plane
        
        wire      = geom.shapes.Tubs('TPCWire_' + self.view, 
                                     rmin = '0cm',                   
                                     rmax = 0.5*self.wireDiam, 
                                     dz   = planeDim[2])
        wire_lv   = geom.structure.Volume('volTPCWire_' + self.view, material='Steel', shape=wire)


        # define readout plane shape and volume
        readPlaneBox = geom.shapes.Box( 'TPCPlane' + self.view,      dx=0.5*self.readPlaneDim[0], 
                                        dy=0.5*self.readPlaneDim[1], dz=0.5*self.readPlaneDim[2]  )
        readPlane_lv = geom.structure.Volume('volTPCPlane' + self.view, material='LAr', shape=readPlaneBox)
        self.add_volume(readPlane_lv)

        if not self.nowires:
            wireSpan_z = self.nWires * self.wirePitch # center to center
            if (wireSpan_z > planeDim[2]):
                raise Exception('Wire span ' + str(wireSpan_z) + ' excedes ' + str(planeDim[2]))
            

            for i in range(self.nWires):
                
                zpos = -0.5 * wireSpan_z + i*self.wirePitch
                
                posName = 'Wire-'+str(i)+'_in_Plane' + self.view
                wire_in_plane = geom.structure.Position(posName, 
                                                        '0cm','0cm',zpos)
                
                pWire_in_Plane = geom.structure.Placement('place'+posName,
                                                          volume = wire_lv,
                                                          pos = wire_in_plane,
                                                          rot = "r90aboutX")
                readPlane_lv.placements.append(pWire_in_Plane.name)
