#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 15:37:12 2026

@author: dzanaborovic
"""

#importing programs 
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns

plt.rcParams['figure.dpi'] = 300

utm18n = 26918

#Making the Geography figure
county = gpd.read_file('geography_data.gpkg',layer='county').to_crs(utm18n)
utica = gpd.read_file('city_data.gpkg',layer='city').to_crs(utm18n)
geo= gpd.read_file( 'store_data.gpkg', layer= 'stores').to_crs(utm18n)
income = pd.read_csv("income_by_bg.csv", dtype={'GEOID': str})
pop = pd.read_csv("population_by_bg.csv", dtype={'GEOID': str})

#Finding the ditance of the blockgroups to the grocery stores
uticacity= gpd.sjoin(county, utica, how='inner', predicate= 'intersects')
centroids = uticacity.copy()
centroids = centroids.drop(columns= 'index_right')
centroids['geometry'] = uticacity.centroid
centroids.to_file('geography_data.gpkg',layer='centroids')
served_by = centroids.sjoin_nearest(geo,how='left',distance_col='dist')
served_by['dist'] = served_by['dist'].astype(float)
served_by['dist_miles']= served_by['dist']/1609.34
served_by['dist_miles_numeric']= served_by['dist_miles']

#Making bins for the ditances 
bins = [0,1,2,3,4,5,10,15,20,25,30]
served_by['dist_miles']= pd.cut(served_by['dist_miles'], bins=bins)
counts= served_by['dist_miles'].value_counts().sort_index()

#Making the chart figure. 
fig,ax = plt.subplots()
counts.plot(kind='bar', ax=ax, color='blue')
ax.set_xlabel('Distance') 
ax.set_ylabel('Counts') 
ax.set_title("Utica's Block Groups Distance to the Nearest Grocery Store")
fig.tight_layout()
fig.savefig('bindistance.png')


#Making a Scatterplot wih distance and income
served_by["GEOID_left"] = served_by["GEOID_left"].astype(str)
merged= served_by.merge(income, left_on="GEOID_left", right_on="GEOID", how="left")
merged= merged.merge(pop, left_on="GEOID_left", right_on="GEOID", how="left")
merged['median_household_income']= merged['median_household_income'].replace('-', float('nan'))
merged['median_household_income']= pd.to_numeric(merged['median_household_income'])

#Scatterplot
fig, ax = plt.subplots()
sns.regplot(data= merged, x="dist_miles_numeric", y="median_household_income", ax=ax, scatter=False)
sns.scatterplot(data= merged, x="dist_miles_numeric", y="median_household_income", size="population", hue="population", alpha=0.6, sizes= (10,150),palette="viridis", ax=ax)
ax.set_xlabel('Distance from Nearest Grocery Store') 
ax.set_ylabel('Median Household Income') 
ax.set_title("Distance to the Nearest Grocery Store v. Median Household Income")
ax.legend(loc='lower right')
ax.axhline(49250, color='black')
ax.axvline(1.0, color='black')
fig.tight_layout()
fig.savefig('inc.v.dist.scatterplot.png', bbox_inches='tight')


