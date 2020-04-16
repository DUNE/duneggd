#!/usr/bin/env python
'''
Subbuilder of the FieldCage
'''

import gegede.builder
from gegede import Quantity as Q
from gegede import units

class FieldCageBuilder(gegede.builder.Builder):
    '''
    Build the field cage
    '''
    # ^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def configure(self,
                  barWidth            = None,
                  barHeight           = None,
                  horizontalBarLength = None,
                  verticalBarLength   = None,
                  material            = None,
                  APAFrameSize        = None,
                  APAGap_y            = None,
                  APAGap_z            = None,
                  **kwds):
        self.barWidth            = barWidth           
        self.barHeight           = barHeight          
        self.horizontalBarLength = horizontalBarLength
        self.verticalBarLength   = verticalBarLength  
        self.material            = material
        self.APAFrameSize        = APAFrameSize
        self.APAGap_y            = APAGap_y 
        self.APAGap_z            = APAGap_z

    # ^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
    def construct(self, geom):

        ii = 0
        lenHorizontalBar = (25*self.APAFrameSize[2]) + (24*self.APAGap_z)
        lenVerticalBar   = (2 *self.APAFrameSize[1]) + (1 *self.APAGap_y)
        CageBox = geom.shapes.Box('CageSegment',
                                  dx=0.5*(Q("6cm")*250),
                                  dy=0.5*Q('100m'),
                                  dz=0.5*Q('100m'))
        cage_lv = geom.structure.Volume('volFieldCage_'+str(ii), material=self.material, shape=CageBox)
        self.add_volume(cage_lv)

        # Make the horizontal beam
        HorizontalBox = geom.shapes.Box('FieldCageHorizontalSegment',
                                        dx=0.5*self.barWidth,
                                        dy=0.5*self.barHeight,
                                        dz=0.5*lenHorizontalBar)
        Horizontal_lv = geom.structure.Volume('vol_FieldCageHorizontalSegment', material=self.material, shape=HorizontalBox)

        # Make the vertical beam
        VerticalBox = geom.shapes.Box('FieldCageVerticalSegment',
                                      dx=0.5*self.barWidth,
                                      dy=0.5*(lenVerticalBar-(2*self.barHeight)),
                                      dz=0.5*self.barHeight)
        Vertical_lv = geom.structure.Volume('vol_FieldCageVerticalSegment', material=self.material, shape=VerticalBox)
        
        posHorizontal = [Q("3cm"), 0.5*(lenVerticalBar-self.barHeight), Q("0m")]
        posVertical   = [Q("3cm"), Q("0m"), 0.5*(lenHorizontalBar-self.barHeight)]

        for i in range(123):
            # Define the positions of the bar
            topBeamPos = geom.structure.Position('TopBeamPos_'+str(i)    ,
                                                 posHorizontal[0]+(i*Q("6cm")),  posHorizontal[1], posHorizontal[2])
            botBeamPos = geom.structure.Position('BottomBeamPos_'+str(i) ,
                                                 posHorizontal[0]+(i*Q("6cm")), -posHorizontal[1], posHorizontal[2])
            lefBeamPos = geom.structure.Position('LeftBeamPos_'+str(i)   ,
                                                 posVertical[0]+(i*Q("6cm")), posVertical[1],  posVertical[2])
            rigBeamPos = geom.structure.Position('RightBeamPos_'+str(i)  ,
                                                 posVertical[0]+(i*Q("6cm")), posVertical[1], -posVertical[2])

            topBeamNeg = geom.structure.Position('TopBeamPos_-'+str(i)    ,
                                                 -posHorizontal[0]-(i*Q("6cm")),  posHorizontal[1], posHorizontal[2])
            botBeamNeg = geom.structure.Position('BottomBeamPos_-'+str(i) ,
                                                 -posHorizontal[0]-(i*Q("6cm")), -posHorizontal[1], posHorizontal[2])
            lefBeamNeg = geom.structure.Position('LeftBeamPos_-'+str(i)   ,
                                                 -posVertical[0]-(i*Q("6cm")), posVertical[1],  posVertical[2])
            rigBeamNeg = geom.structure.Position('RightBeamPos_-'+str(i)  ,
                                                 -posVertical[0]-(i*Q("6cm")), posVertical[1], -posVertical[2])

            
            # Define the placements of the volumes
            Placement_topBeamPos = geom.structure.Placement('placeTopBeam_'+str(i)    , volume=Horizontal_lv, pos=topBeamPos)
            Placement_botBeamPos = geom.structure.Placement('placeBottomBeam_'+str(i) , volume=Horizontal_lv, pos=botBeamPos)
            Placement_lefBeamPos = geom.structure.Placement('placeLeftBeam_'+str(i)   , volume=Vertical_lv  , pos=lefBeamPos)
            Placement_rigBeamPos = geom.structure.Placement('placeRightBeam_'+str(i)  , volume=Vertical_lv  , pos=rigBeamPos)

            Placement_topBeamNeg = geom.structure.Placement('placeTopBeam_-'+str(i)    , volume=Horizontal_lv, pos=topBeamNeg)
            Placement_botBeamNeg = geom.structure.Placement('placeBottomBeam_-'+str(i) , volume=Horizontal_lv, pos=botBeamNeg)
            Placement_lefBeamNeg = geom.structure.Placement('placeLeftBeam_-'+str(i)   , volume=Vertical_lv  , pos=lefBeamNeg)
            Placement_rigBeamNeg = geom.structure.Placement('placeRightBeam_-'+str(i)  , volume=Vertical_lv  , pos=rigBeamNeg)

            cage_lv.placements.append(Placement_topBeamPos.name)
            cage_lv.placements.append(Placement_botBeamPos.name)
            cage_lv.placements.append(Placement_lefBeamPos.name)
            cage_lv.placements.append(Placement_rigBeamPos.name)

            cage_lv.placements.append(Placement_topBeamNeg.name)
            cage_lv.placements.append(Placement_botBeamNeg.name)
            cage_lv.placements.append(Placement_lefBeamNeg.name)
            cage_lv.placements.append(Placement_rigBeamNeg.name)
        
