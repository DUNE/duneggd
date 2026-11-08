#!/usr/bin/env python
'''
Foam Builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class FoamBuilder(gegede.builder.Builder):
    '''Build the foam for ProtoDUNE-VD'''

    def configure(self,
                 FoamPadding=None,
                 cryostat_parameters=None,
                 steel_parameters=None,
                 beam_parameters=None,
                 print_config=False,
                 print_construct=False,
                 **kwargs):

        if print_config:
            print('Configure Foam <- ProtoDUNE-VD <- World')

        self.print_construct = print_construct
        self.FoamPadding = FoamPadding
        self.cryo = cryostat_parameters
        self.steel = steel_parameters
        self.beam = beam_parameters

    def construct(self, geom):
        if self.print_construct:
            print('Construct Foam <- ProtoDUNE-VD <- World')

        # Create the main foam block shape
        foam_block = geom.shapes.Box(
            "FoamPadBlock",
            dx=(self.cryo['Cryostat_x'] + 2*self.FoamPadding)/2,
            dy=(self.cryo['Cryostat_y'] + 2*self.FoamPadding)/2,
            dz=(self.cryo['Cryostat_z'] + 2*self.FoamPadding)/2
        )
        # Create steel plate block shape
        steel_plate_block = geom.shapes.Box(
            "SteelPlateBlock",
            dx=(self.cryo['Cryostat_x'] + 2*self.FoamPadding + 2*self.steel['SteelPlate'])/2,
            dy=(self.cryo['Cryostat_y'] + 2*self.FoamPadding + 2*self.steel['SteelPlate'])/2,
            dz=(self.cryo['Cryostat_z'] + 2*self.FoamPadding + 2*self.steel['SteelPlate'])/2
        )

        # Create steel support block shape
        steel_support_block = geom.shapes.Box(
            "SteelSupportBlock",
            dx=(self.cryo['Cryostat_x'] + 2*self.FoamPadding + 2*self.steel['SteelSupport_x'])/2,
            dy=(self.cryo['Cryostat_y'] + 2*self.FoamPadding + 2*self.steel['SteelSupport_y'])/2,
            dz=(self.cryo['Cryostat_z'] + 2*self.FoamPadding + 2*self.steel['SteelSupport_z'])/2
        )

        # Create cryostat shape to subtract
        cryostat_builder = self.get_builder('cryostat')
        cryostat_vol = cryostat_builder.get_volume('volCryostat')
        cryo_shape = cryostat_vol.shape
        #cryo_shape = geom.shapes.Box(
        #    "cryo_shape",
        #    dx=self.cryo['Cryostat_x']/2,
        #    dy=self.cryo['Cryostat_y']/2,
        #    dz=self.cryo['Cryostat_z']/2
        #)

        # Create subtraction to make foam shell
        foam_nobw = geom.shapes.Boolean(
            "FoamPaddingNoBW",
            type='subtraction',
            first=foam_block,
            second=cryo_shape
        )
        steel_support_nobw = geom.shapes.Boolean(
            "SteelSupportNoBW",
            type='subtraction',
            first=steel_support_block,
            second=foam_block
        )

        # Get beam window parameters   These are the same as the beam elements ...
        bw_foam_rem = geom.shapes.CutTubs(
            "BeamWindowFoamRemp",
            rmin=Q('0cm'),
            rmax=self.beam['BeamPipeRad'],
            dz=self.beam['BeamWFoRemLe']/2,
            sphi=Q('0deg'),
            dphi=Q('360deg'),
            normalm=(-0.71030185483404029, 0, -0.70389720486682006),
            normalp=(0.71030185483404018, 0, 0.70389720486682017)
        )
        bw_steel_plate = geom.shapes.CutTubs(
            "BeamWindowStPlatep",
            rmin=Q('0cm'),
            rmax=self.beam['BeamPipeRad'],
            dz=self.beam['BeamWStPlateLe']/2,
            sphi=Q('0deg'),
            dphi=Q('360deg'),
            normalm=(-0.71030185483404029, 0, -0.70389720486682006),
            normalp=(0.71030185483404018, 0, 0.70389720486682017)
        )

        # Final foam shape with beam window hole
        foam_shape = geom.shapes.Boolean(
            "FoamPadding",
            type='subtraction',
            first=foam_nobw,
            second=bw_foam_rem,
            pos=geom.structure.Position(
                "posBWFoPa",
                x=self.beam['BeamWFoRem_x'],
                y=self.beam['BeamWFoRem_y'],
                z=self.beam['BeamWFoRem_z']
            ),
            rot='rBeamW3'
        )
        # Final steel support shape with beam window hole
        steel_support_shape = geom.shapes.Boolean(
            "SteelSupport",
            type='subtraction',
            first=steel_support_nobw,
            second=bw_steel_plate,
            pos=geom.structure.Position(
                "posBWStPl",
                x=self.beam['BeamWStPlate_x'],
                y=self.beam['BeamWStPlate_y'],
                z=self.beam['BeamWStPlate_z']
            ),
            rot='rBeamW3'
        )

        # Create foam volume
        foam_vol = geom.structure.Volume(
            "volFoamPadding",
            material="foam_protoDUNE_RPUF_assayedSample",
            shape=foam_shape
        )

        steel_support_vol = geom.structure.Volume(
            "volSteelSupport",
            material="STEEL_STAINLESS_Fe7Cr2Ni",
            shape=steel_support_shape
        )

        # Add volumes
        self.add_volume(foam_vol)
        self.add_volume(steel_support_vol)

    def place_in_volume(self, geom, main_lv):
        """Place foam padding in the main volume"""
        foam_vol = self.get_volume('volFoamPadding')

        foam_pos = geom.structure.Position(
            "posFoamPadding",
            x=self.steel['posCryoInDetEnc']['x'],
            y=self.steel['posCryoInDetEnc']['y'],
            z=self.steel['posCryoInDetEnc']['z']
        )

        foam_place = geom.structure.Placement(
            "placeFoamPadding",
            volume=foam_vol,
            pos=foam_pos
        )

        main_lv.placements.append(foam_place.name)

        # Place steel support
        steel_vol = self.get_volume('volSteelSupport')
        steel_pos = geom.structure.Position(
            "posSteelSupport",
            x=self.steel['posCryoInDetEnc']['x'],
            y=self.steel['posCryoInDetEnc']['y'],
            z=self.steel['posCryoInDetEnc']['z']
        )
        steel_place = geom.structure.Placement(
            "placeSteelSupport",
            volume=steel_vol,
            pos=steel_pos
        )
        main_lv.placements.append(steel_place.name)
