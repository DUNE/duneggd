#!/usr/bin/env python
'''
Subbuilder of DetEncBuilder
'''

import gegede.builder
from gegede import Quantity as Q

#https://docs.dunescience.org/cgi-bin/private/RetrieveFile?docid=464&filename=LBNF%20-%20Underground%20-%20North%20Cavern%20Clearance%20Envelopes%20-%202018-12-07.pdf&version=10
class CavernBuilder(gegede.builder.Builder):
    '''
    Build the Cavern.
    '''


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, 
                  cavernDim     = None,
                  topArchRadius = None,
                  topArchCenter = None,
                  rockThickness = None,
                  **kwds):

        self.cavernDim    = cavernDim
        self.topArchRadiu = topArchRadius
        self.topArchCente = topArchCenter
        self.rockThicknes = rockThickness
  
        self.cryoBldr  = self.get_builder('DetEnclusureLAr')

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):
        print("constructing the cavern.")
