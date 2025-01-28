#!/usr/bin/env python
'''
Wires builder for DUNE FD-VD
'''

import gegede.builder
from utils import *
from math import *
import sys

# line clip on the rectangle boundary
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

    return endpts

class WiresBuilder(gegede.builder.Builder):
    def configure(self, **kwds):
        self.winfos = {}
        self._generated = [False]*3 # for each plane

    def generate_wires(self, plane):
        # generate the wires for a given plane
        if all(self._generated):
            print("Already generated the wires for all planes. Doing nothing")
            return
        plane_id = 0
        if plane == 'V':
            plane_id = 1
        if plane == 'Z':
            plane_id = 2

        nchs = globals.get("nChans")
        pitch = globals.get("wirePitch"+plane).magnitude
        theta_deg = globals.get("wireAngle"+plane) if plane != 'Z' else Q('0deg')
        theta = theta_deg.to('radian').magnitude
        dia = globals.get("padWidth").magnitude
        self.winfos[plane] = []

        if plane == 'Z':
            length = globals.get("TPCActive_y").magnitude
            nch = nchs['Col']
            for ch in range(nch):
                zpos = (ch + 0.5*(1 - nch))*pitch
                self.winfos[plane].append(['', zpos, 0., length])
        else:
            length = globals.get("TPCActive_z").magnitude - 0.02
            width = globals.get("TPCActive_y").magnitude - 0.02
            #  width = 0.
            nch = nchs['Ind1'] if plane == 'U' else nchs['Ind2']
            nchb = nchs['Ind1Bot']
            # Wire and pitch direction unit vectors
            dirw = [cos(theta), sin(theta)]
            dirp = [cos(theta - pi/2), sin(theta - pi/2)]

            # Alpha is angle for pitch calculations
            #  alpha = theta if theta <= pi/2 else pi - theta
            #
            #  # Calculate wire spacing
            #  dX = pitch / sin(alpha)
            #  dY = pitch / sin(pi/2 - alpha)
            #  if length <= 0:
            #      length = dX * nchb
            #  if width <= 0:
            #      width = dY * (nch - nchb)

            # Starting point adjusted for direction
            orig = [0, 0]
            if dirp[0] < 0:
                orig[0] = length
            if dirp[1] < 0:
                orig[1] = width

            # Generate wires
            offset = pitch/2.  # Starting point determined by offsets

            for ch in range(nch):
                # Reference point for this wire
                wcn = [orig[0] + offset * dirp[0],
                       orig[1] + offset * dirp[1]]

                # Get endpoints from line clipping
                endpts = line_clip(wcn[0], wcn[1], dirw[0], dirw[1], length, width)

                if len(endpts) != 4:
                    print("Could not find endpoints for wire %d" % ch)
                    offset += pitch
                    continue

                # Recenter coordinates
                endpts[0] -= length/2
                endpts[2] -= length/2
                endpts[1] -= width/2
                endpts[3] -= width/2

                # Calculate wire center
                offsetZ = 0.
                offsetY = 0.
                wcn[0] = (endpts[0] + endpts[2])/2 + offsetZ
                wcn[1] = (endpts[1] + endpts[3])/2 + offsetY

                # Calculate wire length
                dx = endpts[0] - endpts[2]
                dy = endpts[1] - endpts[3]

                wlen = (dx**2 + dy**2)**(0.5)

                # Store wire info
                wire = [ch, wcn[0], wcn[1], wlen] + endpts

                self.winfos[plane].append(wire)
                offset += pitch

        self._generated[plane_id] = True
        return

    # not returned as pint quantitites but raw numbers. expected that the conversion happens later
    @property
    def WireInfo(self):
        if not all(self._generated):
            print("Unable to access WireInfo, Maybe wire generation is set to False")
            sys.exit(1)
        return self.winfos

    def construct(self, geom):
        # for leaf builders, get the rest of the derived global parameters
        globals.SetDerived()
        # don't bother if upstream builders don't want it
        if not globals.get("wires"):
            return
        for plane in ['U', 'V', 'Z']:
            # generate the wires
            self.generate_wires(plane)
            winfo = self.winfos[plane]
            if plane == 'Z':
                z = Q(str(winfo[0][3])+'cm')
                shape = geom.shapes.Tubs('CRMWireZ',
                                         rmin = Q('0cm'),
                                         rmax = 0.5*globals.get("padWidth"),
                                         dz = 0.5*z,
                                         sphi = Q("0deg"),
                                         dphi = Q("360deg"))
                vol = geom.structure.Volume('volTPCWire'+plane+str(winfo[0][0]),
                                            material = "Copper_Beryllium_alloy25",
                                            shape = shape)
                self.add_volume(vol)
            else:
                for wire in winfo:
                    z = Q(str(wire[3])+'cm')
                    shape = geom.shapes.Tubs('CRMWire'+plane+str(wire[0]),
                                             rmin = Q('0cm'),
                                             rmax = 0.5*globals.get("padWidth"),
                                             dz = 0.5*z,
                                             sphi = Q("0deg"),
                                             dphi = Q("360deg"))
                    vol = geom.structure.Volume('volTPCWire'+plane+str(wire[0]),
                                                material = "Copper_Beryllium_alloy25",
                                                shape = shape)
                    self.add_volume(vol)
        return
