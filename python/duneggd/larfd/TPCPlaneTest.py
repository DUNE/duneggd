#!/usr/bin/env python
'''
Subbuilder of TPCBuilder
'''

import numpy as np
import gegede.builder
from gegede import Quantity as Q
from gegede import units
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

class TPCPlaneBuilder(gegede.builder.Builder):
    '''
    Build the TPCPlane.
    '''

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, 
                  wireDiam                = None,
                  wirePitch               = None,
                  wireAngle               = None,
                  nChannels               = None,
                  nowires                 = None,
                  frameDim                = None,
                  view                    = None,
                  **kwds):

        if view is None:
            raise ValueError("No value given for view") 
        if wirePitch is None:
            raise ValueError("No value given for wirePitch")
        if wireAngle is None:
            raise ValueError("No value given for wireAngle")
        if nChannels is None:
            raise ValueError("No value given for nChannels")

        self.wireDiam                = wireDiam
        self.wirePitch               = wirePitch
        self.wireAngle               = wireAngle
        self.nChannels               = nChannels
        self.nowires                 = nowires
        self.frameDim                = frameDim
        self.view                    = view
        
    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        readPlaneBox = geom.shapes.Box('TPCPlane' + self.view,
                                       dx=0.5*self.frameDim[0], 
                                       dy=0.5*self.frameDim[1],
                                       dz=0.5*self.frameDim[2])
        readPlane_lv = geom.structure.Volume('volTPCPlane' + self.view, material='LAr', shape=readPlaneBox)
        self.add_volume(readPlane_lv)

        if not self.nowires:
            if (self.view == 'Z'):
                self.MakeCollectionPlane(geom,readPlane_lv, readPlaneBox)
            if (self.view == 'V'):
                self.MakeInductionPlaneV(geom,readPlane_lv, readPlaneBox)
            if (self.view == 'U'):
                self.MakeInductionPlaneU(geom,readPlane_lv, readPlaneBox)

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def MakeCollectionPlane( self, geom, readPlane_lv, readPlaneBox):
        print('\nCreating collection wires.')

        index = 0
        zWire = geom.shapes.Tubs('TPCWire'+self.view,
                                 rmin = Q('0m'),
                                 rmax = 0.5*self.wireDiam,
                                 dz   = readPlaneBox.dy)
        zWire_lv = geom.structure.Volume('volTPCWireVertInner', material='CuBe', shape=zWire)

        initialPos = -0.5*(self.wirePitch) - (0.25*(self.nChannels) - 1)*self.wirePitch
        wirePos    = [Q('0m'), Q('0m'), initialPos]
        
        while (wirePos[2] <= readPlaneBox.dz):
            posName       = 'Wire-'+str(index)+'_in_Plane-'+self.view
            wire_in_plane = geom.structure.Position(posName,
                                                    wirePos[0],
                                                    wirePos[1],
                                                    wirePos[2])
            pWire_in_plane = geom.structure.Placement('place_'+posName,
                                                      volume = zWire_lv,
                                                      pos    = wire_in_plane,
                                                      rot    = 'r90aboutX')
            readPlane_lv.placements.append(pWire_in_plane.name)
            index += 1
            wirePos[2] += self.wirePitch

        print('DONE - Creating ' + str(index)+' collection wires.')        

    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def MakeInductionPlaneU( self, geom, readPlane_lv, readPlaneBox):
        print('\nCreating induction wires.')

        index = 0

        # Setting the initial values for the lower corner wires
        zIncriment = self.wirePitch / np.cos(self.wireAngle.to('rad').magnitude)
        yIncriment = self.wirePitch / np.sin(self.wireAngle.to('rad').magnitude)
        degAboutX  = Q(90, 'degree') - self.wireAngle
        wireRot    = geom.structure.Rotation('r'+self.view+'Wire', degAboutX, '0deg', '0deg')

        # Placing the lower corner wires
        wirePos = [Q('0m'), Q('-298.607295234439cm'), Q('114.944152403539cm') ]
        offset  = 0.5*(self.frameDim[2]) - wirePos[2]
        
        for i in range(400):
            wireLength = (offset + (i*zIncriment)) / np.sin(self.wireAngle.to('rad').magnitude)
            wire       = geom.shapes.Tubs('TPCWire'+self.view+'_'+str(i),
                                          rmin = Q('0m'),
                                          rmax = 0.5*self.wireDiam,
                                          dz   = 0.5*wireLength)
            wire_lv        = geom.structure.Volume('volTPCWire'+self.view+str(i)+'Inner', material='CuBe', shape=wire)
            posName        = 'Wire-'+str(i)+'_in_Plane'+self.view
            wire_in_plane  = geom.structure.Position(posName, wirePos[0], wirePos[1], wirePos[2])
            pWire_in_plane = geom.structure.Placement('place_'+posName, volume=wire_lv, pos=wire_in_plane, rot=wireRot)
            readPlane_lv.placements.append(pWire_in_plane.name)
            wirePos[2] -= 0.5*zIncriment
            wirePos[1] += 0.5*yIncriment
            index += 1

        # Defining the center common wires
        wire = geom.shapes.Tubs('TPCWireUCommon',
                                rmin = Q('0m'),
                                rmax = 0.5*self.wireDiam,
                                dz   = 0.5*Q('395.141754317532cm'))
        wire_lv = geom.structure.Volume('volTPCWireUCommon', material='CuBe', shape=wire)
        wirePos = [Q('0m'), Q('-138.678934415913cm')+Q('0.229795cm'), Q('0m')]        

        # Placing the center common wires
        for i in range(400, 748):
            posName       = 'Wire-'+str(i)+'_in_Plane'+self.view
            wire_in_plane = geom.structure.Position(posName,
                                                    wirePos[0],
                                                    wirePos[1],
                                                    wirePos[2])
            pWire_in_plane = geom.structure.Placement('place_'+posName,
                                                      volume = wire_lv,
                                                      pos    = wire_in_plane,
                                                      rot    = wireRot)
            readPlane_lv.placements.append(pWire_in_plane.name)
            wirePos[1] += yIncriment
            index += 1

        wirePos = [Q('0m'), Q('139.539123392393cm')-Q('0.414153cm'), Q('-0.323874896934043cm')]
        side    = Q('394.031991204821cm') * np.sin(self.wireAngle.to('rad').magnitude)
        offset  = side + wirePos[2]
        for i in range(400):
            wireLength = (offset - (i*zIncriment)) / np.sin(self.wireAngle.to('rad').magnitude)
            wire       = geom.shapes.Tubs('TPCWire'+self.view+'_'+str(i+748),
                                          rmin = Q('0m'),
                                          rmax = 0.5*self.wireDiam,
                                          dz   = 0.5*wireLength)
            wire_lv        = geom.structure.Volume('volTPCWire'+self.view+str(i+748)+'Inner', material='CuBe', shape=wire)
            posName        = 'Wire-'+str(i+748)+'_in_Plane'+self.view
            wire_in_plane  = geom.structure.Position(posName, wirePos[0], wirePos[1], wirePos[2])
            pWire_in_plane = geom.structure.Placement('place_'+posName, volume=wire_lv, pos=wire_in_plane, rot=wireRot)

            readPlane_lv.placements.append(pWire_in_plane.name)
            wirePos[2] -= 0.5*zIncriment
            wirePos[1] += 0.5*yIncriment
            index += 1
            
        

        print('DONE - Creating ' + str(index)+' U plane wires.')        



        
    #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def MakeInductionPlaneV( self, geom, readPlane_lv, readPlaneBox):
        print('\nCreating induction wires.')

        index = 0
        zIncriment = self.wirePitch / np.cos(self.wireAngle.to('rad').magnitude)
        yIncriment = self.wirePitch / np.sin(self.wireAngle.to('rad').magnitude)

        # Setting the initial values for the lower corner wires
        wirePos    = [Q("0cm"), Q('-299.005966291239cm')+Q('0.32193cm'), Q('-114.75125cm')]
        degAboutX  = Q(90, 'degree') + self.wireAngle
        wireRot    = geom.structure.Rotation('r'+self.view+'Wire', degAboutX, '0deg', '0deg')

        # Placing the lower corner wires
        for i in range(400):
            wireLength = (Q('0.5cm') + (i*zIncriment)) / np.sin(self.wireAngle.to('rad').magnitude)
            wire       = geom.shapes.Tubs('TPCWire'+self.view+'_'+str(i),
                                          rmin = Q('0m'),
                                          rmax = 0.5*self.wireDiam,
                                          dz   = 0.5*wireLength)
            wire_lv        = geom.structure.Volume('volTPCWire'+self.view+str(i)+'Inner', material='CuBe', shape=wire)
            posName        = 'Wire-'+str(i)+'_in_Plane'+self.view
            wire_in_plane  = geom.structure.Position(posName, wirePos[0], wirePos[1], wirePos[2])
            pWire_in_plane = geom.structure.Placement('place_'+posName, volume=wire_lv, pos=wire_in_plane, rot=wireRot)

            readPlane_lv.placements.append(pWire_in_plane.name)
            wirePos[2] += 0.5*zIncriment
            wirePos[1] += 0.5*yIncriment
            index += 1

        # Defining the center common wires
        wire = geom.shapes.Tubs('TPCWireVCommon',
                                rmin = Q('0m'),
                                rmax = 0.5*self.wireDiam,
                                dz   = 0.5*Q('393.761556005478cm'))
        wire_lv = geom.structure.Volume('volTPCWireVCommon', material='CuBe', shape=wire)
        wirePos = [Q('0m'), Q('-139.131182219385cm'), Q('0m')]

        # Placing the center common wires
        for i in range(400, 748):
            posName       = 'Wire-'+str(i)+'_in_Plane'+self.view
            wire_in_plane = geom.structure.Position(posName,
                                                    wirePos[0],
                                                    wirePos[1],
                                                    wirePos[2])
            pWire_in_plane = geom.structure.Placement('place_'+posName,
                                                      volume = wire_lv,
                                                      pos    = wire_in_plane,
                                                      rot    = wireRot)
            readPlane_lv.placements.append(pWire_in_plane.name)
            wirePos[1] += yIncriment
            index += 1


        wirePos    = [Q("0cm"), Q('139.40768767658cm')+Q('0.32193cm')-Q('0.525198cm'), Q('0.0260094309125662cm')]
        side       = Q('393.761556005478cm') * np.sin(self.wireAngle.to('rad').magnitude)
        offset     = side - (2.0*wirePos[2])
        for i in range(400):
            wireLength = (offset - ((i)*zIncriment)) / np.sin(self.wireAngle.to('rad').magnitude)
            wire       = geom.shapes.Tubs('TPCWire'+self.view+'_'+str(i+748),
                                          rmin = Q('0m'),
                                          rmax = 0.5*self.wireDiam,
                                          dz   = 0.5*wireLength)
            wire_lv        = geom.structure.Volume('volTPCWire'+self.view+str(i+748)+'Inner', material='CuBe', shape=wire)
            posName        = 'Wire-'+str(i+748)+'_in_Plane'+self.view
            wire_in_plane  = geom.structure.Position(posName, wirePos[0], wirePos[1], wirePos[2])
            pWire_in_plane = geom.structure.Placement('place_'+posName, volume=wire_lv, pos=wire_in_plane, rot=wireRot)

            readPlane_lv.placements.append(pWire_in_plane.name)
            wirePos[2] += 0.5*zIncriment
            wirePos[1] += 0.5*yIncriment
            index += 1

        print('DONE - Creating ' + str(index)+' V plane wires.')        
            
