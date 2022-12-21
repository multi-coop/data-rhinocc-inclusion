import os
import argparse
import csv
from geopy.geocoders import BANFrance

### update 15/12/2022

geocoder = BANFrance()

parser = argparse.ArgumentParser(description="Geocode a csv dataset",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-v", "--verbose", action="store_true", help="increase verbosity")
parser.add_argument("src", help="Path to source dataset to geocode")
parser.add_argument("-out", help="Path to source dataset to geocode", default="csv/geocoding")
parser.add_argument("-adress", "--col_adress", type=str, help="Column name of the line/item full adress", default='')
parser.add_argument("-cols_a", "--cols_adress", type=str, nargs="+", help="Column name of the line/item full adress", default='')
parser.add_argument("-sep", "--separator", type=str, help="CSV separator",  default=',')
parser.add_argument("-is_latlon", "--is_latitude_longitude", type=str, help="Existing Lat. and Lon. columns. If columns already exists keep the values from columnsand copy it into BAN_latitude and BAN_longitude", default=None)
parser.add_argument("-debug", "--debug", type=bool, help="Debugging", default=False)

args = parser.parse_args()

### Get args

debug = args.debug
if debug: print("\nargs : ", args)

sep = args.separator

col_adress = args.col_adress
if debug: print("\n geocoder ... col_adress : ", col_adress)
cols_adress = args.cols_adress
if debug: print("\n geocoder ... cols_adress : ", cols_adress)

cols_is_latlon = args.is_latitude_longitude.split(',') if args.is_latitude_longitude else None
if debug: print("\n geocoder ... cols_is_latlon : ", cols_is_latlon)
if cols_is_latlon:
  col_lat = cols_is_latlon[0]
  col_lon = cols_is_latlon[1]
  if debug: print(" geocoder ... col_lat : ", col_lat)
  if debug: print(" geocoder ... col_lon : ", col_lon)

### Create values for output file

srcFilename = os.path.basename(args.src)
if debug: print("\n geocoder ... srcFilename : ", srcFilename)
outFile = f'{args.out}/{os.path.splitext(srcFilename)[0]}-geocoded.csv'
if debug: print("\n geocoder ... outFile : ", outFile)

inputFile = open(args.src, 'r')
outputFile = open(outFile, 'w')
if debug: print("\n geocoder ... args.out : ", args.out)

inputData = csv.reader(inputFile, delimiter=sep)
outputData = csv.writer(outputFile, delimiter=sep, lineterminator='\n')

### Count lines for debugging

total_rows = 0
with open(args.src) as f:
  total_rows = sum(1 for line in f)
if debug: print("\n geocoder ... total_rows : ", total_rows)

### just copy columns headers to output
for row in inputData:
  if debug: print("\n geocoder ... row : ", row)
  
  # Get index of adress column
  if col_adress :
    try :
      col_adress_idx = row.index(col_adress)
      if debug: print("\n geocoder ... col_adress_idx : ", col_adress_idx)
    except : 
      print("\n geocoder ... col_adress_idx > idx can't be found for col_adress: ", col_adress)

  elif cols_adress :
    cols_adress_idx = []
    for col in cols_adress :
      try :
        cols_adress_idx.append(row.index(col))
        if debug: print("\n geocoder ... cols_adress > row.index(col) : ", row.index(col))
      except : 
        print("\n geocoder ... cols_adress > idx can't be found for col: ", col)
    if debug: print("\n geocoder ... cols_adress > cols_adress_idx : ", cols_adress_idx)

  if cols_is_latlon:
    col_lat_idx = row.index(col_lat)
    col_lon_idx = row.index(col_lon)
    if debug: print("geocoder ... col_lat_idx : ", col_lat_idx)
    if debug: print("geocoder ... col_lon_idx : ", col_lon_idx)

  new_cols = [
    *row,
    'BAN_latitude',
    'BAN_longitude',
    'BAN_adress',
    'BAN_adress_full',
    'BAN_city', 
    'BAN_postcode',
    'BAN_depcode'
    ]
  if debug: print("\n geocoder ... new_cols : ", new_cols)

  # Write first row of output
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

    if col_adress :
      adress = row[col_adress_idx]
      if debug: print("... adress : ", adress)
    elif cols_adress :
      adress_concac = '' 
      for col_i in cols_adress_idx :
        a = row[col_i]
        adress_concac = f'{adress_concac} {a}'
      if debug: print("... adress_concac : ", adress_concac)

    if cols_is_latlon:
      row_lat = row[col_lat_idx]
      row_lon = row[col_lon_idx]
    else:
      row_lat = ''
      row_lon = ''
    if debug: print("... row_lat : ", row_lat)
    if debug: print("... row_lon : ", row_lon)

    try:
      if col_adress :
        location = geocoder.geocode(adress, exactly_one=True, timeout=30)
      elif cols_adress :
        location = geocoder.geocode(adress_concac, exactly_one=True, timeout=30)
      
      if debug: print("... location : ", location)
      if debug: print("... location.latitude : ", location.latitude)
      if debug: print("... location.longitude : ", location.longitude)
      if debug: print("... location.raw : ", location.raw)
      props = location.raw['properties']
      if debug: print("... props : ", props)
      
      BAN_lat = row_lat if cols_is_latlon and row_lat != '' else location.latitude
      BAN_lon = row_lon if cols_is_latlon and row_lon != '' else location.longitude

      BAN_adress = props.get('name', '')
      BAN_adress_full = props.get('label', '')
      BAN_city = props.get('city', '')
      BAN_postcode = props.get('postcode', '')
      BAN_depcode = BAN_postcode[0:2] if BAN_postcode != '' else ''
      if debug: print("... BAN_lat : ", BAN_lat)
      if debug: print("... BAN_lon : ", BAN_lon)
      if debug: print("... BAN_adress : ", BAN_adress)
      if debug: print("... BAN_adress_full : ", BAN_adress_full)
      if debug: print("... BAN_city : ", BAN_city)
      if debug: print("... BAN_postcode : ", BAN_postcode)
      if debug: print("... BAN_depcode : ", BAN_depcode)

      outputData.writerow((*row, BAN_lat, BAN_lon, BAN_adress, BAN_adress_full, BAN_city, BAN_postcode, BAN_depcode))
      rows_geocoded += 1
    except Exception as inst:
      print(inst)
      outputData.writerow((*row, row_lat, row_lon, '', '', '', '', ''))
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
