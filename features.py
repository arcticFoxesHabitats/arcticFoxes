'''
This script executes all functions related to 
feature engineering for the arctic foxes project.
-> The homeranges get calculated
-> A final dataframe gets created, 
   containing the homeranges as target=1 
   and the remaining points as target=0
-> The distance to the forest is added as a feature
-> For the categorical features, 
   dummie variables are created

The logic behind these functions is explained in the 
notebooks EDA_home_ranges and Feature_Engineering
'''

import pandas as pd
import geopandas as geopd

import sys
sys.path.append("modeling")
import home_ranges as hr

print("The feature engineering is applied. This might take several minutes")
#data of all foxes:
foxes_all = geopd.read_file("data/cleaned_shapefiles/foxes_all.shp")
#resampled data of all foxes (over 2 hours):
foxes_resamp = geopd.read_file("data/cleaned_shapefiles/foxes_resamp.shp")
#sample points:
sample_points = geopd.read_file("data/cleaned_shapefiles/sample_points.shp")

#individual points for each fox:
indiv_fox_all = {}
for i in foxes_all.id.unique():
    indiv_fox_all[i] = foxes_all[foxes_all.id == i]

foxes = list(indiv_fox_all.values())

indiv_fox_resamp = {}
for i in foxes_resamp.id.unique():
    indiv_fox_resamp[i] = foxes_resamp[foxes_resamp.id == i]

foxes_indiv_resamp = list(indiv_fox_resamp.values())

#create the geometries for the homeranges:
fox_area = [hr.hr_geometry_df(fox, 0.95) for fox in foxes]
fox_hulls = [hr.hr_area(fox, 0.95) for fox in foxes]

#delete the points within the homeranges from sample_points:
sample_points_all = sample_points.copy()
for fox in fox_hulls:
    sample_points_all = sample_points_all.difference(fox)

#create dataframe for foxes, including only the data within the homeranges:
foxes_all = []
for i in range(0,len(foxes)-1):
    if i == 0:
        foxes_all = pd.concat([foxes[i], foxes[i+1]])
    else:
        foxes_all = pd.concat([foxes_all, foxes[i+1]])

fox_all = []
for i in range(0,len(fox_area)-1):
    if i == 0:
        fox_all = pd.concat([fox_area[i], fox_area[i+1]])
    else:
        fox_all = pd.concat([fox_all, fox_area[i+1]])

fox_all_merged = foxes_all.merge(fox_all, on = ["geometry", "id"])

#create dataframe with data only outside of the homeranges:
sample_points_df = geopd.GeoDataFrame(geometry = sample_points_all)

sample_points_all_merged = sample_points.merge(sample_points_df, on = "geometry")
sample_points_all_merged.shape

#combining the dataframes:
fox_all_merged["target"] = 1

sample_points_all_merged["target"] = 0
sample_points_all_merged["id"] = "available"
sample_points_all_merged = sample_points_all_merged.rename(columns = {"x" : "x_",
                                            "y" : "y_"})

df_all = pd.concat([fox_all_merged, sample_points_all_merged])

#repeat for resampled foxes:
fox_area_resamp = [hr.hr_geometry_df(fox, 0.95) for fox in foxes_indiv_resamp]
fox_hulls_resamp = [hr.hr_area(fox, 0.95) for fox in foxes_indiv_resamp]

sample_points_resamp = sample_points.copy()
for fox in fox_hulls_resamp:
    sample_points_resamp = sample_points_resamp.difference(fox)

foxes_resamp = []
for i in range(0,len(foxes_indiv_resamp)-1):
    if i == 0:
        foxes_resamp = pd.concat([foxes_indiv_resamp[i], foxes_indiv_resamp[i+1]])
    else:
        foxes_resamp = pd.concat([foxes_resamp, foxes_indiv_resamp[i+1]])

fox_resamp = []
for i in range(0,len(fox_area_resamp)-1):
    if i == 0:
        fox_resamp = pd.concat([fox_area_resamp[i], fox_area_resamp[i+1]])
    else:
        fox_resamp = pd.concat([fox_resamp, fox_area_resamp[i+1]])

fox_resamp_merged = foxes_resamp.merge(fox_resamp, on = ["geometry", "id"])
fox_resamp_merged.shape

sample_resamp_df = geopd.GeoDataFrame(geometry = sample_points_resamp)

sample_points_resamp_merged = sample_points.merge(sample_resamp_df, on = "geometry")
sample_points_resamp_merged.shape

sample_points_resamp_merged = sample_points_resamp_merged.iloc[::5, :]
sample_points_resamp_merged.shape

fox_resamp_merged["target"] = 1

sample_points_resamp_merged["target"] = 0
sample_points_resamp_merged["id"] = "available"
sample_points_resamp_merged = sample_points_resamp_merged.rename(columns = {"x" : "x_",
                                            "y" : "y_"})

df_resamp = pd.concat([fox_resamp_merged, sample_points_resamp_merged])

print("The homeranges are done. Now, the distance to the nearest forest is calculated for every point.")

#calculate distance to forest:
forest = geopd.read_file("data/forest_study_area.shp")

forest = forest.explode(ignore_index=True)
forest = forest.to_crs(3006)

def distance_to_forest(forest, point):
    return min(forest.distance(point))

df_all["distForest"] = df_all.geometry
df_all.distForest = df_all.distForest.apply(lambda x: distance_to_forest(forest,x))

print("The distance to the forest is calculated for the full dataset. Now, this calculation is repeated for the resampled dataset and the sample points.")
print("You're approximately halfway done.")

df_resamp["distForest"] = df_resamp.geometry
df_resamp.distForest = df_resamp.distForest.apply(lambda x: distance_to_forest(forest,x))

sample_points["distForest"] = sample_points.geometry
sample_points.distForest = sample_points.distForest.apply(lambda x: distance_to_forest(forest,x))

print("The calculation of the distance to the forest is done. Now, some dummie variables are created.")

#create dummie variables:
#in a fist step, the category "N" is created twice
df_all["asp"] = pd.cut(df_all.aspect, 
                                bins = [-1.1,0,22.5,67.5,112.5,157.5,202.5,247.5,292.5,337.5,360],
                                labels = ["None", "N", "NE", "E", "SE", "S", "SW", "W", "NW", "N2"])
#in a second step, the second category is renamed to resemble the first
df_all["asp"] = df_all.asp.replace("N2","N")

#repeat for resamp:
df_resamp["asp"] = pd.cut(df_resamp.aspect, 
                                bins = [-1.1,0,22.5,67.5,112.5,157.5,202.5,247.5,292.5,337.5,360],
                                labels = ["None", "N", "NE", "E", "SE", "S", "SW", "W", "NW", "N2"])
df_resamp["asp"] = df_resamp.asp.replace("N2","N")

cat_variables = ["soil", "veg", "asp"]

categories_all = pd.get_dummies(df_all[cat_variables], drop_first=True)
categories_resamp = pd.get_dummies(df_resamp[cat_variables], drop_first=True)

df_all = pd.concat([df_all, categories_all], axis = 1)
df_resamp = pd.concat([df_resamp, categories_resamp], axis = 1)

df_all = df_all.drop("asp", axis = 1)
df_resamp = df_resamp.drop("asp", axis = 1)

#save the data:
df_all.to_file("data/final_shapefiles/foxes_modelling_all.shp")
df_resamp.to_file("data/final_shapefiles/foxes_modelling_resamp.shp")
sample_points.to_file("data/final_shapefiles/sample_points.shp")

print("Done :)")
