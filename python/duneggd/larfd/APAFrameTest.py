#!/usr/bin/env python
'''
Subbuilder of APAFrame
'''

from math import cos, sin, tan
import gegede.builder
from gegede import Quantity as Q
from gegede import units

class APAFrameBuilder(gegede.builder.Builder):
    '''
    Build the FRAME.
    '''

    # ^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self, 
                  size                       = None,
                  footsize                   = None,
                  headsize                   = None,
                  footthickness              = None,
                  nribs                      = None,
                  ribsize                    = None,
                  ribthickness               = None,
                  APAGap_y                   = None,
                  APAGap_z                   = None,
                  APAFrameZSide_y            = None,
                  APAFrameZSide_z            = None,
                  LightPaddle_x              = None,
                  LightPaddle_y              = None,
                  LightPaddle_z              = None,
                  nLightPaddlePerAPA         = None,
                  LightPaddleHeadOffset      = None,
                  LightPaddleVerticalSpacing = None,
                  **kwds):

        self.size                       = size
        self.footsize                   = footsize
        self.headsize                   = headsize
        self.footthickness              = footthickness
        self.nribs                      = nribs
        self.ribsize                    = ribsize
        self.ribthickness               = ribthickness
        self.APAGap_y                   = APAGap_y
        self.APAGap_z                   = APAGap_z
        self.APAFrameZSide_y            = APAFrameZSide_y
        self.APAFrameZSide_z            = APAFrameZSide_z
        self.LightPaddle_x              = LightPaddle_x  
        self.LightPaddle_y              = LightPaddle_y  
        self.LightPaddle_z              = LightPaddle_z
        self.nLightPaddlePerAPA         = nLightPaddlePerAPA
        self.LightPaddleHeadOffset      = LightPaddleHeadOffset
        self.LightPaddleVerticalSpacing = LightPaddleVerticalSpacing

    # ^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def ConstructHollowBeam(self, geom, name, sizeouter, thickness):
        SurroundingBox = geom.shapes.Box(name+'Box',
                                         dx=0.5*sizeouter[0],
                                         dy=0.5*sizeouter[1],
                                         dz=0.5*sizeouter[2])

        SubtractionBox = geom.shapes.Box(name+'SubtractionBox',
                                         dx=0.5*sizeouter[0]-thickness, 
                                         dy=0.5*sizeouter[1]-thickness,
                                         dz=0.5*sizeouter[2])
        Pos = geom.structure.Position(name+'SubtractionPos',
                                      Q('0m'), Q('0m'), Q('0m'))
        
        SubVol = geom.shapes.Boolean(name+"_BoolSub",
                                     type='subtraction',
                                     first=SurroundingBox,
                                     second=SubtractionBox,
                                     pos=Pos)
        Vol_lv = geom.structure.Volume('vol'+name, material='Steel', shape=SubVol)
        return Vol_lv

    # ^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def ConstructMiddleBeam(self, geom, name, sizeouter, thickness, paddle, spacing):
        SurroundingBox = geom.shapes.Box(name+'Box',
                                         dx=0.5*sizeouter[0],
                                         dy=0.5*sizeouter[1],
                                         dz=0.5*sizeouter[2])

        SubtractionBox = geom.shapes.Box(name+'SubtractionBox',
                                         dx=0.5*sizeouter[0]-thickness, 
                                         dy=0.5*sizeouter[1]-thickness,
                                         dz=0.5*sizeouter[2])
        Pos = geom.structure.Position(name+'SubtractionPos',
                                      Q('0m'), Q('0m'), Q('0m'))
        
        SubVol = geom.shapes.Boolean(name+"_BoolSub",
                                     type='subtraction',
                                     first=SurroundingBox,
                                     second=SubtractionBox,
                                     pos=Pos)

        paddlePosition = 0.5*sizeouter[1] - self.LightPaddleHeadOffset - 0.5*paddle.dz
        for i in range(self.nLightPaddlePerAPA):
            pos = geom.structure.Position('paddleSubtractionBox_'+str(i), Q('0m'),
                                          Q('0m'), paddlePosition - i*self.LightPaddleVerticalSpacing)
            SubVol = geom.shapes.Boolean(name+'PaddleSubtraction_'+str(i+1),
                                         type='subtraction',
                                         first=SubVol,
                                         second=paddle,
                                         pos=pos)

        Vol_lv = geom.structure.Volume('vol'+name, material='Steel', shape=SubVol)
        return Vol_lv

    # ^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):
        
        FrameBox = geom.shapes.Box('Frame', dx=0.5*self.footsize[0], dy=0.5*self.size[1], dz=0.5*self.size[2])
        frame_lv = geom.structure.Volume('volAPAFrame', material='LAr', shape=FrameBox)
        self.add_volume(frame_lv)

        # Calculating the Light Paddle spacing
        self.PaddleYInterval    = (2*self.size[1] + self.APAGap_y - self.LightPaddle_y - 2*self.APAFrameZSide_y) / (2*self.nLightPaddlePerAPA - 1)
        # print(self.PaddleYInterval)
        self.FrameToPaddleSpace = (self.PaddleYInterval - self.APAGap_y)/2

        # Light Paddle construction
        LightPaddle_box = geom.shapes.Box('LightPaddle_temp',
                                          dx=0.5*self.LightPaddle_x,
                                          dy=0.5*self.LightPaddle_z,
                                          dz=0.5*self.LightPaddle_y)

        # Head and Foot of the APA Frame
        Foot_lv = self.ConstructHollowBeam(geom, 'APAFrameFoot', self.footsize, self.footthickness)
        Head_lv = self.ConstructHollowBeam(geom, 'APAFrameHead', self.headsize, self.footthickness)

        # Side struts of the APA Frame
        size_side = [self.footsize[0], self.footsize[1], self.size[1]-self.footsize[1]-self.headsize[1]]
        Side_lv   = self.ConstructHollowBeam(geom, 'APAFrameSide',  size_side, self.footthickness)

        # Middle strut of the APA Frame
        size_middle = [self.footsize[0], self.footsize[1], self.size[1]-self.footsize[1]-self.headsize[1]]
        Middle_lv   = self.ConstructMiddleBeam(geom,
                                               'APAFrameMiddle',
                                               size_middle,
                                               self.footthickness,
                                               LightPaddle_box,
                                               self.PaddleYInterval)
        
        size_rib    = [self.ribsize[0], self.ribsize[1], 0.5*self.size[2]-1.5*self.footsize[0]]
        Rib_lv    = self.ConstructHollowBeam(geom, 'APAFrameRib',     size_rib   , self.ribthickness)
        
        
        FootPosition = geom.structure.Position('APAFrameFootPos',
                                               Q('0m'),0.5*(-self.size[1]+self.footsize[1]), Q('0m'))
        
        HeadPosition  = geom.structure.Position('APAFrameHeadPos',
                                                Q('0m'),0.5*(self.size[1]-self.headsize[1]), Q('0m'))
        
        yoffset = 0.5*(self.footsize[1]-self.headsize[1])
        MiddlePosition = geom.structure.Position('APAFrameMiddlePos',
                                                 Q('0m'), yoffset, Q('0m'))
        
        LeftPosition = geom.structure.Position('APAFrameLeftPos',
                                               Q('0m'), yoffset, 0.5*(-self.size[2]+self.footsize[1]))
        
        RightPosition = geom.structure.Position('APAFrameRightPos',
                                                Q('0m'), yoffset, 0.5*(self.size[2]-self.footsize[1]))
        
        
        
        Placement_Foot   = geom.structure.Placement("placeAPAFrameFoot",
                                                    volume=Foot_lv,   pos=FootPosition,   rot='identity')
        Placement_Head   = geom.structure.Placement("placeAPAFrameHead",
                                                    volume=Head_lv,   pos=HeadPosition,   rot='identity')        
        Placement_Middle = geom.structure.Placement("placeAPAFrameMiddle",
                                                    volume=Middle_lv, pos=MiddlePosition, rot='r90aboutX')        
        Placement_Left   = geom.structure.Placement("placeAPAFrameLeft",
                                                    volume=Side_lv,   pos=LeftPosition,   rot='r90aboutX')
        Placement_Right  = geom.structure.Placement("placeAPAFrameRight",
                                                    volume=Side_lv,   pos=RightPosition,  rot='r90aboutX')
        
        frame_lv.placements.append(Placement_Foot  .name)
        frame_lv.placements.append(Placement_Head  .name)
        frame_lv.placements.append(Placement_Middle.name)
        frame_lv.placements.append(Placement_Left  .name)
        frame_lv.placements.append(Placement_Right .name)
        
        # print("low "+str(-0.5*self.size[1]))
        # print("hig "+str( 0.5*self.size[1]))

        LightPaddleBox = geom.shapes.Box('LightPaddle',
                                         dx=0.5*self.LightPaddle_x,
                                         dy=0.5*self.LightPaddle_y,
                                         dz=0.5*(self.size[2] - 2*Q('4in')))
        LightPaddle_lv = geom.structure.Volume('volLightPaddle', material='Acrylic', shape=LightPaddleBox)

        paddlePosition = 0.5*size_middle[2] - self.LightPaddleHeadOffset - 0.5*self.LightPaddle_y

        for i in range(self.nLightPaddlePerAPA):
            pos = geom.structure.Position('LightPaddlePosition_'+str(i),
                                          Q('0m'),
                                          paddlePosition - i*self.LightPaddleVerticalSpacing,
                                          Q('0m'))
            place = geom.structure.Placement('placeLightPaddle_'+str(i),
                                             volume = LightPaddle_lv,
                                             pos    = pos)
            frame_lv.placements.append(place.name)
        
        #^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
        for iRib in range(self.nribs):
            #posy = -0.5*self.size[1] + self.footsize[1] + (iRib+1) * (self.size[1] - 2*self.footsize[1]) / self.nribs
            posy = -0.5 * size_middle[2] + (1+iRib) * size_middle[2] / (self.nribs+1) + yoffset
            # print("Rib "+str(posy))
            name = 'APAFrameRib'+str(2*iRib+1)
            RibPosition = geom.structure.Position(name+'Pos',
                                                  Q('0m'), posy, 0.25*(self.size[2]-self.footsize[1]))
            Placement_Rib = geom.structure.Placement("place"+name, volume=Rib_lv, pos=RibPosition,
                                                     rot='r90aboutZ')
            frame_lv.placements.append(Placement_Rib.name)
            
            
            name = 'APAFrameRib'+str(2*iRib)
            RibPosition = geom.structure.Position(name+'Pos',
                                                  Q('0m'), posy, -0.25*(self.size[2]-self.footsize[1]))
            Placement_Rib = geom.structure.Placement("place"+name, volume=Rib_lv, pos=RibPosition,
                                                     rot='r90aboutZ')
            frame_lv.placements.append(Placement_Rib.name)


