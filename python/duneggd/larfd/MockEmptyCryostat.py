#!/usr/bin/env python
'''
Subbuilder of MockEmptyCryostat
'''

import gegede.builder
from gegede import Quantity as Q


class MockEmptyCryostatBuilder(gegede.builder.Builder):
    '''
    Build a mock empty volume of liquid argon
    '''
    
    def configure(self,
                  Size = None):
        self.Size = Size

    def construct(self, geom):
        CryoBox = geom.shapes.Box('EmptyCryoBox',
                                  dx=0.5*self.Size[0], 
                                  dy=0.5*self.Size[1],
                                  dz=0.5*self.Size[2])
        CryoBox_lv = geom.structure.Volume('volEmptyCryostat', material='LAr', shape=CryoBox)
        
        self.add_volume(CryoBox_lv)
