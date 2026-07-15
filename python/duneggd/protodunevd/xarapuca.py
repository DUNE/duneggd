#!/usr/bin/env python
'''
xarapuca builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class XARAPUCABuilder(gegede.builder.Builder):
    '''
    Build the Xarapucas for ProtoDUNE-VD.
    '''

    def __init__(self, name):
        super(XARAPUCABuilder, self).__init__(name)
        self.params = None
        self.cathode = None

    def configure(self, xarapuca_parameters=None, cathode_parameters=None, print_config=False, print_construct=False, **kwargs):
        """Configure the X-ARAPUCA geometry.

        Args:
            xarapuca_parameters: Dictionary containing X-ARAPUCA parameters
            cathode_parameters: Dictionary containing cathode parameters
            print_config: Whether to print configuration info
            print_construct: Whether to print construct info
            **kwargs: Additional configuration parameters
        """
        if print_config:
            print('Configure XARAPUCA <- Cryostat <- ProtoDUNE-VD <- World')
        if hasattr(self, '_configured'):
            return

        # Store parameters
        if xarapuca_parameters:
            self.params = xarapuca_parameters
        if cathode_parameters:
            self.cathode = cathode_parameters

        self.print_construct = print_construct

        # Calculate additional parameters
        if self.params and self.cathode:


            # Calculate positions of the 4 arapucas with respect to the Frame center
            self.list_posx_bot = []
            self.list_posz_bot = []

            # First arapuca
            self.list_posx_bot.append(-1.0*self.cathode['widthCathodeVoid'] -
                                    2.0*self.cathode['CathodeBorder'] -
                                    self.params['GapPD'] -
                                    0.5*self.params['ArapucaOut_x'])
            self.list_posz_bot.append(-0.5*self.cathode['lengthCathodeVoid'] -
                                    self.cathode['CathodeBorder'])

            # Second arapuca
            self.list_posx_bot.append(self.cathode['widthCathodeVoid'] +
                                    self.cathode['CathodeBorder'] -
                                    self.params['GapPD'] -
                                    0.5*self.params['ArapucaOut_x'])
            self.list_posz_bot.append(-1.5*self.cathode['lengthCathodeVoid'] -
                                    2.0*self.cathode['CathodeBorder'])

            # Third arapuca
            self.list_posx_bot.append(-self.cathode['CathodeBorder'] -
                                    self.params['GapPD'] -
                                    0.5*self.params['ArapucaOut_x'])
            self.list_posz_bot.append(-self.list_posz_bot[1])

            # Fourth arapuca
            self.list_posx_bot.append(2.0*self.cathode['widthCathodeVoid'] +
                                    2.0*self.cathode['CathodeBorder'] -
                                    self.params['GapPD'] -
                                    0.5*self.params['ArapucaOut_x'])
            self.list_posz_bot.append(-self.list_posz_bot[0])

        if self.params:
            # Calculate derived mesh parameters
            self.params['MeshInnerStructureSeparation'] = (
                self.params['MeshInnerStructureSeparation_base'] +
                self.params['MeshRodOuterRadius']
            )

            # Calculate number of mesh bars for cathode X-ARAPUCA
            if self.cathode:
                self.params['CathodeArapucaMeshNumberOfBars_vertical'] = int(
                    self.cathode['lengthCathodeVoid'] /
                    self.params['CathodeArapucaMeshRodSeparation']
                )
                self.params['CathodeArapucaMeshNumberOfBars_horizontal'] = int(
                    self.cathode['widthCathodeVoid'] /
                    self.params['CathodeArapucaMeshRodSeparation']
                )

            # Calculate distance between mesh and window
            self.params['Distance_Mesh_Window'] = Q('1.8cm') + self.params['MeshOuterRadius']

        self._configured = True

    def construct_cathode_mesh(self, geom):
        """Construct mesh for double-sided cathode X-ARAPUCAs"""


        # Create outer module box to contain the mesh
        module_shape = geom.shapes.Box(
            "CathodeArapucaMeshModule",
            dx=2*self.params['CathodeArapucaMeshRodRadius'],
            dy=self.cathode['widthCathodeVoid']/2.,
            dz=self.cathode['lengthCathodeVoid']/2.
        )

        # Create vertical rod shape
        vert_rod = geom.shapes.Tubs(
            "CathodeArapucaMeshRod_vertical",
            rmin=Q('0cm'),
            rmax=self.params['CathodeArapucaMeshRodRadius'],
            dz=self.cathode['widthCathodeVoid']/2.
        )

        # Create horizontal rod shape
        horiz_rod = geom.shapes.Tubs(
            "CathodeArapucaMeshRod_horizontal",
            rmin=Q('0cm'),
            rmax=self.params['CathodeArapucaMeshRodRadius'],
            dz=self.cathode['lengthCathodeVoid']/2.,
        )

        # Create volume for module
        mesh_vol = geom.structure.Volume(
            "volCathodeArapucaMesh",
            material="LAr",
            shape=module_shape
        )

        # print(int(self.params['CathodeArapucaMeshNumberOfBars_vertical']),int(self.params['CathodeArapucaMeshNumberOfBars_horizontal']))

        # Add vertical rods
        n_vert = int(self.params['CathodeArapucaMeshNumberOfBars_vertical'])
        for i in range(n_vert):
            # Create volume for vertical rod
            vert_rod_vol = geom.structure.Volume(
                f"volCathodeArapucaMeshRod_vertical_{i}",
                material="STEEL_STAINLESS_Fe7Cr2Ni",
                shape=vert_rod
            )

            # Place vertical rod in module
            pos = geom.structure.Position(
                f"posCathodeMeshRod_vertical{i}",
                x=-(self.params['CathodeArapucaMeshRodRadius']),
                y=Q('0cm'),
                z=-self.cathode['lengthCathodeVoid']/2 + \
                self.params['CathodeArapucaMesh_verticalOffset'] + \
                i*self.params['CathodeArapucaMeshRodSeparation']
            )

            place = geom.structure.Placement(
                f"placeCathodeMeshRod_vertical{i}",
                volume=vert_rod_vol,
                pos=pos,
                rot='rPlus90AboutX'
            )
            mesh_vol.placements.append(place.name)

        # Add horizontal rods
        n_horiz = int(self.params['CathodeArapucaMeshNumberOfBars_horizontal'])
        for i in range(n_horiz):
            # Create volume for horizontal rod
            horiz_rod_vol = geom.structure.Volume(
                f"volCathodeArapucaMeshRod_horizontal_{i}",
                material="STEEL_STAINLESS_Fe7Cr2Ni",
                shape=horiz_rod
            )

            # Place horizontal rod in module
            pos = geom.structure.Position(
                f"posCathodeMeshRod_horizontal{i}",
                x=(self.params['CathodeArapucaMeshRodRadius']),
                y=-self.cathode['widthCathodeVoid']/2 + \
                self.params['CathodeArapucaMesh_horizontalOffset'] + \
                i*self.params['CathodeArapucaMeshRodSeparation'],
                z=Q('0cm')
            )

            place = geom.structure.Placement(
                f"placeCathodeMeshRod_horizontal{i}",
                volume=horiz_rod_vol,
                pos=pos,
            )
            mesh_vol.placements.append(place.name)

        self.add_volume(mesh_vol)
        return mesh_vol

    def construct_membrane_mesh(self, geom):
        """Construct mesh for membrane X-ARAPUCAs following PERL implementation"""

        # Create module box
        module = geom.shapes.Box(
            "ArapucaMeshModule",
            dx=(self.params['MeshInnerStructureLength_horizontal']
             + 2*(self.params['MeshOuterRadius'] + self.params['MeshTorRad']))/2,
            dy=(2*self.params['MeshRodOuterRadius'] + Q('1cm'))/2,
            dz=(self.params['MeshInnerStructureLength_vertical'] +
            2*(self.params['MeshOuterRadius'] +Q('1cm')
            #    + self.params['MeshTorRad'])  this volume leads to a overlapping situation
            ))/2
        )

        # Create main mesh volume
        mesh_vol = geom.structure.Volume(
            "volArapucaMesh",
            material="LAr",
            shape=module
        )

        # Create base shapes
        corner = geom.shapes.Torus(
            "ArapucaMeshCorner",
            rmin=Q('0cm'),
            rmax=self.params['MeshOuterRadius'],
            rtor=self.params['MeshTorRad'],
            startphi=Q('0deg'),
            deltaphi=Q('90deg')
        )

        tube_vert = geom.shapes.Tubs(
            "ArapucaMeshtube_vertical",
            rmin=Q('0cm'),
            rmax=self.params['MeshOuterRadius'],
            dz=self.params['MeshTubeLength_vertical']/2.
        )

        tube_horiz = geom.shapes.Tubs(
            "ArapucaMeshtube_horizontal",
            rmin=Q('0cm'),
            rmax=self.params['MeshOuterRadius'],
            dz=self.params['MeshTubeLength_horizontal']/2.
        )

        mesh_params = [
            {
                "name": "union1",
                "second": corner,
                "pos": (-self.params['MeshTorRad'], Q('0cm'), self.params['MeshTubeLength_vertical']/2),
                "rot": {'x': '90deg', 'y': '0deg', 'z': '0deg'}
            },
            {
                "name": "union2",
                "second": tube_horiz,
                "pos": (-(self.params['MeshTubeLength_horizontal']/2 + self.params['MeshTorRad']),
                        Q('0cm'),
                        self.params['MeshTubeLength_vertical']/2 + self.params['MeshTorRad']),
                "rot": {'x': '0deg', 'y': '90deg', 'z': '0deg'}
            },
            {
                "name": "union3",
                "second": corner,
                "pos": (-(self.params['MeshTubeLength_horizontal'] + self.params['MeshTorRad']),
                        Q('0cm'),
                        self.params['MeshTubeLength_vertical']/2),
                "rot": {'x': '90deg', 'y': '270deg', 'z': '0deg'}
            },
            {
                "name": "union4",
                "second": tube_vert,
                "pos": (-(self.params['MeshTubeLength_horizontal'] + 2*self.params['MeshTorRad']),
                        Q('0cm'),
                        Q('0cm')),
                "rot": {'x': '0deg', 'y': '0deg', 'z': '0deg'}
            },
            {
                "name": "union5",
                "second": corner,
                "pos": (-(self.params['MeshTubeLength_horizontal'] + self.params['MeshTorRad']),
                        Q('0cm'),
                        -self.params['MeshTubeLength_vertical']/2),
                "rot": {'x': '90deg', 'y': '180deg', 'z': '0deg'}
            },
            {
                "name": "union6",
                "second": tube_horiz,
                "pos": (-(self.params['MeshTubeLength_horizontal']/2 + self.params['MeshTorRad']),
                        Q('0cm'),
                        -(self.params['MeshTubeLength_vertical']/2 + self.params['MeshTorRad'])),
                "rot": {'x': '0deg', 'y': '90deg', 'z': '0deg'}
            },
            {
                "name": "union7",
                "second": corner,
                "pos": (-self.params['MeshTorRad'],
                        Q('0cm'),
                        -self.params['MeshTubeLength_vertical']/2),
                "rot": {'x': '90deg', 'y': '90deg', 'z': '0deg'}
            }
        ]

        # Build frame through loop
        mesh_shape = tube_vert  # Start with vertical tube
        for i, params in enumerate(mesh_params, 1):
            pos = geom.structure.Position(
                f"Mesh{params['name']}",
                x=params['pos'][0],
                y=params['pos'][1],
                z=params['pos'][2]
            )

            rot = geom.structure.Rotation(
                f"Meshrot{i}",
                x=params['rot']['x'],
                y=params['rot']['y'],
                z=params['rot']['z']
            )

            mesh_shape = geom.shapes.Boolean(
                f"Meshunion{i}",
                type='union',
                first=mesh_shape,
                second=params['second'],
                pos=pos,
                rot=rot
            )

        mesh_final = mesh_shape  # Final result

        # Add frame
        mesh_frame = geom.structure.Volume(
            "volMeshunion",
            material="STEEL_STAINLESS_Fe7Cr2Ni",
            shape=mesh_final
        )

        # Place frame in mesh volume
        mesh_vol.placements.append(
            geom.structure.Placement(
            "meshframe_place",
            volume=mesh_frame,
            pos=geom.structure.Position(
            "meshframe_pos",
            x=self.params['MeshTubeLength_horizontal']/2 + self.params['MeshTorRad'],
            y=Q('0cm'),
            z=Q('0cm')
            )
            ).name
        )



        # Create volumes for mesh parts and rods
        rod_vol_vert = geom.structure.Volume(
            "volArapucaMeshRod_vertical",
            material="STEEL_STAINLESS_Fe7Cr2Ni",
            shape=geom.shapes.Tubs(
            "ArapucaMeshRod_vertical",
            rmin=Q('0cm'),
            rmax=self.params['MeshRodOuterRadius'],
            dz=self.params['MeshInnerStructureLength_vertical']/2.
            )
        )

        rod_vol_horiz = geom.structure.Volume(
            "volArapucaMeshRod_horizontal",
            material="STEEL_STAINLESS_Fe7Cr2Ni",
            shape=geom.shapes.Tubs(
            "ArapucaMeshRod_horizontal",
            rmin=Q('0cm'),
            rmax=self.params['MeshRodOuterRadius'],
            dz=self.params['MeshInnerStructureLength_horizontal']/2.
            )
        )

        # Add vertical rods
        for i in range(self.params['MeshInnerStructureNumberOfBars_vertical']):
            mesh_vol.placements.append(
            geom.structure.Placement(
            f"meshrod_v_{i}_place",
            volume=rod_vol_vert,
            pos=geom.structure.Position(
            f"meshrod_v_{i}_pos",
            x=-5*self.params['MeshInnerStructureSeparation'] +
            i*self.params['MeshInnerStructureSeparation'],
            y=Q('0.00001cm') + 2*self.params['MeshRodOuterRadius'],
            z=Q('0cm')
            )
            ).name
            )

        # Add horizontal rods
        for i in range(self.params['MeshInnerStructureNumberOfBars_horizontal']):
            mesh_vol.placements.append(
            geom.structure.Placement(
            f"meshrod_h_{i}_place",
            volume=rod_vol_horiz,
            pos=geom.structure.Position(
            f"meshrod_h_{i}_pos",
            x=Q('0cm'),
            y=Q('0cm'),
            z=-4*self.params['MeshInnerStructureSeparation'] +
            i*self.params['MeshInnerStructureSeparation']
            ),
            rot='rot90AboutY'
            ).name
            )

        self.add_volume(mesh_vol)
        return mesh_vol




    def construct(self, geom):
        """Construct the X-ARAPUCA geometry."""
        if self.print_construct:
            print('Construct XARAPUCA <- Cryostat <- ProtoDUNE-VD <- World')

        # Regular ARAPUCA shapes
        out_box = geom.shapes.Box("XARAPUCA_out_shape",
                                dx=self.params['ArapucaOut_x']/2.0,
                                dy=self.params['ArapucaOut_y']/2.0,
                                dz=self.params['ArapucaOut_z']/2.0)

        in_box = geom.shapes.Box("XARAPUCA_in_shape",
                            dx=self.params['ArapucaIn_x']/2.0,
                            dy=self.params['ArapucaOut_y']/2.0,  # Note: Uses ArapucaOut_y
                            dz=self.params['ArapucaIn_z']/2.0)

        # Regular ARAPUCA walls - subtraction with offset
        wall_shape = geom.shapes.Boolean("XARAPUCA_wall_shape",
                        type='subtraction',
                        first=out_box,
                        second=in_box,
                        pos=geom.structure.Position(
                            "posArapucaSub",
                            x=Q('0cm'),
                            y=self.params['ArapucaOut_y']/2.0,
                            z=Q('0cm')))

        # Regular acceptance window
        window_shape = geom.shapes.Box("XARAPUCA_window_shape",
                                    dx=self.params['ArapucaAcceptanceWindow_x']/2.0,
                                    dy=self.params['ArapucaAcceptanceWindow_y']/2.0,
                                    dz=self.params['ArapucaAcceptanceWindow_z']/2.0)



        # Double ARAPUCA shapes
        double_in_box = geom.shapes.Box("XARAPUCA_double_in_shape",
                                    dx=self.params['ArapucaIn_x']/2.0,
                                    dy=(self.params['ArapucaOut_y'] + Q('1.0cm'))/2.0,
                                    dz=self.params['ArapucaIn_z']/2.0)

        # Double ARAPUCA walls - centered subtraction
        double_wall_shape = geom.shapes.Boolean("XARAPUCA_double_wall_shape",
                                type='subtraction',
                                first=out_box,
                                second=double_in_box)

        # Double acceptance window - different dimensions
        double_window_shape = geom.shapes.Box("XARAPUCA_double_window_shape",
                                            dx=self.params['ArapucaAcceptanceWindow_x']/2.0,
                                            dy=(self.params['ArapucaOut_y'] - Q('0.02cm'))/2.0,
                                            dz=self.params['ArapucaAcceptanceWindow_z']/2.0)


        # Create volumes
        # Regular ARAPUCA
        wall_vol = geom.structure.Volume("volXARAPUCAWall",
                                    material="G10",
                                    shape=wall_shape)
        # Strict larsoft rules on sensitive volume naming volOpDetSensitive*
        window_vol = geom.structure.Volume("volOpDetSensitive_XARAPUCAWindow",
                                        material="LAr",
                                        shape=window_shape)
        #window_vol.params.append(("SensDet","PhotonDetector"))

        # Double ARAPUCA
        double_wall_vol = geom.structure.Volume("volXARAPUCADoubleWall",
                                            material="G10",
                                            shape=double_wall_shape)
        # Strict larsoft rules on sensitive volume naming volOpDetSensitive*
        double_window_vol = geom.structure.Volume("volOpDetSensitive_XARAPUCADoubleWindow",
                                                material="LAr",
                                                shape=double_window_shape)
        #double_window_vol.params.append(("SensDet","PhotonDetector"))





        # Add volumes to builder
        self.add_volume(wall_vol)
        self.add_volume(window_vol)
        self.add_volume(double_wall_vol)
        self.add_volume(double_window_vol)

        self.construct_cathode_mesh(geom)
        self.construct_membrane_mesh(geom)


    def calculate_cathode_positions(self, idx, cathode_center_x, cathode_center_y, cathode_center_z):
        '''Calculate positions of X-ARAPUCAs over the cathode'''
        positions = []

        for i in range(4):
            # Calculate x,y,z position for each ARAPUCA
            # Use the existing position calculations from PERL
            z = cathode_center_z + self.list_posz_bot[i]
            x = cathode_center_x

            if (idx == 0 and i == 0):
                y = cathode_center_y + self.list_posx_bot[2]
            else:
                y = cathode_center_y + self.list_posx_bot[i]

            y = y - self.params['heightElectronicBox']

            positions.append((x,y,z))

        return positions

    def calculate_lateral_positions(self, frame_center_x, frame_center_y, frame_center_z):
        '''Calculate positions of X-ARAPUCAs on lateral walls

        Returns:
            List of tuples (x, y, y_sens, z, rotation) containing:
            - x,y,z: Main ARAPUCA position
            - y_sens: Sensor Y position with offset
            - rotation: Rotation reference name
        '''
        positions = []

        # print(self.params['VerticalPDdist'])

        # Calculate positions for 8 ARAPUCAs
        x = frame_center_x

        # print(frame_center_x, self.params['Upper_FirstFrameVertDist'], self.params['VerticalPDdist'], self.params['Lower_FirstFrameVertDist'])

        for i in range(8):

            y = frame_center_y
            z = frame_center_z

            # Handle Y positions and rotations
            if i < 4:
                # Left side
                y_sens = (y + 0.5*self.params['ArapucaOut_y'] -
                        0.5*self.params['ArapucaAcceptanceWindow_y'] -
                        Q('0.01cm'))
                rotation = 'rIdentity'
            else:
                # Right side - adjust Y position
                y = (y + 2*self.cathode['widthCathode'] +
                    2*(self.params['CathodeFrameToFC'] +
                        self.params['FCToArapucaSpaceLat'] -
                        self.params['ArapucaOut_y']/2))
                y_sens = (y - 0.5*self.params['ArapucaOut_y'] +
                        0.5*self.params['ArapucaAcceptanceWindow_y'] +
                        Q('0.01cm'))
                rotation = 'rPlus180AboutX'

            # Handle X positions
            if i == 0 or i == 4:
                # First tile position from top anode
                x = frame_center_x + self.params['Upper_FirstFrameVertDist']
            elif i == 1 or i == 5:
                # Second tile position
                x -= self.params['VerticalPDdist'] + Q('1cm') # need to add 1cm to avoid overlapping
            elif i == 2 or i == 6:
                # First tile position from bottom anode
                x = frame_center_x - self.params['Lower_FirstFrameVertDist']
            elif i == 3 or i == 7:
                # Last tile position
                x += self.params['VerticalPDdist'] + Q('1cm') # need to add 1cm to avoid overlapping

            # Store all position information
            positions.append({
                'index': i,
                'x': x,
                'y': y,
                'y_sens': y_sens,
                'z': z,
                'rotation': rotation
            })

        return positions

    def place_lateral_xarapucas(self, geom, volume, frame_center_x, frame_center_y, frame_center_z):
        '''Place the lateral ARAPUCAs in the given volume'''

        positions = self.calculate_lateral_positions(
            frame_center_x,
            frame_center_y,
            frame_center_z
        )

        lat_z = 0

        wall_vol = self.get_volume('volXARAPUCAWall')
        window_vol = self.get_volume('volOpDetSensitive_XARAPUCAWindow')
        mesh_vol = self.get_volume('volArapucaMesh')

        for pos in positions:
            i = pos['index']

            # print(pos['x'], pos['y'], pos['z'])

            # Place main ARAPUCA volume
            main_pos = geom.structure.Position(
                f"posArapuca{i}-Lat-{lat_z}",
                x=pos['x'],
                y=pos['y'],
                z=pos['z'])

            main_place = geom.structure.Placement(
                f"placeArapuca{i}-Lat-{lat_z}",
                volume=wall_vol,
                pos=main_pos,
                rot=pos['rotation'])

            volume.placements.append(main_place.name)

            # Place sensitive volume
            sens_pos = geom.structure.Position(
                f"posOpArapuca{i}-Lat-{lat_z}",
                x=pos['x'],
                y=pos['y_sens'],
                z=pos['z'])

            sens_place = geom.structure.Placement(
                f"placeOpArapuca{i}-Lat-{lat_z}",
                volume=window_vol,
                pos=sens_pos)

            volume.placements.append(sens_place.name)

            if hasattr(self, 'arapucamesh_switch') and self.arapucamesh_switch:
                mesh_y = pos['y'] + self.params['Distance_Mesh_Window'] if i<4 else \
                        pos['y'] - self.params['Distance_Mesh_Window']

                mesh_place = geom.structure.Placement(
                    f"lateral_arapuca_mesh_place_{i}",
                    volume=mesh_vol,
                    pos=geom.structure.Position(
                        f"lateral_arapuca_mesh_pos_{i}",
                        x=pos['x'], y=mesh_y, z=pos['z']
                    ),
                    rot='rot90AboutY' if i<4 else 'rot05'
                )
                volume.placements.append(mesh_place.name)
