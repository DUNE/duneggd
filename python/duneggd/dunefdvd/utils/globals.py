import sys
from gegede import Quantity as Q

class Params:
    _params = {}
    _world = {}
    _tpc = {}
    _cryostat = {}
    _detenc = {}
    _fieldcage = {}
    _cathode = {}
    _arapuca = {}
    # have the derived parameters been calculated yet
    _hasDerived = False

    # set the long list of defaults
    _world['FieldCage_switch'] = True
    _world['Cathode_switch'] = True
    _world['workspace'] = 0
    _world['pdsconfig'] = 0
    _world['wires'] = True
    _world['tpc'] = True

    _tpc['nChans'] = {'Ind1': 286, 'Ind1Bot': 96, 'Ind2': 286, 'Col': 292}
    _tpc['wirePitchU'] = Q('0.765cm')
    _tpc['wirePitchV'] = Q('0.765cm')
    _tpc['wirePitchZ'] = Q('0.51cm')
    _tpc['wireAngleU'] = Q('150.0deg')
    _tpc['wireAngleV'] = Q('30.0deg')
    _tpc['widthPCBActive'] = Q('167.7006cm')
    _tpc['borderCRM'] = Q('0.0cm')
    _tpc['borderCRP'] = Q('0.5cm')
    _tpc['nCRM_y'] = 4*2
    _tpc['nCRM_z'] = 20*2
    _tpc['nCRM_x'] = 2
    _tpc['driftTPCActive'] = Q('650.0cm')
    _tpc['padWidth'] = Q('0.02cm')

    _cryostat['Argon_x'] = Q('1510cm')
    _cryostat['Argon_y'] = Q('1510cm')
    _cryostat['Argon_z'] = Q('6200cm')
    _cryostat['HeightGaseousAr'] = Q('100cm')
    _cryostat['SteelThickness'] = Q('0.12cm') # membrane

    _detenc['SteelSupport_x'] = Q('100cm')
    _detenc['SteelSupport_y'] = Q('100cm')
    _detenc['SteelSupport_z'] = Q('100cm')
    _detenc['FoamPadding'] = Q('80cm')
    _detenc['FracMassOfSteel'] = 0.5
    _detenc['SpaceSteelSupportToWall']    = Q('100cm')
    _detenc['SpaceSteelSupportToCeiling'] = Q('100cm')
    _detenc['RockThickness'] = Q('4000cm')

    _fieldcage['FieldShaperInnerRadius'] = Q('0.5cm')
    _fieldcage['FieldShaperOuterRadius'] = Q('2.285cm')
    _fieldcage['FieldShaperOuterRadiusSlim'] = Q('0.75cm')
    _fieldcage['FieldShaperTorRad'] = Q('2.3cm')
    _fieldcage['FieldCageArapucaWindowLength'] = Q('670cm')
    _fieldcage['FieldShaperSeparation'] = Q('6.0cm')

    _cathode['heightCathode'] = Q('4.0cm')
    _cathode['CathodeBorder'] = Q('4.0cm')
    _cathode['widthCathodeVoid'] = Q('76.35cm')
    _cathode['lengthCathodeVoid'] = Q('67.0cm')

    _arapuca['ArapucaOut_x'] = Q('65.0cm')
    _arapuca['ArapucaOut_y'] = Q('2.5cm')
    _arapuca['ArapucaOut_z'] = Q('65.0cm')
    _arapuca['ArapucaIn_x'] = Q('60.0cm')
    _arapuca['ArapucaIn_y'] = Q('2.0cm')
    _arapuca['ArapucaIn_z'] = Q('60.0cm')
    _arapuca['ArapucaAcceptanceWindow_x'] = Q('60.0cm')
    _arapuca['ArapucaAcceptanceWindow_y'] = Q('1.0cm')
    _arapuca['ArapucaAcceptanceWindow_z'] = Q('60.0cm')
    _arapuca['GapPD'] = Q('0.5cm')
    _arapuca['FrameToArapucaSpace'] = Q('1.0cm')
    _arapuca['FrameToArapucaSpaceLat'] = Q('10.0cm')
    _arapuca['VerticalPDdist'] = Q('75.0cm')
    _arapuca['FirstFrameVertDist'] = Q('40.0cm')

    _params.update(_world)
    _params.update(_tpc)
    _params.update(_cryostat)
    _params.update(_detenc)
    _params.update(_fieldcage)
    _params.update(_cathode)
    _params.update(_arapuca)

    @property
    def World(self):
        return type(self)._world

    @World.setter
    def World(self, inputdict):
        if inputdict:
            type(self)._world.update(inputdict)
        type(self)._params.update(type(self)._world)

    @property
    def TPC(self):
        return type(self)._tpc

    @TPC.setter
    def TPC(self, inputdict):
        if inputdict:
            type(self)._tpc.update(inputdict)
        type(self)._params.update(type(self)._tpc)

    @property
    def Cryostat(self):
        return type(self)._cryostat

    @Cryostat.setter
    def Cryostat(self, inputdict):
        if inputdict:
            type(self)._cryostat.update(inputdict)
        type(self)._params.update(type(self)._cryostat)

    @property
    def Enclosure(self):
        return type(self)._detenc

    @Enclosure.setter
    def Enclosure(self, inputdict):
        if inputdict:
            type(self)._detenc.update(inputdict)
        type(self)._params.update(type(self)._detenc)

    @property
    def FieldCage(self):
        return type(self)._fieldcage

    @FieldCage.setter
    def FieldCage(self, inputdict):
        if inputdict:
            type(self)._fieldcage.update(inputdict)
        type(self)._params.update(type(self)._fieldcage)

    @property
    def Cathode(self):
        return type(self)._cathode

    @Cathode.setter
    def Cathode(self, inputdict):
        if inputdict:
            type(self)._cathode.update(inputdict)
        type(self)._params.update(type(self)._cathode)

    @property
    def Arapuca(self):
        return type(self)._arapuca

    @Arapuca.setter
    def Arapuca(self, inputdict):
        if inputdict:
            type(self)._arapuca.update(inputdict)
        type(self)._params.update(type(self)._arapuca)

    def SetDerived(self):
        # calculate all the other parameters
        # accessible only once construction begins
        if type(self)._hasDerived:
            return

        # TPC parameters
        type(self)._tpc['nViews'] = len(type(self)._tpc['nChans'])
        type(self)._tpc['lengthPCBActive'] = type(self)._tpc['wirePitchZ'] * type(self)._tpc['nChans']['Col']
        type(self)._tpc['widthCRM_active'] = type(self)._tpc['widthPCBActive']
        type(self)._tpc['lengthCRM_active'] = type(self)._tpc['lengthPCBActive']
        type(self)._tpc['widthCRM'] = type(self)._tpc['widthPCBActive'] + 2 * type(self)._tpc['borderCRM']
        type(self)._tpc['lengthCRM'] = type(self)._tpc['lengthPCBActive'] + 2 * type(self)._tpc['borderCRM']

        if type(self)._world['workspace'] == 1:
            type(self)._tpc['nCRM_y'] = 1 * 2
            type(self)._tpc['nCRM_z'] = 1 * 2
            type(self)._tpc['nCRM_x'] = 1
        if type(self)._world['workspace'] == 2:
            type(self)._tpc['nCRM_y'] = 2 * 2
            type(self)._tpc['nCRM_z'] = 2 * 2
            type(self)._tpc['nCRM_x'] = 1
        if type(self)._world['workspace'] == 3:
            type(self)._tpc['nCRM_y'] = 4 * 2
            type(self)._tpc['nCRM_z'] = 3 * 2
            type(self)._tpc['nCRM_x'] = 1
        # 1x8x6
        if type(self)._world['workspace'] == 4:
            type(self)._tpc['nCRM_y'] = 4 * 2
            type(self)._tpc['nCRM_z'] = 7 * 2
            type(self)._tpc['nCRM_x'] = 1
        # 1x8x14
        if type(self)._world['workspace'] == 5:
            type(self)._tpc['nCRM_y'] = 4 * 2
            type(self)._tpc['nCRM_z'] = 20 * 2
            type(self)._tpc['nCRM_x'] = 1
        # 2x8x6
        if type(self)._world['workspace'] == 6:
            type(self)._tpc['nCRM_y'] = 4 * 2
            type(self)._tpc['nCRM_z'] = 3 * 2
            type(self)._tpc['nCRM_x'] = 2
        # 2x8x14
        if type(self)._world['workspace'] == 7:
            type(self)._tpc['nCRM_y'] = 4 * 2
            type(self)._tpc['nCRM_z'] = 7 * 2
            type(self)._tpc['nCRM_x'] = 2

        type(self)._tpc['widthTPCActive'] = type(self)._tpc['nCRM_y'] * (type(self)._tpc['widthCRM'] + type(self)._tpc['borderCRP'])
        type(self)._tpc['lengthTPCActive'] = type(self)._tpc['nCRM_z'] * (type(self)._tpc['lengthCRM'] + type(self)._tpc['borderCRP'])
        type(self)._tpc['ReadoutPlane'] = type(self)._tpc['nViews'] * type(self)._tpc['padWidth']
        type(self)._tpc['anodePlateWidth'] = type(self)._tpc['padWidth']/2.
        type(self)._tpc['TPCActive_x'] = type(self)._tpc['driftTPCActive']
        type(self)._tpc['TPCActive_y'] = type(self)._tpc['widthCRM_active']
        type(self)._tpc['TPCActive_z'] = type(self)._tpc['lengthCRM_active']
        type(self)._tpc['TPC_x'] = type(self)._tpc['TPCActive_x'] + type(self)._tpc['ReadoutPlane']
        type(self)._tpc['TPC_y'] = type(self)._tpc['widthCRM']
        type(self)._tpc['TPC_z'] = type(self)._tpc['lengthCRM']

        # Cryostat parameters
        if type(self)._world['workspace'] != 0:
            if type(self)._tpc['nCRM_x']== 1:
                type(self)._cryostat['Argon_x'] = type(self)._tpc['driftTPCActive'] + type(self)._cryostat['HeightGaseousAr'] +                 \
                                                  type(self)._tpc['ReadoutPlane'] + Q('100cm')
            type(self)._cryostat['Argon_y'] = type(self)._tpc['widthTPCActive'] + Q('162cm')
            type(self)._cryostat['Argon_z'] = type(self)._tpc['lengthTPCActive'] + Q('214.0cm')

        if type(self)._tpc['nCRM_x'] == 1:
            type(self)._cryostat['xLArBuffer'] = type(self)._cryostat['Argon_x'] - type(self)._tpc['driftTPCActive'] -                          \
                                                 type(self)._cryostat['HeightGaseousAr'] - type(self)._tpc['ReadoutPlane'] -                    \
                                                 type(self)._cathode['heightCathode']
        else:
            type(self)._cryostat['xLArBuffer'] = type(self)._cryostat['Argon_x'] - 2*type(self)._tpc['driftTPCActive'] -                        \
                                                 type(self)._cryostat['HeightGaseousAr'] - 2*type(self)._tpc['ReadoutPlane'] -                  \
                                                 type(self)._cathode['heightCathode']
        type(self)._cryostat['yLArBuffer'] = 0.5 * (type(self)._cryostat['Argon_y'] - type(self)._tpc['widthTPCActive'])
        type(self)._cryostat['zLArBuffer'] = 0.5 * (type(self)._cryostat['Argon_z'] - type(self)._tpc['lengthTPCActive'])
        type(self)._cryostat['Cryostat_x'] = type(self)._cryostat['Argon_x'] + 2*type(self)._cryostat['SteelThickness']
        type(self)._cryostat['Cryostat_y'] = type(self)._cryostat['Argon_y'] + 2*type(self)._cryostat['SteelThickness']
        type(self)._cryostat['Cryostat_z'] = type(self)._cryostat['Argon_z'] + 2*type(self)._cryostat['SteelThickness']
        type(self)._cryostat['TPCEnclosure_x'] = type(self)._cryostat['Argon_x'] -                                                              \
                                                 type(self)._cryostat['HeightGaseousAr'] +                                                      \
                                                 type(self)._tpc['nCRM_x']*type(self)._tpc['anodePlateWidth'] -                                 \
                                                 type(self)._cryostat['xLArBuffer']
        type(self)._cryostat['TPCEnclosure_y'] = type(self)._tpc['nCRM_y']*(type(self)._tpc['widthCRM'] + type(self)._tpc['borderCRP'])
        type(self)._cryostat['TPCEnclosure_z'] = type(self)._tpc['nCRM_z']*(type(self)._tpc['lengthCRM'] + type(self)._tpc['borderCRP'])


        # Enclosure parameters
        type(self)._detenc['FracMassOfAir'] = 1 - type(self)._detenc['FracMassOfSteel']
        type(self)._detenc['DetEncX']  =    type(self)._cryostat['Cryostat_x'] +                                                                \
                                            2*(type(self)._detenc['SteelSupport_x'] +                                                           \
                                            type(self)._detenc['FoamPadding']) +                                                                \
                                            type(self)._detenc['SpaceSteelSupportToCeiling']
        type(self)._detenc['DetEncY']  =    type(self)._cryostat['Cryostat_y'] +                                                                \
                                            2*(type(self)._detenc['SteelSupport_y'] +                                                           \
                                            type(self)._detenc['FoamPadding']) +                                                                \
                                            2*type(self)._detenc['SpaceSteelSupportToWall']
        type(self)._detenc['DetEncZ']  =    type(self)._cryostat['Cryostat_z'] +                                                                \
                                            2*(type(self)._detenc['SteelSupport_z'] +                                                           \
                                            type(self)._detenc['FoamPadding']) +                                                                \
                                            2*type(self)._detenc['SpaceSteelSupportToWall']

        type(self)._detenc['posCryoInDetEnc_x'] = - type(self)._detenc['DetEncX']/2 +                                                           \
                                                    type(self)._detenc['SteelSupport_x'] +                                                      \
                                                    type(self)._detenc['FoamPadding'] +                                                         \
                                                    type(self)._cryostat['Cryostat_x']/2

        type(self)._detenc['OriginXSet'] =  type(self)._detenc['DetEncX']/2.0 - type(self)._detenc['SteelSupport_x'] -                          \
                                            type(self)._detenc['FoamPadding'] - type(self)._cryostat['SteelThickness'] -                        \
                                            type(self)._cryostat['xLArBuffer'] - type(self)._tpc['driftTPCActive']/2.0 -                        \
                                            type(self)._cathode['heightCathode']
        if type(self)._tpc['nCRM_x'] == 2:
            type(self)._detenc['OriginXSet'] =  type(self)._detenc['DetEncX']/2.0 - type(self)._detenc['SteelSupport_x'] -                      \
                                                type(self)._detenc['FoamPadding'] - type(self)._cryostat['SteelThickness'] -                    \
                                                type(self)._cryostat['xLArBuffer'] - type(self)._tpc['driftTPCActive']/2.0 -                    \
                                                type(self)._cathode['heightCathode']/2.

        type(self)._detenc['OriginYSet'] =  type(self)._detenc['DetEncY']/2.0 - type(self)._detenc['SpaceSteelSupportToWall'] -                 \
                                            type(self)._detenc['SteelSupport_y'] - type(self)._detenc['FoamPadding'] -                          \
                                            type(self)._cryostat['SteelThickness'] - type(self)._cryostat['yLArBuffer'] -                       \
                                            type(self)._tpc['widthTPCActive']/2.0
        type(self)._detenc['OriginZSet'] =  type(self)._detenc['DetEncZ']/2.0 - type(self)._detenc['SpaceSteelSupportToWall'] -                 \
                                            type(self)._detenc['SteelSupport_z'] - type(self)._detenc['FoamPadding'] -                          \
                                            type(self)._cryostat['SteelThickness'] - type(self)._cryostat['zLArBuffer'] -                       \
                                            type(self)._tpc['borderCRM']


        # FieldCage parameters
        type(self)._fieldcage['FieldShaperLongTubeLength']  =  type(self)._tpc['lengthTPCActive']
        type(self)._fieldcage['FieldShaperShortTubeLength'] =  type(self)._tpc['widthTPCActive']
        type(self)._fieldcage['FieldShaperLength'] = type(self)._fieldcage['FieldShaperLongTubeLength'] +                                       \
                                                     2*type(self)._fieldcage['FieldShaperOuterRadius'] +                                        \
                                                     2*type(self)._fieldcage['FieldShaperTorRad']
        type(self)._fieldcage['FieldShaperWidth'] =  type(self)._fieldcage['FieldShaperShortTubeLength'] +                                      \
                                                     2*type(self)._fieldcage['FieldShaperOuterRadius'] +                                        \
                                                     2*type(self)._fieldcage['FieldShaperTorRad']
        type(self)._fieldcage['NFieldShapers']  = (type(self)._tpc['driftTPCActive']/type(self)._fieldcage['FieldShaperSeparation']) - 1
        type(self)._fieldcage['FieldCageSizeX'] = type(self)._fieldcage['FieldShaperSeparation']*type(self)._fieldcage['NFieldShapers'] +       \
                                                  Q('2cm')
        type(self)._fieldcage['FieldCageSizeY'] = type(self)._fieldcage['FieldShaperWidth'] + Q('2cm')
        type(self)._fieldcage['FieldCageSizeZ'] = type(self)._fieldcage['FieldShaperLength'] + Q('2cm')


        # Cathode parameters
        type(self)._cathode['widthCathode'] =2*(type(self)._tpc['widthCRM'] + type(self)._tpc['borderCRP'])
        type(self)._cathode['lengthCathode']=2*(type(self)._tpc['lengthCRM'] + type(self)._tpc['borderCRP'])

        # Arapuca parameters
        type(self)._arapuca['list_posy_bot'] = [0]*4
        type(self)._arapuca['list_posz_bot'] = [0]*4
        type(self)._arapuca['list_posy_bot'][0]= -2.0*type(self)._cathode['widthCathodeVoid'] -                                                 \
                                                 2.0*type(self)._cathode['CathodeBorder'] +                                                     \
                                                 type(self)._arapuca['GapPD'] + 0.5*type(self)._arapuca['ArapucaOut_x']
        type(self)._arapuca['list_posz_bot'][0]= -(0.5*type(self)._cathode['lengthCathodeVoid'] + type(self)._cathode['CathodeBorder'])
        type(self)._arapuca['list_posy_bot'][1]= type(self)._cathode['CathodeBorder'] + type(self)._arapuca['GapPD'] +                          \
                                                 0.5*type(self)._arapuca['ArapucaOut_x']
        type(self)._arapuca['list_posz_bot'][1]=-1.5*type(self)._cathode['lengthCathodeVoid'] - 2.0*type(self)._cathode['CathodeBorder']
        type(self)._arapuca['list_posy_bot'][2]=-type(self)._arapuca['list_posy_bot'][1]
        type(self)._arapuca['list_posz_bot'][2]=-type(self)._arapuca['list_posz_bot'][1]
        type(self)._arapuca['list_posy_bot'][3]=-type(self)._arapuca['list_posy_bot'][0]
        type(self)._arapuca['list_posz_bot'][3]=-type(self)._arapuca['list_posz_bot'][0]

        # add it to global list
        type(self)._params.update(type(self)._tpc)
        type(self)._params.update(type(self)._cryostat)
        type(self)._params.update(type(self)._detenc)
        type(self)._params.update(type(self)._fieldcage)
        type(self)._params.update(type(self)._cathode)
        type(self)._params.update(type(self)._arapuca)
        type(self)._hasDerived = True

    def get(self, key):
        if key not in type(self)._params:
            print("Unable to access requested parameter. Maybe you need to call SetDerived(). Exiting")
            sys.exit(1)
        return type(self)._params[key]
