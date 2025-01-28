#!/usr/bin/env python
'''
TPC (Time Projection Chamber) builder for ProtoDUNE-VD geometry
'''

import gegede.builder
from gegede import Quantity as Q
import math
from collections import namedtuple


def line_clip(x0, y0, nx, ny, rcl, rcw):
    tol = 1.0E-4
    endpts = []
    
    if abs(nx) < tol:
        return [x0, 0, x0, rcw]
    if abs(ny) < tol:
        return [0, y0, rcl, y0]
        
    # Left border
    y = y0 - x0 * ny/nx
    if 0 <= y <= rcw:
        endpts.extend([0, y])
        
    # Right border
    y = y0 + (rcl-x0) * ny/nx
    if 0 <= y <= rcw:
        endpts.extend([rcl, y])
        if len(endpts) == 4:
            return endpts
            
    # Bottom border
    x = x0 - y0 * nx/ny
    if 0 <= x <= rcl:
        endpts.extend([x, 0])
        if len(endpts) == 4:
            return endpts
            
    # Top border
    x = x0 + (rcw-y0)* nx/ny
    if 0 <= x <= rcl:
        endpts.extend([x, rcw])
        
    # print(endpts)
    return endpts


def split_wires(wires, width, theta_deg):
    """Split wires at y=0 line into two halves.
    
    Args:
        wires: List of wire info
        width: Width to split at
        theta_deg: Wire angle in degrees
        
    Returns:
        Tuple of (lower_wires, upper_wires)
    """
    def make_wire(ich, endpts, wire_len=None):
        """Helper to create a wire with calculated center and length"""
        wcn = [(endpts[0] + endpts[2])/2, (endpts[1] + endpts[3])/2]
        if wire_len is None:
            dx, dy = endpts[0] - endpts[2], endpts[1] - endpts[3]
            wire_len = (dx*dx + dy*dy)**0.5
        return [ich] + wcn + [wire_len] + endpts

    theta = math.radians(theta_deg)
    nx, ny = math.cos(theta), math.sin(theta)
    winfo1, winfo2 = [], []  # Lower and upper halves
    ich1 = ich2 = 0
    
    for wire in wires:
        endpts = wire[4:8]
        y1, y2 = min(endpts[1], endpts[3]), max(endpts[1], endpts[3])
        
        if y2 < 0:  # Wire fully in lower half
            winfo1.append(make_wire(ich1, endpts, wire[3]))
            ich1 += 1
        elif y1 > 0:  # Wire fully in upper half
            winfo2.append(make_wire(ich2, endpts, wire[3]))
            ich2 += 1
        else:  # Wire crosses y=0
            x = wire[1] + (-wire[2]) * nx/ny  # Intersection point
            
            # Split endpoints at intersection
            endpts1 = endpts[:2] + [x, 0] if endpts[1] < 0 else [x, 0] + endpts[2:]
            endpts2 = [x, 0] + endpts[2:] if endpts[1] < 0 else endpts[:2] + [x, 0]
            
            winfo1.append(make_wire(ich1, endpts1))
            winfo2.append(make_wire(ich2, endpts2))
            ich1 += 1
            ich2 += 1

    # Adjust y positions
    for winfo, y_offset in [(winfo1, -0.25), (winfo2, 0.25)]:
        for w in winfo:
            w[5] -= y_offset * width  # y1
            w[7] -= y_offset * width  # y2
            w[2] = 0.5 * (w[5] + w[7])  # ycenter
            
    return winfo1, winfo2

def flip_wires(wires):
    """Flip wire configuration 180 degrees for second CRU.
    
    Args:
        wires: Input wire configurations
        
    Returns:
        list: Flipped wire configurations with negated x,y coordinates
    """
    return [
        [wire[0],                    # Keep channel number
         -0.5*(wire[4] + wire[6]),  # Flip x center
         -0.5*(wire[5] + wire[7]),  # Flip y center
         wire[3],                    # Keep wire length
         -wire[4], -wire[5],        # Flip endpoint 1
         -wire[6], -wire[7]]        # Flip endpoint 2
        for wire in wires
    ]

def generate_wires(length, width, nch, pitch, theta_deg, dia, w1offx, w1offy):
    """
    Generate wire positions for a single CRU plane without splitting.
    This matches the original PERL gen_wires() function.
    """
    # Convert angle to radians
    theta = math.radians(theta_deg)
    
    # Wire and pitch direction unit vectors
    dirw = [math.cos(theta), math.sin(theta)]
    dirp = [math.cos(theta - math.pi/2), math.sin(theta - math.pi/2)]
    
    # Alpha is angle for pitch calculations
    alpha = theta if theta <= math.pi/2 else math.pi - theta
    
    # Calculate wire spacing
    # dX = pitch / math.sin(alpha)
    # dY = pitch / math.sin(math.pi/2 - alpha)
    
    # Starting point adjusted for direction
    orig = [w1offx, w1offy]
    if dirp[0] < 0:
        orig[0] = length - w1offx
    if dirp[1] < 0:
        orig[1] = width - w1offy
        
    # Generate wires
    winfo = []
    offset = 0  # Starting point determined by offsets
    
    for ch in range(nch):
        # Reference point for this wire
        wcn = [orig[0] + offset * dirp[0],
            orig[1] + offset * dirp[1]]
            
        # Get endpoints from line clipping
        endpts = line_clip(wcn[0], wcn[1], dirw[0], dirw[1], length, width)
        
        if len(endpts) != 4:
            print(f"Could not find endpoints for wire {ch}")
            offset += pitch
            continue
            
        # Recenter coordinates
        endpts[0] -= length/2
        endpts[2] -= length/2
        endpts[1] -= width/2 
        endpts[3] -= width/2
        
        # Calculate wire center
        wcn[0] = (endpts[0] + endpts[2])/2
        wcn[1] = (endpts[1] + endpts[3])/2
        
        # Calculate wire length
        dx = endpts[0] - endpts[2]
        dy = endpts[1] - endpts[3]

        wlen = (dx**2 + dy**2)**(0.5)

        # Store wire info
        wire = [ch, wcn[0], wcn[1], wlen] + endpts

        # print(ch, wcn[0], wcn[1])

        winfo.append(wire)
        
        offset += pitch
    
    return winfo



class TPCBuilder(gegede.builder.Builder):
    '''
    Build the TPC volumes including wire planes
    '''
    def __init__(self, name):
        super(TPCBuilder, self).__init__(name)
        
        # Initialize parameters as None
        self.params = None
        self.wire_planes = {'U': None, 'V': None}

        # Add the subbuilders
        for name, builder in self.builders.items():
            self.add_builder(name, builder)

    def configure(self, tpc_parameters=None, print_config=False, print_construct=False, **kwds):
        if print_config:
            print('Configure TPC <- Cryostat <- ProtoDUNE-VD <- World')
        if (hasattr(self, '_configured')):
            return 
        # Store the parameters
        if tpc_parameters:
            self.params = tpc_parameters

        # print(self.params)

        self.print_construct = print_construct

        self._configured = True


    def construct_crm(self, geom, quad):
        

        # print(vols['tpc'].name)

        return vols['tpc']

    def construct_top_crp(self, geom):
        """Construct the Cold Readout Plane (CRP).
        Creates and processes wire configurations for U,V views.
        """
        # CRP total dimensions
        CRP_x = self.params['driftTPCActive'] + self.params['ReadoutPlane']
        CRP_y = self.params['widthCRP']
        CRP_z = self.params['lengthCRP']

        if self.print_construct:
            print(f"Construct CRP dimensions: {CRP_x} x {CRP_y} x {CRP_z}")

        # Generate wire configurations for first CRU
        if self.params.get('wires_on', 1):  # Check if wires are enabled
            # U wires
            winfo_u1 = generate_wires(
            self.params['lengthPCBActive'], 
            self.params['widthPCBActive'],
            self.params['nChans']['Ind1'],
            self.params['wirePitch']['U'],
            self.params['wireAngle']['U'].to('deg').magnitude,
            self.params['padWidth'],
            self.params['offsetUVwire'][0],
            self.params['offsetUVwire'][1])

            # V wires  
            winfo_v1 = generate_wires(
            self.params['lengthPCBActive'],
            self.params['widthPCBActive'], 
            self.params['nChans']['Ind2'],
            self.params['wirePitch']['V'],
            self.params['wireAngle']['V'].to('deg').magnitude,
            self.params['padWidth'],
            self.params['offsetUVwire'][0], 
            self.params['offsetUVwire'][1])

            # Generate flipped wires for second CRU
            winfo_u2 = flip_wires(winfo_u1)
            winfo_v2 = flip_wires(winfo_v1)

            # Split wires for each quadrant
            winfo_u1a, winfo_u1b = split_wires(winfo_u1, 
                               self.params['widthPCBActive'],
                               self.params['wireAngle']['U'].to('deg').magnitude)
            winfo_v1a, winfo_v1b = split_wires(winfo_v1,
                               self.params['widthPCBActive'],
                               self.params['wireAngle']['V'].to('deg').magnitude)

            winfo_u2a, winfo_u2b = split_wires(winfo_u2,
                               self.params['widthPCBActive'],
                               self.params['wireAngle']['U'].to('deg').magnitude)  
            winfo_v2a, winfo_v2b = split_wires(winfo_v2,
                               self.params['widthPCBActive'],
                               self.params['wireAngle']['V'].to('deg').magnitude)

            # Store wire configurations for CRM construction
            self.wire_configs = {
                'U': [winfo_u1a, winfo_u1b, winfo_u2a, winfo_u2b],
                'V': [winfo_v1a, winfo_v1b, winfo_v2a, winfo_v2b]
            }

        # Construct CRM volumes with wire configurations
        def make_box(name, dx, dy, dz, quad=""):
            """Create a box shape with given dimensions"""
            return geom.shapes.Box(f"{name}{quad}", dx=dx/2, dy=dy/2, dz=dz/2)
        
        def make_volume(name, shape, material="LAr", quad="", **params):
            """Create a volume with given shape and parameters"""
            vol = geom.structure.Volume(f"{name}{quad}", material=material, shape=shape)
            if params.get('params'):
                for param_type, param_value in params['params']:
                    vol.params.append((param_type, param_value))
            return vol
        
        # Calculate dimensions
        dims = {
            'active': (
                self.params['driftTPCActive'],
                self.params['widthPCBActive'] / 2,
                self.params['lengthPCBActive']
            ),
            'tpc': (
                self.params['driftTPCActive'] + self.params['ReadoutPlane'],
                self.params['widthPCBActive'] / 2,
                self.params['lengthPCBActive']
            ),
            'plane': (
                self.params['padWidth'],
                self.params['widthPCBActive'] / 2,
                self.params['lengthPCBActive']
            )
        }

        # Create shapes
        shapes = {
            'active': make_box('CRMActive', *dims['active']),
            **{plane: make_box(f'CRM{plane}Plane', *dims['plane']) 
               for plane in ['U', 'V', 'Z']}
        }

        # Create volumes
        vols = {
            'active': make_volume('volTPCActive', shapes['active']),
            **{f'plane_{p}': make_volume(f'volTPCPlane{p}', shapes[p]) 
               for p in ['U', 'V', 'Z']}
        }
        vols['active'].params.append(("SensDet","SimEnergyDeposit"))
        vols['active'].params.append(("StepLimit","0.5*cm"))
        vols['active'].params.append(("Efield","500*V/cm"))

        for quad in range(4):
            """Construct one CRM (Cold Readout Module) quadrant."""
           
            shapes['tpc'] = make_box('CRM', *dims['tpc'], quad=f"_{quad}")
            vols['tpc'] = make_volume('volTPC', shapes['tpc'], quad=f"_{quad}")
            vols['tpc'].params.append(("SensDet","SimEnergyDeposit"))
            vols['tpc'].params.append(("StepLimit","0.5*cm"))
            vols['tpc'].params.append(("Efield","500*V/cm"))
        
            # If wires are enabled
            if hasattr(self, 'wire_configs'):
                # Create wire shapes and volumes for U plane
                if 'U' in self.wire_configs:
                    for wire in self.wire_configs['U'][quad]:
                        # print(quad, wire[0],wire[3], wire[2])
                        wid = wire[0]
                        wlen = wire[3]
                        wire_shape = geom.shapes.Tubs(
                            f"CRMWireU{wid}_{quad}",
                            rmax=self.params['padWidth']/2,
                            dz=wlen/2.,
                            sphi="0deg",
                            dphi="360deg")
                        wire_vol = geom.structure.Volume(
                            f"volTPCWireU{wid}_{quad}",
                            material="Copper_Beryllium_alloy25",
                            shape=wire_shape)
                        # Place wire in U plane
                        pos = geom.structure.Position(
                            f"posWireU{wid}_{quad}",
                            x=Q("0cm"),
                            y=wire[2],  # ycenter
                            z=wire[1])  # xcenter
                        rot = "rUWireAboutX"
                        place = geom.structure.Placement(
                            f"placeWireU{wid}_{quad}",
                            volume=wire_vol,
                            pos=pos,
                            rot=rot)
                        vols['plane_U'].placements.append(place.name)

                # Create wire shapes and volumes for V plane  
                if 'V' in self.wire_configs:
                    for wire in self.wire_configs['V'][quad]:
                        wid = wire[0]
                        wlen = wire[3]
                        wire_shape = geom.shapes.Tubs(
                            f"CRMWireV{wid}_{quad}",
                            rmax=self.params['padWidth']/2,
                            dz=wlen/2.,
                            sphi="0deg",
                            dphi="360deg")
                        wire_vol = geom.structure.Volume(
                            f"volTPCWireV{wid}_{quad}",
                            material="Copper_Beryllium_alloy25",
                            shape=wire_shape)
                        # Place wire in V plane
                        pos = geom.structure.Position(
                            f"posWireV{wid}_{quad}",
                            x=Q("0cm"),
                            y=wire[2],  # ycenter 
                            z=wire[1])  # xcenter
                        rot = "rVWireAboutX"
                        place = geom.structure.Placement(
                            f"placeWireV{wid}_{quad}",
                            volume=wire_vol,
                            pos=pos,
                            rot=rot)
                        vols['plane_V'].placements.append(place.name)

                # Create and place Z wires
                nch = self.params['nChans']['Col']//2
                zdelta = self.params['lengthPCBActive'] - self.params['wirePitch']['Z'] * nch
                if zdelta < 0:
                    print("Warning: Z delta should be positive or 0")
                    zdelta = 0

                zoffset = zdelta if quad <= 1 else 0
                
                wire_shape_z = geom.shapes.Tubs(
                    f"CRMWireZ{quad}",
                    rmax=self.params['padWidth']/2,
                    dz=dims['plane'][1]/2.,  # Half width
                    sphi="0deg",
                    dphi="360deg")
                wire_vol_z = geom.structure.Volume(
                    f"volTPCWireZ{quad}",
                    material="Copper_Beryllium_alloy25", 
                    shape=wire_shape_z)

                # Place Z wires
                for i in range(nch):
                    zpos = zoffset + (i + 0.5) * self.params['wirePitch']['Z'] - 0.5 * self.params['lengthPCBActive']
                    if abs(0.5 * self.params['lengthPCBActive'] - abs(zpos)) < 0:
                        raise ValueError(f"Cannot place wire {i} in view Z, plane too small")
                        
                    wid = i + quad * nch
                    pos = geom.structure.Position(
                        f"posWireZ{wid}_{quad}",
                        x=Q("0cm"),
                        y=Q("0cm"),
                        z=zpos)
                    rot = "rPlus90AboutX"
                    place = geom.structure.Placement(
                        f"placeWireZ{wid}_{quad}",
                        volume=wire_vol_z,
                        pos=pos,
                        rot=rot)
                    vols['plane_Z'].placements.append(place.name)


            # Define placements
            placements = {
                'active': (-self.params['ReadoutPlane']/2, 0, 0),
                'plane_U': (0.5*dims['tpc'][0] - 2.5*self.params['padWidth'], 0, 0),
                'plane_V': (0.5*dims['tpc'][0] - 1.5*self.params['padWidth'], 0, 0),
                'plane_Z': (0.5*dims['tpc'][0] - 0.5*self.params['padWidth'], 0, 0)
            }

            # Place all volumes
            for name, (x, y, z) in placements.items():
                pos = geom.structure.Position(f"pos{name}{quad}_pos", x=x, y=Q('0cm'), z=Q('0cm'))
                place = geom.structure.Placement(f"pos{name.split('_')[-1]}{quad}", 
                                              volume=vols[name], 
                                              pos=pos)
                vols['tpc'].placements.append(place.name)

            self.add_volume(vols['tpc'])


    def construct(self, geom):
        if self.print_construct:
            print('Construct TPC <- Cryostat <- ProtoDUNE-VD <- World')
        
        #print(self.params)

        # Build top CRP
        self.construct_top_crp(geom)

        
    def place_tpcs(self, geom, cryo_vol, argon_dim, params):
        '''Place TPC volumes in cryostat
        
        Args:
            geom: Geometry object
            cryo_vol: Volume to place TPCs in 
            argon_dim: Tuple of LAr dimensions (x,y,z)
            params: Dictionary of relevant parameters
        '''
        # Calculate base positions for top/bottom TPCs
        posX = argon_dim[0]/2 - params['HeightGaseousAr'] - params['Upper_xLArBuffer'] - \
               0.5*(params['driftTPCActive'] + params['ReadoutPlane'])
        posXBot = posX - params['driftTPCActive'] - params['heightCathode'] - params['ReadoutPlane']

        CRP_y = params['widthCRP'] 
        CRP_z = params['lengthCRP']
        
        # Start from front of detector
        posZ = -0.5*argon_dim[2] + params['zLArBuffer'] + 0.5*CRP_z

        # Loop over CRM rows and columns
        idx = 0
        for ii in range(params['nCRM_z']):
            # Increment Z position every 2 rows
            if ii % 2 == 0 and ii > 0:
                posZ += CRP_z
                
            # Start from left side
            posY = -0.5*argon_dim[1] + params['yLArBuffer'] + 0.5*CRP_y

            for jj in range(params['nCRM_x']):
                # Increment Y position every 2 columns  
                if jj % 2 == 0 and jj > 0:
                    posY += CRP_y
                
                # Calculate quadrant and offsets
                if ii % 2 == 0:
                    if jj % 2 == 0:
                        quad = 0
                        pcbOffsetY = params['borderCRP']/2
                        pcbOffsetZ = params['borderCRP']/2 - params['gapCRU']/4
                        myposTPCY = posY - CRP_y/4 + pcbOffsetY
                        myposTPCZ = posZ - CRP_z/4 + pcbOffsetZ
                    else:
                        quad = 1
                        pcbOffsetY = -params['borderCRP']/2
                        pcbOffsetZ = params['borderCRP']/2 - params['gapCRU']/4
                        myposTPCY = posY + CRP_y/4 + pcbOffsetY  
                        myposTPCZ = posZ - CRP_z/4 + pcbOffsetZ
                else:
                    if jj % 2 == 0:
                        quad = 2
                        pcbOffsetY = params['borderCRP']/2
                        pcbOffsetZ = -(params['borderCRP']/2 - params['gapCRU']/4)
                        myposTPCY = posY - CRP_y/4 + pcbOffsetY
                        myposTPCZ = posZ + CRP_z/4 + pcbOffsetZ
                    else:
                        quad = 3
                        pcbOffsetY = -params['borderCRP']/2 
                        pcbOffsetZ = -(params['borderCRP']/2 - params['gapCRU']/4)
                        myposTPCY = posY + CRP_y/4 + pcbOffsetY
                        myposTPCZ = posZ + CRP_z/4 + pcbOffsetZ

                # Get TPC volume for this quadrant
                tpc_vol = self.get_volume(f'volTPC_{quad}')

                # Place top TPC
                pos_top = geom.structure.Position(
                    f"posTopTPC_{idx}",
                    x=posX,
                    y=myposTPCY, 
                    z=myposTPCZ
                )
                place_top = geom.structure.Placement(
                    f"placeTopTPC_{idx}",
                    volume=tpc_vol,
                    pos=pos_top
                )
                cryo_vol.placements.append(place_top.name)

                # Place bottom TPC
                pos_bot = geom.structure.Position(
                    f"posBotTPC_{idx}",
                    x=posXBot,
                    y=myposTPCY,
                    z=myposTPCZ 
                )
                place_bot = geom.structure.Placement(
                    f"placeBotTPC_{idx}",
                    volume=tpc_vol,
                    pos=pos_bot,
                    rot='rPlus180AboutY'  # Rotate bottom TPC
                )
                cryo_vol.placements.append(place_bot.name)

                idx += 1
