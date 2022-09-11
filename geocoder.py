import argparse
import csv
from geopy.geocoders import BANFrance

geocoder = BANFrance()

parser = argparse.ArgumentParser(description="Geocode a csv dataset",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-v", "--verbose", action="store_true", help="increase verbosity")
parser.add_argument("src", help="Path to source dataset to geocode")
parser.add_argument("-out", help="Path to source dataset to geocode", default="csv/geocoding/geocoded.csv")
parser.add_argument("-adress", "--col_adress", type=str, help="Column name of the line/item full adress", default='full_adress')
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

inputData = csv.reader(inputFile, delimiter=sep)
outputData = csv.writer(outputFile, delimiter=sep, lineterminator='\n')

total_rows = 0
with open(args.src) as f:
  total_rows = sum(1 for line in f)
if debug: print("\n geocoder ... total_rows : ", total_rows)

### just copy columns headers to output
for row in inputData:
  if debug: print("\n geocoder ... row : ", row)
  col_adress_idx = row.index(col_adress)

  if debug: print("\n geocoder ... col_adress_idx : ", col_adress_idx)
  outputData.writerow((*row, 'latitude', 'longitude'))
  break

### Start looping rows
counter = 0
errors = 0
rows_geocoded = 0
try:
  ### loop input csv
  for row in inputData:
    print(f'\n... geocoding row : {counter} / {total_rows}')
    if debug: print("\nrow : ", row)

    adress = row[col_adress_idx]
    if debug: print("... adress : ", adress)

    try:
      location = geocoder.geocode(adress, exactly_one=True, timeout=30)
      if debug: print("... location : ", location)
      if debug: print("... location.latitude : ", location.latitude)
      if debug: print("... location.longitude : ", location.longitude)
      outputData.writerow((*row, location.latitude, location.longitude))
      rows_geocoded += 1
    except Exception as inst:
      print(inst)
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
