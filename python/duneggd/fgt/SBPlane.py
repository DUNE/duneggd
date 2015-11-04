#!/usr/bin/env python
'''
Example gegede builders for a trivial LAr geometry
'''

import gegede.builder
import math

class SBPlaneBuilder(gegede.builder.Builder):

    def configure(self, # cfg parameters here
                  **kwds):
        # define builder data here

    def construct(self, geom):

        # Make the scint bar shape and volume


        # Make the scint bar plane, used for both orientations


        # Place the bars in the plane
