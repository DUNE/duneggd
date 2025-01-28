#!/usr/bin/env python
'''
Field Cage builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q

class FieldCageBuilder(gegede.builder.Builder):
    '''
    Build the field cage for ProtoDUNE-VD.
    Implements both thick and slim field shapers arranged vertically.
    '''

    def configure(self, 
                 fieldcage_parameters=None,
                 print_config=False,
                 print_construct=False,
                 **kwds):
        
        if print_config:
            print('Configure Field Cage <- Cryostat <- ProtoDUNE-VD <- World')
        # Add guard against double configuration
        if hasattr(self, '_configured'):
            return
        
        if fieldcage_parameters:
            self.inner_radius = fieldcage_parameters.get('FieldShaperInnerRadius')
            self.outer_radius = fieldcage_parameters.get('FieldShaperOuterRadius')
            self.slim_inner_radius = fieldcage_parameters.get('FieldShaperSlimInnerRadius')
            self.slim_outer_radius = fieldcage_parameters.get('FieldShaperSlimOuterRadius')
            self.tor_rad = fieldcage_parameters.get('FieldShaperTorRad')
            self.separation = fieldcage_parameters.get('FieldShaperSeparation') 
            self.n_shapers = fieldcage_parameters.get('NFieldShapers')
            self.base_length = fieldcage_parameters.get('FieldShaperBaseLength')
            self.base_width = fieldcage_parameters.get('FieldShaperBaseWidth')
            self.first_shaper_to_roof = fieldcage_parameters.get('FirstFieldShaper_to_MembraneRoof')

            # Calculate derived dimensions
            self.length = self.base_length - 2*self.tor_rad
            self.width = self.base_width - 2*self.tor_rad
            
            self.cut_length = self.length + Q('0.02cm')
            self.cut_width = self.width + Q('0.02cm')

            self.cage_size_x = self.separation * self.n_shapers + Q('2cm')
            self.cage_size_y = self.width + Q('2cm') 
            self.cage_size_z = self.length + Q('2cm')

        self.print_construct = print_construct

        # Mark as configured
        self._configured = True

    def create_profile_components(self, geom, is_long=False):
        """Helper method to create basic field cage components"""
        length = self.width if is_long else self.length
        cut_length = self.cut_width if is_long else self.cut_length
        prefix = "Long" if is_long else "Short"
        
        components = {}
        
        # Basic shapes parameters
        shapes_params = {
            'halfcirc': {
                'rmin': Q('0mm'),
                'rmax': Q('3.18mm'),
                'dz': length/2.,
                'sphi': "-90deg",
                'dphi': "180deg"
            },
            'rect': {
                'dx': Q('10.42mm')/2,
                'dy': Q('1mm')/2,
                'dz': length/2
            },
            'cutter': {
                'dx': Q('0.51mm')/2,
                'dy': Q('6.37mm')/2,
                'dz': cut_length/2
            },
            'arc1': {
                'rmin': Q('27.58mm'),
                'rmax': Q('28.58mm'),
                'dz': length/2.,
                'sphi': "56deg",
                'dphi': "25deg"
            },
            'arc2': {
                'rmin': Q('64.09mm'),
                'rmax': Q('65.09mm'),
                'dz': length/2.,
                'sphi': "81deg",
                'dphi': "9deg"
            }
        }
        
        # Create basic shapes
        components['halfcirc'] = geom.shapes.Tubs(f"{prefix}FChalfcirc", **shapes_params['halfcirc'])
        components['rect'] = geom.shapes.Box(f"{prefix}FCrect", **shapes_params['rect'])
        components['cutter'] = geom.shapes.Box(f"{prefix}FCcutter", **shapes_params['cutter'])
        components['arc1'] = geom.shapes.Tubs(f"{prefix}FCarc1", **shapes_params['arc1'])
        components['arc2'] = geom.shapes.Tubs(f"{prefix}FCarc2", **shapes_params['arc2'])
        
        return components

    def create_profile(self, geom, components, prefix):
        """Helper method to create a field cage profile through Boolean operations"""
        # Boolean operations parameters
        bool_ops = [
            {
                'name': f"{prefix}FChalfcircCut",
                'type': 'subtraction',
                'first': components['halfcirc'],
                'second': components['cutter'],
                'pos': {'x': Q('0.249mm'), 'y': Q('0mm'), 'z': Q('0mm')}
            },
            {
                'name': f"{prefix}FCcircAndRect",
                'type': 'union',
                'second': components['rect'],
                'pos': {'x': Q('-4.705mm'), 'y': Q('-2.68mm'), 'z': Q('0mm')}
            },
            {
                'name': f"{prefix}FCwithArc1",
                'type': 'union',
                'second': components['arc1'],
                'pos': {'x': Q('-14.204mm'), 'y': Q('-21.1mm'), 'z': Q('0mm')}
            },
            {
                'name': f"{prefix}FCwithArc2",
                'type': 'union',
                'second': components['arc2'],
                'pos': {'x': Q('-19.84mm'), 'y': Q('-57.16mm'), 'z': Q('0mm')}
            }
        ]
        
        result = None
        for i, op in enumerate(bool_ops):
            pos = geom.structure.Position(f"pos{prefix}{i+1}", **op['pos'])
            if i == 0:
                result = geom.shapes.Boolean(op['name'], type=op['type'],
                                          first=op['first'], second=op['second'], pos=pos)
            else:
                result = geom.shapes.Boolean(op['name'], type=op['type'],
                                          first=result, second=op['second'], pos=pos)
        
        # Create final mirrored profile
        final_profile = geom.shapes.Boolean(
            f"{prefix}FCProfile",
            type='union',
            first=result,
            second=result,
            pos=geom.structure.Position(f"pos{prefix}final", x=Q('-39.68mm'), y=Q('0mm'), z=Q('0mm')),
            rot=geom.structure.Rotation(f"rot{prefix}final", x="0deg", y="180deg", z="0deg")
        )
        
        return final_profile

    def construct_thick_profile(self, geom, fc_corner):
        """Construct the thick field cage profile"""
        # Create short and long components
        short_components = self.create_profile_components(geom, is_long=False)
        long_components = self.create_profile_components(geom, is_long=True)
        
        # Create short and long profiles
        short_profile = self.create_profile(geom, short_components, "Short")
        long_profile = self.create_profile(geom, long_components, "Long")
        
        # Define complete field cage assembly parameters
        fc_assembly_params = [
            {
                'name': "FSunion1",
                'second': fc_corner,
                'pos': {'x': Q('-2cm'), 'y': -self.tor_rad, 'z': 0.5*self.length},
                'rot': "rPlus90AboutXPlus90AboutZ"
            },
            {
                'name': "FSunion2",
                'second': long_profile,
                'pos': {'x': Q('0cm'), 'y': -(0.5*self.width + self.tor_rad), 
                       'z': 0.5*self.length + self.tor_rad},
                'rot': "rPlus90AboutX"
            },
            {
                'name': "FSunion3",
                'second': fc_corner,
                'pos': {'x': Q('-2cm'), 'y': -(self.width + self.tor_rad), 
                       'z': 0.5*self.length},
                'rot': geom.structure.Rotation("rotfs3", x="270deg", y="270deg", z="270deg")
            },
            {
                'name': "FSunion4",
                'second': short_profile,
                'pos': {'x': Q('-3.968cm'), 'y': -(self.width + 2*self.tor_rad), 
                       'z': Q('0cm')},
                'rot': geom.structure.Rotation("rotfs4", x="0deg", y="0deg", z="180deg")
            },
            {
                'name': "FSunion5",
                'second': fc_corner,
                'pos': {'x': Q('-2cm'), 
                        'y': -(self.width + self.tor_rad),
                        'z': -0.5*self.length},
                'rot': geom.structure.Rotation("rotfs5", x="90deg", y="180deg", z="90deg")
            },
            {
                'name': "FSunion6",
                'second': long_profile,
                'pos': {'x': Q('0cm'),
                        'y': -(0.5*self.width + self.tor_rad),
                        'z': -(0.5*self.length + self.tor_rad)},
                'rot': geom.structure.Rotation("rotfs6", x="270deg", y="0deg", z="0deg")
            },
            {
                'name': "FieldShaperSolid",
                'second': fc_corner,
                'pos': {'x': Q('-2cm'), 'y': -self.tor_rad, 'z': -0.5*self.length},
                'rot': geom.structure.Rotation("rotfs7", x="90deg", y="90deg", z="90deg")
            }
        ]
        
        # Build field cage assembly
        result = short_profile
        for i, params in enumerate(fc_assembly_params):
            pos = geom.structure.Position(f"cornerpos{i+1}", **params['pos'])
            result = geom.shapes.Boolean(
                params['name'],
                type='union',
                first=result,
                second=params['second'],
                pos=pos,
                rot=params['rot']
            )
        
        return result
    
    def construct_slim_profile(self, geom, fc_slim_corner):
        """Construct the slim field cage profile through extrusions and Boolean operations"""
        
        # Create the extruded profile for long field cage
        long_vertices = (
            # Vertex coordinates from PERL script 
            (Q('3.719961039mm'), Q('-0.1389959507mm')),
            (Q('3.571767039mm'), Q('1.831707049mm')),
            (Q('3.129995039mm'), Q('3.452312049mm')),
            (Q('2.779043039mm'), Q('4.059650951mm')),
            (Q('2.404897039mm'), Q('4.869304049mm')),
            (Q('2.357290039mm'), Q('4.929363049mm')),
            (Q('2.300893039mm'), Q('4.981365049mm')),
            (Q('2.218862039mm'), Q('5.034099049mm')),
            (Q('2.108022039mm'), Q('5.075359049mm')),
            (Q('1.990712039mm'), Q('5.089275049mm')),
            (Q('-1.277475961mm'), Q('5.089275049mm')),
            (Q('-1.277475961mm'), Q('3.089275049mm')),
            (Q('-1.292001961mm'), Q('2.969646049mm')),
            (Q('-1.334726961mm'), Q('2.856853049mm')),
            (Q('-1.403207961mm'), Q('2.757732049mm')),
            (Q('-1.493417961mm'), Q('2.677898049mm')),
            (Q('-1.600229961mm'), Q('2.621746049mm')),
            (Q('-1.717172961mm'), Q('2.592937049mm')),
            (Q('-1.837778961mm'), Q('2.592937049mm')),
            (Q('-1.954721961mm'), Q('2.621746049mm')),
            (Q('-2.061533961mm'), Q('2.677898049mm')),
            (Q('-2.151743961mm'), Q('2.757732049mm')),
            (Q('-2.220224961mm'), Q('2.856853049mm')),
            (Q('-2.262949961mm'), Q('2.969646049mm')),
            (Q('-2.277475961mm'), Q('3.089275049mm')),
            (Q('-2.277475961mm'), Q('6.372722049mm')),
            (Q('-2.250742961mm'), Q('6.602214049mm')),
            (Q('-2.172128961mm'), Q('6.819500049mm')),
            (Q('-2.045663961mm'), Q('7.013103049mm')),
            (Q('-1.878183961mm'), Q('7.172283049mm')),
            (Q('-1.678598961mm'), Q('7.288738049mm')),
            (Q('-1.036630961mm'), Q('7.502361049mm')),
            (Q('-0.3783059606mm'), Q('7.587810049mm')),
            (Q('0.4213770394mm'), Q('7.515545049mm')),
            (Q('1.198232039mm'), Q('7.255291049mm')),
            (Q('2.028676039mm'), Q('6.743816049mm')),
            (Q('2.970571039mm'), Q('5.791179049mm')),
            (Q('3.796865039mm'), Q('4.436443049mm')),
            (Q('4.324453039mm'), Q('3.021892049mm')),
            (Q('4.633535039mm'), Q('1.497966049mm')),
            (Q('4.700551039mm'), Q('-0.6121409507mm')),
            (Q('4.413686039mm'), Q('-2.505695951mm')),
            (Q('4.633535039mm'), Q('-1.497966049mm')),
            (Q('4.324453039mm'), Q('-3.021892049mm')),
            (Q('3.796865039mm'), Q('-4.436443049mm')),
            (Q('2.970571039mm'), Q('-5.791179049mm')),
            (Q('2.028676039mm'), Q('-6.743816049mm')),
            (Q('1.198232039mm'), Q('-7.255291049mm')),
            (Q('0.4213770394mm'), Q('-7.515545049mm')),
            (Q('-0.3783059606mm'), Q('-7.587810049mm')),
            (Q('-1.036630961mm'), Q('-7.502361049mm')),
            (Q('-1.678598961mm'), Q('-7.288738049mm')),
            (Q('-1.878183961mm'), Q('-7.172283049mm')),
            (Q('-2.045663961mm'), Q('-7.013103049mm')),
            (Q('-2.172128961mm'), Q('-6.819500049mm')),
            (Q('-2.250742961mm'), Q('-6.602214049mm')),
            (Q('-2.277475961mm'), Q('-6.372722049mm')),
            (Q('-2.277475961mm'), Q('-3.089275049mm')),
            (Q('-2.262949961mm'), Q('-2.969646049mm')),
            (Q('-2.220224961mm'), Q('-2.856853049mm')),
            (Q('-2.151743961mm'), Q('-2.757732049mm')),
            (Q('-2.061533961mm'), Q('-2.677898049mm')),
            (Q('-1.954721961mm'), Q('-2.621746049mm')),
            (Q('-1.837778961mm'), Q('-2.592937049mm')),
            (Q('-1.717172961mm'), Q('-2.592937049mm')),
            (Q('-1.600229961mm'), Q('-2.621746049mm')),
            (Q('-1.493417961mm'), Q('-2.677898049mm')),
            (Q('-1.403207961mm'), Q('-2.757732049mm')),
            (Q('-1.334726961mm'), Q('-2.856853049mm')),
            (Q('-1.292001961mm'), Q('-2.969646049mm')),
            (Q('-1.277475961mm'), Q('-3.089275049mm')),
            (Q('-1.277475961mm'), Q('-5.089275049mm')),
            (Q('1.990712039mm'), Q('-5.089275049mm')),
            (Q('2.108022039mm'), Q('-5.075359049mm')),
            (Q('2.218862039mm'), Q('-5.034099049mm')),
            (Q('2.300893039mm'), Q('-4.981365049mm')),
            (Q('2.357290039mm'), Q('-4.929363049mm')),
            (Q('2.404897039mm'), Q('-4.869304049mm')),
            (Q('2.779043039mm'), Q('-4.059650951mm')),
            (Q('3.129995039mm'), Q('-3.452312049mm')),
            (Q('3.571767039mm'), Q('-1.831707049mm'))
        )

        zsections=[
            dict(z=-0.5*self.width, offset=(Q('0mm'), Q('0mm')), scale = 1.0),
            dict(z=0.5*self.width, offset=(Q('0mm'), Q('0mm')), scale = 1.0),
            ]

        # Create long profile extrusion
        long_fc_slim = geom.shapes.ExtrudedMany(
            "LongFCProfileSlim",
            polygon = long_vertices,
            zsections = zsections)

        # Create the extruded profile for short field cage
        short_vertices = long_vertices  # Using the same vertices as long profile
        zsections_short = [
            dict(z=-0.5*self.length, offset=(Q('0mm'), Q('0mm')), scale=1.0),
            dict(z=0.5*self.length, offset=(Q('0mm'), Q('0mm')), scale=1.0),
        ]

        # Create short profile extrusion
        short_fc_slim = geom.shapes.ExtrudedMany(
            "ShortFCProfileSlim",
            polygon=short_vertices,
            zsections=zsections_short
        )

        # Define complete slim field cage assembly parameters
        slim_assembly_params = [
            {
                'name': "FSunion1_Slim",
                'second': fc_slim_corner,
                'pos': {
                    'x': -self.tor_rad,
                    'y': Q('0cm'),
                    'z': 0.5*self.width
                },
                'rot': "rPlus90AboutX"
            },
            {
                'name': "FSunion2_Slim",
                'second': short_fc_slim,
                'pos': {
                    'x': -(0.5*self.length + self.tor_rad),
                    'y': Q('0cm'),
                    'z': 0.5*self.width + self.tor_rad
                },
                'rot': geom.structure.Rotation("rot2", x="0deg", y="-90deg", z="0deg")
            },
            {
                'name': "FSunion3_Slim",
                'second': fc_slim_corner,
                'pos': {
                    'x': -(self.length + self.tor_rad),
                    'y': Q('0cm'),
                    'z': 0.5*self.width
                },
                'rot': geom.structure.Rotation("rot3", x="90deg", y="-90deg", z="0deg")
            },
            {
                'name': "FSunion4_Slim",
                'second': long_fc_slim,
                'pos': {
                    'x': -(self.length + 2*self.tor_rad),
                    'y': Q('0cm'),
                    'z': Q('0cm')
                },
                'rot': geom.structure.Rotation("rot4", x="0deg", y="0deg", z="180deg")
            },
            {
                'name': "FSunion5_Slim",
                'second': fc_slim_corner,
                'pos': {
                    'x': -(self.length + self.tor_rad),
                    'y': Q('0cm'),
                    'z': -0.5*self.width
                },
                'rot': geom.structure.Rotation("rot5", x="90deg", y="180deg", z="0deg")
            },
            {
                'name': "FSunion6_Slim",
                'second': short_fc_slim,
                'pos': {
                    'x': -(0.5*self.length + self.tor_rad),
                    'y': Q('0cm'),
                    'z': -(0.5*self.width + self.tor_rad)
                },
                'rot': geom.structure.Rotation("rot6", x="270deg", y="90deg", z="90deg")
            },
            {
                'name': "FieldShaperSolidSlim",
                'second': fc_slim_corner,
                'pos': {
                    'x': -self.tor_rad,
                    'y': Q('0cm'),
                    'z': -0.5*self.width
                },
                'rot': geom.structure.Rotation("rot7", x="90deg", y="90deg", z="0deg")
            }
        ]

        # Build slim field cage assembly
        result = long_fc_slim
        for i, params in enumerate(slim_assembly_params):
            pos = geom.structure.Position(f"cornerposSlim{i+1}", **params['pos'])
            result = geom.shapes.Boolean(
                params['name'],
                type='union',
                first=result,
                second=params['second'],
                pos=pos,
                rot=params['rot']
            )

        return result

    def construct(self, geom):
        """Construct the Field Cage geometry"""
        if self.print_construct:
            print('Construct Field Cage <- Cryostat <- ProtoDUNE-VD <- World')

        # Create corner torus shapes for thick and slim field shapers
        fc_corner = geom.shapes.Torus(
            "FieldShaperCorner",
            rmin=self.inner_radius,
            rmax=self.outer_radius,
            rtor=self.tor_rad,
            startphi="0deg",
            deltaphi="90deg"
        )

        fc_slim_corner = geom.shapes.Torus(
            "FieldShaperSlimCorner", 
            rmin=self.slim_inner_radius,
            rmax=self.slim_outer_radius,
            rtor=self.tor_rad,
            startphi="0deg",
            deltaphi="90deg"
        )

        # Create the full field cage assembly using Boolean operations
        # First build the thick field cage profile
        fc_shape = self.construct_thick_profile(geom, fc_corner)
        
        # Then build the slim field cage profile 
        fc_slim_shape = self.construct_slim_profile(geom, fc_slim_corner)

        # Create volumes
        fc_vol = geom.structure.Volume(
            "volFieldShaper",
            material="ALUMINUM_Al",
            shape=fc_shape
        )

        fc_slim_vol = geom.structure.Volume(
            "volFieldShaperSlim",
            material="ALUMINUM_Al", 
            shape=fc_slim_shape
        )

        self.add_volume(fc_vol)
        self.add_volume(fc_slim_vol)

    def place_in_volume(self, geom, volume, offset_x):
        """Place field cage shapers in the given volume"""
        
        # Get field cage volumes
        fc_vol = self.get_volume('volFieldShaper')
        fc_slim_vol = self.get_volume('volFieldShaperSlim')

        # Place field cage shapers
        for i in range(self.n_shapers):
            # Calculate position
            dist = i * self.separation
            pos_x = offset_x - self.first_shaper_to_roof - dist
            
            if i < 36 or i > 77:  # Slim shapers at start and end
                #Create placement for slim shaper
                pos = geom.structure.Position(
                    f"posFieldShaper{i}",
                    x=pos_x,
                    y=Q('0cm'),
                    z=0.5*self.length + self.tor_rad
                )
                place = geom.structure.Placement(
                    f"placeFieldShaper{i}",
                    volume=fc_slim_vol,
                    pos=pos,
                    rot="rPlus90AboutXPlus90AboutZ"
                )
            else:  # Thick shapers in middle
                # Create placement for thick shaper
                pos = geom.structure.Position(
                    f"posFieldShaper{i}",
                    x=pos_x,
                    y=0.5*self.width + self.tor_rad,
                    z=Q('0cm')
                )
                place = geom.structure.Placement(
                    f"placeFieldShaper{i}", 
                    volume=fc_vol,
                    pos=pos,
                    rot="rIdentity"
                )
            
            volume.placements.append(place.name)
