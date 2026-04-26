#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 13:14:19 2026

@author: dzanaborovic
"""
#Importing varaibles 
import pandas as pd
import requests as req
import numpy as np

# Importing programs
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['figure.dpi'] = 300

# Reading the data
df = pd.read_csv("Quant_Project_Data_Collection_County_by_County_.csv")
df = df.dropna(subset=['Year', 'County'])

# Cleaning numeric columns
df['Median Housing Price (Real)'] = df['Median Housing Price (Real)'].replace('-', float('nan'))
df['Median Housing Price (Real)'] = df['Median Housing Price (Real)'].str.replace(',', '').str.strip()
df['Median Housing Price (Real)'] = pd.to_numeric(df['Median Housing Price (Real)'], errors='coerce')

df['Population '] = df['Population '].astype(str).str.replace(',', '').str.strip()
df['Population '] = pd.to_numeric(df['Population '], errors='coerce')

# Average across counties per year (weighted by population optional)
yearly = df.groupby('Year').agg(
    median_price=('Median Housing Price (Real)', 'median'),
    total_pop=('Population ', 'sum')
).reset_index()

# Scatterplot
fig, ax = plt.subplots(figsize=(12, 6))
sns.scatterplot(data=yearly, x='Year', y='median_price',
                size='total_pop',
                sizes=(50, 500),
                alpha=0.7,
                ax=ax)
ax.set_xlabel('Year')
ax.set_ylabel('Median Housing Price (Real, 2024 $)')
ax.set_title('Median Housing Prices Across New York Counties Over Time')
ax.legend(title='Total Population', loc='upper left')
fig.tight_layout()
fig.savefig('housing_prices_over_time.png', bbox_inches='tight')