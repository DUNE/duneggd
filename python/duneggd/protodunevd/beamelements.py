#!/usr/bin/env python
'''
beamelements builder for ProtoDUNE-VD geometry 
'''

import gegede.builder
from gegede import Quantity as Q
import math

class BeamElementsBuilder(gegede.builder.Builder):
    '''
    Build the ProtoDUNE-VD beamelements
    '''

    def __init__(self, name):
        super(BeamElementsBuilder, self).__init__(name)
        self.beam = None
        self.FoamPadding = None
        self.steel = None
        self.cryo = None

    def calculate_beam_angles(self):
        """Calculate derived beam angle parameters"""
        
        # Convert angles to radians
        theta3XZ_rad = float(self.beam['theta3XZ'].to('rad').magnitude)
        thetaYZ_rad = float(self.beam['thetaYZ'].to('rad').magnitude)

        # Calculate beam angles
        BeamTheta3 = math.atan(math.sqrt(math.tan(theta3XZ_rad)**2 + 
                                       math.tan(thetaYZ_rad)**2))
        BeamPhi3 = math.atan(math.tan(thetaYZ_rad)/math.tan(theta3XZ_rad))

        # Store calculated angles
        self.beam['BeamTheta3'] = BeamTheta3
        self.beam['BeamPhi3'] = BeamPhi3
        self.beam['BeamTheta3Deg'] = math.degrees(BeamTheta3)
        self.beam['BeamPhi3Deg'] = math.degrees(BeamPhi3)

        # Calculate deltas
        self.beam['DeltaXZ3'] = math.tan(BeamTheta3)*math.cos(BeamPhi3)
        self.beam['DeltaYZ3'] = math.tan(BeamTheta3)*math.sin(BeamPhi3)

       

    def configure(self, steel_parameters=None, cryostat_parameters=None, 
                 beam_parameters=None, FoamPadding=None, 
                 OriginXSet=None, OriginYSet=None, OriginZSet=None,  # Add these parameters
                 print_config=False,  
                 print_construct=False,
                 **kwargs):
        """Configure beam parameters"""
        
        if print_config:
            print('Configure BeamElements <- ProtoDUNE-VD <- World')
        if hasattr(self, '_configured'):
            return

        self.beam = beam_parameters
        self.steel = steel_parameters
        self.cryo = cryostat_parameters
        self.FoamPadding = FoamPadding

        # Store origin coordinates directly in the class
        self.OriginXSet = OriginXSet
        self.OriginYSet = OriginYSet
        self.OriginZSet = OriginZSet

        if self.beam and self.steel and self.cryo and self.FoamPadding:
            # Calculate derived beam angles
            self.calculate_beam_angles()

            # Calculate beam vacuum pipe radius
            self.beam['BeamVaPipeRad'] = self.beam['BeamPipeRad'] - Q('0.2cm')
            self.beam['BeamVaPipeLe'] = self.beam['BeamPipeLe']

            # Calculate positions and lengths
            cos_theta3 = math.cos(self.beam['BeamTheta3'])
            
            # Calculate beam plug parameters
            self.beam['BeamPlugUSAr'] = Q('1cm')/cos_theta3
            self.beam['BeamPlugLe'] = Q('188cm')/cos_theta3 - self.beam['BeamPlugUSAr']
            self.beam['BeamPlugNiLe'] = self.beam['BeamPlugLe'] - Q('0.59cm')/cos_theta3
            self.beam['BeamPlugNiPos_z'] = Q('0.59cm')/(2*cos_theta3)

            # Steel plate front face coordinates
            self.beam['BeamWStPlateFF_x'] = Q('634.2cm') - self.cryo['Cryostat_x']/2
            self.beam['BeamWStPlateFF_y'] = (self.cryo['Cryostat_y']/2 + 
                                            self.steel['SteelSupport_y'] + 
                                            self.FoamPadding)
            self.beam['BeamWStPlateFF_z'] = -(self.cryo['Cryostat_z']/2 + 
                                            self.FoamPadding + 
                                            self.steel['SteelPlate'])

            # Steel plate parameters
            self.beam['BeamWStPlateLe'] = self.steel['SteelPlate']/cos_theta3 + Q('0.001cm')
            self.beam['BeamWStPlate_x'] = (self.beam['BeamWStPlateFF_x'] - 
                                        (self.steel['SteelPlate']/2)*self.beam['DeltaXZ3'])
            self.beam['BeamWStPlate_y'] = (self.beam['BeamWStPlateFF_y'] - 
                                        (self.steel['SteelPlate']/2)*self.beam['DeltaYZ3'])
            self.beam['BeamWStPlate_z'] = (self.beam['BeamWStPlateFF_z'] + 
                                        self.steel['SteelPlate']/2)

            # Foam removal parameters
            self.beam['BeamWFoRemLe'] = self.FoamPadding/cos_theta3 + Q('0.001cm')
            self.beam['BeamWFoRemPosDZ'] = self.steel['SteelPlate'] + self.FoamPadding/2
            self.beam['BeamWFoRem_x'] = (self.beam['BeamWStPlateFF_x'] - 
                                        self.beam['BeamWFoRemPosDZ']*self.beam['DeltaXZ3'])
            self.beam['BeamWFoRem_y'] = (self.beam['BeamWStPlateFF_y'] - 
                                        self.beam['BeamWFoRemPosDZ']*self.beam['DeltaYZ3'])
            self.beam['BeamWFoRem_z'] = (self.beam['BeamWStPlateFF_z'] + 
                                        self.beam['BeamWFoRemPosDZ'])

            # Steel support parameters
            self.beam['BeamWStSuLe'] = ((self.steel['SteelSupport_z'] - 
                                        self.steel['SteelPlate'])/cos_theta3 + Q('0.001cm'))
            self.beam['BeamWStSuPosDZ'] = -(self.steel['SteelSupport_z'] - 
                                        self.steel['SteelPlate'])/2
            self.beam['BeamWStSu_x'] = (self.beam['BeamWStPlateFF_x'] - 
                                    self.beam['BeamWStSuPosDZ']*self.beam['DeltaXZ3'])
            self.beam['BeamWStSu_y'] = (self.beam['BeamWStPlateFF_y'] - 
                                    self.beam['BeamWStSuPosDZ']*self.beam['DeltaYZ3'])
            self.beam['BeamWStSu_z'] = (self.beam['BeamWStPlateFF_z'] + 
                                    self.beam['BeamWStSuPosDZ'])

            # Foam window parameters
            self.beam['BeamWFoPosDZ'] = (self.steel['SteelPlate'] + self.FoamPadding - 
                                        self.beam['BeamWFoLe']*cos_theta3/2)
            self.beam['BeamWFo_x'] = (self.beam['BeamWStPlateFF_x'] - 
                                    self.beam['BeamWFoPosDZ']*self.beam['DeltaXZ3'])
            self.beam['BeamWFo_y'] = (self.beam['BeamWStPlateFF_y'] - 
                                    self.beam['BeamWFoPosDZ']*self.beam['DeltaYZ3'] + 
                                    self.steel['posCryoInDetEnc']['y'])
            self.beam['BeamWFo_z'] = (self.beam['BeamWStPlateFF_z'] + 
                                    self.beam['BeamWFoPosDZ'])

            # Glass window parameters
            self.beam['BeamWGlPosDZ'] = (self.steel['SteelPlate'] + self.FoamPadding - 
                                        (self.beam['BeamWFoLe'] + 
                                        self.beam['BeamWGlLe']/2)*cos_theta3)
            self.beam['BeamWGl_x'] = (self.beam['BeamWStPlateFF_x'] - 
                                    self.beam['BeamWGlPosDZ']*self.beam['DeltaXZ3'])
            self.beam['BeamWGl_y'] = (self.beam['BeamWStPlateFF_y'] - 
                                    self.beam['BeamWGlPosDZ']*self.beam['DeltaYZ3'] + 
                                    self.steel['posCryoInDetEnc']['y'])
            self.beam['BeamWGl_z'] = (self.beam['BeamWStPlateFF_z'] + 
                                    self.beam['BeamWGlPosDZ'])

            # Vacuum window parameters
            self.beam['BeamWVaPosDZ'] = (self.steel['SteelPlate'] + self.FoamPadding - 
                                        (self.beam['BeamWFoLe'] + self.beam['BeamWGlLe'] + 
                                        self.beam['BeamPipeLe']/2)*cos_theta3)
            self.beam['BeamWVa_x'] = (self.beam['BeamWStPlateFF_x'] - 
                                    self.beam['BeamWVaPosDZ']*self.beam['DeltaXZ3'])
            self.beam['BeamWVa_y'] = (self.beam['BeamWStPlateFF_y'] - 
                                    self.beam['BeamWVaPosDZ']*self.beam['DeltaYZ3'] + 
                                    self.steel['posCryoInDetEnc']['y'])
            self.beam['BeamWVa_z'] = (self.beam['BeamWStPlateFF_z'] + 
                                    self.beam['BeamWVaPosDZ'])

            # Calculate beam plug parameters
            self.beam['BeamPlugPosDZ'] = (self.steel['SteelPlate'] + self.FoamPadding + 
                                        self.cryo['SteelThickness'] + 
                                        self.beam['BeamPlugUSAr'] + 
                                        self.beam['BeamPlugLe']*cos_theta3/2)
            self.beam['BeamPlug_x'] = (self.beam['BeamWStPlateFF_x'] - 
                                    self.beam['BeamPlugPosDZ']*self.beam['DeltaXZ3'])
            self.beam['BeamPlug_y'] = (self.beam['BeamWStPlateFF_y'] - 
                                    self.beam['BeamPlugPosDZ']*self.beam['DeltaYZ3'])
            self.beam['BeamPlug_z'] = (self.beam['BeamWStPlateFF_z'] + 
                                    self.beam['BeamPlugPosDZ'])

            # Beam plug flange parameters
            self.beam['BePlFlangePosDZ'] = (self.steel['SteelPlate'] + self.FoamPadding + 
                                        self.cryo['SteelThickness'] + 
                                        self.beam['BeamPlugUSAr'] + 
                                        self.beam['BeamPlugLe']*cos_theta3)
            self.beam['BePlFlange_x'] = (self.beam['BeamWStPlateFF_x'] - 
                                        self.beam['BePlFlangePosDZ']*self.beam['DeltaXZ3'])
            self.beam['BePlFlange_y'] = (self.beam['BeamWStPlateFF_y'] - 
                                        self.beam['BePlFlangePosDZ']*self.beam['DeltaYZ3'])
            self.beam['BePlFlange_z'] = (self.beam['BeamWStPlateFF_z'] + 
                                        self.beam['BePlFlangePosDZ'] + Q('1.8cm'))

            # Beam plug membrane parameters
            self.beam['BeamPlugMembPosDZ'] = (self.steel['SteelPlate'] + self.FoamPadding + 
                                            self.cryo['SteelThickness'])
            self.beam['BeamPlugMemb_x'] = (self.beam['BeamWStPlateFF_x'] - 
                                        self.beam['BeamPlugMembPosDZ']*self.beam['DeltaXZ3'])
            self.beam['BeamPlugMemb_y'] = (self.beam['BeamWStPlateFF_y'] - 
                                        self.beam['BeamPlugMembPosDZ']*self.beam['DeltaYZ3'])
            self.beam['BeamPlugMemb_z'] = (self.beam['BeamWStPlateFF_z'] + 
                                        self.beam['BeamPlugMembPosDZ'])

            # Add beam window coordinates
            self.beam['BWFFCoord3X'] = (self.beam['BeamWStPlateFF_x'] - 
                                       self.beam['BeamWStSuPosDZ'] * self.beam['DeltaXZ3'] * 2 +
                                       self.OriginXSet)  # Use local variable
            self.beam['BWFFCoord3Y'] = (self.beam['BeamWStPlateFF_y'] - 
                                       self.beam['BeamWStSuPosDZ'] * self.beam['DeltaYZ3'] * 2 +
                                       self.OriginYSet +   # Use local variable
                                       self.steel['posCryoInDetEnc']['y'])
            self.beam['BWFFCoord3Z'] = (-(self.cryo['Cryostat_z']/2 + 
                                         self.steel['SteelSupport_z'] + 
                                         self.FoamPadding) +
                                       self.OriginZSet)  # Use local variable

            # Beam window steel plate coordinates
            self.beam['BW3StPlCoordX'] = (self.beam['BeamWStPlateFF_x'] + 
                                         self.OriginXSet)  # Use local variable
            self.beam['BW3StPlCoordY'] = (self.beam['BeamWStPlateFF_y'] + 
                                         self.OriginYSet +   # Use local variable
                                         self.steel['posCryoInDetEnc']['y'])
            self.beam['BW3StPlCoordZ'] = (self.beam['BeamWStPlateFF_z'] + 
                                         self.OriginZSet)  # Use local variable

            # PD2 Beam Plug calculations
            self.beam['thetaIIYZ'] = self.beam['thetaYZ']
            self.beam['thetaII3XZ'] = self.beam['theta3XZ']
            
            thetaIIYZ_rad = float(self.beam['thetaIIYZ'].to('rad').magnitude)
            thetaII3XZ_rad = float(self.beam['thetaII3XZ'].to('rad').magnitude)
            
            self.beam['BeamThetaII3'] = math.atan(math.sqrt(
                math.tan(thetaII3XZ_rad)**2 + math.tan(thetaIIYZ_rad)**2))
            self.beam['BeamPhiII3'] = math.atan(
                math.tan(thetaIIYZ_rad)/math.tan(thetaII3XZ_rad))

            # Calculate secondary angles
            self.beam['thetaIIYZ3prime'] = math.degrees(math.atan(
                math.sin(self.beam['BeamThetaII3']) * 
                math.sin(self.beam['BeamPhiII3'] + math.pi) /
                math.sqrt(math.cos(self.beam['BeamThetaII3'])**2 + 
                         math.sin(self.beam['BeamThetaII3'])**2 * 
                         math.cos(self.beam['BeamPhiII3'])**2)))

            # Calculate deltas
            self.beam['DeltaIIXZ3'] = math.tan(self.beam['BeamThetaII3']) * math.cos(self.beam['BeamPhiII3'])
            self.beam['DeltaIIYZ3'] = math.tan(self.beam['BeamThetaII3']) * math.sin(self.beam['BeamPhiII3'])

            # Beam plug membrane coordinates
            self.beam['BeamPlIIMem_x'] = self.beam['BeamPlugMemb_x']
            self.beam['BeamPlIIMem_y'] = self.beam['BeamPlugMemb_y']
            self.beam['BeamPlIIMem_z'] = self.beam['BeamPlugMemb_z']

            # Beam plug parameters
            inch = Q('2.54cm')
            self.beam['BeamPlIIRad'] = 11 * inch / 2
            self.beam['BeamPlIINiRad'] = 10 * inch / 2
            self.beam['BeamPlIIUSAr'] = Q('1cm') / math.cos(self.beam['BeamThetaII3'])
            self.beam['BeamPlIILe'] = (self.cryo['zLArBuffer'] - Q('5.3cm')) / math.cos(self.beam['BeamThetaII3'])
            self.beam['BeamPlIINiLe'] = self.beam['BeamPlIILe']
            self.beam['BeamPlIICapDZ'] = Q('0.5cm') * math.cos(self.beam['BeamThetaII3'])

            # Calculate positions
            self.beam['BeamPlIIPosDZ'] = (self.beam['BeamPlIICapDZ'] + 
                                         self.beam['BeamPlIILe'] * math.cos(self.beam['BeamThetaII3']) / 2.0)
            self.beam['BeamPlII_x'] = (self.beam['BeamPlIIMem_x'] - 
                                      self.beam['BeamPlIIPosDZ'] * self.beam['DeltaIIXZ3'])
            self.beam['BeamPlII_y'] = (self.beam['BeamPlIIMem_y'] - 
                                      self.beam['BeamPlIIPosDZ'] * self.beam['DeltaIIYZ3'])
            self.beam['BeamPlII_z'] = self.beam['BeamPlIIMem_z'] + self.beam['BeamPlIIPosDZ']

            # Cap positions
            self.beam['BeamPlIIUSCap_x'] = (self.beam['BeamPlIIMem_x'] - 
                                           self.beam['BeamPlIICapDZ'] / 2.0 * self.beam['DeltaIIXZ3'])
            self.beam['BeamPlIIUSCap_y'] = (self.beam['BeamPlIIMem_y'] - 
                                           self.beam['BeamPlIICapDZ'] / 2.0 * self.beam['DeltaIIYZ3'])
            self.beam['BeamPlIIUSCap_z'] = (self.beam['BeamPlIIMem_z'] + 
                                           self.beam['BeamPlIICapDZ'] / 2.0)

            self.beam['BeamPlIIDSPosDZ'] = (self.beam['BeamPlIICapDZ'] + 
                                           self.beam['BeamPlIILe'] * math.cos(self.beam['BeamThetaII3']) + 
                                           self.beam['BeamPlIICapDZ'] / 2)
            self.beam['BeamPlIIDSCap_x'] = (self.beam['BeamPlIIMem_x'] - 
                                           self.beam['BeamPlIIDSPosDZ'] * self.beam['DeltaIIXZ3'])
            self.beam['BeamPlIIDSCap_y'] = (self.beam['BeamPlIIMem_y'] - 
                                           self.beam['BeamPlIIDSPosDZ'] * self.beam['DeltaIIYZ3'])
            self.beam['BeamPlIIDSCap_z'] = (self.beam['BeamPlIIMem_z'] + 
                                           self.beam['BeamPlIIDSPosDZ'])
            
            self.print_construct = print_construct
            self._configured = True

    def construct_rotations(self, geom):
        """Define standard rotations used throughout the geometry"""
        rotations = {
        }
        rotations['rBeamW3'] = geom.structure.Rotation(
            'rBeamW3',
            x='0deg', y=f'-{self.beam["BeamTheta3Deg"]}deg', z=f'{self.beam["BeamPhi3Deg"]}deg'
        )
        rotations['rBeamWRev3'] = geom.structure.Rotation(
            'rBeamWRev3',
            x='-45deg', y='5.4611410351968113deg', z='-84.563498378865177deg'
        )
        rotations['rBeamPlII3'] = geom.structure.Rotation(
            'rBeamPlII3',
            x='-45deg', y='5.4611410351968113deg', z='-84.563498378865177deg'
        )
        return rotations

    def construct_shapes(self, geom):
        """Create all beam-related shapes"""
        
        # Common cut tube parameters
        common_params = {
            'rmin': Q('0cm'),
            'sphi': Q('0deg'),
            'dphi': Q('360deg'),
            'normalm': (-0.71030185483404029, 0, -0.70389720486682006),  # Lower normal vector
            'normalp': (0.71030185483404018, 0, 0.70389720486682017)     # Upper normal vector
        }

        shapes = {}

        # Create cut tubes
        tubes = {
            'BeamWindowFoam': {'rmax': self.beam['BeamPipeRad'], 
                            'z': self.beam['BeamWFoLe']},
            'BeamWindowGlassWool': {'rmax': self.beam['BeamPipeRad'],
                                'z': self.beam['BeamWGlLe']},
            'BeamPipe': {'rmax': self.beam['BeamPipeRad'],
                        'z': self.beam['BeamPipeLe']},
            'BeamPipeVacuum': {'rmax': self.beam['BeamVaPipeRad'],
                            'z': self.beam['BeamVaPipeLe']},
            'BeamWindowStPlate': {'rmax': self.beam['BeamPipeRad'],
                                'z': self.beam['BeamWStPlateLe']},
            'BeamWindowFoamRem': {'rmax': self.beam['BeamPipeRad'],
                                'z': self.beam['BeamWFoRemLe']},
            'BeamWindowStSu': {'rmax': self.beam['BeamPipeRad'],
                            'z': self.beam['BeamWStSuLe']},
        }

        for name, params in tubes.items():
            shapes[name] = geom.shapes.CutTubs(
                name,
                rmax=params['rmax'],
                dz=params['z']/2.,
                **common_params
            )

        # Create beam plug shapes
        shapes['BeamPlIIIn'] = geom.shapes.CutTubs(
            'BeamPlIIIn',
            rmax=self.beam['BeamPlIINiRad'],
            dz=self.beam['BeamPlIILe']/2.,
            **common_params
        )

        shapes['BeamPlIIOut'] = geom.shapes.CutTubs(
            'BeamPlIIOut',
            rmax=self.beam['BeamPlIIRad'],
            dz=self.beam['BeamPlIILe']/2.,
            **common_params
        )

        shapes['BeamPlIICap'] = geom.shapes.CutTubs(
            'BeamPlIICap',
            rmax=self.beam['BeamPlIIRad'],
            dz=Q('0.5cm')/2.,
            **common_params
        )

        return shapes

    def construct_volumes(self, geom, shapes):
        """Create volumes for all beam elements"""
        
        volumes = {}

        # Create BeamPlIINi volume with auxiliaries
        vol_ni = geom.structure.Volume(
            'volBeamPlIINi',
            material='NiGas1atm80K',
            shape=shapes['BeamPlIIIn']
        )
        vol_ni.params.append(("SensDet","SimEnergyDeposit"))
        vol_ni.params.append(("StepLimit","0.47625*cm"))
        vol_ni.params.append(("Efield","0*V/cm"))
        volumes['BeamPlIINi'] = vol_ni

        # Create BeamPlIIMod volume with BeamPlIINi inside
        vol_mod = geom.structure.Volume(
            'volBeamPlIIMod',
            material='G10',
            shape=shapes['BeamPlIIOut']
        )
        pos_ni = geom.structure.Position("posBeamPlIINi", x=Q('0cm'), y=Q('0cm'), z=Q('0cm'))
        place_ni = geom.structure.Placement("placeBeamPlIINi", volume=vol_ni, pos=pos_ni)
        vol_mod.placements.append(place_ni.name)
        volumes['BeamPlIIMod'] = vol_mod

        # Create cap volumes
        volumes['BeamPlIIUSCap'] = geom.structure.Volume(
            'volBeamPlIIUSCap',
            material='STEEL_STAINLESS_Fe7Cr2Ni',
            shape=shapes['BeamPlIICap']
        )

        volumes['BeamPlIIDSCap'] = geom.structure.Volume(
            'volBeamPlIIDSCap', 
            material='STEEL_STAINLESS_Fe7Cr2Ni',
            shape=shapes['BeamPlIICap']
        )

        # Create beam window volumes
        volumes['BeamWinFoam'] = geom.structure.Volume(
            'volBeamWinFoam',
            material='ProtoDUNEBWFoam',
            shape=shapes['BeamWindowFoam']
        )

        volumes['BeamWinGlassWool'] = geom.structure.Volume(
            'volBeamWinGlassWool',
            material='GlassWool', 
            shape=shapes['BeamWindowGlassWool']
        )

        # Create beam pipe with vacuum inside
        vol_vac = geom.structure.Volume(
            'volBeamPipeVac',
            material='Vacuum',
            shape=shapes['BeamPipeVacuum']
        )
        volumes['BeamPipeVac'] = vol_vac

        vol_pipe = geom.structure.Volume(
            'volBeamPipe',
            material='STEEL_STAINLESS_Fe7Cr2Ni',
            shape=shapes['BeamPipe']
        )
        pos_center = geom.structure.Position("posCenter", x=Q('0cm'), y=Q('0cm'), z=Q('0cm'))
        place_vac = geom.structure.Placement("placeBeamPipeVac", volume=vol_vac, pos=pos_center)
        vol_pipe.placements.append(place_vac.name)
        volumes['BeamPipe'] = vol_pipe

        return volumes

    def construct(self, geom):  # Add this line
        if self.print_construct:
            print('Construct Beam Elements <- ProtoDUNE-VD <- World')

        self.construct_rotations(geom)
        
        # Create all beam-related shapes
        shapes = self.construct_shapes(geom)
        
        # Create all beam-related volumes
        volumes = self.construct_volumes(geom, shapes)

        # Add volumes to be retrieved later
        for name, vol in volumes.items():
            self.add_volume(vol)

    def place_in_volume(self, geom, main_lv, cryo_lv):
        """
        Place all beam elements in the given volume
        
        Parameters
        ----------
        geom : gegede.construct.Geometry
            The geometry object
        main_lv : gegede.construct.Volume 
            The volume in which to place the beam elements
        """

        # Get all the volumes
        beam_foam_vol = self.get_volume('BeamWinFoam')
        beam_glass_vol = self.get_volume('BeamWinGlassWool')
        beam_pipe_vol = self.get_volume('BeamPipe')
        beam_plug_vol = self.get_volume('BeamPlIIMod')
        beam_plug_us_cap_vol = self.get_volume('BeamPlIIUSCap')
        beam_plug_ds_cap_vol = self.get_volume('BeamPlIIDSCap')

        # Place beam window foam
        pos_foam = geom.structure.Position(
            "posBeamWinFoam",
            x=self.beam['BeamWFo_x'],
            y=self.beam['BeamWFo_y'],
            z=self.beam['BeamWFo_z']
        )

        place_foam = geom.structure.Placement(
            "placeBeamWinFoam",
            volume=beam_foam_vol,
            pos=pos_foam,
            rot='rBeamWRev3'
        )
        main_lv.placements.append(place_foam.name)

        # Place glass wool 
        pos_glass = geom.structure.Position(
            "posBeamWinGlassWool",
            x=self.beam['BeamWGl_x'],
            y=self.beam['BeamWGl_y'],
            z=self.beam['BeamWGl_z']
        )

        place_glass = geom.structure.Placement(
            "placeBeamWinGlassWool",
            volume=beam_glass_vol,
            pos=pos_glass,
            rot='rBeamWRev3'
        )
        main_lv.placements.append(place_glass.name)

        # Place beam pipe
        pos_pipe = geom.structure.Position(
            "posBeamPipe",
            x=self.beam['BeamWVa_x'],
            y=self.beam['BeamWVa_y'],
            z=self.beam['BeamWVa_z']
        )

        place_pipe = geom.structure.Placement(
            "placeBeamPipe",
            volume=beam_pipe_vol,
            pos=pos_pipe,
            rot='rBeamWRev3'
        )
        main_lv.placements.append(place_pipe.name)

        # Place beam plug
        pos_plug = geom.structure.Position(
            "posBeamPlII",
            x=self.beam['BeamPlII_x'],
            y=self.beam['BeamPlII_y'],
            z=self.beam['BeamPlII_z']
        )
        
        place_plug = geom.structure.Placement(
            "placeBeamPlug",
            volume=beam_plug_vol,
            pos=pos_plug,
            rot='rBeamWRev3'
        )
        cryo_lv.placements.append(place_plug.name)

        # Place upstream cap
        pos_us_cap = geom.structure.Position(
            "posBeamPlugUSCap",
            x=self.beam['BeamPlIIUSCap_x'],
            y=self.beam['BeamPlIIUSCap_y'],
            z=self.beam['BeamPlIIUSCap_z']
        )

        place_us_cap = geom.structure.Placement(
            "placeBeamPlugUSCap",
            volume=beam_plug_us_cap_vol,
            pos=pos_us_cap,
            rot='rBeamWRev3'
        )
        cryo_lv.placements.append(place_us_cap.name)

        # Place downstream cap
        pos_ds_cap = geom.structure.Position(
            "posBeamPlugDSCap",
            x=self.beam['BeamPlIIDSCap_x'],
            y=self.beam['BeamPlIIDSCap_y'],
            z=self.beam['BeamPlIIDSCap_z']
        )

        place_ds_cap = geom.structure.Placement(
            "placeBeamPlugDSCap",
            volume=beam_plug_ds_cap_vol,
            pos=pos_ds_cap,
            rot='rBeamWRev3'
        )
        cryo_lv.placements.append(place_ds_cap.name)