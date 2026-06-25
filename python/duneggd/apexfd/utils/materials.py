# ---------------------------------------------------------------------------
# Optical property data + unit helpers.
# Geant4 11+ reads GDML <matrix> values as bare numbers in internal units:
#   energy = MeV, length = mm, time = ns.  NO automatic eV->MeV conversion.
# ---------------------------------------------------------------------------
def _eV(x): return x * 1.0e-6   # eV -> MeV
def _cm(x): return x * 10.0     # cm -> mm
def _m(x):  return x * 1000.0   # m  -> mm
def _um(x): return x * 1.0e-3   # um -> mm

# ===================== LAr (liquid argon) =====================
_LAR_RINDEX_E_eV = [
 1.88901692613609,1.915491549763,1.94434453495496,1.9740800365654,2.00473917327901,
 2.03636565851099,2.0690060083582,2.1027097698752,2.1375297720313,2.17352240202191,
 2.21074790997382,2.24927074550798,2.28915993011439,2.33048946986518,2.37333881365753,
 2.41779336295621,2.46394503991691,2.51189292184303,2.56174395119099,2.61361373183203,
 2.66762742404865,2.72392075285046,2.78264114670945,2.84394902682875,2.90801927068415,
 2.97504287795441,3.04522887226339,3.11880647861692,3.19602762431763,3.27716982084588,
 3.36253949617556,3.45247586185779,3.54735541774646,3.64759722049586,3.75366907130329,
 3.86609481562225,3.98546299517591,4.11243715385428,4.24776817847434,4.39230915909235,
 4.54703339014745,4.71305631519082,4.89166246132417,5.08433873911506,5.29281593505014,
 5.51912084854449,5.76564240171605,6.03521629502331,6.33123457629323,6.65778911807759,
 7.01986191167459,7.42358102512033,7.80768693883725,8.18166617653237,8.49578904787588,
 8.75179837892604,8.97145190403002,9.21112941189563,9.40734062594689,9.56190983757659,
 9.71915769371575,9.88023992289941,9.99798584772925,10.0930619775564,10.1644798618311,
 10.2587258039568,10.3321720936895,10.3923239488175,10.4560982471211,10.4827908882082,
 10.5288181909777,10.5783779318939]
_LAR_RINDEX_N = [
 1.2310665394518083,1.2311200318147684,1.2312727482978456,1.2313496348295065,1.2313506914097514,
 1.2314023012909403,1.2321538166889967,1.231909947460871,1.2321384938953646,1.2323923169803301,
 1.232443926861519,1.2328668458034384,1.233095392237932,1.233053736213583,1.233509772502325,
 1.2335361057330418,1.2334866090123424,1.2338668153496684,1.2343481282888824,1.2344502914710154,
 1.2346282846045646,1.2350337675923626,1.2354898038811046,1.2358874461725522,1.2361238333033957,
 1.2364787629902494,1.2371038951359457,1.2374666655191495,1.237720488604115,1.2384292913975776,
 1.2388853276863196,1.2393413639750617,1.2402271033218288,1.2409106294648191,1.2417458155106422,
 1.2425810015564651,1.2435678475051206,1.2446558000556642,1.245844859208096,1.2472614082147766,
 1.2488296171242892,1.2505242092861624,1.2525221212537003,1.2548739063278473,1.257579564508603,
 1.2607654790483278,1.2644822032479663,1.269108886864599,1.2747719131505861,1.2816987719601767,
 1.2910690403154002,1.302368759656658,1.316713517166515,1.3329411664124329,1.3493804523854165,
 1.365926455672306,1.3820018039345536,1.4010549636291998,1.423580491960391,1.442600693158671,
 1.46103487273757,1.4894895758980782,1.508978836972031,1.5300372520419365,1.5496431051408859,
 1.5737334642006038,1.5996151986767673,1.6187496758472137,1.6361783106957755,1.6540241603412935,
 1.672490509546729,1.69156768392026]
_LAR_RINDEX = [(_eV(e), n) for e, n in zip(_LAR_RINDEX_E_eV, _LAR_RINDEX_N)]

_LAR_RAYLEIGH = [(_eV(e), _cm(l)) for e, l in zip(
 [2.80,3.00,3.50,4.00,5.00,6.00,7.00,8.00,8.50,9.00,9.20,9.40,9.50,9.60,9.70,9.80,9.90,10.0,10.2,10.4,10.6,10.8],
 [47923.,35981.,18825.,10653.,3972.,1681.,750.9,334.7,216.8,135.0,109.7,88.06,78.32,69.34,61.06,53.46,46.50,40.13,28.91,19.81,12.61,7.20])]

_LAR_ABSLENGTH = [(_eV(e), _m(l)) for e, l in zip(
 [2.5,5.0,7.0,7.5,8.0,9.0,9.5,10.136],
 [80,80,80,80,20,20,20,20])]

_LAR_SCINT_E_eV = [6.0,6.7,7.1,7.4,7.7,7.9,8.1,8.4,8.5,8.6,8.8,9.0,9.1,9.4,9.8,10.4,10.7]
_LAR_SCINT_SPEC = [0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
_LAR_SCINT1 = [(_eV(e), v) for e, v in zip(_LAR_SCINT_E_eV, _LAR_SCINT_SPEC)]
_LAR_SCINT2 = list(_LAR_SCINT1)

# ===================== pTP (p-Terphenyl WLS) =====================
_PTP_RINDEX = [(_eV(e), 1.35) for e in [1,3.0,3.8,6.20,8.27,12.40,24.80,123.99,200]]

_PTP_WLSABS_E_eV = [2.0,3.0,4.0,4.5,5.0,5.5,6.0,6.5,7.0,7.5,8.0,8.27,12.40,24.80,123.99]
_PTP_WLSABS_mm   = [_m(0.3)]*6 + [_um(0.3)]*9
_PTP_WLSABSLENGTH = [(_eV(e), l) for e, l in zip(_PTP_WLSABS_E_eV, _PTP_WLSABS_mm)]

_PTP_WLSCOMP = [(_eV(e), v) for e, v in zip(
 [3.06434,3.1098,3.14086,3.18325,3.24903,3.31176,3.33517,3.37092,3.4198,3.45108,
  3.47012,3.48937,3.51537,3.53513,3.55512,3.59577,3.62339,3.63736,3.65144,3.66562,3.67992,3.7235],
 [0.016285,0.0520565,0.0788851,0.132542,0.275628,0.409771,0.543914,0.678057,0.722772,0.821143,
  0.955286,1.0,0.946343,0.8122,0.740657,0.8122,0.678057,0.534971,0.400828,0.266685,0.132542,0.00734215])]

# Optical-surface energy grid (eV -> MeV) : 2.5,5,7,7.5,8,9,9.5,10.136 eV
_SURF_E = [2.5, 5.0, 7.0, 7.5, 8.0, 9.0, 9.5, 10.136]

def _surf(vals):
    return [(_eV(e), v) for e, v in zip(_SURF_E, vals)]

_ZERO_EFF      = _surf([0.0]*8)
_ANODE_REFL    = _surf([0.20,0.20,0.20,0.20, 0.0,0.0,0.0,0.0])
_FC_REFL       = _surf([0.7]*8)
_ARABACK_REFL  = _surf([1.0]*8)
_CRYO_REFL     = _surf([0.4,0.4,0.4,0.4, 0.3,0.3,0.3,0.3])

##################### Now start building materials #####################
def construct_materials(geom):
    e_vacuum = geom.matter.Element("videRef", "VACUUM", 1, "1g/mole")
    e_pb = geom.matter.Element("lead", "Pb", 82, "207.2g/mole")
    e_cu = geom.matter.Element("copper", "Cu", 29, "63.546g/mole")
    e_be = geom.matter.Element("beryllium", "Be", 4, "9.0121831g/mole")
    e_br = geom.matter.Element("bromine", "Br", 35, "79.904g/mole")
    e_h = geom.matter.Element("hydrogen", "H", 1, "1.0079g/mole")
    e_n = geom.matter.Element("nitrogen", "N", 7, "14.0067g/mole")
    e_o = geom.matter.Element("oxygen", "O", 8, "15.999g/mole")
    e_al = geom.matter.Element("aluminum", "Al", 13, "26.9815g/mole")
    e_si = geom.matter.Element("silicon", "Si", 14, "28.0855g/mole")
    e_c = geom.matter.Element("carbon", "C", 6, "12.0107g/mole")
    e_k = geom.matter.Element("potassium", "K", 19, "39.0983g/mole")
    e_cr = geom.matter.Element("chromium", "Cr", 24, "51.9961g/mole")
    e_fe = geom.matter.Element("iron", "Fe", 26, "55.8450g/mole")
    e_ni = geom.matter.Element("nickel", "Ni", 28, "58.6934g/mole")
    e_ca = geom.matter.Element("calcium", "Ca", 20, "40.078g/mole")
    e_mg = geom.matter.Element("magnesium", "Mg", 12, "24.305g/mole")
    e_na = geom.matter.Element("sodium", "Na", 11, "22.99g/mole")
    e_ti = geom.matter.Element("titanium", "Ti", 22, "47.867g/mole")
    e_ar = geom.matter.Element("argon", "Ar", 18, "39.9480g/mole")
    e_s = geom.matter.Element("sulphur", "S", 16, "32.065g/mole")
    e_p = geom.matter.Element("phosphorus", "P", 15, "30.973g/mole")
    e_mn = geom.matter.Element("manganese", "Mn", 25, "54.94g/mole")
    e_b11 = geom.matter.Element("boron11", "B11", 4, "11.00g/mole")
    e_b10 = geom.matter.Element("boron10", "B10", 4, "10.00g/mole")
    m_vacuum = geom.matter.Mixture("Vacuum", density = "1.e-25g/cc",
                                                components = (("videRef", 1.0),))
    m_aluminum_al = geom.matter.Mixture("ALUMINIUM_Al", density = "2.6990g/cc",
                                                components = (("aluminum", 1.0000),))
    skin_aluminum_al = geom.surfaces.OpticalSurface("AlSurface", 
                                                    model="unified", finish="ground",
                                                    type="dielectric_metal", value=0.0,
                                                    properties=(("REFLECTIVITY", _FC_REFL),
                                                                ("EFFICIENCY",   _ZERO_EFF)))
    m_silicon_si = geom.matter.Mixture("SILICON_Si", density = "2.3300g/cc",
                                                components = (("silicon", 1.0000),))
    m_epoxy_resin = geom.matter.Molecule("epoxy_resin", density = "1.1250g/cc",
                                                elements = (("carbon", 38),
                                                                        ("hydrogen", 40),
                                                                        ("oxygen", 6),
                                                                        ("bromine", 4)))
    m_sio2 = geom.matter.Molecule("SiO2", density = "2.2g/cc",
                                                elements = (("silicon", 1),
                                                                        ("oxygen", 2)))
    m_al2o3 = geom.matter.Molecule("Al2O3", density = "3.97g/cc",
                                                elements = (("aluminum", 2),
                                                                        ("oxygen", 3)))
    m_fe2o3 = geom.matter.Molecule("Fe2O3", density = "5.24g/cc",
                                                elements = (("iron", 2),
                                                                        ("oxygen", 3)))
    m_cao = geom.matter.Molecule("CaO", density = "3.35g/cc",
                                                elements = (("calcium", 1),
                                                                        ("oxygen", 1)))
    m_delrin = geom.matter.Molecule("Delrin", density = "1.41g/cc",
                                                elements = (("carbon", 1),
                                                                        ("hydrogen", 2),
                                                                        ("oxygen", 1)))
    m_mgo = geom.matter.Molecule("MgO", density = "3.58g/cc",
                                                elements = (("magnesium", 1),
                                                                        ("oxygen", 1)))
    m_na2o = geom.matter.Molecule("Na2O", density = "2.27g/cc",
                                                elements = (("sodium", 2),
                                                                        ("oxygen", 1)))
    m_tio2 = geom.matter.Molecule("TiO2", density = "4.23g/cc",
                                                elements = (("titanium", 1),
                                                                        ("oxygen", 2)))
    m_feo = geom.matter.Molecule("FeO", density = "5.745g/cc",
                                                elements = (("iron", 1),
                                                                        ("oxygen", 1)))
    m_co2 = geom.matter.Molecule("CO2", density = "1.562g/cc",
                                                elements = (("iron", 1),
                                                                        ("oxygen", 2)))
    m_p2o5 = geom.matter.Molecule("P2O5", density = "1.562g/cc",
                                                elements = (("phosphorus", 2),
                                                                        ("oxygen", 5)))
    m_dusel_rock = geom.matter.Mixture("DUSEL_Rock", density = "2.82g/cc",
                                                components = (("SiO2", 0.5267),
                                                                          ("FeO", 0.1174),
                                                                          ("Al2O3", 0.1025),
                                                                          ("MgO", 0.0473),
                                                                          ("CO2", 0.0422),
                                                                          ("CaO", 0.0382),
                                                                          ("carbon", 0.0240),
                                                                          ("sulphur", 0.0186),
                                                                          ("Na2O", 0.0053),
                                                                          ("P2O5", 0.00070),
                                                                          ("oxygen", 0.0771)))
    m_air = geom.matter.Mixture("Air", density = "0.001205g/cc",
                                                components = (("nitrogen", 0.781154),
                                                                          ("oxygen", 0.209476),
                                                                          ("argon", 0.00934)))
    m_fibrous_glass = geom.matter.Mixture("fibrous_glass", density = "2.74351g/cc",
                                                components = (("SiO2", 0.600),
                                                                          ("Al2O3", 0.118),
                                                                          ("Fe2O3", 0.001),
                                                                          ("CaO", 0.224),
                                                                          ("MgO", 0.034),
                                                                          ("Na2O", 0.010),
                                                                          ("TiO2", 0.013)))
    m_fd_foam = geom.matter.Mixture("FD_foam", density = "0.09g/cc",
                                                components = (("Air", 0.95),
                                                                          ("fibrous_glass", 0.05)))
    m_foam_protodune_rpuf_assayedsample = geom.matter.Molecule("foam_protoDUNE_RPUF_assayedSample", density = "0.09g/cc",
                                                elements = (("carbon", 54),
                                                                        ("hydrogen", 60),
                                                                        ("nitrogen", 4),
                                                                        ("oxygen", 15)))
    m_foam_3x1x1dp = geom.matter.Mixture("foam_3x1x1dp", density = "0.07g/cc",
                                                components = (("Air", 0.95),
                                                                          ("fibrous_glass", 0.05)))
    m_foam_protodunedp = geom.matter.Molecule("foam_protoDUNEdp", density = "0.135g/cc",
                                                elements = (("carbon", 17),
                                                                        ("hydrogen", 16),
                                                                        ("nitrogen", 2),
                                                                        ("oxygen", 4)))
    m_fr4 = geom.matter.Mixture("FR4", density = "1.98281g/cc",
                                                components = (("epoxy_resin", 0.47),
                                                                          ("fibrous_glass", 0.53)))
    m_fr4sussexapa = geom.matter.Mixture("FR4SussexAPA", density = "1.75g/cc",
                                                components = (("FR4", 1),))
    m_steel_stainless_fe7cr2ni = geom.matter.Mixture("STEEL_STAINLESS_Fe7Cr2Ni", density = "7.9300g/cc",
                                                components = (("carbon", 0.0010),
                                                                          ("chromium", 0.1792),
                                                                          ("iron", 0.7298),
                                                                          ("nickel", 0.0900)))
    m_copper_beryllium_alloy25 = geom.matter.Mixture("Copper_Beryllium_alloy25", density = "8.26g/cc",
                                                components = (("copper", 0.981),
                                                                          ("beryllium", 0.019)))
    m_lar = geom.matter.Mixture("LAr", density = "1.40g/cc",
                                                components = (("argon", 1.0000),),
                                                properties = (("RINDEX", _LAR_RINDEX),
                                                              ("RAYLEIGH", _LAR_RAYLEIGH),
                                                              ("ABSLENGTH", _LAR_ABSLENGTH),
                                                              ("SCINTILLATIONCOMPONENT1", _LAR_SCINT1),
                                                              ("SCINTILLATIONCOMPONENT2", _LAR_SCINT2),
                                                              ("SCINTILLATIONTIMECONSTANT1", [(6.0,)]),
                                                              ("SCINTILLATIONTIMECONSTANT2", [(1590.0,)]),
                                                              ("SCINTILLATIONYIELD", [(25000.0,)]),
                                                              ("SCINTILLATIONYIELD1", [(0.3,)]),
                                                              ("RESOLUTIONSCALE", [(1.0,)])))
    m_argas = geom.matter.Mixture("ArGas", density = "0.00166g/cc",
                                                components = (("argon", 1.0),))
    m_g10 = geom.matter.Mixture("G10", density = "1.7g/cc",
                                                components = (("silicon", 0.2805),
                                                                          ("oxygen", 0.3954),
                                                                          ("carbon", 0.2990),
                                                                          ("hydrogen", 0.0251)))
    m_granite = geom.matter.Mixture("Granite", density = "2.7g/cc",
                                                components = (("oxygen", 0.438),
                                                                          ("silicon", 0.257),
                                                                          ("sodium", 0.222),
                                                                          ("aluminum", 0.049),
                                                                          ("iron", 0.019),
                                                                          ("potassium", 0.015)))
    m_shotrock = geom.matter.Mixture("ShotRock", density = "1.62g/cc",
                                                components = (("oxygen", 0.438),
                                                                          ("silicon", 0.257),
                                                                          ("sodium", 0.222),
                                                                          ("aluminum", 0.049),
                                                                          ("iron", 0.019),
                                                                          ("potassium", 0.015)))
    m_dirt = geom.matter.Mixture("Dirt", density = "1.7g/cc",
                                                components = (("oxygen", 0.438),
                                                                          ("silicon", 0.257),
                                                                          ("sodium", 0.222),
                                                                          ("aluminum", 0.049),
                                                                          ("iron", 0.019),
                                                                          ("potassium", 0.015)))
    m_concrete = geom.matter.Mixture("Concrete", density = "2.3g/cc",
                                                components = (("oxygen", 0.530),
                                                                          ("silicon", 0.335),
                                                                          ("calcium", 0.060),
                                                                          ("sodium", 0.015),
                                                                          ("iron", 0.020),
                                                                          ("aluminum", 0.040)))
    m_water = geom.matter.Mixture("Water", density = "1.0g/cc",
                                                components = (("hydrogen", 0.1119),
                                                                          ("oxygen", 0.8881)))
    m_titanium = geom.matter.Mixture("Titanium", density = "4.506g/cc",
                                                components = (("titanium", 1.),))
    m_tpb = geom.matter.Mixture("TPB", density = "1.40g/cc",
                                                components = (("argon", 1.0000),))
    m_glass = geom.matter.Mixture("Glass", density = "2.74351g/cc",
                                                components = (("SiO2", 0.600),
                                                                          ("Al2O3", 0.118),
                                                                          ("Fe2O3", 0.001),
                                                                          ("CaO", 0.224),
                                                                          ("MgO", 0.034),
                                                                          ("Na2O", 0.010),
                                                                          ("TiO2", 0.013)))
    m_acrylic = geom.matter.Mixture("Acrylic", density = "1.19g/cc",
                                                components = (("carbon", 0.600),
                                                                          ("oxygen", 0.320),
                                                                          ("hydrogen", 0.080)))
    m_mylar = geom.matter.Molecule("Mylar", density = "1.40g/cc",
                        elements = (("hydrogen", 4),
                                    ("carbon", 5),
                                    ("oxygen", 2)))
    skin_mylar = geom.surfaces.OpticalSurface("MylarSurface",
                                            model="unified", finish="ground",
                                            type="dielectric_metal", value=0.0,
                                            properties=(("REFLECTIVITY", _ARABACK_REFL),
                                                        ("EFFICIENCY", _ZERO_EFF)))
    m_ptp = geom.matter.Molecule("pTP", density = "1.079g/cc",
                        elements = (("carbon", 18),
                                    ("hydrogen", 14)),
                        properties = (("RINDEX", _PTP_RINDEX),
                                      ("WLSABSLENGTH", _PTP_WLSABSLENGTH),
                                      ("WLSCOMPONENT", _PTP_WLSCOMP),
                                      ("WLSTIMECONSTANT", [(5.0,)])))
    m_nigas1atm80k = geom.matter.Mixture("NiGas1atm80K", density = "0.0039g/cc",
                                                components = (("nitrogen", 1.000),))
    m_nigas = geom.matter.Mixture("NiGas", density = "0.001165g/cc",
                                                components = (("nitrogen", 1.000),))
    m_polyurethanefoam = geom.matter.Molecule("PolyurethaneFoam", density = "0.088g/cc",
                                                elements = (("carbon", 17),
                                                                        ("hydrogen", 16),
                                                                        ("nitrogen", 2),
                                                                        ("oxygen", 4)))
    m_protodunefoam = geom.matter.Molecule("ProtoDUNEFoam", density = "0.135g/cc",
                                                elements = (("carbon", 17),
                                                                        ("hydrogen", 16),
                                                                        ("nitrogen", 2),
                                                                        ("oxygen", 4)))
    m_lightpolyurethanefoam = geom.matter.Molecule("LightPolyurethaneFoam", density = "0.009g/cc",
                                                elements = (("carbon", 17),
                                                                        ("hydrogen", 16),
                                                                        ("nitrogen", 2),
                                                                        ("oxygen", 4)))
    m_protodunebwfoam = geom.matter.Molecule("ProtoDUNEBWFoam", density = "0.021g/cc",
                                                elements = (("carbon", 17),
                                                                        ("hydrogen", 16),
                                                                        ("nitrogen", 2),
                                                                        ("oxygen", 4)))
    m_glasswool = geom.matter.Mixture("GlassWool", density = "0.035g/cc",
                                                components = (("SiO2", 0.65),
                                                                          ("Al2O3", 0.09),
                                                                          ("CaO", 0.07),
                                                                          ("MgO", 0.03),
                                                                          ("Na2O", 0.16)))
    m_polystyrene = geom.matter.Molecule("Polystyrene", density = "1.06g/cc",
                                                elements = (("carbon", 8),
                                                                        ("hydrogen", 8)))
    m_airsteelmixture = geom.matter.Mixture("AirSteelMixture", density = "3.9656025g/cc",
                                                components = (("STEEL_STAINLESS_Fe7Cr2Ni", 0.5),
                                                                          ("Air", 0.5)))
    m_vm2000 = geom.matter.Molecule("vm2000", density = "1.2g/cc",
                                                elements = (("carbon", 2),
                                                                        ("hydrogen", 4)))
    skin_anode = geom.surfaces.OpticalSurface("AnodeSurface", 
                                              model="unified", finish="ground",
                                              type="dielectric_metal", value=0.0,
                                              properties=(("REFLECTIVITY", _ANODE_REFL),
                                                          ("EFFICIENCY", _ZERO_EFF)))
    WoodMaterial = geom.matter.Mixture("Wood", density = "0.5g/cc",
                                                components = (("hydrogen", 0.06),
                                                                        ("carbon", 0.5),
                                                                        ("oxygen", 0.44)))
    m_dunesteel = geom.matter.Mixture("fDuneSteel", density = "7.93g/cc",
                                                components =(("iron", 0.958),
                                                                        ("manganese", 0.018),
                                                                        ("nickel", 0.008),
                                                                        ("silicon", 0.006),
                                                                        ("copper", 0.005),
                                                                        ("chromium", 0.003),
                                                                        ("carbon", 0.002)))
    skin_dunesteel = geom.surfaces.OpticalSurface("fDuneSteelSurface",
                                                  model="unified", finish="ground",
                                                  type="dielectric_metal", value=0.0,
                                                  properties=(("REFLECTIVITY", _CRYO_REFL),
                                                              ("EFFICIENCY", _ZERO_EFF)))
    m_bp = geom.matter.Mixture("BP", density = "0.95g/cc",
                               components = (("hydrogen", 0.116),
                                             ("carbon", 0.612),
                                             ("boron11", 0.04),
                                             ("boron10", 0.01),
                                             ("oxygen", 0.222)))
    m_radioshotcrete = geom.matter.Mixture("RadioShotcretePeteLein", density="2.4g/cc",
                                      components = (("oxygen", 0.5654),
                                                    ("iron", 0.0013),
                                                    ("calcium", 0.2106),
                                                    ("potassium", 0.0028),
                                                    ("silicon", 0.0417),
                                                    ("aluminum", 0.0051),
                                                    ("magnesium", 0.0038),
                                                    ("sodium", 0.0012),
                                                    ("nitrogen", 0.0007),
                                                    ("carbon", 0.1201),
                                                    ("hydrogen", 0.0472)
                                                    ))
    m_radioconcrete = geom.matter.Mixture("RadioConcretePeteLein", density="2.4g/cc",
                                      components = (("oxygen", 0.5654),
                                                    ("iron", 0.0013),
                                                    ("calcium", 0.2106),
                                                    ("potassium", 0.0028),
                                                    ("silicon", 0.0417),
                                                    ("aluminum", 0.0051),
                                                    ("magnesium", 0.0038),
                                                    ("sodium", 0.0012),
                                                    ("nitrogen", 0.0007),
                                                    ("carbon", 0.1201),
                                                    ("hydrogen", 0.0472)
                                                    ))
    m_radiorock = geom.matter.Mixture("RadioAverageDuneRock", density="2.65g/cc",
                                      components = (("oxygen", 0.5874),
                                                    ("iron", 0.0150),
                                                    ("manganese", 0.0003),
                                                    ("calcium", 0.0011),
                                                    ("potassium", 0.0155),
                                                    ("silicon", 0.1985),
                                                    ("aluminum", 0.0494),
                                                    ("magnesium", 0.0358),
                                                    ("sodium", 0.0069),
                                                    ("hydrogen", 0.09)
                                      ))
    m_leadShield = geom.matter.Mixture("Lead", density="11.348g/cc",
                                      components = (("lead", 1.0),
                                      ))
