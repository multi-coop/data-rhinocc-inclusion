import argparse
import csv
from geopy.geocoders import BANFrance

geocoder = BANFrance()

parser = argparse.ArgumentParser(description="Geocode a csv dataset",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-v", "--verbose", action="store_true", help="increase verbosity")
parser.add_argument("src", help="Path to source dataset to geocode")
parser.add_argument("-out", help="Path to source dataset to geocode", default="csv/geocoding/geocoded.csv")
parser.add_argument("-adress", "--col_adress", type=str, help="Column name of the line/item full adress", default='adresse_full')
parser.add_argument("-sep", "--separator", type=str, help="CSV separator",  default=',')
parser.add_argument("-debug", "--debug", type=bool, help="Debugging", default=False)

args = parser.parse_args()

debug = args.debug
if debug: print("\nargs : ", args)

sep = args.separator

col_adress = args.col_adress
if debug: print("\n geocoder ... col_adress : ", col_adress)

inputFile = open(args.src, 'r')
outputFile = open(args.out, 'w')
if debug: print("\n geocoder ... args.out : ", args.out)

inputData = csv.reader(inputFile, delimiter=sep)
outputData = csv.writer(outputFile, delimiter=sep, lineterminator='\n')

total_rows = 0
with open(args.src) as f:
  total_rows = sum(1 for line in f)
if debug: print("\n geocoder ... total_rows : ", total_rows)

### just copy columns headers to output
for row in inputData:
  if debug: print("\n geocoder ... row : ", row)
  
  # Get index of adress column
  col_adress_idx = row.index(col_adress)
  if debug: print("\n geocoder ... col_adress_idx : ", col_adress_idx)

  new_cols = [*row, 'latitude', 'longitude', 'BAN_adress', 'BAN_adress_full', 'BAN_city', 'BAN_postcode']
  if debug: print("\n geocoder ... new_cols : ", new_cols)

  # Write first row of output
  # outputData.writerow((*row, 'latitude', 'longitude'))
  # outputData.writerow((*row, *new_cols))
  outputData.writerow(new_cols)
  break

### Start looping rows
counter = 0
errors = 0
rows_geocoded = 0
try:
  ### loop input csv
  for row in inputData:
    print(f'\n... geocoding row : {counter} / {total_rows}')
    # if debug: print("row : \n", row)

    adress = row[col_adress_idx]
    if debug: print("... adress : ", adress)

    try:
      location = geocoder.geocode(adress, exactly_one=True, timeout=30)
      if debug: print("... location : ", location)
      if debug: print("... location.latitude : ", location.latitude)
      if debug: print("... location.longitude : ", location.longitude)
      if debug: print("... location.raw : ", location.raw)
      props = location.raw['properties']
      if debug: print("... props : ", props)
      
      lat = location.latitude
      lon = location.longitude
      BAN_adress = props.get('name', '')
      BAN_adress_full = props.get('label', '')
      BAN_city = props.get('city', '')
      BAN_postcode = props.get('postcode', '')
      if debug: print("... lat : ", lat)
      if debug: print("... lon : ", lon)
      if debug: print("... BAN_adress : ", BAN_adress)
      if debug: print("... BAN_adress_full : ", BAN_adress_full)
      if debug: print("... BAN_city : ", BAN_city)
      if debug: print("... BAN_postcode : ", BAN_postcode)

      outputData.writerow((*row, lat, lon, BAN_adress, BAN_adress_full, BAN_city, BAN_postcode))
      rows_geocoded += 1
    except Exception as inst:
      print(inst)
      outputData.writerow((*row, '', '', '', '', '', ''))
      errors += 1
    counter += 1

finally:
  inputFile.close()
  outputFile.close()

print(f'\n... Geocoding finished ...')
print(f'... Total rows : {counter} rows')
print(f'... Rows geocoded : {rows_geocoded} rows / {counter}')
print(f'... Errors : {errors} / {counter} rows')
print(f'... Output file here : {args.out} \n')
