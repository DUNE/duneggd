#!/usr/bin/env python
'''An example GeGeDe module.

This provides some builder classes to build a Rubik's cube.

Warning: any resemblance between the result and an actual Rubik's cube
is purely accidental.  It's really just a 3x3x3 stack of blocks less
one at the origin.
'''

import gegede.builder
from gegede import Quantity as Q

class WorldBuilder(gegede.builder.Builder):
    '''
    Build a simple box world of given material and size.
    '''
    def configure(self, material = 'Air', size = Q("1m"), **kwds):
        self.material, self.size = (material, size)
        pass

    def construct(self, geom):
        dim = (0.5*self.size,)*3
        shape = geom.shapes.Box(self.name + '_box_shape', *dim)
        lv = geom.structure.Volume(self.name+'_volume', material=self.material, shape=shape)
        self.add_volume(lv)

        # Note: this block adds all LVs of all sub builders at default
        # position/rotation which is probably not what is wanted in
        # general.
        for sbname, sbld in self.builders.items():
            for svname, svol in sbld.volumes.items():
                pname = '%s_in_%s' % (svol.name, self.name)
                p = geom.structure.Placement(pname, volume = svol)
                lv.placements.append(pname)        
                

class RubikBuilder(gegede.builder.Builder):
    '''Build a Rubik's cube (kind of).  

    Delegate to three sub-builders assumed to provide each one of, in
    order, corner, edge and center blocks.  Blocks are assumed to be
    cubes of equal size.

    '''

    def configure(self, material = 'Air', gap = Q("1mm"), **kwds):
        self.material, self.gap = (material, gap)
        pass

    def construct(self, geom):

        # get volumes from sub-builders.  Note, implicitly assume
        # order, which must be born out by configuration.  Once could
        # remove this by querying each sub-builder for its "location"
        # configuration parameter, but this then requires other
        # assumptions.
        blocks = []        
        for key, value in self.builders.items():
            print(value.volumes.items()[0][1].shape)
            blocks.append(list(value.volumes.items())[0][1])
        corner, edge, center = blocks
        
        block_shape = geom.store.shapes.get("block1_box_shape")
        blocks.reverse()        # you'll see why

        # Calculate overall dimensions from daughters.  Assume identical cubes!
        half_size = (block_shape.dx + self.gap) * 3
        dim = (half_size,)*3

        # make overall shape and LV
        shape = geom.shapes.Box(self.name + '_box_shape', *dim)
        block_lv = geom.structure.Volume(self.name+'_volume', material=self.material, shape=shape)
        print(type(block_lv))
        self.add_volume(block_lv)
        
        # distance between two adjacent blocks
        step = (block_shape.dx + self.gap)*2

        # place daughter LV
        for ii in [-1,0,1]:         # x
            for jj in [-1,0,1]:     # y
                for kk in [-1,0,1]: # z
                    trip = (ii,jj,kk)
                    if trip == (0,0,0):
                        continue

                    which = sum([abs(x) for x in trip]) - 1
                    lv = blocks[which] # that's why
                    trip_name = '%d%d%d' % trip
                    pos = geom.structure.Position('pos_'+trip_name, x=ii*step,y=jj*step,z=kk*step)
                    placement = geom.structure.Placement('place_' + trip_name, volume=lv, pos=pos)
                    block_lv.placements.append(placement.name)
                    
                    continue
                continue
            continue
        return
    

class RubikBlockBuilder(gegede.builder.Builder):
    '''
    Build a corner, edge or center Rubik's cube block.
    '''
    def configure(self, location = "center", material = 'Plastic', size = Q("20cm"), **kwds):
        self.material, self.size = (material, size)
        pass

    def construct(self, geom):
        dim = (0.5*self.size,)*3
        shape = geom.shapes.Box(self.name + '_box_shape', *dim)
        lv = geom.structure.Volume(self.name+'_volume', material=self.material, shape=shape)
        self.add_volume(lv)
