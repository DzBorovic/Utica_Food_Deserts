#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 10:14:27 2026

@author: dzanaborovic
"""

#importing programs 
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os

plt.rcParams['figure.dpi'] = 300

#Reading geograpahy file and turning it into a geopackage (only Oneida)
input_file = 'tl_2025_36_bg.zip'
reader = gpd.read_file(input_file)
oneida= reader.query("COUNTYFP== '065'")
oneida.to_file("geography_data.gpkg", layer="county")

#Reading geography and turning it into a geopackage (Oneida and surrounding counties)
border_counties= ['043', '049', '053', '065', '075', '077']
multi_counties= reader[reader['COUNTYFP'].isin(border_counties)]
multi_counties.to_file("geography_data.gpkg", layer="multi_county")

#Reading the places file and turning it into a geopackage 
input2_file= 'tl_2025_36_place.zip'
places = gpd.read_file(input2_file)
places= places.query("NAME == 'Utica'")
places.to_file("city_data.gpkg", layer="city")

#Reading the Retail Stores file 
store_file = 'Retail_Food_Stores2.csv'
wgs84 = 4326
utm18n = 26918
raw = pd.read_csv(store_file)

#Filtering the data to only Onieda County and missing data 
trim = raw.query("County == 'Oneida'")
trim = trim.dropna(subset='Georeference').copy()

#Filtering data down to the bigger retail stores 
big_stores = [
    'ALDI',
    'BJS WHOLESALE',
    'BARGAIN GROCERY',
    'CHANATRYS',
    'COSTCO',
    'HANNAFORD',
    'MARKET 32',
    'PRICE CHOPPER',
    'TARGET',
    'TOPS',
    'TRADER JOES',
    'WAL-MART',
    'WALMART',
    'WEGMANS'
    ]

trim['big'] = False

for store in big_stores:

    is_big = trim['DBA Name'].str.startswith(store)
    is_gas = trim['DBA Name'].str.contains('XPRESS')

    this_store = (is_big == True) & (is_gas == False)

    trim['big'] = trim['big'] | this_store

big = trim[ trim['big'] ]


#Making the data into a geo-series
coords = gpd.GeoSeries.from_wkt(big['Georeference'])
data_only = big.drop(columns='Georeference')
geo = gpd.GeoDataFrame( data=data_only, geometry=coords, crs=wgs84)
geo = geo.to_crs(utm18n)
geo.to_file("store_data.gpkg", layer="stores")

#Filtering to include all of the surrounding counties 
border_counties=['Oneida', 'Herkimer', 'Lewis', 'Madison', 'Otsego', 'Oswego']
trim_multi= raw[raw['County'].isin(border_counties)]
trim_multi = trim_multi.dropna(subset='Georeference').copy()

#Finding the big stores and removing the missing data 
trim_multi['big'] = False
for store in big_stores:
    is_big = trim_multi['DBA Name'].str.startswith(store)
    is_gas = trim_multi['DBA Name'].str.contains('XPRESS')

    this_store = (is_big == True) & (is_gas == False)

    trim_multi['big'] = trim_multi['big'] | this_store

big_multi = trim_multi[ trim_multi['big'] ]

#Making the data into a geo-series
coords_multi = gpd.GeoSeries.from_wkt(big_multi['Georeference'])
data_multi = big_multi.drop(columns='Georeference')
geo_multi = gpd.GeoDataFrame( data=data_multi, geometry=coords_multi, crs=wgs84)
geo_multi = geo_multi.to_crs(utm18n)
geo_multi.to_file("store_data.gpkg", layer="stores_multi")
