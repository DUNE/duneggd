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
    _world['simple'] = True

    _tpc['nChans'] = {'Ind1': 286, 'Ind1Bot': 96, 'Ind2': 286, 'Col': 292}
    _tpc['wirePitchU'] = Q('0.765cm')
    _tpc['wirePitchV'] = Q('0.765cm')
    _tpc['wirePitchZ'] = Q('0.51cm')
    _tpc['wireAngleU'] = Q('150.0deg')
    _tpc['wireAngleV'] = Q('30.0deg')
    _tpc['widthPCBActive'] = Q('167.9cm')

    _tpc['borderCRP'] = Q('0.85cm')
    _tpc['gapCRP'] = Q('0.5cm')
    _tpc['borderCRUBottom_z'] = Q('0.8cm')
    _tpc['borderCRUBottom_y'] = Q('0.85cm')
    _tpc['borderCRUBottom1side_z'] = Q('0.5cm')
    _tpc['gapCRP'] = Q('0.5cm')

    _tpc['nCRM_x'] = 2
    _tpc['nSST1_z'] = 6
    _tpc['nSST2_z'] = 2
    _tpc['nSST_y'] = 2

    _tpc['driftTPCActive'] = Q('650.0cm')
    _tpc['padWidth'] = Q('0.02cm')

    _cryostat['Argon_x'] = Q('1510cm')
    _cryostat['Argon_y'] = Q('1510cm')
    _cryostat['Argon_z'] = Q('6200cm')
    _cryostat['HeightGaseousAr'] = Q('100cm')
    _cryostat['SteelThickness'] = Q('0.12cm') # membrane

    # support structure dimensions (simple boxes)
    _detenc['SteelSupport_x'] = Q('100cm')
    _detenc['SteelSupport_y'] = Q('100cm')
    _detenc['SteelSupport_z'] = Q('100cm')
    _detenc['FoamPadding'] = Q('80cm')
    _detenc['FracMassOfSteel'] = 0.5
    _detenc['SpaceSteelSupportToWall']    = Q('100cm')
    _detenc['SpaceSteelSupportToCeiling'] = Q('100cm')
    _detenc['RockThickness'] = Q('40000cm')

    # includes current support structure design (and some modest buffer for shield walls)
    # outer cryostat membrane
    _detenc['ShieldThickness'] = Q('77.48cm')
    _detenc['ColdSkinThickness'] = Q('0.1cm')
    _detenc['WoodThickness'] = Q('2.4cm')
    _detenc['WarmSkinThickness'] = Q('0.1cm')
    # ibeams, belts, shield walls, flooring etc
    _detenc['Spacing'] = Q('64.732/41.0m')
    _detenc['IFlangeWidth'] = Q('40.2cm')
    _detenc['IFlangeThick'] = Q('4cm')
    _detenc['IFlangeWaist'] = Q('2.2cm')
    _detenc['BeamDepth'] = Q('110.8cm')
    _detenc['IFlangeHeight'] = _detenc['BeamDepth'] - 2*_detenc['IFlangeThick']
    _detenc['ITopLength'] = Q('1894cm')
    _detenc['ISideLength'] = Q('1784cm') - 2*_detenc['BeamDepth']
    _detenc['IPortSpacing'] = Q('4m')
    _detenc['ISidePortLoc'] = Q('5.907m')
    _detenc['IBotPortLoc'] = Q('5m')
    _detenc['IPortHoleRad'] = Q('40cm')
    _detenc['ShieldWallThickness'] = Q('23cm')
    _detenc['ShieldWallHeight'] = Q('100cm')
    _detenc['ShieldWallWidth'] = Q('100cm')
    _detenc['BeltBuffer'] = Q('25cm')
    _detenc['FullCryostat_x'] = Q('17.84m') + 2*_detenc['ShieldWallThickness'] + Q('0.2cm')
    _detenc['FullCryostat_y'] = Q('18.94m') + 2*_detenc['ShieldWallThickness'] + Q('0.2cm')
    _detenc['FullCryostat_z'] = Q('65.84m') + _detenc['IFlangeWidth'] + 2*_detenc['BeltBuffer'] + Q('10cm')

    # Cavern dimensions
    _detenc['archRadius'] = Q('12.84m')
    _detenc['archHalfAngle'] = Q('50deg')
    _detenc['Cavern_x'] = Q('23.15m')
    _detenc['Cavern_y'] = Q('19.80m')
    _detenc['Cavern_z'] = 2*(Q('3.3m') + Q('5.55m') + Q('6m') + Q('60.45m'))
    _detenc['ConcreteBeamGap_x'] = Q('0mm')
    _detenc['ConcreteBeamGap_y'] = Q('427mm')
    _detenc['ConcreteBeamGap_z'] = Q('427mm')
    _detenc['RadioRockThickness'] = Q('200cm')
    _detenc['ShotCreteThickness'] = Q('6in')
    _detenc['ConcreteThickness'] = Q('11in')
    _detenc['GroutThickness'] = Q('1in')

    # field cage and downstream
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
        cls = type(self)
        # calculate all the other parameters
        # accessible only once construction begins
        if cls._hasDerived:
            return

        # TPC parameters
        cls._tpc['nViews'] = len(cls._tpc['nChans'])
        cls._tpc['lengthPCBActive'] = cls._tpc['wirePitchZ'] * cls._tpc['nChans']['Col']
        cls._tpc['widthCRM_active'] = cls._tpc['widthPCBActive']
        cls._tpc['lengthCRM_active'] = cls._tpc['lengthPCBActive']
        cls._tpc['widthCRM'] = cls._tpc['widthPCBActive']
        cls._tpc['lengthCRM'] = cls._tpc['lengthPCBActive']

        cls._tpc['gapSST1_z'] = Q('3cm') - cls._tpc['gapCRP']
        cls._tpc['gapSST2_z'] = Q('2.4cm') - cls._tpc['gapCRP']
        cls._tpc['gapSST_y'] = Q('2.4cm') - cls._tpc['gapCRP']
        cls._tpc['gapSST_ybottom'] = Q('2.4cm') - cls._tpc['gapCRP']

        # create a smaller geometry :  with SST2 and SST1 it is 1x8x14
        if cls._world['workspace'] == 1:
            cls._tpc['nCRM_x'] = 1
            cls._tpc['nSST_y'] = 2
            cls._tpc['nSST1_z'] = 2
            cls._tpc['nSST2_z'] = 1
        # create full geometry with only one drift volume 1x8x40
        if cls._world['workspace'] == 2:
            cls._tpc['nCRM_x'] = 1
            cls._tpc['nSST_y'] = 2
            cls._tpc['nSST1_z'] = 6
            cls._tpc['nSST2_z'] = 2
        #test with a final SST2 and bottom
        if cls._world['workspace'] == 3:
            cls._tpc['nCRM_x'] = 2
            cls._tpc['nSST_y'] = 2
            cls._tpc['nSST1_z'] = 2
            cls._tpc['nSST2_z'] = 2
        # create full geometry with top and bottom drift volume 2x8x40
        if cls._world['workspace'] == 4:
            cls._tpc['nCRM_x'] = 2
            cls._tpc['nSST_y'] = 2
            cls._tpc['nSST1_z'] = 6
            cls._tpc['nSST2_z'] = 2

        cls._tpc['nCRM_z'] = cls._tpc['nSST1_z'] * 3 * 2 + \
                                    cls._tpc['nSST2_z'] * 2
        cls._tpc['nCRM_y'] = cls._tpc['nSST_y'] * 2 * 2


        cls._tpc['widthTPCActive'] = cls._tpc['nCRM_y'] * (cls._tpc['widthCRM'] + cls._tpc['borderCRP']) + (cls._tpc['nSST_y'] - 1) * cls._tpc['gapSST_y']
        cls._tpc['lengthTPCActive'] = cls._tpc['nCRM_z'] * (cls._tpc['lengthCRM'] + cls._tpc['borderCRP']) + (cls._tpc['nSST1_z'] - 1) * cls._tpc['gapSST1_z'] + cls._tpc['nSST2_z'] * cls._tpc['gapSST2_z']
        cls._tpc['lengthTPCActivebottom'] = cls._tpc['nCRM_z'] * (cls._tpc['lengthCRM'] + cls._tpc['borderCRUBottom_z']) + cls._tpc['gapSST1_z']


        cls._tpc['ReadoutPlane'] = cls._tpc['nViews'] * cls._tpc['padWidth']
        cls._tpc['anodePlateWidth'] = cls._tpc['padWidth']/2.
        cls._tpc['lengthAnodeBottom'] = cls._tpc['lengthCRM']
        cls._tpc['TPCActive_x'] = cls._tpc['driftTPCActive']
        cls._tpc['TPCActive_y'] = cls._tpc['widthCRM_active']
        cls._tpc['TPCActive_z'] = cls._tpc['lengthCRM_active']
        cls._tpc['TPC_x'] = cls._tpc['TPCActive_x'] + cls._tpc['ReadoutPlane']
        cls._tpc['TPC_y'] = cls._tpc['widthCRM']
        cls._tpc['TPC_z'] = cls._tpc['lengthCRM']

        if not cls._world['simple'] and (cls._world['workspace'] == 0 or cls._world['workspace'] == 4):
            # actual dimensions
            cls._cryostat['Argon_x'] = Q('1400cm')
            cls._cryostat['HeightGaseousAr'] = Q('5cm')

        # Cryostat parameters
        if cls._world['workspace'] != 0:
            if cls._tpc['nCRM_x']== 1:
                cls._cryostat['Argon_x'] = cls._tpc['driftTPCActive'] + cls._cryostat['HeightGaseousAr'] +                 \
                                                  cls._tpc['ReadoutPlane'] + Q('100cm')
            cls._cryostat['Argon_y'] = cls._tpc['widthTPCActive'] + Q('162cm')
            cls._cryostat['Argon_z'] = cls._tpc['lengthTPCActive'] + Q('214.0cm')

        if cls._tpc['nCRM_x'] == 1:
            cls._cryostat['xLArBuffer'] = cls._cryostat['Argon_x'] - cls._tpc['driftTPCActive'] -                          \
                                                 cls._cryostat['HeightGaseousAr'] - cls._tpc['ReadoutPlane'] -                    \
                                                 cls._cathode['heightCathode']
        else:
            cls._cryostat['xLArBuffer'] = cls._cryostat['Argon_x'] - 2*cls._tpc['driftTPCActive'] -                        \
                                                 cls._cryostat['HeightGaseousAr'] - 2*cls._tpc['ReadoutPlane'] -                  \
                                                 cls._cathode['heightCathode']
        cls._cryostat['yLArBuffer'] = 0.5 * (cls._cryostat['Argon_y'] - cls._tpc['widthTPCActive'])
        cls._cryostat['zLArBuffer'] = 0.5 * (cls._cryostat['Argon_z'] - cls._tpc['lengthTPCActive'])
        cls._cryostat['Cryostat_x'] = cls._cryostat['Argon_x'] + 2*cls._cryostat['SteelThickness']
        cls._cryostat['Cryostat_y'] = cls._cryostat['Argon_y'] + 2*cls._cryostat['SteelThickness']
        cls._cryostat['Cryostat_z'] = cls._cryostat['Argon_z'] + 2*cls._cryostat['SteelThickness']
        cls._cryostat['TPCEnclosure_x'] = cls._cryostat['Argon_x'] -                                                              \
                                                 cls._cryostat['HeightGaseousAr'] +                                                      \
                                                 cls._tpc['nCRM_x']*cls._tpc['anodePlateWidth'] -                                 \
                                                 cls._cryostat['xLArBuffer']

        cls._cryostat['TPCEnclosure_y'] = cls._tpc['nCRM_y']*(cls._tpc['widthCRM'] + cls._tpc['borderCRP']) + (cls._tpc['nSST_y'] - 1) * cls._tpc['gapSST_y']
        cls._cryostat['TPCEnclosure_ybottom'] = cls._tpc['nCRM_y']*(cls._tpc['widthCRM'] + cls._tpc['borderCRUBottom_y']) + cls._tpc['gapSST_ybottom']
        cls._cryostat['TPCEnclosure_z'] = cls._tpc['nCRM_z']*(cls._tpc['lengthCRM'] + cls._tpc['borderCRP']) + (cls._tpc['nSST1_z'] - 1) * cls._tpc['gapSST1_z'] + cls._tpc['nSST2_z'] * cls._tpc['gapSST2_z']



        # Enclosure parameters
        cls._detenc['FracMassOfAir'] = 1 - cls._detenc['FracMassOfSteel']
        cls._detenc['DetEncX']  =    cls._cryostat['Cryostat_x'] +                                                                \
                                            2*(cls._detenc['SteelSupport_x'] +                                                           \
                                            cls._detenc['FoamPadding']) +                                                                \
                                            cls._detenc['SpaceSteelSupportToCeiling']
        cls._detenc['DetEncY']  =    cls._cryostat['Cryostat_y'] +                                                                \
                                            2*(cls._detenc['SteelSupport_y'] +                                                           \
                                            cls._detenc['FoamPadding']) +                                                                \
                                            2*cls._detenc['SpaceSteelSupportToWall']
        cls._detenc['DetEncZ']  =    cls._cryostat['Cryostat_z'] +                                                                \
                                            2*(cls._detenc['SteelSupport_z'] +                                                           \
                                            cls._detenc['FoamPadding']) +                                                                \
                                            2*cls._detenc['SpaceSteelSupportToWall']

        cls._detenc['posCryoInDetEnc_x'] = - cls._detenc['DetEncX']/2 +                                                           \
                                                    cls._detenc['SteelSupport_x'] +                                                      \
                                                    cls._detenc['FoamPadding'] +                                                         \
                                                    cls._cryostat['Cryostat_x']/2
        cls._detenc['posCryoInDetEnc_y'] = Q('0m')
        cls._detenc['posCryoInDetEnc_z'] = Q('0m')

        cls._detenc['OriginXSet'] =  cls._detenc['DetEncX']/2.0 - cls._detenc['SteelSupport_x'] -                          \
                                            cls._detenc['FoamPadding'] - cls._cryostat['SteelThickness'] -                        \
                                            cls._cryostat['xLArBuffer'] - cls._tpc['driftTPCActive']/2.0 -                        \
                                            cls._cathode['heightCathode']
        if cls._tpc['nCRM_x'] == 2:
            cls._detenc['OriginXSet'] =  cls._detenc['DetEncX']/2.0 - cls._detenc['SteelSupport_x'] -                      \
                                                cls._detenc['FoamPadding'] - cls._cryostat['SteelThickness'] -                    \
                                                cls._cryostat['xLArBuffer'] - cls._tpc['driftTPCActive']/2.0 -                    \
                                                cls._cathode['heightCathode']/2.

        cls._detenc['OriginYSet'] =  cls._detenc['DetEncY']/2.0 - cls._detenc['SpaceSteelSupportToWall'] -                 \
                                            cls._detenc['SteelSupport_y'] - cls._detenc['FoamPadding'] -                          \
                                            cls._cryostat['SteelThickness'] - cls._cryostat['yLArBuffer'] -                       \
                                            cls._tpc['widthTPCActive']/2.0
        cls._detenc['OriginZSet'] =  cls._detenc['DetEncZ']/2.0 - cls._detenc['SpaceSteelSupportToWall'] -                 \
                                            cls._detenc['SteelSupport_z'] - cls._detenc['FoamPadding'] -                          \
                                            cls._cryostat['SteelThickness'] - cls._cryostat['zLArBuffer']

        if not cls._world['simple'] and (cls._world['workspace'] == 0 or cls._world['workspace'] == 4):
            cls._detenc['DetEncX'] = cls._detenc['Cavern_x']
            cls._detenc['DetEncY'] = cls._detenc['Cavern_y']
            cls._detenc['DetEncZ'] = cls._detenc['Cavern_z']

            cls._detenc['posCryoInDetEnc_x'] = -0.5*cls._detenc['DetEncX'] +              \
                                                      cls._detenc['ConcreteBeamGap_x'] +         \
                                                      cls._detenc['ConcreteThickness'] +         \
                                                      cls._detenc['GroutThickness'] +            \
                                                      0.5*cls._detenc['FullCryostat_x'] +    \
                                                      0.5*cls._detenc['RadioRockThickness']
            cls._detenc['posCryoInDetEnc_y'] = Q('0m')
            cls._detenc['posCryoInDetEnc_z'] = -0.5*cls._detenc['DetEncZ'] +              \
                                                      cls._detenc['ConcreteBeamGap_z'] +         \
                                                      0.5*cls._detenc['FullCryostat_z']

            cls._detenc['OriginXSet'] =  cls._detenc['DetEncX']/2.0  -                    \
                                                cls._detenc['ConcreteBeamGap_x'] -               \
                                                cls._detenc['ConcreteThickness'] -               \
                                                cls._detenc['GroutThickness'] -                  \
                                                0.5*cls._detenc['RadioRockThickness'] -          \
                                                cls._cryostat['SteelThickness'] -                \
                                                cls._cryostat['xLArBuffer'] -                    \
                                                cls._tpc['driftTPCActive']/2.0 -                 \
                                                cls._cathode['heightCathode']/2.
            cls._detenc['OriginYSet'] =  cls._detenc['DetEncY']/2.0 -                     \
                                                cls._cryostat['SteelThickness'] -                \
                                                cls._cryostat['yLArBuffer'] -                    \
                                                cls._tpc['widthTPCActive']/2.0
            cls._detenc['OriginZSet'] =  cls._detenc['DetEncZ']/2.0 -                     \
                                                cls._cryostat['SteelThickness'] -                \
                                                cls._detenc['ConcreteBeamGap_z'] -               \
                                                cls._cryostat['zLArBuffer']


        # FieldCage parameters
        cls._fieldcage['FieldShaperLongTubeLength']  =  cls._tpc['lengthTPCActive']
        cls._fieldcage['FieldShaperShortTubeLength'] =  cls._tpc['widthTPCActive']
        cls._fieldcage['FieldShaperLength'] = cls._fieldcage['FieldShaperLongTubeLength'] +                                       \
                                                     2*cls._fieldcage['FieldShaperOuterRadius'] +                                        \
                                                     2*cls._fieldcage['FieldShaperTorRad']
        cls._fieldcage['FieldShaperWidth'] =  cls._fieldcage['FieldShaperShortTubeLength'] +                                      \
                                                     2*cls._fieldcage['FieldShaperOuterRadius'] +                                        \
                                                     2*cls._fieldcage['FieldShaperTorRad']
        cls._fieldcage['NFieldShapers']  = (cls._tpc['driftTPCActive']/cls._fieldcage['FieldShaperSeparation']) - 1
        cls._fieldcage['FieldCageSizeX'] = cls._fieldcage['FieldShaperSeparation']*cls._fieldcage['NFieldShapers'] +       \
                                                  Q('2cm')
        cls._fieldcage['FieldCageSizeY'] = cls._fieldcage['FieldShaperWidth'] + Q('2cm')
        cls._fieldcage['FieldCageSizeZ'] = cls._fieldcage['FieldShaperLength'] + Q('2cm')


        # Cathode parameters
        cls._cathode['widthCathode'] =2*(cls._tpc['widthCRM'] + cls._tpc['borderCRP'])
        cls._cathode['widthCathodeBottom'] =2*(cls._tpc['widthCRM'] + cls._tpc['borderCRUBottom_y'])
        cls._cathode['lengthCathode']=2*(cls._tpc['lengthCRM'] + cls._tpc['borderCRP'])
        cls._cathode['lengthCathodeBottom'] =2*(cls._tpc['lengthCRM'] + cls._tpc['borderCRUBottom_z'])

        # Arapuca parameters
        cls._arapuca['list_posy_bot'] = [0]*4
        cls._arapuca['list_posz_bot'] = [0]*4
        cls._arapuca['list_posy_bot'][0]= -2.0*cls._cathode['widthCathodeVoid'] -                                                 \
                                                 2.0*cls._cathode['CathodeBorder'] +                                                     \
                                                 cls._arapuca['GapPD'] + 0.5*cls._arapuca['ArapucaOut_x']
        cls._arapuca['list_posz_bot'][0]= -(0.5*cls._cathode['lengthCathodeVoid'] + cls._cathode['CathodeBorder'])
        cls._arapuca['list_posy_bot'][1]= cls._cathode['CathodeBorder'] + cls._arapuca['GapPD'] +                          \
                                                 0.5*cls._arapuca['ArapucaOut_x']
        cls._arapuca['list_posz_bot'][1]=-1.5*cls._cathode['lengthCathodeVoid'] - 2.0*cls._cathode['CathodeBorder']
        cls._arapuca['list_posy_bot'][2]=-cls._arapuca['list_posy_bot'][1]
        cls._arapuca['list_posz_bot'][2]=-cls._arapuca['list_posz_bot'][1]
        cls._arapuca['list_posy_bot'][3]=-cls._arapuca['list_posy_bot'][0]
        cls._arapuca['list_posz_bot'][3]=-cls._arapuca['list_posz_bot'][0]

        # add it to global list
        cls._params.update(cls._tpc)
        cls._params.update(cls._cryostat)
        cls._params.update(cls._detenc)
        cls._params.update(cls._fieldcage)
        cls._params.update(cls._cathode)
        cls._params.update(cls._arapuca)
        cls._hasDerived = True

    def get(self, key):
        if key not in type(self)._params:
            print("Unable to access requested parameter : %s, maybe you need to call SetDerived(). Exiting" % key)
            sys.exit(1)
        return type(self)._params[key]
