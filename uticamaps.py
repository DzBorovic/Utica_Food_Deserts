#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 20:44:22 2026

@author: dzanaborovic
"""
#importing programs 
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os

plt.rcParams['figure.dpi'] = 300

utm18n = 26918

#Reading the Geography files
county = gpd.read_file('geography_data.gpkg',layer='county').to_crs(utm18n)
multi = gpd.read_file('geography_data.gpkg',layer='multi_county').to_crs(utm18n)
utica = gpd.read_file('city_data.gpkg',layer='city').to_crs(utm18n)
geo= gpd.read_file( 'store_data.gpkg', layer= 'stores').to_crs(utm18n)
geo_multi= gpd.read_file( 'store_data.gpkg', layer= 'stores_multi').to_crs(utm18n)
income = pd.read_csv("income_by_bg.csv", dtype={'GEOID': str})
pop = pd.read_csv("population_by_bg.csv", dtype={'GEOID': str})

#Finding the stores within 1 miles of Utica's border
geo_utica = gpd.sjoin(geo, utica, how='inner', predicate='intersects')
geo_utica = geo_utica.drop(columns= 'index_right')
utica_buffered= utica.copy()
utica_buffered['geometry'] = utica.buffer(1609.34)
geo_nearby= gpd.sjoin(geo_multi, utica_buffered, how='inner', predicate='intersects')
geo_nearby= geo_nearby.drop(columns= 'index_right')

#Making the buffers
geo_buffer= geo_nearby.copy()
geo_buffer['geometry'] = geo_nearby.buffer(1609.34)

#Making the buffer figure
fig,ax = plt.subplots()
utica.plot(color='lightgray', edgecolor='black', linewidth=1.5, ax=ax)
geo_buffer.plot(color='plum', alpha= 0.3, ax=ax)
geo_nearby.plot(color='purple',markersize=3,ax=ax)
ax.set_title("1 mile Buffers from Grocery Stores in Utica and Surrounding Areas")
ax.axis('off')
fig.tight_layout()
fig.savefig('uticabuffers.png')

#Finding the distance of the utica blockgroups to the grocery stores 
utica_blocks= gpd.sjoin(county, utica, how='inner', predicate= 'within')
utica_blocks = utica_blocks.rename(columns={'GEOID_left':'GEOID'})
utica_blocks = utica_blocks.drop(columns='index_right')

centroids_utica = utica_blocks.copy()
centroids_utica['geometry'] = utica_blocks.centroid
centroids_utica.to_file('geography_data.gpkg',layer='centroids_utica')
served_by_utica = centroids_utica.sjoin_nearest(geo_utica,how='left',distance_col='dist')
served_by_utica['dist'] = served_by_utica['dist'].astype(float)
served_by_utica['dist_miles']= served_by_utica['dist']/1609.34

#Joining the distance on the plot 
dist_to_store_utica = served_by_utica[['GEOID_left','dist_miles']]
dist_to_store_utica = dist_to_store_utica.rename(columns={'GEOID_left': 'GEOID'})
utica_blocks = utica_blocks.merge(dist_to_store_utica,on='GEOID',validate='1:1',indicator=True)

#Finding the amount of population inside and outside of the buffers 
utica_blocks = utica_blocks.merge(pop[['GEOID', 'population']], on='GEOID', how='left') 
utica_blocks["bg_area"]= utica_blocks.geometry.area
geo_buffer_dissolved= geo_buffer.dissolve()
cutout= gpd.overlay(utica_blocks, geo_buffer_dissolved, how='intersection')
cutout = cutout.merge(utica_blocks[['GEOID', 'population']], left_on='GEOID_1', right_on='GEOID', how='left') 
cutout['clip_area'] = cutout.geometry.area
cutout['area_share']= cutout['clip_area']/cutout['bg_area']

#Doing an Allocation block
realloc= pd.DataFrame()
for v in ['population_x']:
    realloc[v]= cutout[v].mul(cutout['area_share'], axis='index')

inside = realloc['population_x'].sum()
outside= utica_blocks['population'].sum()-inside

print(f"Population within one mile of a grocery store: {inside}")
print(f"Population outside one mile of a grocery store: {outside}")

#Making the heatmap 3
fig,ax = plt.subplots()
utica_blocks.plot('dist_miles',ax=ax,legend=True, cmap= 'RdYlGn_r')
utica.plot(color='none', edgecolor='black', linewidth=1.5, ax=ax)
geo_utica.plot(color='red',markersize=10,ax=ax)
ax.set_title("Heatmap of Distance to Grocery Stores in Utica")
ax.axis('off')
fig.tight_layout()
fig.savefig('uticaheatmap.png')

#Get rid of the missing data 
income['median_household_income']= income['median_household_income'].replace('-', float('nan'))
income['median_household_income']= pd.to_numeric(income['median_household_income'])
utica_blocks= utica_blocks.merge(income[['GEOID', "median_household_income", 'imputed']], on="GEOID", how="left")

#Missing Blockgroup data transform to tracts
fig,ax = plt.subplots()
utica_blocks.plot('median_household_income',ax=ax,legend=True, cmap= 'RdYlGn', missing_kwds = {'color': 'lightgrey'})
imputed_blocks = utica_blocks[utica_blocks["imputed"]==1]
imputed_blocks.plot(ax=ax, facecolor='none', edgecolor= 'black', linewidth=0.5, hatch='///')

#Making the heatmap 4
utica.plot(color='none', edgecolor='black', linewidth=1.5, ax=ax)
geo_utica.plot(color='red',markersize=10,ax=ax)
ax.set_title("Heatmap of Utica's Median Household Income")
ax.axis('off')
fig.tight_layout()
fig.savefig('uticaincomeheatmap.png')

