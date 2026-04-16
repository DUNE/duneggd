#!/usr/bin/env python
'''
Cathode builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class CathodeBuilder(gegede.builder.Builder):
    '''Build the cathode structure including mesh'''

    def __init__(self, name):
        super(CathodeBuilder, self).__init__(name)
        self.params = None

    def configure(self, cathode_parameters=None, tpc_params=None,
                 arapucamesh_switch=True,  # Add this line
                 xarapuca_parameters=None,
                 print_config=False, print_construct=False, **kwargs):
        """Configure the cathode geometry.

        Args:
            cathode_parameters (dict): Cathode parameters from config
            tpc_params (dict): TPC parameters from parent builder
            arapucamesh_switch (bool): Switch to enable/disable X-ARAPUCA mesh placement
            print_config (bool): Whether to print configuration info
            print_construct (bool): Whether to print construction info
            **kwargs: Additional configuration parameters
        """
        if print_config:
            print('Configure Cathode <- Cryostat <- ProtoDUNE-VD <- World')
        # Add guard against double configuration
        # if hasattr(self, '_configured'):
        #     return

        # Store cathode params
        if cathode_parameters:
            self.params = cathode_parameters

            # Calculate additional derived parameters
            # Mesh parameters
            self.params['mesh_length'] = self.params['lengthCathodeVoid']
            self.params['mesh_width'] = self.params['widthCathodeVoid']

            # Define void positions for 4x4 grid in a single cathode
            self.params['void_positions'] = []

            # Calculate void positions
            for i in range(4):  # rows
                for j in range(4):  # columns
                    # Calculate x position
                    if i < 2:
                        x = (i - 1.5) * self.params['widthCathodeVoid'] + \
                            (i - 2) * self.params['CathodeBorder']
                    else:
                        x = (i - 1.5) * self.params['widthCathodeVoid'] + \
                            (i - 1) * self.params['CathodeBorder']

                    if j < 2:
                        z = (j - 1.5) * self.params['lengthCathodeVoid'] + \
                            (j - 2) * self.params['CathodeBorder']
                    else:
                        z = (j - 1.5) * self.params['lengthCathodeVoid'] + \
                            (j - 1) * self.params['CathodeBorder']

                    self.params['void_positions'].append([x, z])



        # Store TPC params we need
        if tpc_params:
            # Set width and length based on CRP dimensions
            self.params['widthCathode'] = tpc_params['widthCRP']
            self.params['lengthCathode'] = tpc_params['lengthCRP']

            # Set mesh dimensions based on void dimensions
            self.params['CathodeMeshInnerStructureLength_vertical'] = \
                self.params['lengthCathodeVoid']
            self.params['CathodeMeshInnerStructureLength_horizontal'] = \
                self.params['widthCathodeVoid']

        if xarapuca_parameters:
            self.params['CathodeArapucaMeshRodRadius']=xarapuca_parameters['CathodeArapucaMeshRodRadius']

        # Update with any overrides from kwargs
        if kwargs:
            self.params.update(kwargs)

        # Store parameters
        self.arapucamesh_switch = arapucamesh_switch  # Add this line

        # Mark as configured
        # self._configured = True
        self.print_construct = print_construct

    def construct(self, geom):
        '''Construct cathode geometry'''
        if self.print_construct:
            print('Construct Cathode <- Cryostat <- ProtoDUNE-VD <- World')

        # Create base cathode box
        cathode_box = geom.shapes.Box(
            self.name + "_box",
            dx=self.params['heightCathode']/2,
            dy=self.params['widthCathode']/2,
            dz=self.params['lengthCathode']/2)

        # Create void box for subtraction
        void_box = geom.shapes.Box(
            self.name + "_void",
            dx=self.params['heightCathode']/2 + Q('0.5cm'),
            dy=self.params['widthCathodeVoid']/2,
            dz=self.params['lengthCathodeVoid']/2)

        # Create cathode frame by subtracting all voids
        shape = cathode_box
        for i, (void_y, void_z) in enumerate(self.params['void_positions']):
            shape = geom.shapes.Boolean(
                self.name + f"_shape{i+1}",
                type='subtraction',
                first=shape,
                second=void_box,
                pos=geom.structure.Position(
                    self.name + f"_void_pos{i+1}",
                    x=Q('0cm'),
                    y=void_y,
                    z=void_z))

        # Create main cathode volume with G10 material
        cathode_vol = geom.structure.Volume(
            self.name+"_volume",
            material="G10",
            shape=shape)

        # Add main volume to builder
        self.add_volume(cathode_vol)

        # Create mesh rod shapes
        mesh_rod_vertical = geom.shapes.Box(
            self.name+"_mesh_rod_vertical",
            dx=self.params['CathodeMeshInnerStructureThickness'],  # Thickness
            dy=self.params['CathodeMeshInnerStructureWidth'],  # Width
            dz=self.params['mesh_length']/2)  # Length

        # Build complete mesh starting with first vertical rod
        mesh_shape = mesh_rod_vertical

        # Add remaining vertical rods
        for i in range(1, self.params['CathodeMeshInnerStructureNumberOfStrips_vertical']):
            pos_y = i*self.params['CathodeMeshInnerStructureSeparation']
            mesh_shape = geom.shapes.Boolean(
                self.name + f"_mesh_v{i}",
                type='union',
                first=mesh_shape,
                second=mesh_rod_vertical,
                pos=geom.structure.Position(
                    self.name + f"_vrod_pos{i}",
                    x=Q('0cm'),
                    y=pos_y,
                    z=Q('0cm'))
            )

        # Create horizontal rod shape
        mesh_rod_horizontal = geom.shapes.Box(
            self.name+"_mesh_rod_horizontal",
            dx=self.params['CathodeMeshInnerStructureThickness'],  # Thickness
            dy=self.params['mesh_width']/2,  # Width
            dz=self.params['CathodeMeshInnerStructureWidth'])  # Height

        # Add horizontal rods
        for i in range(self.params['CathodeMeshInnerStructureNumberOfStrips_horizontal']):
            pos_z = -self.params['mesh_length']/2 + (i+1)*self.params['CathodeMeshInnerStructureSeparation']
            mesh_shape = geom.shapes.Boolean(
                self.name + f"_mesh_h{i}",
                type='union',
                first=mesh_shape,
                second=mesh_rod_horizontal,
                pos=geom.structure.Position(
                    self.name + f"_hrod_pos{i}",
                    x=Q('0cm'),
                    y=self.params['mesh_width']/2-self.params['CathodeMeshInnerStructureSeparation'],
                    z=pos_z
                )
            )

        # Create volume for complete mesh
        mesh_vol = geom.structure.Volume(
            self.name+"_mesh_vol",
            material="G10",
            shape=mesh_shape)

        # Store mesh volume and add to builder
        self.mesh_vol = mesh_vol
        self.add_volume(mesh_vol)


        # Create anode box
        anode_plate_box = geom.shapes.Box(
            "anode_plate_box",
            dx=self.params['anodePlateWidth']/2,
            dy=self.params['widthCathode']/2,
            dz=self.params['lengthCathode']/2)
        # Create main anode volume with vm2000 material
        anode_vol = geom.structure.Volume(
            "anode_plate",
            material="vm2000",
            shape=anode_plate_box)
        self.anode_vol = anode_vol
        self.add_volume(anode_vol)

    def place_in_volume(self, geom, volume, argon_dim, params, xarapuca_builder=None):
        '''Place cathode modules and associated X-ARAPUCAs in the given volume

        Args:
            geom: Geometry object
            volume: Volume to place cathodes in
            argon_dim: Tuple of LAr dimensions (x,y,z)
            params: Dict containing placement parameters
        '''

        # Calculate base position
        cathode_x = argon_dim[0]/2 - params['HeightGaseousAr'] - \
                    params['Upper_xLArBuffer'] - \
                    (params['driftTPCActive'] + params['ReadoutPlane']) - \
                    self.params['heightCathode']/2

        base_y = -argon_dim[1]/2 + params['yLArBuffer'] + self.params['widthCathode']/2
        base_z = -argon_dim[2]/2 + params['zLArBuffer'] + self.params['lengthCathode']/2


        # print(argon_dim[0], argon_dim[1], argon_dim[2])
        # print(-argon_dim[1]/2, params['yLArBuffer'], self.params['widthCathode']/2)
        # print(-argon_dim[2]/2, params['zLArBuffer'], self.params['lengthCathode']/2)

        cathode_vol = self.get_volume('cathode_volume')
        mesh_vol = self.mesh_vol
        anode_vol = self.anode_vol

        # Get CRM dimensions from params
        n_crm_z = params.get('nCRM_z', 4)  # Default 4 if not specified
        n_crm_x = params.get('nCRM_x', 4)  # Default 4 if not specified

        # Get X-ARAPUCA volumes if builder is available
        double_arapuca_wall = None
        double_arapuca_window = None
        double_arapuca_mesh = None
        if xarapuca_builder:
            double_arapuca_wall = xarapuca_builder.get_volume('volXARAPUCADoubleWall')
            double_arapuca_window = xarapuca_builder.get_volume('volOpDetSensitive_XARAPUCADoubleWindow')
            double_arapuca_mesh = xarapuca_builder.get_volume('volCathodeArapucaMesh')

        # Place cathodes and meshes in 2x2 grid
        for i in range(n_crm_x//2):  # y direction
            for j in range(n_crm_z//2):  # z direction
                # Calculate center position of this cathode module
                module_x = cathode_x
                module_y = base_y + i*self.params['widthCathode']
                module_z = base_z + j*self.params['lengthCathode']

                # Place cathode frame
                pos = geom.structure.Position(
                    f"{self.name}_pos_{i}_{j}",
                    x=module_x,
                    y=module_y,
                    z=module_z
                )
                place = geom.structure.Placement(
                    f"{self.name}_place_{i}_{j}",
                    volume=cathode_vol,
                    pos=pos
                )
                volume.placements.append(place.name)

                # Place top and bottom anode
                anode_top_x = cathode_x + 0.5*self.params['heightCathode'] + params['driftTPCActive'] + params['nViews']*params['padWidth'] + self.params['anodePlateWidth']/2; #right above TPC vol
                anode_top_y = module_y
                anode_top_z = module_z
                anode_bot_x = anode_top_x -2.*(params['driftTPCActive'] + params['nViews']*params['padWidth']) - self.params['anodePlateWidth'] - self.params['heightCathode'];
                anode_bot_y = module_y
                anode_bot_z = module_z

                pos_anode_top = geom.structure.Position(
                    f"posAnodePlateTop_{i}_{j}",
                    x=anode_top_x,
                    y=anode_top_y,
                    z=anode_top_z
                )
                place_anode_top = geom.structure.Placement(
                    f"placeAnodePlateTop_{i}_{j}",
                    volume=anode_vol,
                    pos=pos_anode_top,
                    rot='rIdentity'
                )
                pos_anode_bot = geom.structure.Position(
                    f"posAnodePlateBot_{i}_{j}",
                    x=anode_bot_x,
                    y=anode_bot_y,
                    z=anode_bot_z
                )
                place_anode_bot = geom.structure.Placement(
                    f"placeAnodePlateBot_{i}_{j}",
                    volume=anode_vol,
                    pos=pos_anode_bot,
                    rot='rIdentity'
                )
                volume.placements.append(place_anode_top.name)
                volume.placements.append(place_anode_bot.name)

                # Place X-ARAPUCAs associated with this cathode module
                if xarapuca_builder and double_arapuca_wall:

                    # Calculate X-ARAPUCA positions relative to this cathode module
                    arapuca_positions = xarapuca_builder.calculate_cathode_positions(i,
                        module_x, module_y, module_z
                    )

                    # # Place each X-ARAPUCA with rotation
                    for idx, (x, y, z) in enumerate(arapuca_positions):


                        # Include rotation in placement
                        arapuca_place = geom.structure.Placement(
                            f"place_cathode_{i}_{j}_xarapuca_{idx}",
                            volume=double_arapuca_wall,
                            pos= geom.structure.Position(
                                f"pos_cathode_{i}_{j}_xarapuca_{idx}",
                                x=x, y=y, z=z
                            ),
                            rot='rPlus90AboutXPlus90AboutZ'    # Add rotation here
                        )
                        volume.placements.append(arapuca_place.name)

                        # place the window
                        window_place = geom.structure.Placement(
                            f"place_cathode_{i}_{j}_xwindow_{idx}",
                            volume=double_arapuca_window,
                            pos=geom.structure.Position(
                                f"pos_cathode_{i}_{j}_xwindow_{idx}",
                                x=x, y=y, z=z
                            ),
                            rot='rPlus90AboutXPlus90AboutZ'    # Add rotation here
                        )
                        volume.placements.append(window_place.name)



                # Place mesh in each void position
                for void_idx, (void_y, void_z) in enumerate(self.params['void_positions']):
                    flag_construct = True

                    # skip the mesh if there is a X-ARAPUCA in the same position
                    for idx, (x, y, z) in enumerate(arapuca_positions):
                        if (abs(base_y + i*self.params['widthCathode'] + void_y + self.params['CathodeMeshInnerStructureSeparation'] - y)<Q('10cm') and abs(base_z + j*self.params['lengthCathode'] + void_z - z)<Q('1cm')):
                            flag_construct = False
                            break

                    if (flag_construct):
                        resistive_mesh_top_place = geom.structure.Placement(
                            f"{self.name}_resistive_mesh_top_place_{i}_{j}_{void_idx}",
                            volume=mesh_vol,
                            pos=geom.structure.Position(
                                f"{self.name}_resistive_mesh_top_pos_{i}_{j}_{void_idx}",
                                x=cathode_x + self.params['heightCathode']/2 - 2*self.params['CathodeMeshInnerStructureThickness'],
                                y=base_y + i*self.params['widthCathode'] + void_y - \
                                self.params['mesh_width']/2 + self.params['CathodeMeshInnerStructureSeparation'],
                                z=base_z + j*self.params['lengthCathode'] + void_z
                            )
                        )

                        volume.placements.append(resistive_mesh_top_place.name)

                        resistive_mesh_bottom_place = geom.structure.Placement(
                            f"{self.name}_resistive_mesh_bottom_place_{i}_{j}_{void_idx}",
                            volume=mesh_vol,
                            pos=geom.structure.Position(
                                f"{self.name}_resistive_mesh_bottom_pos_{i}_{j}_{void_idx}",
                                x=cathode_x - self.params['heightCathode']/2 + 2*self.params['CathodeMeshInnerStructureThickness'],
                                y=base_y + i*self.params['widthCathode'] + void_y - \
                                self.params['mesh_width']/2 + self.params['CathodeMeshInnerStructureSeparation'],
                                z=base_z + j*self.params['lengthCathode'] + void_z
                            )
                        )

                        volume.placements.append(resistive_mesh_bottom_place.name)
                    else:
                        # Only place X-ARAPUCA mesh if switch is enabled
                        # print(self.arapucamesh_switch)
                        if self.arapucamesh_switch:
                            # add cathode xarapuca mesh ...  double_arapuca_mesh
                            mesh_top_place = geom.structure.Placement(
                                f"place_cathode_{i}_{j}_top_xmesh_{idx}",
                                volume=double_arapuca_mesh,
                                pos = geom.structure.Position(
                                    f"cathode_mesh_top_{i}_{j}_{idx}",
                                    x=cathode_x + self.params['heightCathode']/2 - 2*self.params['CathodeArapucaMeshRodRadius'],
                                    y=base_y + i*self.params['widthCathode'] + void_y,
                                    z=base_z + j*self.params['lengthCathode'] + void_z
                                )
                            )
                            volume.placements.append(mesh_top_place.name)

                            mesh_bottom_place = geom.structure.Placement(
                                f"place_cathode_{i}_{j}_bottom_xmesh_{idx}",
                                volume=double_arapuca_mesh,
                                pos = geom.structure.Position(
                                    f"cathode_mesh_bottom_{i}_{j}_{idx}",
                                    x=cathode_x - self.params['heightCathode']/2 + 2*self.params['CathodeArapucaMeshRodRadius'],
                                    y=base_y + i*self.params['widthCathode'] + void_y,
                                    z=base_z + j*self.params['lengthCathode'] + void_z
                                )
                            )
                            volume.placements.append(mesh_bottom_place.name)
