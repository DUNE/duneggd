#!/usr/bin/env python
'''
CRT (Cosmic Ray Tagger) builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class CRTBuilder(gegede.builder.Builder):
    '''
    Build the Cosmic Ray Tagger (CRT) for ProtoDUNE-VD.
    Implements both HD-CRT and DP-CRT modules.
    '''

    def __init__(self, name):
        super(CRTBuilder, self).__init__(name)
        self.crt = None
        self.steel = None
        self.OriginXSet = None
        self.OriginYSet = None
        self.OriginZSet = None
        self.DP_CRT_switch = None  # Add this line
        self.HD_CRT_switch = None  # Add this line

    def configure(self, crt_parameters=None, steel_parameters=None, 
                 OriginXSet=None, OriginYSet=None, OriginZSet=None,
                 DP_CRT_switch=None, HD_CRT_switch=None,  # Add these lines
                 print_config=False,  
                 print_construct=False,  # Add this line
                 **kwargs):
        """Configure the CRT geometry.
        
        Args:
            crt_parameters (dict): CRT parameters from config
            steel_parameters (dict): Steel support parameters
            OriginXSet (Quantity): X origin coordinate 
            OriginYSet (Quantity): Y origin coordinate
            OriginZSet (Quantity): Z origin coordinate
            DP_CRT_switch (bool): Flag to control DP CRT switch
            HD_CRT_switch (bool): Flag to control HD CRT switch
            print_config (bool): Flag to control printing
            print_construct (bool): Flag to control printing during construction
            **kwargs: Additional configuration parameters
        """
        if print_config:
            print('Configure CRT <- ProtoDUNE-VD <- World')
        # Add guard against double configuration
        if hasattr(self, '_configured'):
            return

        # Store parameters
        if crt_parameters:
            self.crt = crt_parameters
        if steel_parameters:
            self.steel = steel_parameters

        # Store origin coordinates
        self.OriginXSet = OriginXSet
        self.OriginYSet = OriginYSet 
        self.OriginZSet = OriginZSet

        # Store CRT switch settings
        self.DP_CRT_switch = DP_CRT_switch
        self.HD_CRT_switch = HD_CRT_switch

        self.print_construct = print_construct

        # Mark as configured
        self._configured = True

    def calculate_positions(self):
        '''Calculate all the CRT module positions'''
        
        self.posCRTDS_x = []
        self.posCRTDS_y = []
        self.posCRTDS_z = [] 
        self.posCRTDS_rot = []
        
        self.posCRTUS_x = []
        self.posCRTUS_y = []
        self.posCRTUS_z = []
        self.posCRTUS_rot = []

        # Helper function to calculate positions
        def add_DS_position(index, x, y, z, rot):
            self.posCRTDS_x.append(x)
            self.posCRTDS_y.append(y)
            self.posCRTDS_z.append(z)
            self.posCRTDS_rot.append(rot)

        def add_US_position(index, x, y, z, rot):
            self.posCRTUS_x.append(x)
            self.posCRTUS_y.append(y)
            self.posCRTUS_z.append(z)
            self.posCRTUS_rot.append(rot)

        # Define CRT module configurations
        ds_configs = [
            # Top Left
            ('DSTopLeft', 'DSTopLeftBa', [-1, -1, 1], "rPlus90AboutX", 0),
            ('DSTopLeft', 'DSTopLeftBa', [1, -1, 1], "rPlus90AboutX", 1),
            ('DSTopLeft', 'DSTopLeftFr', [-1, -1, 1], "rMinus90AboutYMinus90AboutX", 2),
            ('DSTopLeft', 'DSTopLeftFr', [-1, 1, 1], "rMinus90AboutYMinus90AboutX", 3),
            # Bottom Left
            ('DSBotLeft', 'DSBotLeftFr', [-1, 1, 1], "rPlus90AboutX", 4),
            ('DSBotLeft', 'DSBotLeftFr', [1, 1, 1], "rPlus90AboutX", 5),
            ('DSBotLeft', 'DSBotLeftBa', [-1, -1, 1], "rMinus90AboutYMinus90AboutX", 6),
            ('DSBotLeft', 'DSBotLeftBa', [-1, 1, 1], "rMinus90AboutYMinus90AboutX", 7),
            # Top Right
            ('DSTopRight', 'DSTopRightFr', [-1, -1, 1], "rPlus90AboutX", 8),
            ('DSTopRight', 'DSTopRightFr', [1, -1, 1], "rPlus90AboutX", 9),
            ('DSTopRight', 'DSTopRightBa', [1, -1, 1], "rMinus90AboutYMinus90AboutX", 10),
            ('DSTopRight', 'DSTopRightBa', [1, 1, 1], "rMinus90AboutYMinus90AboutX", 11),
            # Bottom Right
            ('DSBotRight', 'DSBotRightBa', [-1, 1, 1], "rPlus90AboutX", 12),
            ('DSBotRight', 'DSBotRightBa', [1, 1, 1], "rPlus90AboutX", 13),
            ('DSBotRight', 'DSBotRightFr', [1, -1, 1], "rMinus90AboutYMinus90AboutX", 14),
            ('DSBotRight', 'DSBotRightFr', [1, 1, 1], "rMinus90AboutYMinus90AboutX", 15),
        ]

        us_configs = [
            # US Top Left configs
            ('USTopLeft', 'USTopLeftBa', [-1, -1, 1], "rPlus90AboutX", 0),
            ('USTopLeft', 'USTopLeftBa', [1, -1, 1], "rPlus90AboutX", 1),
            ('USTopLeft', 'USTopLeftFr', [-1, -1, 1], "rMinus90AboutYMinus90AboutX", 2),
            ('USTopLeft', 'USTopLeftFr', [-1, 1, 1], "rMinus90AboutYMinus90AboutX", 3),
            # US Bottom Left configs
            ('USBotLeft', 'USBotLeftFr', [-1, 1, 1], "rPlus90AboutX", 4),
            ('USBotLeft', 'USBotLeftFr', [1, 1, 1], "rPlus90AboutX", 5),
            ('USBotLeft', 'USBotLeftBa', [-1, -1, 1], "rMinus90AboutYMinus90AboutX", 6),
            ('USBotLeft', 'USBotLeftBa', [-1, 1, 1], "rMinus90AboutYMinus90AboutX", 7),
            # US Top Right configs
            ('USTopRight', 'USTopRightFr', [-1, -1, 1], "rPlus90AboutX", 8),
            ('USTopRight', 'USTopRightFr', [1, -1, 1], "rPlus90AboutX", 9),
            ('USTopRight', 'USTopRightBa', [1, -1, 1], "rMinus90AboutYMinus90AboutX", 10),
            ('USTopRight', 'USTopRightBa', [1, 1, 1], "rMinus90AboutYMinus90AboutX", 11),
            # US Bottom Right configs 
            ('USBotRight', 'USBotRightBa', [-1, 1, 1], "rPlus90AboutX", 12),
            ('USBotRight', 'USBotRightBa', [1, 1, 1], "rPlus90AboutX", 13),
            ('USBotRight', 'USBotRightFr', [1, -1, 1], "rMinus90AboutYMinus90AboutX", 14),
            ('USBotRight', 'USBotRightFr', [1, 1, 1], "rMinus90AboutYMinus90AboutX", 15),
        ]

        # Process downstream modules
        for base, z_pos, mods, rot, idx in ds_configs:
            x = (self.steel['posCryoInDetEnc']['x'] + self.crt['CRTSurveyOrigin_x'] + 
                 self.crt[f'CRT_{base}_x'] + 
                 mods[0] * (self.crt['ModuleLongCorr'] if idx % 4 in [2, 3] else self.crt['ModuleSMDist']))
            y = (self.steel['posCryoInDetEnc']['y'] + self.crt['CRTSurveyOrigin_y'] + 
                 self.crt[f'CRT_{base}_y'] + 
                 mods[1] * (self.crt['ModuleLongCorr'] if idx % 4 in [0, 1] else self.crt['ModuleSMDist']))
            z = (self.crt['CRTSurveyOrigin_z'] + 
                 self.crt[f'CRT_{z_pos}_z'] + 
                 mods[2] * self.crt['ModuleOff_z'])
            add_DS_position(idx, x, y, z, rot)
            

        # Process upstream modules
        for base, z_pos, mods, rot, idx in us_configs:
            x = (self.steel['posCryoInDetEnc']['x'] + self.crt['CRTSurveyOrigin_x'] + 
                 self.crt[f'CRT_{base}_x'] + 
                 mods[0] * (self.crt['ModuleLongCorr'] if idx % 4 in [2, 3] else self.crt['ModuleSMDist']))
            y = (self.steel['posCryoInDetEnc']['y'] + self.crt['CRTSurveyOrigin_y'] + 
                 self.crt[f'CRT_{base}_y'] + 
                 mods[1] * (self.crt['ModuleLongCorr'] if idx % 4 in [0, 1] else self.crt['ModuleSMDist']))
            z = (self.crt['CRTSurveyOrigin_z'] + 
                 self.crt[f'CRT_{z_pos}_z'] + 
                 mods[2] * self.crt['ModuleOff_z'])
            add_US_position(idx, x, y, z, rot)
            # print(self.crt['CRTSurveyOrigin_z'], self.crt[f'CRT_{z_pos}_z'], z_pos, self.crt['ModuleOff_z'])

        # Calculate Beam Spot position
        self.BeamSpot_x = self.steel['posCryoInDetEnc']['x'] + self.crt['CRTSurveyOrigin_x'] + self.crt['BeamSpotDSS_x'] + self.OriginXSet
        self.BeamSpot_y = self.steel['posCryoInDetEnc']['y'] + self.crt['CRTSurveyOrigin_y'] + self.crt['BeamSpotDSS_y'] + self.OriginYSet
        self.BeamSpot_z = self.steel['posCryoInDetEnc']['z'] + self.crt['CRTSurveyOrigin_z'] + self.crt['BeamSpotDSS_z'] + self.OriginZSet

    def construct(self, geom):
        if self.print_construct:
            print('Construct CRT <- ProtoDUNE-VD <- World')
        '''Construct the CRT geometry'''     
        
        def create_paddle_volume(name, shape, material="Polystyrene"):
            """Helper to create a paddle volume"""
            return geom.structure.Volume(name, material=material, shape=shape)
            
        def create_module_volume(name, shape, material="Air"):
            """Helper to create a module volume"""
            return geom.structure.Volume(name, material=material, shape=shape)

        def place_paddle(module_vol, paddle_vol, pos_x, pos_y, pos_z, paddle_id, rotation="rIdentity"):
            """Helper to place a paddle in a module"""
            pos = geom.structure.Position(
                f"posCRTPaddleSensitive_{paddle_id}",
                x=pos_x, y=pos_y, z=pos_z)
            place = geom.structure.Placement(
                f"placePaddle_{paddle_id}",
                volume=paddle_vol,
                pos=pos,
                rot=rotation)
            module_vol.placements.append(place.name)

        if self.HD_CRT_switch:
            # Create HD CRT basic shapes
            crt_paddle = geom.shapes.Box(
                "CRTPaddle",
                dx=self.crt['CRTPaddleWidth']/2,
                dy=self.crt['CRTPaddleHeight']/2,
                dz=self.crt['CRTPaddleLength']/2)

            crt_module = geom.shapes.Box(
                "CRTModule", 
                dx=self.crt['CRTModWidth']/2,
                dy=self.crt['CRTModHeight']/2,
                dz=self.crt['CRTModLength']/2)

            def build_module(side, modnum):
                """Build a complete CRT module for either U or D side"""
                # Create paddle volumes
                paddle_vols = {
                    f"{side}{modnum}_{i+1}": create_paddle_volume(
                        f"volAuxDetSensitive_CRTPaddle_{side}{modnum}_{i+1}",
                        crt_paddle)
                    for i in range(64)
                }
                
                # Add paddle volumes to builder
                for vol in paddle_vols.values():
                    self.add_volume(vol)
                
                # Create and populate module
                mod_vol = create_module_volume(
                    f"volAuxDet_CRTModule_{side}{modnum}",
                    crt_module)
                
                # Place paddles in pairs
                for i in range(32):
                    paddle_x1 = -self.crt['CRTModWidth']/2 + self.crt['CRTPaddleWidth']*(i + 0.5)
                    paddle_x2 = -self.crt['CRTModWidth']/2 + self.crt['CRTPaddleWidth']*(i + 1)
                    
                    # Place paddle pair
                    place_paddle(mod_vol, paddle_vols[f"{side}{modnum}_{i+1}"], 
                               paddle_x1, self.crt['CRTPaddleHeight']/2, Q('0cm'),
                               f"{side}{modnum}_{i+1}")
                    place_paddle(mod_vol, paddle_vols[f"{side}{modnum}_{i+33}"],
                               paddle_x2, -self.crt['CRTPaddleHeight']/2, Q('0cm'),
                               f"{side}{modnum}_{i+33}")
                
                return mod_vol

            # Build all U and D modules
            for modnum in range(1, 17):
                for side in ['U', 'D']:
                    mod_vol = build_module(side, modnum)
                    self.add_volume(mod_vol)

        if self.DP_CRT_switch:
            # Create DP CRT shapes
            def create_dp_shapes():
                shapes = {
                    'top_paddle': geom.shapes.Box(
                        "scintBox_Top",
                        dx=self.crt['TopCRTDPPaddleHeight']/2,
                        dy=self.crt['TopCRTDPPaddleLength']/2,
                        dz=self.crt['TopCRTDPPaddleWidth']/2),
                    'bottom_paddle': geom.shapes.Box(
                        "scintBox_Bottom",
                        dx=self.crt['BottomCRTDPPaddleHeight']/2,
                        dy=self.crt['BottomCRTDPPaddleLength']/2,
                        dz=self.crt['BottomCRTDPPaddleWidth']/2),
                    'top_module': geom.shapes.Box(
                        "ModulescintBox_Top",
                        dx=self.crt['TopCRTDPModHeight']/2,
                        dy=self.crt['TopCRTDPModWidth']/2,
                        dz=self.crt['TopCRTDPModLength']/2),
                    'bottom_module': geom.shapes.Box(
                        "ModulescintBox_Bottom",
                        dx=self.crt['BottomCRTDPModHeight']/2,
                        dy=self.crt['BottomCRTDPModWidth']/2,
                        dz=self.crt['BottomCRTDPModLength']/2)
                }
                return shapes

            shapes = create_dp_shapes()
            
            # Create volumes
            top_paddle_vol = create_paddle_volume("volAuxDetSensitiveCRTDPPaddleTop", shapes['top_paddle'])
            top_paddle_vol.params.append(("SensDet","AuxDet"))
            top_paddle_vol.params.append(("Solid","True"))
            bottom_paddle_vol = create_paddle_volume("volAuxDetSensitiveCRTDPPaddleBottom", shapes['bottom_paddle'])
            bottom_paddle_vol.params.append(("SensDet","AuxDet"))
            bottom_paddle_vol.params.append(("Solid","True"))

            def build_dp_module(is_top):
                """Build a DP CRT module (top or bottom)"""
                prefix = "Top" if is_top else "Bottom"
                mod_vol = create_module_volume(
                    f"volAuxDetCRTDPModule{prefix}",
                    shapes[f'{prefix.lower()}_module'])
                
                paddle_vol = top_paddle_vol if is_top else bottom_paddle_vol
                paddle_height = self.crt[f'{prefix}CRTDPPaddleHeight']
                module_height = self.crt[f'{prefix}CRTDPModHeight']
                
                pos_x = module_height/2 - paddle_height/2
                
                for i in range(8):
                    copynumber = i if is_top else 8+i
                    place_paddle(mod_vol, paddle_vol, 
                               pos_x, Q('0mm'), Q('0mm'),
                               f"{prefix.lower()}_{i}",
                               rotation="rMinus90AboutX")
                    pos_x -= self.crt['CRTDPPaddleSpacing']
                
                return mod_vol

            # Build and add top and bottom modules
            self.add_volume(build_dp_module(is_top=True))
            self.add_volume(build_dp_module(is_top=False))

    def place_in_volume(self, geom, enclosure_vol):
        '''Place CRT components in the detector enclosure volume.
        
        Args:
            geom: Geometry object
            enclosure_vol: The detector enclosure volume to place CRT modules in
        '''
        

        self.calculate_positions()

        # Place HD CRT modules if enabled
        if self.HD_CRT_switch:
            # Place upstream CRT modules
            for i in range(16):
                modnum = i + 1
                # Place U-side modules
                pos = geom.structure.Position(
                    f"posvolAuxDet_CRTModule_U{modnum}",
                    x=self.posCRTUS_x[i],
                    y=self.posCRTUS_y[i],
                    z=self.posCRTUS_z[i])
                
                place = geom.structure.Placement(
                    f"placeAuxDet_CRTModule_U{modnum}",
                    volume=self.get_volume(f"volAuxDet_CRTModule_U{modnum}"),
                    pos=pos,
                    rot=self.posCRTUS_rot[i])
                
                enclosure_vol.placements.append(place.name)

            # Place downstream CRT modules
            for i in range(16):
                modnum = i + 1
                # Place D-side modules
                pos = geom.structure.Position(
                    f"posvolAuxDet_CRTModule_D{modnum}",
                    x=self.posCRTDS_x[i],
                    y=self.posCRTDS_y[i],
                    z=self.posCRTDS_z[i])
                
                place = geom.structure.Placement(
                    f"placeAuxDet_CRTModule_D{modnum}",
                    volume=self.get_volume(f"volAuxDet_CRTModule_D{modnum}"),
                    pos=pos,
                    rot=self.posCRTDS_rot[i])
                
                enclosure_vol.placements.append(place.name)

        # Place DP CRT modules if enabled  
        if self.DP_CRT_switch:
            # Place top DP CRT module
            pos_top = geom.structure.Position(
                "posCRTDPTOPSensitive_1",
                x=Q('3848mm'),  # Updated from PERL script 
                y=Q('5882mm'),
                z=Q('0mm'))
            
            place_top = geom.structure.Placement(
                "placeCRTDPTOP",
                volume=self.get_volume("volAuxDetCRTDPModuleTop"),
                pos=pos_top,
                rot="rIdentity")
            
            enclosure_vol.placements.append(place_top.name)

            # Place bottom DP CRT module
            pos_bottom = geom.structure.Position(
                "posCRTDPBOTTOMSensitive_1",
                x=Q('-4406mm'),
                y=Q('-5882mm'), 
                z=Q('0mm'))
            
            place_bottom = geom.structure.Placement(
                "placeCRTDPBOTTOM",
                volume=self.get_volume("volAuxDetCRTDPModuleBottom"),
                pos=pos_bottom,
                rot="rIdentity")
            
            enclosure_vol.placements.append(place_bottom.name)