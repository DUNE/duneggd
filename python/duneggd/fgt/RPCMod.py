#!/usr/bin/env python
'''
Subbuilder of RPCTrayBuilder
'''

import gegede.builder

class RPCModBuilder(gegede.builder.Builder):
    '''
    Build the RPC modules, the effective unit of the MuID, 
    constituting an X and Y plane of RPC strips 
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self,  **kwds):




    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        # define box and volume for RPC strip


        # define box and volume for resistive plate (maybe the same volume for anode and cathode?)

        # define box and volume for whole RPCMod,
        # to be retrieved by RPCTray*Builder 


        # position and place resistive plates in RPCMod
        

        # for loop to position and place X strips in RPCMod


        # for loop to position and place Y strips in RPCMod
        

        return
