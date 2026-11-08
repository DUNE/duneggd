#!/usr/bin/env python
'''
Main builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

# Import the CryostatBuilder
from cryostat import CryostatBuilder
from foam import FoamBuilder
from steelsupport import SteelSupportBuilder
from beamelements import BeamElementsBuilder

class ProtoDUNEVDBuilder(gegede.builder.Builder):
    '''
    Build the ProtoDUNE-VD detector enclosure and components
    '''

    def __init__(self, name):
        super(ProtoDUNEVDBuilder, self).__init__(name)

        # Initialize parameters as None
        self.cryo = None
        self.tpc = None
        self.steel = None
        self.cathode = None
        self.fieldcage = None
        self.pmt = None

        self.DetEncX = None
        self.DetEncY = None
        self.DetEncZ = None

        self.OriginXSet = None
        self.OriginYSet = None
        self.OriginZSet = None

        self.DP_CRT_switch = None  # Add this line
        self.HD_CRT_switch = None  # Add this line

        # Add the subbuilders
        # for name, builder in self.builders.items():
        #     self.add_builder(name, builder)

    def configure(self, cryostat_parameters=None, tpc_parameters=None,
                 steel_parameters=None, beam_parameters=None, crt_parameters=None,
                 cathode_parameters=None, xarapuca_parameters=None,
                 fieldcage_parameters=None,
                 pmt_parameters=None,
                 DetEncX=None, DetEncY=None, DetEncZ=None, FoamPadding=None,
                 OriginXSet=None, OriginYSet=None, OriginZSet=None,
                 cathode_switch=True, fieldcage_switch=True, arapucamesh_switch=True,  # Add these lines
                 DP_CRT_switch=None, HD_CRT_switch=None,  # Add these lines
                 print_config=False,
                 print_construct=False,
                 **kwds):

        if print_config:
            print('Configure ProtoDUNE-VD <- World')
        # Add guard against double configuration
        if hasattr(self, '_configured'):
            return

        # Store the parameters
        self.DetEncX = DetEncX
        self.DetEncY = DetEncY
        self.DetEncZ = DetEncZ
        self.FoamPadding = FoamPadding

        # Store Origin coordinates
        self.OriginXSet = OriginXSet
        self.OriginYSet = OriginYSet
        self.OriginZSet = OriginZSet

        if cryostat_parameters:
            self.cryo = cryostat_parameters
        if tpc_parameters:
            self.tpc = tpc_parameters
        if steel_parameters:
            self.steel = steel_parameters
        if cathode_parameters:
            self.cathode = cathode_parameters
        if xarapuca_parameters:
            self.xarapuca = xarapuca_parameters
        if fieldcage_parameters:
            self.fieldcage = fieldcage_parameters
        if pmt_parameters:
            self.pmt = pmt_parameters

        self.cathode_switch = cathode_switch  # Add this line
        self.fieldcage_switch = fieldcage_switch  # Add this line
        self.arapucamesh_switch = arapucamesh_switch  # Add this line

        # Store CRT switch settings
        self.DP_CRT_switch = DP_CRT_switch
        self.HD_CRT_switch = HD_CRT_switch

        self.print_construct = print_construct
        # Mark as configured
        self._configured = True

        # Pass parameters to sub builders
        for name, builder in self.builders.items():
            if name == 'beamelements':
                builder.configure(steel_parameters=self.steel,
                    cryostat_parameters=self.cryo,
                    beam_parameters=beam_parameters,
                    FoamPadding=self.FoamPadding,
                    OriginXSet=self.OriginXSet,  # Add these three lines
                    OriginYSet=self.OriginYSet,
                    OriginZSet=self.OriginZSet,
                    print_config=print_config,
                    print_construct=print_construct,
                    **kwds)
            if name == 'cryostat':
                builder.configure(cryostat_parameters=self.cryo,
                      tpc_parameters=self.tpc,
                      cathode_parameters=self.cathode,
                      xarapuca_parameters=self.xarapuca,
                      fieldcage_parameters=self.fieldcage,
                      pmt_parameters=self.pmt,
                      cathode_switch=self.cathode_switch,  # Add this line
                      fieldcage_switch=self.fieldcage_switch,  # Add this line
                      arapucamesh_switch=self.arapucamesh_switch,  # Add this line
                      print_config=print_config,
                      print_construct=print_construct,
                      **kwds)
            if name == 'crt':
                builder.configure(crt_parameters=crt_parameters,
                    steel_parameters=self.steel,
                    OriginXSet=self.OriginXSet,
                    OriginYSet=self.OriginYSet,
                    OriginZSet=self.OriginZSet,
                    DP_CRT_switch=self.DP_CRT_switch,  # Add this line
                    HD_CRT_switch=self.HD_CRT_switch,  # Add this line
                    print_config=print_config,
                    print_construct=print_construct,
                    **kwds)
            if name == 'steelsupport':
                builder.configure(steel_parameters=self.steel,
                    print_config=print_config,
                    print_construct=print_construct,
                    **kwds)
            if name == 'foam':
                builder.configure(
                    FoamPadding=self.FoamPadding,
                    cryostat_parameters=self.cryo,
                    steel_parameters=self.steel,
                    beam_parameters=beam_parameters,
                    print_config=print_config,
                    print_construct=print_construct,
                    **kwds
                )

    def construct(self, geom):
        if self.print_construct:
            print('Construct ProtoDUNE-VD <- World')

        # Create the main volume
        main_shape = geom.shapes.Box(self.name + '_shape',
                                   dx=self.DetEncX,
                                   dy=self.DetEncY,
                                   dz=self.DetEncZ)

        main_lv = geom.structure.Volume(self.name,
                                      material='Air',
                                      shape=main_shape)

        # Get the cryostat volume from the cryostat builder
        cryo_builder = self.get_builder("cryostat")
        cryo_vol = cryo_builder.get_volume()

        # Place beam elements - add this
        beam_builder = self.get_builder("beamelements")
        beam_builder.place_in_volume(geom, main_lv, cryo_vol)

        # Place steel support structure
        steel_builder = self.get_builder("steelsupport")
        steel_builder.place_in_volume(geom, main_lv)

        # Place foam padding
        foam_builder = self.get_builder("foam")
        foam_builder.place_in_volume(geom, main_lv)

        # Place CRT modules
        crt_builder = self.get_builder('crt')
        crt_builder.place_in_volume(geom, main_lv)

        # NOTICE: volCryostat has to be added at the end per LArSoft requirement
        # Add the cryostat placement to the detector enclosure volume
        # Create a placement for the cryostat in the detector enclosure
        # Place it at the center (0,0,0) since the PERL script shows posCryoInDetEnc=(0,0,0)
        cryo_pos = geom.structure.Position(
            "cryo_pos",
            x=Q('0cm'),
            y=Q('0cm'),
            z=Q('0cm'))

        cryo_place = geom.structure.Placement(
            "cryo_place",
            volume=cryo_vol,
            pos=cryo_pos)
        main_lv.placements.append(cryo_place.name)

        self.add_volume(main_lv)
