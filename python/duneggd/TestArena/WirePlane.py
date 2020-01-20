#!/usr/bin/env python
'''
Subbuilder of APAFrame
'''

from math import cos, sin, tan
import gegede.builder
from gegede import Quantity as Q
from gegede import units

class WirePlaneBuilder(gegede.builder.Builder):

    def configure(self,                   
                  nWires                  = None,
                  view                    = None,
                  pitch                   = None,
                  wireDiam                = None,
                  G10ThicknessFoot        = None,
                  G10ThicknessSide        = None,
                  HeadBoardScrewCentre    = None,
                  HeadAPAFrameScrewCentre = None,
                  wrapCover               = None,
                  APAFrameDim             = None,
                  **kwds):


        self.nWires                   = nWires
        self.view                     = view
        self.pitch                    = pitch                   
        self.wireDiam                 = wireDiam                
        self.G10ThicknessFoot         = G10ThicknessFoot        
        self.G10ThicknessSide         = G10ThicknessSide        
        self.HeadBoardScrewCentre     = HeadBoardScrewCentre                            
        self.HeadAPAFrameScrewCentre  = HeadAPAFrameScrewCentre                         
        self.wrapCover                = wrapCover               
        self.APAFrameDim              = APAFrameDim             


    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):


        self.planeDim = list(self.APAFrameDim)


        if self.view == 'Z':
            self.planeDim[1] += - self.HeadBoardScrewCentre[1] - self.HeadAPAFrameScrewCentre[1]
            self.planeDim[2] += 2 * (-self.HeadAPAFrameScrewCentre[2] + self.HeadBoardScrewCentre[2])

            ZPlane_box = geom.shapes.Box('TPCPlane'+self.view,
                                         dx=0.5*self.wireDiam,
                                         dy=0.5*self.planeDim[1],
                                         dz=0.5*self.planeDim[2])
            zwire    = geom.shapes.Tubs('TPCWire' + self.view,
                                        rmin = Q('0cm'),
                                        rmax = 0.5*self.wireDiam, 
                                        dz   = 0.5*self.planeDim[1] )
            ZPlane_lv = geom.structure.Volume('volTPCPlaneZ', material='LAr', shape=ZPlane_box)
            self.add_volume(ZPlane_lv)
            # ZPlane_Box = geom.shapes.Boolean('testSubtraction', type='subtraction',
            #                                  first=ZPlane_box, second=zwire, pos=[Q('0m'), Q('0m'), Q('0m')], rot='r90aboutX')
            
            # self.ConstructCollectionPlane(geom, self.nWires, zwire, ZPlane_box)
            print("X Plane Dimenstions: ", self.planeDim)
            

                                   
    def ConstructCollectionPlane(self, geom, nwires):
        pass

        # --- Define all the volumes -------------------------

        # zwire_lv = geom.structure.Volume('volTPCWireVertInner', material='CuBe', shape=zwire)

        # wirePos = [Q('0m'), Q('0'), (-0.5*self.pitch) + (((-0.5*nwires)-1) * self.pitch)]



        # ZPlane_lv = geom.structure.Volume('volTPCPlane'+self.view, material="LAr", shape=ZPlane_box)
        # self.add_volume(ZPlane_lv)
        
        # wirePos = [Q('0m'), Q('0'), (0.5*self.pitch) * (((0.5*self.nwires)-1) * self.pitch)]
        # for i in range(nwires):
        #     posName = 'Wire-'+str(i)+'_in_Plane-'+self.view
        #     pWire_in_Plane = geom.structure.Placement('place_'+posName,
        #                                               volume = zwire_lv,
        #                                               pos    = wirePos,
        #                                               rot    = 'r90aboutX')
        #     ZPlane_lv.placements.append(pWire_in_Plane.name)
