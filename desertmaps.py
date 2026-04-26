#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 15:00:22 2026

@author: dzanaborovic
"""
#importing programs 
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os

plt.rcParams['figure.dpi'] = 300

utm18n = 26918

#Making the Geography figure
county = gpd.read_file('geography_data.gpkg',layer='county').to_crs(utm18n)
multi = gpd.read_file('geography_data.gpkg',layer='multi_county').to_crs(utm18n)
utica = gpd.read_file('city_data.gpkg',layer='city').to_crs(utm18n)
geo= gpd.read_file( 'store_data.gpkg', layer= 'stores').to_crs(utm18n)
geo_multi= gpd.read_file( 'store_data.gpkg', layer= 'stores_multi').to_crs(utm18n)

#Making figure 1
fig,ax1 = plt.subplots()
county.plot(color='gray',ax=ax1)
utica.plot(color='tan',ax=ax1)
geo.plot(color='blue',markersize=1,ax=ax1)
ax1.set_title("Oneida County and Utica Grocery Store Map")
ax1.axis('off')
fig.tight_layout()
fig.savefig('oneidacounty_storesmap.png')

#Finding the ditance of the blockgroups to the grocery stores
centroids = county.copy()
centroids['geometry'] = county.centroid
centroids.to_file('geography_data.gpkg',layer='centroids')
served_by = centroids.sjoin_nearest(geo,how='left',distance_col='dist')
served_by['dist'] = served_by['dist'].astype(float)
served_by['dist_miles']= served_by['dist']/1609.34

#Joining the distance onto the plot 
dist_to_store = served_by[['GEOID','dist_miles']]
county = county.merge(dist_to_store,on='GEOID',validate='1:1',indicator=True)
county= county.drop(columns='_merge')

#Making the heatmap 1
fig,ax = plt.subplots()
county.plot('dist_miles',ax=ax,legend=True, cmap= 'RdYlGn_r')
utica.plot(color='none', edgecolor='black', linewidth=0.5, ax=ax)
geo.plot(color='red',markersize=0.5,ax=ax)
ax.set_title("Oneida County Food Desert Heatmap")
ax.axis('off')
fig.tight_layout()
fig.savefig('oneidacountyheatmap.png')

#Finding the ditance of the blockgroups to the grocery stores
centroids_multi = multi.copy()
centroids_multi['geometry'] = multi.centroid
centroids_multi.to_file('geography_data.gpkg',layer='centroids_multi')
served_by_multi = centroids_multi.sjoin_nearest(geo_multi,how='left',distance_col='dist')
served_by_multi['dist'] = served_by_multi['dist'].astype(float)
served_by_multi['dist_miles']= served_by_multi['dist']/1609.34

#Joining the distance onto the plot 
dist_to_store_multi = served_by_multi[['GEOID','dist_miles']]
multi = multi.merge(dist_to_store_multi,on='GEOID',validate='1:1',indicator=True)
multi= multi.drop(columns='_merge')

#Making the heatmap 2
fig,ax = plt.subplots()
multi.plot('dist_miles',ax=ax,legend=True, cmap= 'RdYlGn_r')
county.plot(color='none', edgecolor='black', linewidth=0.5, ax=ax)
county_borders= multi.dissolve(by='COUNTYFP')
county_borders.plot(color='none', edgecolor='black', linewidth=1.5, ax=ax)
utica.plot(color='none', edgecolor='black', linewidth=1.5, ax=ax)
ax.set_title("Border Counties Food Desert Heat Map")
geo_multi.plot(color='red',markersize=0.5,ax=ax)
ax.axis('off')
fig.tight_layout()
fig.savefig('multicountyheatmap.png')

