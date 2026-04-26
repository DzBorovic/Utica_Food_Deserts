#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 15:58:41 2026

@author: dzanaborovic
"""
#Importing varaibles 
import pandas as pd
import requests as req
import numpy as np

#Making API for Block-group data
#making a dictionary 
variables = {'B19013_001E':'median_household_income'}
var_list =variables.keys()
var_string = ",".join(var_list)

#Setting up the api
with open('apikey4.txt') as fh:
    apikey = fh.readline().strip()
api = "https://api.census.gov/data/2024/acs/acs5"

#Pulling the dataframe
for_clause = "block group:*"
in_clause = "state:36 county:065"
payload= {'get':var_string,'for': for_clause,'in': in_clause,'key':apikey}
response = req.get(api, payload)
income= pd.DataFrame(response.json()[1:], columns=response.json()[0])

#Making variables 
income= income.replace("-666666666", np.nan)
income = income.rename(columns=variables)
income["GEOID"]= income["state"]+income["county"]+income["tract"]+income["block group"]
income = income.set_index("GEOID")
keep_cols = variables.values()

#Saving and trimming the dataframe 
income= income[keep_cols]
income.to_csv("income_by_bg.csv")

#Making API for Tract-Level Data
#Pulling the dataframe
for_clause = "tract:*"
in_clause = "state:36 county:065"
payload_tract= {'get':var_string,'for': for_clause,'in': in_clause,'key':apikey}
response_tract = req.get(api, payload_tract)
tract_income= pd.DataFrame(response_tract.json()[1:], columns=response_tract.json()[0])

#Making variables 
tract_income= tract_income.replace("-666666666", np.nan)
tract_income = tract_income.rename(columns={ "B19013_001E":"tract_median_income"})
tract_income["TRACTID"]= tract_income["state"]+tract_income["county"]+tract_income["tract"]
tract_income = tract_income.set_index("TRACTID")[["tract_median_income"]]

#Filling in the missing blockgroups with the tract group data
income["TRACTID"]= income.index.str[:11]
income= income.join(tract_income, on="TRACTID")
income["imputed"] = income["median_household_income"].isna().astype(int)
income["median_household_income"]= income["median_household_income"].fillna(income["tract_median_income"])
income= income.drop(columns=["TRACTID", "tract_median_income"])
income.to_csv("income_by_bg.csv")

#Making API for Block-group data
#making a dictionary 
variables2 = {'B01003_001E':'population'}
var_list2 =variables2.keys()
var_string2 = ",".join(var_list2)

#Setting up the api
with open('apikey4.txt') as fh:
    apikey = fh.readline().strip()
api = "https://api.census.gov/data/2024/acs/acs5"


#Pulling the dataframe
for_clause = "block group:*"
in_clause = "state:36 county:065"
payload= {'get':var_string2,'for': for_clause,'in': in_clause,'key':apikey}
response = req.get(api, payload)
population= pd.DataFrame(response.json()[1:], columns=response.json()[0])

#Making variables 
population= population.replace("-666666666", np.nan)
population= population.rename(columns=variables2)
population["GEOID"]= population["state"]+population["county"]+population["tract"]+population["block group"]
population = population.set_index("GEOID")
keep_cols2 = variables2.values()

#Saving and trimming the dataframe 
population= population[keep_cols2]
population.to_csv("population_by_bg.csv")