#!/usr/bin/env python
'''
TPC builder for DUNE FD-VD
'''

import gegede.builder
from utils import *

class TPCBuilder(gegede.builder.Builder):
    def configure(self, **kwds):
        if not set(kwds).issubset(globals.TPC): # no unknown keywords
            msg = 'Unknown parameter in: "%s"' % (', '.join(sorted(kwds.keys())), )
            raise ValueError(msg)

        # The builder hierarchy takes care of all the configuration parameters
        globals.TPC = kwds

    def construct(self, geom):
        # for leaf builders, get the rest of the derived global parameters
        globals.SetDerived()
        # define the CRM shapes
        crmBox = geom.shapes.Box('CRM',
                                 dx = 0.5*globals.get("TPC_x"),
                                 dy = 0.5*globals.get("TPC_y"),
                                 dz = 0.5*globals.get("TPC_z"))
        crmactiveBox = geom.shapes.Box('CRMActive',
                                       dx = 0.5*globals.get("TPCActive_x"),
                                       dy = 0.5*globals.get("TPCActive_y"),
                                       dz = 0.5*globals.get("TPCActive_z"))
        crmplaneBoxes = {}
        for plane in ['U', 'V', 'Z']:
            crmplaneBoxes[plane] = geom.shapes.Box('CRM'+plane+'plane',
                                                   dx = 0.5*globals.get("padWidth"),
                                                   dy = 0.5*globals.get("TPCActive_y"),
                                                   dz = 0.5*globals.get("TPCActive_z"))

        # get the constituent logical volumes
        tpcactive_LV = geom.structure.Volume('vol'+self.name+'Active',
                                             material = "LAr",
                                             shape = crmactiveBox)
        tpcactive_LV.params.append(("SensDet","SimEnergyDeposit"))
        tpcactive_LV.params.append(("StepLimit","0.5208*cm"))
        tpcactive_LV.params.append(("Efield","500*V/cm"))
        tpcactive_pos = (-0.5*globals.get("ReadoutPlane"), Q('0cm'), Q('0cm'))

        # get the wires if asked for
        wires = None
        wireinfo = None
        if globals.get("wires"):
            wires = self.get_builder("Wires")
            wireinfo = wires.WireInfo

        postpcs = {}
        tpcplanes_LV = {}
        pid = 0
        for plane in ['U', 'V', 'Z']:
            tpcplane_LV = geom.structure.Volume('vol'+self.name+'Plane'+plane,
                                                material = "LAr",
                                                shape = crmplaneBoxes[plane])
            rotation = "rPlus90AboutX" if plane == 'Z' else "r%sWireAboutX" % plane
            if wires:
                n = 0
                for w in wireinfo[plane]:
                    if plane == 'Z' and (globals.get("TPCActive_z").magnitude < 2*abs(w[1])):
                        print("Cannot place wire %d in view Z, as plane is too small\n" % n)
                    pos = geom.structure.Position('posWire%s%d' % (plane, n),
                                                  x = Q('0cm'),
                                                  y = Q(str(w[2])+'cm'),
                                                  z = Q(str(w[1])+'cm'))
                    id = str(n) if plane != 'Z' else w[0]
                    wire_place = geom.structure.Placement('place%sWire%s%d'%(self.name, plane, n),
                                                          volume = wires.get_volume(
                                                                     "vol%sWire%s%s"%(self.name, plane, id)
                                                                   ),
                                                          pos = pos,
                                                          rot = rotation)
                    # place the wires inside each place
                    tpcplane_LV.placements.append(wire_place.name)
                    n += 1
            tpcplanes_LV[plane] = tpcplane_LV
            postpcs[plane] = (0.5*globals.get("TPC_x") - (2.5 - pid)*globals.get("padWidth"),
                              Q('0cm'),
                              Q('0cm'))
            pid += 1

        # final placements
        tpc_LV = geom.structure.Volume('vol'+self.name,
                                       material = "LAr",
                                       shape = crmBox)
        self.add_volume(tpc_LV)
        # place the individual place
        for plane in ['U', 'V', 'Z']:
            tpc_place = geom.structure.Placement('place%sPlane%s'%(self.name, plane),
                                                 volume = tpcplanes_LV[plane],
                                                 pos = geom.structure.Position('posPlane%s'%plane,
                                                                               x = postpcs[plane][0],
                                                                               y = postpcs[plane][1],
                                                                               z = postpcs[plane][2]),
                                                 rot = "rIdentity")
            tpc_LV.placements.append(tpc_place.name)
        # place the active block
        tpcactive_place = geom.structure.Placement('place%sActive'%self.name,
                                                   volume = tpcactive_LV,
                                                   pos = geom.structure.Position('posActive',
                                                                                 x = tpcactive_pos[0],
                                                                                 y = tpcactive_pos[1],
                                                                                 z = tpcactive_pos[2]),
                                                   rot = "rIdentity")
        tpc_LV.placements.append(tpcactive_place.name)
        return


