#!/usr/bin/env python
'''
PMTs builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class PMTBuilder(gegede.builder.Builder):
    '''
    Build the PMTs for ProtoDUNE-VD.
    Implements both thick and slim field shapers arranged vertically.
    '''

    def configure(self,
                 pmt_parameters=None,
                 print_config=False,
                 print_construct=False,
                 **kwds):

        if print_config:
            print('Configure PMTs <- Cryostat <- ProtoDUNE-VD <- World')
        if hasattr(self, '_configured'):
            return

        if pmt_parameters:
            self.params = pmt_parameters

        # Generate all PMT positions
        self.generate_pmt_positions()

        self._configured = True
        self.print_construct = print_construct

    def generate_pmt_positions(self):
        '''Generate the full list of PMT positions'''
        self.pmt_positions = []

        # Helper to make position dictionary
        def make_pos(x=None, y=None, z=None):
            pos = {}
            pos['x'] = x if x is not None else Q('0cm')
            pos['y'] = y if y is not None else Q('0cm')
            pos['z'] = z if z is not None else Q('0cm')
            return pos

        y = self.params['pmt_y_positions']
        z = self.params['pmt_z_positions']

        # Vertical PMTs
        self.pmt_positions.extend([
            make_pos(y=y[4], z=z[4]),      # pos1 - y=-405.3, z=68.1
            make_pos(y=y[4], z=z[5]),      # pos2 - y=-405.3, z=0
            make_pos(y=y[0], z=z[5]),      # pos3 - y=405.3, z=0
            make_pos(y=y[0], z=z[4]),      # pos4 - y=405.3, z=68.1
            make_pos(y=y[1], z=z[1]),      # pos5 - y=170.0, z=204.0
            make_pos(y=y[2], z=z[1]),      # pos6 - y=0, z=204.0
            make_pos(y=y[3], z=z[1]),      # pos7 - y=-170.0, z=204.0
            make_pos(y=y[1], z=z[0]),      # pos8 - y=170.0, z=306.0
            make_pos(y=y[2], z=z[0]),      # pos9 - y=0, z=306.0
            make_pos(y=y[3], z=z[0]),      # pos10 - y=-170.0, z=306.0
        ])
         # Horizontal PMTs
        htop = self.params['horizontal_pmt_pos_top']
        hbot = self.params['horizontal_pmt_pos_bot']
        hz = self.params['horizontal_pmt_z']
        hy = self.params['horizontal_pmt_y']
        pmtoffset = self.params['pmt_offset']

        self.pmt_positions.extend([
            make_pos(x=htop, y=hy, z=hz),        # pos11 - # Horizontal PMTs nonTCO side PEN
            make_pos(x=hbot, y=hy, z=hz),        # pos12 - # Horizontal PMTs nonTCO side PEN
            make_pos(x=htop, y=-hy, z=hz),       # pos13 - # Horizontal PMTs TCO side TPB
            make_pos(x=hbot, y=-hy, z=hz),       # pos14 - # Horizontal PMTs TCO side TPB
            make_pos(y=y[1], z=z[2]),      # pos15 - y=170.0, z=-204.0
            make_pos(y=y[2], z=z[2]),      # pos16 - y=0, z=-204.0
            make_pos(y=y[3], z=z[2]),      # pos17 - y=-170.0, z=-204.0
            make_pos(y=y[1], z=z[3]),      # pos18 - y=170.0, z=-306.0
            make_pos(y=y[2], z=z[3]),      # pos19 - y=0, z=-306.0
            make_pos(y=y[3], z=z[3]),      # pos20 - y=-170.0, z=-306.0
        ])

        self.pmt_positions.extend([
            make_pos(x=htop, y=hy+pmtoffset, z=-hz),       # pos21 - # Horizontal PMTs near the beam plug TPB + offset
            make_pos(x=hbot, y=hy+pmtoffset, z=-hz),       # pos22 - # Horizontal PMTs near the beam plug TPB + offset
            make_pos(x=htop, y=-hy, z=-hz),      # pos23 - # Horizontal PMTs TCO side TPB
            make_pos(x=hbot, y=-hy, z=-hz),      # pos24 - # Horizontal PMTs TCO side TPB
        ])

    def construct(self, geom):
        if self.print_construct:
            print('Construct PMTs <- Cryostat <- ProtoDUNE-VD <- World')

        # Create PMT shapes
        # TPB plate shape
        pen_plate = geom.shapes.Tubs("PMT_PENPlate",
            rmin=Q('0cm'),
            rmax=Q('12cm'),
            dz=Q('0.125cm'),
            sphi=Q('0deg'),
            dphi=Q('360deg'))

        # Main PMT volume shape
        pmt_vol = geom.shapes.Tubs("PMTVolume",
            rmin=Q('0cm'),
            rmax=self.params['pmt_radius'],
            dz=self.params['pmt_height'],
            sphi=Q('0deg'),
            dphi=Q('360deg'))

        # PMT detailed shapes for realistic geometry
        mid_cylinder = geom.shapes.Tubs("pmtMiddleCylinder",
            rmin=Q('100.351822048586mm'),
            rmax=Q('102.351822048586mm'),
            dz=Q('54mm')/2.,
            sphi=Q('0deg'),
            dphi=Q('360deg'))

        # Top spherical part
        top_sphere = geom.shapes.Sphere("sphPartTop",
            rmin=Q('131mm'),
            rmax=Q('133mm'),
            sphi=Q('0deg'),
            dphi=Q('360deg'),
            stheta=Q('0deg'),
            dtheta=Q('50deg'))

        # Combine middle and top
        pmt_shape1 = geom.shapes.Boolean("pmt_shape1",
            type='union',
            first=mid_cylinder,
            second=top_sphere,
            pos=geom.structure.Position("pmt_pos1",
                x=Q('0mm'), y=Q('0mm'), z=Q('-57.2051768689367mm')))

        # Bottom spherical part
        btm_sphere = geom.shapes.Sphere("sphPartBtm",
            rmin=Q('131mm'),
            rmax=Q('133mm'),
            sphi=Q('0deg'),
            dphi=Q('360deg'),
            stheta=Q('130deg'),
            dtheta=Q('31.477975238527deg'))

        # Add bottom sphere
        pmt_shape2 = geom.shapes.Boolean("pmt_shape2",
            type='union',
            first=pmt_shape1,
            second=btm_sphere,
            pos=geom.structure.Position("pmt_pos2",
                x=Q('0mm'), y=Q('0mm'), z=Q('57.2051768689367mm')))

        # Bottom tube
        btm_tube = geom.shapes.Tubs("pmtBtmTube",
            rmin=Q('42.25mm'),
            rmax=Q('44.25mm'),
            dz=Q('72mm')/2.,
            sphi=Q('0deg'),
            dphi=Q('360deg'))

        # Final PMT solid
        solid_pmt = geom.shapes.Boolean("solidpmt",
            type='union',
            first=pmt_shape2,
            second=btm_tube,
            pos=geom.structure.Position("pmt_pos3",
                x=Q('0mm'), y=Q('0mm'), z=Q('-104.905637496842mm')))

        # TPB coating layer
        coating = geom.shapes.Sphere("pmt_coating",
            rmin=Q('133mm'),
            rmax=Q('133.2mm'),
            sphi=Q('0deg'),
            dphi=Q('360deg'),
            stheta=Q('0deg'),
            dtheta=Q('50deg'))

        # Create volumes
        coat_vol = geom.structure.Volume("volOpDetSensitive_pmtCoatVol",
            material="LAr",
            shape=coating)
        #coat_vol.params.append(("SensDet","PhotonDetector"))

        pmt_main_vol = geom.structure.Volume("allpmt",
            material="Glass",
            shape=solid_pmt)

        # Create TPB-coated PMT volume
        pmt_coated_vol = geom.structure.Volume("volPMT_coated",
            material="LAr",
            shape=pmt_vol)

        # Place PMT and coating in coated volume
        pmt_pos = geom.structure.Position("posallpmt",
            x=Q('0cm'), y=Q('0cm'), z=Q('1.27*2.54cm'))
        coat_pos = geom.structure.Position("posOpDetSensitive0",
            x=Q('0cm'), y=Q('0cm'), z=Q('1.27*2.54cm - 2.23*2.54cm'))

        pmt_place = geom.structure.Placement("pmt_place",
            volume=pmt_main_vol, pos=pmt_pos)
        coat_place = geom.structure.Placement("coat_place",
            volume=coat_vol, pos=coat_pos)

        pmt_coated_vol.placements.append(pmt_place.name)
        pmt_coated_vol.placements.append(coat_place.name)

        # Create PEN foil PMT volume
        pen_vol = geom.structure.Volume("volOpDetSensitive_pmtFoilVol",
            material="LAr",
            shape=pen_plate)
        #pen_vol.params.append(("SensDet","PhotonDetector"))

        pmt_foil_vol = geom.structure.Volume("volPMT_foil",
            material="LAr",
            shape=pmt_vol)

        # Place PMT and foil in foil volume
        pmt_pos2 = geom.structure.Position("posallpmt2",
            x=Q('0cm'), y=Q('0cm'), z=Q('1.27*2.54cm'))
        foil_pos = geom.structure.Position("posOpDetSensitive1",
            x=Q('0cm'), y=Q('0cm'), z=Q('1.27*2.54cm+7.9cm'))

        pmt_place2 = geom.structure.Placement("pmt_place2",
            volume=pmt_main_vol, pos=pmt_pos2)
        foil_place = geom.structure.Placement("foil_place",
            volume=pen_vol, pos=foil_pos)

        pmt_foil_vol.placements.append(pmt_place2.name)
        pmt_foil_vol.placements.append(foil_place.name)

        # Add volumes to builder
        self.add_volume(pmt_coated_vol)
        self.add_volume(pmt_foil_vol)


    def place_pmts(self, geom, cryo_vol):
        '''Place PMTs in cryostat volume'''

        # Loop through all PMT positions
        for i in range(len(self.pmt_positions)):
            k = i + 1

            # Determine rotation based on PMT location
            if k in self.params['pmt_left_rotated']:
                rot = 'rPlus180AboutX'
            elif k in self.params['pmt_right_rotated']:
                rot = 'rIdentity'
            else:
                rot = 'rMinus90AboutY'


            # Determine PMT type (coated vs foil)
            pmt_type = 'volPMT_coated' if k in self.params['pmt_TPB'] else 'volPMT_foil'
            pmt_vol = self.get_volume(pmt_type)

            # Get PMT position
            if k in self.params['pmt_left_rotated'] or k in self.params['pmt_right_rotated']:
                pos = geom.structure.Position(f"posPMT{i}", **self.pmt_positions[i])
            else:
                pos_dict = self.pmt_positions[i]
                pos_dict['x'] = self.params['pmt_pos_x']
                pos = geom.structure.Position(f"posPMT{i}", **pos_dict)


            # Create and add placement
            place = geom.structure.Placement(f"placePMT{i}",
            volume=pmt_vol,
            pos=pos,
            rot=rot)




            cryo_vol.placements.append(place.name)
