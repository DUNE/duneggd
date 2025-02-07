#!/usr/bin/env python
'''
Steel Builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class SteelSupportBuilder(gegede.builder.Builder):
    '''Build the steel support structure for ProtoDUNE-VD'''

    def configure(self,
                 steel_parameters=None,
                 print_config=False,  
                 print_construct=False,  # Add this line
                 **kwargs):
        
        if print_config:
            print('Configure Steel Support  <- ProtoDUNE-VD <- World')
        
        self.print_construct = print_construct

        if steel_parameters:
            self.params = steel_parameters.copy()
        
    def construct_TB(self, geom):
        """Construct the top/bottom steel support structure"""
        
        # Create main TB volume 
        tb_shape = geom.shapes.Box("boxCryoTop",
                                dx=Q("1016.8cm")/2, 
                                dy=Q("1016.8cm")/2,
                                dz=Q("61.8cm")/2)
        
        tb_vol = geom.structure.Volume("volSteelSupport_TB",
                                    material="Air",
                                    shape=tb_shape)

        # Place the center unit volumes (5x5 grid)
        for i in range(5):  # x positions: -320, -160, 0, 160, 320
            for j in range(5):  # y positions: -320, -160, 0, 160, 320
                x = Q(f"{-320 + i*160}cm")
                y = Q(f"{-320 + j*160}cm") 
                z = Q("0cm")
                
                # Get central unit volume from earlier construction
                cent_vol = self.get_volume("volUnitCent")
                
                pos = geom.structure.Position(
                    f"posUnitTBCent_{i}-{j}",
                    x=x, y=y, z=z)
                    
                place = geom.structure.Placement(
                    f"volUnitTBCent_{i}-{j}",
                    volume=cent_vol,
                    pos=pos)
                    
                tb_vol.placements.append(place.name)

        # Place the edge unit volumes (E, S, W, N) for each row
        for i in range(5):  # x positions: -320 to 320 in steps of 160
            x_base = Q(f"{-320 + i*160}cm")
            y_base = Q(f"{-320}cm")  

            # Get edge unit volume
            top_vol = self.get_volume("volUnitTop")

            # East edge (TBE)
            pos_e = geom.structure.Position(
                f"posUnitTBE_{i}",
                x=Q("454.2cm"),
                y=y_base + i*Q("160cm"),
                z=Q("0cm"))
            
            place_e = geom.structure.Placement(
                f"volUnitTBE_{i}",
                volume=top_vol,
                pos=pos_e)
            tb_vol.placements.append(place_e.name)

            # South edge (TBS)
            pos_s = geom.structure.Position(
                f"posUnitTBS_{i}",
                x=x_base,
                y=Q("454.2cm"),
                z=Q("0cm"))
            
            rot_s = geom.structure.Rotation(
                f"rotUnitTBS_{i}", 
                x="0deg", y="0deg", z="-90deg")

            place_s = geom.structure.Placement(
                f"volUnitTBS_{i}",
                volume=top_vol,
                pos=pos_s,
                rot=rot_s)
            tb_vol.placements.append(place_s.name)

            # West edge (TBW)
            pos_w = geom.structure.Position(
                f"posUnitTBW_{i}",
                x=Q("-454.2cm"),
                y=y_base + i*Q("160cm"),
                z=Q("0cm"))
            
            rot_w = geom.structure.Rotation(
                f"rotUnitTBW_{i}",
                x="0deg", y="0deg", z="-180deg")

            place_w = geom.structure.Placement(
                f"volUnitTBW_{i}",
                volume=top_vol,
                pos=pos_w,
                rot=rot_w)
            tb_vol.placements.append(place_w.name)

            # North edge (TBN)
            pos_n = geom.structure.Position(
                f"posUnitTBN_{i}",
                x=x_base,
                y=Q("-454.2cm"),
                z=Q("0cm"))
            
            rot_n = geom.structure.Rotation(
                f"rotUnitTBN_{i}",
                x="0deg", y="0deg", z="-270deg")

            place_n = geom.structure.Placement(
                f"volUnitTBN_{i}",
                volume=top_vol,
                pos=pos_n,
                rot=rot_n)
            tb_vol.placements.append(place_n.name)


        self.add_volume(tb_vol)
        return tb_vol

    def construct_unit_volumes(self, geom):
        """Construct the central and top unit volumes that make up the steel support structure"""
        
        # Define parameters for central and top units
        unit_params = {
            'central': {
                'main_box': {'dx': Q('160cm'), 'dy': Q('160cm'), 'dz': Q('61.8cm')},
                'inner_box': {'dx': Q('158.2cm'), 'dy': Q('158.2cm'), 'dz': Q('56.2cm')},
                'hole': {'dx': Q('137.2cm'), 'dy': Q('137.2cm'), 'dz': Q('61.801cm')},
                'cross_bar': {'dx': Q('158.2cm'), 'dy': Q('13.6cm'), 'dz': Q('27.4cm')},
                'bar_hole': {'dx': Q('158.2cm'), 'dy': Q('6.425cm'), 'dz': Q('24.96cm')},
                'offsets': {'x': Q('0cm'), 'y': Q('0cm')},
                'name': 'Cent'
            },
            'top': {
                'main_box': {'dx': Q('108.4cm'), 'dy': Q('160cm'), 'dz': Q('61.8cm')},
                'inner_box': {'dx': Q('107.5cm'), 'dy': Q('158.2cm'), 'dz': Q('56.2cm')},
                'hole': {'dx': Q('97cm'), 'dy': Q('137.2cm'), 'dz': Q('61.81cm')},
                'cross_bar': {'dx': Q('107.5cm'), 'dy': Q('13.6cm'), 'dz': Q('27.4cm')},
                'bar_hole': {'dx': Q('107.5cm'), 'dy': Q('6.425cm'), 'dz': Q('24.96cm')},
                'offsets': {'x': Q('5.701cm'), 'y': Q('0.451cm')},
                'name': 'Top'
            },
            'wall': {
                'main_box': {'dx': Q('137.8cm'), 'dy': Q('160cm'), 'dz': Q('61.8cm')},
                'inner_box': {'dx': Q('136.9cm'), 'dy': Q('158.2cm'), 'dz': Q('56.2cm')},
                'hole': {'dx': Q('126.4cm'), 'dy': Q('137.2cm'), 'dz': Q('61.801cm')},
                'cross_bar': {'dx': Q('102.5cm'), 'dy': Q('13.6cm'), 'dz': Q('27.4cm')},
                'bar_hole': {'dx': Q('102.5cm'), 'dy': Q('6.425cm'), 'dz': Q('24.96cm')},
                'offsets': {'x': Q('5.701cm'), 'y': Q('0.451cm')},
                'name': 'WallU'
            },
            'wallS': {  # Add parameters for short wall
                'main_box': {'dx': Q('137.8cm'), 'dy': Q('160cm'), 'dz': Q('61.8cm')},
                'inner_box': {'dx': Q('136.9cm'), 'dy': Q('158.2cm'), 'dz': Q('56.2cm')},
                'hole': {'dx': Q('126.4cm'), 'dy': Q('137.2cm'), 'dz': Q('61.801cm')},
                'cross_bar': {'dx': Q('102.5cm'), 'dy': Q('13.6cm'), 'dz': Q('27.4cm')},
                'bar_hole': {'dx': Q('102.5cm'), 'dy': Q('6.425cm'), 'dz': Q('24.96cm')},
                'offsets': {'x': Q('5.701cm'), 'y': Q('0.451cm')},
                'name': 'WallS'
            },
            'wallL': {  # Add parameters for long wall
                'main_box': {'dx': Q('170.2cm'), 'dy': Q('160cm'), 'dz': Q('61.8cm')},
                'inner_box': {'dx': Q('169.3cm'), 'dy': Q('158.2cm'), 'dz': Q('56.2cm')},
                'hole': {'dx': Q('158.8cm'), 'dy': Q('137.2cm'), 'dz': Q('61.801cm')},
                'cross_bar': {'dx': Q('135.8cm'), 'dy': Q('13.6cm'), 'dz': Q('27.4cm')},
                'bar_hole': {'dx': Q('135.8cm'), 'dy': Q('6.425cm'), 'dz': Q('24.96cm')},
                'offsets': {'x': Q('5.701cm'), 'y': Q('0.451cm')},
                'name': 'WallL'
            }
        }

        def create_box(name, dx, dy, dz):
            """Helper to create box shape"""
            return geom.shapes.Box(name, dx=dx/2, dy=dy/2, dz=dz/2)

        def create_bar_with_holes(params, prefix):
            """Helper to create cross bar with holes"""
            bar = create_box(f"box{prefix}Bar", **params['cross_bar'])
            hole = create_box(f"box{prefix}Hole", **params['bar_hole'])

            # Create holes in bar
            bar_i = geom.shapes.Boolean(f"boxBar{prefix}I",
                type='subtraction',
                first=bar,
                second=hole,
                pos=geom.structure.Position(f"posBoxBar{prefix}I",
                    x=Q('0cm'), y=Q('3.5876cm'), z=Q('0cm')))

            return geom.shapes.Boolean(f"boxBar{prefix}",
                type='subtraction',
                first=bar_i,
                second=hole,
                pos=geom.structure.Position(f"posBoxBar{prefix}",
                    x=Q('0cm'), y=Q('-3.5876cm'), z=Q('0cm')))

        # Create bars with respective parameters
        bar_cent = create_bar_with_holes(unit_params['central'], 'central')
        bar_top = create_bar_with_holes(unit_params['top'], 'top')
        bar_wall = create_bar_with_holes(unit_params['wall'], 'wall')
        bar_wallL = create_bar_with_holes(unit_params['wallL'], 'wallL')
        bar_wallS = create_bar_with_holes(unit_params['wallS'], 'wallS')

        # Create unit volumes
        for unit_type, params in unit_params.items():
            # Create main shapes
            box1 = create_box(f"box1_{unit_type}", **params['main_box'])
            box2 = create_box(f"box2_{unit_type}", **params['inner_box'])
            box3 = create_box(f"box3_{unit_type}", **params['hole'])

            # Hollow out main box
            box_hollow = geom.shapes.Boolean(f"boxHoll_{unit_type}",
                type='subtraction',
                first=box1,
                second=box2,
                pos=geom.structure.Position(f"posboxHoll_{unit_type}",
                    x=params['offsets']['y'], y=Q('0cm'), z=Q('0cm')))

            # Remove central hole
            box_large = geom.shapes.Boolean(f"boxLarge_{unit_type}",
                type='subtraction',
                first=box_hollow,
                second=box3,
                pos=geom.structure.Position(f"posboxLarge_{unit_type}",
                    x=params['offsets']['x'], y=Q('0cm'), z=Q('0cm')))


            # Add first cross bar (different for central vs top)
            if unit_type == 'central':
                box_uni = geom.shapes.Boolean("boxUniCent",
                    type='union',
                    first=box_large,
                    second=bar_cent,
                    pos=geom.structure.Position("posBoxUniCent",
                        x=Q('0cm'), y=Q('0cm'), z=Q('-17.2cm')))
            elif unit_type == 'top':
                # For top unit, first union uses bar_cent rotated 90
                box_uni = geom.shapes.Boolean("boxUniTop",
                    type='union',
                    first=box_large,
                    second=bar_cent,
                    pos=geom.structure.Position("posboxUni1",
                        x=Q('5.6cm'), y=Q('0cm'), z=Q('-17.2cm')),
                    rot=geom.structure.Rotation("rotUni1",
                        x="0deg", y="0deg", z="90deg"))
            elif unit_type == 'wall':
                # For wall unit, first union uses bar_cent rotated 90 like top unit
                box_uni = geom.shapes.Boolean("boxUniWallU",
                    type='union',
                    first=box_large,
                    second=bar_cent,
                    pos=geom.structure.Position("posboxUni2",
                        x=Q('-9.1cm'), y=Q('0cm'), z=Q('-17.2cm')),
                    rot=geom.structure.Rotation("rotUni2",
                        x="0deg", y="0deg", z="90deg"))
            elif unit_type == 'wallS':
                # For short wall unit
                box_uni = geom.shapes.Boolean("boxUniWallS",
                    type='union',
                    first=box_large,
                    second=bar_cent,
                    pos=geom.structure.Position("posboxUni3",
                        x=Q('-9.1cm'), y=Q('0cm'), z=Q('-17.2cm')),
                    rot=geom.structure.Rotation("rotUni3",
                        x="0deg", y="0deg", z="90deg"))
            elif unit_type == 'wallL':
                # For long wall unit
                box_uni = geom.shapes.Boolean("boxUniWallL",
                    type='union',
                    first=box_large,
                    second=bar_cent,
                    pos=geom.structure.Position("posboxUni4",
                        x=Q('-25.3cm'), y=Q('0cm'), z=Q('-17.2cm')),
                    rot=geom.structure.Rotation("rotUni4",
                        x="0deg", y="0deg", z="90deg"))


            # Add second bar
            if unit_type == 'central':
                # Central unit: add rotated bar_cent
                final_shape = geom.shapes.Boolean("UnitCent",
                    type='union',
                    first=box_uni,
                    second=bar_cent,
                    pos=geom.structure.Position("posUnitCent",
                        x=Q('0cm'), y=Q('0cm'), z=Q('-17.2cm')),
                    rot=geom.structure.Rotation("rotUnitCent",
                        x="0deg", y="0deg", z="90deg"))
            elif unit_type == 'top':
                # Top unit: add bar_top without rotation
                final_shape = geom.shapes.Boolean("UnitTop", 
                    type='union',
                    first=box_uni,
                    second=bar_top,
                    pos=geom.structure.Position("posUniTop",
                        x=Q('0.45cm'), y=Q('0cm'), z=Q('-17.2cm')))
            elif unit_type == 'wall':
                # Wall unit: add wall bar with offset
                final_shape = geom.shapes.Boolean("UnitWallU",
                    type='union',
                    first=box_uni,
                    second=bar_wall,
                    pos=geom.structure.Position("posUniWallU",
                        x=Q('-16.75cm'), y=Q('0cm'), z=Q('-17.2cm')))
            elif unit_type == 'wallL':
                # Long wall unit: add wall bar with offset
                final_shape = geom.shapes.Boolean("UnitWallL",
                    type='union',
                    first=box_uni,
                    second=bar_wallL,
                    pos=geom.structure.Position("posUniWallL",
                        x=Q('-16.3cm'), y=Q('0cm'), z=Q('-17.2cm')))
            elif unit_type == 'wallS':
                final_shape = geom.shapes.Boolean("UnitWallS",
                    type='union',
                    first=box_uni,
                    second=bar_wallS,
                    pos=geom.structure.Position("posUniWallS",
                        x=Q('-16.75cm'), y=Q('0cm'), z=Q('-17.2cm')))

            # Create volume
            vol = geom.structure.Volume(f"volUnit{params['name']}",
                material="STEEL_STAINLESS_Fe7Cr2Ni",
                shape=final_shape)

            self.add_volume(vol)

    def construct_US(self, geom):
        """Construct the upstream steel support structure"""
        # Create main US volume using same shape as TB
        us_shape = geom.shapes.Box("boxCryoWallSm",
                                dx=Q("1016.8cm")/2,
                                dy=Q("1075.6cm")/2,
                                dz=Q("61.8cm")/2)
        
        us_vol = geom.structure.Volume("volSteelSupport_US",
                                    material="Air",
                                    shape=us_shape)

        # Place the center unit volumes (5x5 grid)
        # Note: All central units have rPlus180AboutY rotation
        for i in range(5):  # x positions: -320 to 320 in steps of 160
            for j in range(5):  # y positions: -320 to 320 in steps of 160
                x = Q(f"{-320 + i*160}cm")
                y = Q(f"{-320 + j*160}cm") 
                z = Q("0cm")
                
                # Get central unit volume
                cent_vol = self.get_volume("volUnitCent")
                
                pos = geom.structure.Position(
                    f"posUnitUSCent_{i}-{j}",
                    x=x, y=y, z=z)
                    
                # Note the rPlus180AboutY rotation for all central units
                place = geom.structure.Placement(
                    f"volUnitUSCent_{i}-{j}",
                    volume=cent_vol,
                    pos=pos,
                    rot="rPlus180AboutY")
                    
                us_vol.placements.append(place.name)

        # Place the edge unit volumes (E, S, W, N) for each row
        for i in range(5):  # x positions: -320 to 320 in steps of 160
            x_base = Q(f"{-320 + i*160}cm")

            # Get edge unit volumes
            top_vol = self.get_volume("volUnitTop") 
            wall_s_vol = self.get_volume("volUnitWallS")

            # East edge (USE)
            pos_e = geom.structure.Position(
                f"posUnitUSE_{i}",
                x=Q("454.2cm"),
                y=x_base,
                z=Q("0cm"))
            
            # Note rPlus180AboutX rotation
            place_e = geom.structure.Placement(
                f"volUnitUSE_{i}",
                volume=top_vol,
                pos=pos_e,
                rot="rPlus180AboutX")
            us_vol.placements.append(place_e.name)

            # South edge (USS) 
            pos_s = geom.structure.Position(
                f"posUnitUSS_{i}", 
                x=x_base,
                y=Q("468.9cm"),
                z=Q("0cm"))
            
            rot_s = geom.structure.Rotation(
                f"rotUnitUSS_{i}",
                x="0deg", y="180deg", z="-90deg")

            place_s = geom.structure.Placement(
                f"volUnitUSS_{i}",
                volume=wall_s_vol,
                pos=pos_s,
                rot=rot_s)
            us_vol.placements.append(place_s.name)

            # West edge (USW)
            pos_w = geom.structure.Position(
                f"posUnitUSW_{i}",
                x=Q("-454.2cm"),
                y=x_base, 
                z=Q("0cm"))

            rot_w = geom.structure.Rotation(
                f"rotUnitUSW_{i}",
                x="180deg", y="0deg", z="-180deg")

            place_w = geom.structure.Placement(
                f"volUnitUSW_{i}",
                volume=top_vol,
                pos=pos_w,
                rot=rot_w)
            us_vol.placements.append(place_w.name)

            # North edge (USN)
            pos_n = geom.structure.Position(
                f"posUnitUSN_{i}",
                x=x_base,
                y=Q("-468.9cm"),
                z=Q("0cm"))
            
            rot_n = geom.structure.Rotation(
                f"rotUnitUSN_{i}",
                x="0deg", y="180deg", z="-270deg")

            place_n = geom.structure.Placement(
                f"volUnitUSN_{i}",
                volume=wall_s_vol,
                pos=pos_n,
                rot=rot_n)
            us_vol.placements.append(place_n.name)

        self.add_volume(us_vol)
        return us_vol

    def construct_LR(self, geom):
        """Construct the left/right steel support structure"""
        
        # Create main LR volume
        lr_shape = geom.shapes.Box("boxCryoWallLg", 
                                dx=Q("1140.4cm")/2,
                                dy=Q("1075.6cm")/2,
                                dz=Q("61.8cm")/2)

        lr_vol = geom.structure.Volume("volSteelSupport_LR",
                                    material="Air",
                                    shape=lr_shape)

        # Place the center unit volumes (5x5 grid)
        for i in range(5):  # x positions: -320 to 320 in steps of 160
            for j in range(5):  # y positions: -320 to 320 in steps of 160
                x = Q(f"{-320 + i*160}cm")
                y = Q(f"{-320 + j*160}cm")
                z = Q("0cm")

                # Place central unit 
                cent_vol = self.get_volume("volUnitCent")
                pos = geom.structure.Position(
                    f"posUnitLRCent_{i}-{j}",
                    x=x, y=y, z=z)

                place = geom.structure.Placement(
                    f"volUnitLRCent_{i}-{j}",
                    volume=cent_vol,
                    pos=pos)

                lr_vol.placements.append(place.name)

        # Get wall volumes
        wall_L_vol = self.get_volume("volUnitWallL")
        wall_S_vol = self.get_volume("volUnitWallS") 

        # Place the edge unit volumes (E, S, W, N) for each row
        for i in range(5):  # positions: -320 to 320 in steps of 160 
            base = Q(f"{-320 + i*160}cm")

            # East edge (LRE)
            pos_e = geom.structure.Position(
                f"posUnitLRE_{i}",
                x=Q("485.1cm"), y=base, z=Q("0cm"))
            
            place_e = geom.structure.Placement(
                f"volUnitLRE_{i}", 
                volume=wall_L_vol,
                pos=pos_e)
            lr_vol.placements.append(place_e.name)

            # South edge (LRS) 
            pos_s = geom.structure.Position(
                f"posUnitLRS_{i}",
                x=base, y=Q("468.9cm"), z=Q("0cm"))
                
            rot_s = geom.structure.Rotation(
                f"rotUnitLRS_{i}",
                x="0deg", y="0deg", z="-90deg")
                
            place_s = geom.structure.Placement(
                f"volUnitLRS_{i}",
                volume=wall_S_vol, 
                pos=pos_s,
                rot=rot_s)
            lr_vol.placements.append(place_s.name)

            # West edge (LRW)
            pos_w = geom.structure.Position(
                f"posUnitLRW_{i}",
                x=Q("-485.1cm"), y=base, z=Q("0cm"))
                
            rot_w = geom.structure.Rotation(
                f"rotUnitLRW_{i}",
                x="0deg", y="0deg", z="-180deg")
                
            place_w = geom.structure.Placement(
                f"volUnitLRW_{i}",
                volume=wall_L_vol,
                pos=pos_w,
                rot=rot_w)
            lr_vol.placements.append(place_w.name)

            # North edge (LRN)
            pos_n = geom.structure.Position(
                f"posUnitLRN_{i}",
                x=base, y=Q("-468.9cm"), z=Q("0cm"))
                
            rot_n = geom.structure.Rotation(
                f"rotUnitLRN_{i}",
                x="0deg", y="0deg", z="-270deg")
                
            place_n = geom.structure.Placement(
                f"volUnitLRN_{i}",
                volume=wall_S_vol,
                pos=pos_n,
                rot=rot_n)
            lr_vol.placements.append(place_n.name)

        self.add_volume(lr_vol)
        return lr_vol


    def construct(self, geom):
        if self.print_construct:
            print('Construct Steel Support <- ProtoDUNE-VD <- World')

        # First construct the component volumes
        self.construct_unit_volumes(geom)
            
        # Construct top/bottom steel support structure
        self.construct_TB(geom)
        
        # Construct upstream steel support structure
        self.construct_US(geom)

        # Construct left/right steel support structure
        self.construct_LR(geom)


    def place_in_volume(self, geom, main_lv):
        """Place steel support structure in the given volume"""
        
        # Get steel support volume
        steel_TB_vol = self.get_volume('volSteelSupport_TB')
        steel_US_vol = self.get_volume('volSteelSupport_US')
        steel_LR_vol = self.get_volume('volSteelSupport_LR')
        
        # Configuration for top and bottom placements
        placements = [
            {
                'name': 'Top',
                'volume': steel_TB_vol,
                'y_offset': Q("61.1cm"), 
                'pos_param': 'posTopSteelStruct',
                'rotation': {
                    'x': "90deg",
                    'y': "0deg", 
                    'z': "0deg"
                }
            },
            {
                'name': 'Bottom',
                'volume': steel_TB_vol,
                'y_offset': -Q("61.1cm"),
                'pos_param': 'posBotSteelStruct', 
                'rotation': {
                    'x': "-90deg",
                    'y': "0deg",
                    'z': "0deg"
                }
            },
            # New US placement
            {
                'name': 'US',
                'volume': steel_US_vol,
                'z_offset': -Q("31.1cm"),
                'pos_param': 'posZFrontSteelStruct',
                'rotation': {
                    'x': "0deg", 
                    'y': "0deg",
                    'z': "0deg"
                }
            },
            # Downstream placement (reusing US volume)
            {
                'name': 'DS',
                'volume': steel_US_vol,  # Reuse US volume
                'z_offset': Q("31.1cm"),  # Note positive offset for DS
                'pos_param': 'posZBackSteelStruct',
                'rotation': {
                    'x': "0deg", 
                    'y': "0deg", 
                    'z': "0deg"
                }
            },
            # Left placement
            {
                'name': 'LS',
                'volume': steel_LR_vol,
                'x_offset': Q("65.1cm"),
                'pos_param': 'posLeftSteelStruct',
                'rotation': {
                    'x': "0deg", 
                    'y': "-90deg", 
                    'z': "0deg"
                }
            },
            # Right placement
            {
                'name': 'RS',
                'volume': steel_LR_vol,
                'x_offset': -Q("65.1cm"),
                'pos_param': 'posRightSteelStruct',
                'rotation': {
                    'x': "0deg", 
                    'y': "90deg", 
                    'z': "0deg"
                }
            }
        ]
        
        # Create placements for both top and bottom
        for cfg in placements:
            # Calculate position
            pos_args = {'x': Q('0cm'), 'y': Q('0cm'), 'z': Q('0cm')}
            

            if 'y_offset' in cfg:
                pos_args['y'] = self.params[cfg['pos_param']] + cfg['y_offset']
                # print(self.params[cfg['pos_param']], cfg['y_offset'])
            elif 'z_offset' in cfg:
                pos_args['z'] = self.params[cfg['pos_param']] + cfg['z_offset']
            elif 'x_offset' in cfg:
                pos_args['x'] = self.params[cfg['pos_param']] + cfg['x_offset']

            

                
            pos = geom.structure.Position(
                f"posSteelSupport_{cfg['name']}",
                **pos_args)
            
            # Create rotation if needed
            if cfg['rotation']['x'] != "0deg" or cfg['rotation']['y'] != "0deg" or cfg['rotation']['z'] != "0deg":
                rot = geom.structure.Rotation(
                    f"rotSteelSupport_{cfg['name']}", 
                    x=cfg['rotation']['x'],
                    y=cfg['rotation']['y'], 
                    z=cfg['rotation']['z'])
                
                # Place with rotation
                place = geom.structure.Placement( 
                    f"placeSteelSupport_{cfg['name']}",
                    volume=cfg['volume'],
                    pos=pos,
                    rot=rot)
            else:
                # Place without rotation
                place = geom.structure.Placement(
                    f"placeSteelSupport_{cfg['name']}",
                    volume=cfg['volume'],
                    pos=pos)
                
            main_lv.placements.append(place.name)

         


