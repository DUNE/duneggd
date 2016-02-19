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
                  **kwds):

        self.wireDiam           = wireDiam
        self.wirePitch          = wirePitch
        self.wireLength         = wireLength
        self.readPlaneDim       = readPlaneDim
        self.nWires             = nWires
        self.nowires            = nowires


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # N.B. -- the names 'volTPCPlane*' and 'volTPCWire*' are required by LArSoft

        # Define wire shape and volume
        #
        # TODO: fix material
        #
        wire      = geom.shapes.Tubs('TPCWire_Z', 
                                     rmin = '0cm',                   
                                     rmax = 0.5*self.wireDiam, 
                                     dz   = 0.5*self.wireLength)
        wire_lv   = geom.structure.Volume('volTPCWire_Z', material='Steel', shape=wire)


        # define readout plane shape and volume
        readPlaneBox = geom.shapes.Box( 'TPCPlane',                  dx=0.5*self.readPlaneDim[0], 
                                        dy=0.5*self.readPlaneDim[1], dz=0.5*self.readPlaneDim[2]  )
        readPlane_lv = geom.structure.Volume('volTPCPlane', material='LAr', shape=readPlaneBox)
        self.add_volume(readPlane_lv)

        if not self.nowires:
            wireSpan_z = self.nWires * self.wirePitch # center to center
            for i in range(self.nWires):
                
                zpos = -0.5 * wireSpan_z + i*self.wirePitch
                
                posName = 'Wire-'+str(i)+'_in_Plane'
                wire_in_plane = geom.structure.Position(posName, 
                                                        '0cm','0cm',zpos)
                
                pWire_in_Plane = geom.structure.Placement('place'+posName,
                                                          volume = wire_lv,
                                                          pos = wire_in_plane,
                                                          rot = "r90aboutX")
                readPlane_lv.placements.append(pWire_in_Plane.name)
