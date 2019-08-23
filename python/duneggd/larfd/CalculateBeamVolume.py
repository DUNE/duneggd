import pandas as pd
from pint import UnitRegistry
ureg = UnitRegistry()
Q = ureg.Quantity

data = pd.read_csv('volume_beam.txt', sep=" ", header=None)
data.columns = ["name", "volume"]

density = Q('7.8g*cm^-3').to('metric_ton*m^-3')

total_volume_mainbeam =Q('0m^3')
total_volume_beamfloor=Q('0m^3')
total_volume_smallbeam=Q('0m^3')

total_number_mainbeam =0
total_number_beamfloor=0
total_number_smallbeam=0

volume_membrane=0
volume_layer2  =0
volume_layer3  =0
volume_warmskin=0

density_membrane=density
density_layer2  =Q('545.91*kg*m^-3')
density_layer3  =Q('90*kg*m^-3')
density_warmskin=density


for index, row in data.iterrows():
    if (row['name'].find("BeamFloor") is not -1):
        if (row['name'].find("hole") is not -1):
            total_volume_beamfloor -= Q(row['volume'], 'm^3')
        else:
            total_volume_beamfloor += Q(row['volume'], 'm^3')
            total_number_beamfloor += 1
    elif (row['name'].find("BeamSmall") is not -1):
        total_volume_smallbeam += Q(row['volume'], 'm^3')
        total_number_smallbeam += 1
    elif (row['name'].find("Beam") is not -1):
        total_volume_mainbeam += Q(row['volume'], 'm^3')
        total_number_mainbeam += 1
    elif (row['name'].find('membrane') is not -1):
        volume_membrane = Q(row['volume'], 'm^3')
    elif (row['name'].find('layer2') is not -1):
        volume_layer2 = Q(row['volume'], 'm^3')
    elif (row['name'].find('layer3') is not -1):
        volume_layer3 = Q(row['volume'], 'm^3')
    elif (row['name'].find('warmskin') is not -1):
        volume_warmskin = Q(row['volume'], 'm^3')
        

print ("volume_membrane", volume_membrane)
print ("volume_layer2  ", volume_layer2  )
print ("volume_layer3  ", volume_layer3  )
print ("volume_warmskin", volume_warmskin)

print ("density_membrane", density_membrane)
print ("density_layer2  ", density_layer2  )
print ("density_layer3  ", density_layer3  )
print ("density_warmskin", density_warmskin)

print ("mass_membrane", (volume_membrane * density_membrane).to('metric_ton'))
print ("mass_layer2  ", (volume_layer2   * density_layer2  ).to('metric_ton'))
print ("mass_layer3  ", (volume_layer3   * density_layer3  ).to('metric_ton'))
print ("mass_warmskin", (volume_warmskin * density_warmskin).to('metric_ton'))

print ("number of main beams      ", total_number_mainbeam )
print ("number of transverse beams", total_number_beamfloor)
print ("number of small beams     ", total_number_smallbeam)

print ("volume main beams      ", total_volume_mainbeam )
print ("volume transverse beams", total_volume_beamfloor)
print ("volume small beams     ", total_volume_smallbeam)
print ("total volume           ", total_volume_mainbeam + total_volume_beamfloor + total_volume_smallbeam)

print ("density of steel (S460ML) ", density)
print ("mass main beams      ", total_volume_mainbeam  * density)
print ("mass transverse beams", total_volume_beamfloor * density)
print ("mass small beams     ", total_volume_smallbeam * density)
print ("total mass           ", (total_volume_mainbeam+total_volume_beamfloor+total_volume_smallbeam) * density)
