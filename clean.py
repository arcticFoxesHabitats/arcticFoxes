'''
hard coded data cleaning for arctic fox project.
The logic behind the code is explained in
Data_cleaning.ipynb
'''

import pandas as pd
import numpy as np
import rasterio
import rasterio.rio
import geopandas as geopd
import pyreadr
import datetime as dt 

print("The data for the arctic foxes is being loaded and cleaned. This might take several minutes")
#data of all foxes:
all_foxes = pyreadr.read_r('data/r_files/track_all.RDS')[None]
#resampled data of all foxes (over 2 hours):
all_foxes_resamp = pyreadr.read_r('data/r_files/track_resamp.RDS')[None]
#metadata:
fox_metadata = pd.read_csv("data/additional_info.csv", sep = "\t")

#load raster layers:
elev = rasterio.open("data/Rasters_for_R/DEM_30.tif")
aspect = rasterio.open("data/Rasters_for_R/aspect_30.tif")
NDVI_NDMI = rasterio.open("data/Rasters_for_R/NDVI_arj_vind.tif")
slope = rasterio.open("data/Rasters_for_R/slope_arj_vind.tif")
veg = rasterio.open("data/Rasters_for_R/veg_nofor_morecats.tif")
soil = rasterio.open("data/Rasters_for_R/soil_av_clip.tif")

print("All data is loaded.")

#DF containing all points:
gdf_all = geopd.GeoDataFrame(
    all_foxes, geometry=geopd.points_from_xy(all_foxes.x_, all_foxes.y_))
coord_list_all = [(x,y) for x,y in zip(gdf_all['geometry'].x , gdf_all['geometry'].y)]
gdf_all['NDVI_NDMI'] = [x for x in NDVI_NDMI.sample(coord_list_all)]
gdf_all["NDVI"] = [gdf_all.NDVI_NDMI[i][2] for i in range(0,gdf_all.shape[0])]
gdf_all["NDMI"] = [gdf_all.NDVI_NDMI[i][1] for i in range(0,gdf_all.shape[0])]
gdf_all['soil'] = [x[0] for x in soil.sample(coord_list_all)]
gdf_all['veg'] = [x[0] for x in veg.sample(coord_list_all)]
gdf_all['slope'] = [x[0] for x in slope.sample(coord_list_all)]
gdf_all['aspect'] = [x[0] for x in aspect.sample(coord_list_all)]
gdf_all['elev'] = [x[0] for x in elev.sample(coord_list_all)]
gdf_all.drop("NDVI_NDMI", inplace = True, axis = 1)

#DF containing resampled points:
gdf_resamp = geopd.GeoDataFrame(
    all_foxes_resamp, geometry=geopd.points_from_xy(all_foxes_resamp.x_, all_foxes_resamp.y_))
coord_list_resamp = [(x,y) for x,y in zip(gdf_resamp['geometry'].x , gdf_resamp['geometry'].y)]
gdf_resamp['NDVI_NDMI'] = [x for x in NDVI_NDMI.sample(coord_list_resamp)]
gdf_resamp["NDVI"] = [gdf_resamp.NDVI_NDMI[i][2] for i in range(0,gdf_resamp.shape[0])]
gdf_resamp["NDMI"] = [gdf_resamp.NDVI_NDMI[i][1] for i in range(0,gdf_resamp.shape[0])]
gdf_resamp['soil'] = [x[0] for x in soil.sample(coord_list_resamp)]
gdf_resamp['veg'] = [x[0] for x in veg.sample(coord_list_resamp)]
gdf_resamp['slope'] = [x[0] for x in slope.sample(coord_list_resamp)]
gdf_resamp['aspect'] = [x[0] for x in aspect.sample(coord_list_resamp)]
gdf_resamp['elev'] = [x[0] for x in elev.sample(coord_list_resamp)]
gdf_resamp.drop("NDVI_NDMI", inplace = True, axis=1)

print("The dataframes containing the positions of the foxes are built.")
print("Now, the dataframe with the sample points gets built.")
print("This is the most time consuming task...")

#DF with sample points
xy = np.mgrid[gdf_all.x_.min():gdf_all.x_.max():70, gdf_all.y_.min():gdf_all.y_.max():70].reshape(2,-1).T
xy = pd.DataFrame(xy, columns= ["x","y"])
sample_points = geopd.GeoDataFrame(
    xy, geometry=geopd.points_from_xy(xy.x, xy.y))

coord_list_sample = [(x,y) for x,y in zip(sample_points['geometry'].x , sample_points['geometry'].y)]
sample_points['NDVI_NDMI'] = [x for x in NDVI_NDMI.sample(coord_list_sample)]
print("The first feature, NDVI_NDMI, is loaded. You are approximately 80 Percent done.")

sample_points["NDVI"] = [sample_points.NDVI_NDMI[i][2] for i in range(0,sample_points.shape[0])]
print("NDVI is extracted.")
sample_points["NDMI"] = [sample_points.NDVI_NDMI[i][1] for i in range(0,sample_points.shape[0])]
print("NDMI is extracted.")
sample_points['soil'] = [x[0] for x in soil.sample(coord_list_sample)]
print("The information describing the soil is loaded")
sample_points['veg'] = [x[0] for x in veg.sample(coord_list_sample)]
print("The information describing the vegetation is loaded")
sample_points['slope'] = [x[0] for x in slope.sample(coord_list_sample)]
print("The information describing the slope is loaded")
sample_points['aspect'] = [x[0] for x in aspect.sample(coord_list_sample)]
print("The information about the aspect is loaded")
sample_points['elev'] = [x[0] for x in elev.sample(coord_list_sample)]
print("The information regarding the elevation is loaded")
sample_points.drop("NDVI_NDMI", inplace = True, axis=1)


#rename categorical variables
# renaming in sample points data frame
sample_points.soil = sample_points.soil.replace(1,"Moraine").replace(2,"Peat(Turf)").replace(3,"Roesberg").replace(4,"Rest").replace(5,"Stone").replace(6,"Water").replace(0, np.nan)
sample_points.veg = sample_points.veg.replace(1,"Water").replace(2,"Snow").replace(3,"Stone").replace(4,"Dry Shrub").replace(5,"Moist Shrub").replace(6,"Grassland").replace(7,"Bush").replace(8,"Bog").replace(0, np.nan)

# renaming in geo data frame with all fox points
gdf_all.soil = gdf_all.soil.replace(1,"Moraine").replace(2,"Peat(Turf)").replace(3,"Roesberg").replace(4,"Rest").replace(5,"Stone").replace(6,"Water").replace(0, np.nan)
gdf_all.veg = gdf_all.veg.replace(1,"Water").replace(2,"Snow").replace(3,"Stone").replace(4,"Dry Shrub").replace(5,"Moist Shrub").replace(6,"Grassland").replace(7,"Bush").replace(8,"Bog").replace(0, np.nan)

# renaming in geo data frame with resampled fox points
gdf_resamp.soil = gdf_resamp.soil.replace(1,"Moraine").replace(2,"Peat(Turf)").replace(3,"Roesberg").replace(4,"Rest").replace(5,"Stone").replace(6,"Water").replace(0, np.nan)
gdf_resamp.veg = gdf_resamp.veg.replace(1,"Water").replace(2,"Snow").replace(3,"Stone").replace(4,"Dry Shrub").replace(5,"Moist Shrub").replace(6,"Grassland").replace(7,"Bush").replace(8,"Bog").replace(0, np.nan)

#replace NaNs:
# replacing in sample points data frame
sample_points.aspect = sample_points.aspect.replace(-9999, np.nan)
sample_points.slope = sample_points.slope.replace(-9999, np.nan)
sample_points.elev = sample_points.elev.apply(lambda x : np.nan if x < -3.4e+38 else x)

# replacing in gdf all data frame
gdf_all.aspect = gdf_all.aspect.replace(-9999, np.nan)
gdf_all.slope = gdf_all.slope.replace(-9999, np.nan)
gdf_all.elev = gdf_all.elev.apply(lambda x : np.nan if x < -3.4e+38 else x)

# replacing in gdf resamp data frame
gdf_resamp.aspect = gdf_resamp.aspect.replace(-9999, np.nan)
gdf_resamp.slope = gdf_resamp.slope.replace(-9999, np.nan)
gdf_resamp.elev = gdf_resamp.elev.apply(lambda x : np.nan if x < -3.4e+38 else x)

#drop missing vegetation values
# Sample points
sample_points_clean = sample_points.dropna(subset = ["veg"])

# gdf all
foxes_all_clean = gdf_all.dropna(subset = ["veg"])

# gdf resampled
foxes_resamp_clean = gdf_resamp.dropna(subset = ["veg"])

#fill NaNs in the other columns
sample_points_clean.NDMI = sample_points_clean.groupby("veg")["NDMI"].transform(lambda x: x.fillna(x.mean()))
sample_points_clean.NDVI = sample_points_clean.groupby("veg")["NDVI"].transform(lambda x: x.fillna(x.mean()))
sample_points_clean.aspect.fillna(-1, inplace=True)
sample_points_clean.dropna(inplace = True)

foxes_all_clean.NDMI = foxes_all_clean.groupby("veg")["NDMI"].transform(lambda x: x.fillna(x.mean()))
foxes_all_clean.NDVI = foxes_all_clean.groupby("veg")["NDVI"].transform(lambda x: x.fillna(x.mean()))
foxes_all_clean.aspect.fillna(-1, inplace=True)
foxes_all_clean.dropna(inplace = True)

foxes_resamp_clean.NDMI = foxes_resamp_clean.groupby("veg")["NDMI"].transform(lambda x: x.fillna(x.mean()))
foxes_resamp_clean.NDVI = foxes_resamp_clean.groupby("veg")["NDVI"].transform(lambda x: x.fillna(x.mean()))
foxes_resamp_clean.aspect.fillna(-1, inplace=True)
foxes_resamp_clean.dropna(inplace = True)

#drop duplicates
foxes_all_clean.sort_values(["id", "t_"], inplace=True)
foxes_all_clean = foxes_all_clean.drop_duplicates()

foxes_resamp_clean.sort_values(["id", "t_"], inplace=True)
foxes_resamp_clean = foxes_resamp_clean.drop_duplicates()

#create timestamps & transform date column
foxes_all_clean.reset_index(drop = True)
foxes_all_clean["timestamp"] = foxes_all_clean["t_"].apply(lambda x: dt.datetime.timestamp(x))
foxes_all_clean["t_"] = foxes_all_clean["t_"].dt.strftime("%Y-%m-%d-%H:%M:%S")

foxes_resamp_clean.reset_index(drop = True)
foxes_resamp_clean["timestamp"] = foxes_resamp_clean["t_"].apply(lambda x: dt.datetime.timestamp(x))
foxes_resamp_clean["t_"] = foxes_resamp_clean["t_"].dt.strftime("%Y-%m-%d-%H:%M:%S")

#change order or columns in foxes_resamp_clean
foxes_resamp_clean = foxes_resamp_clean[["x_", "y_", "t_", "id", "sex", "geometry", "NDVI", "NDMI", "soil", "veg", "slope", "aspect", "elev"]]

print("Almost there. Now the data is being saved to the files")

#save dataframes as shp-files
foxes_all_final = foxes_all_clean.copy()
foxes_all_final.to_file("../data/cleaned_shapefiles/foxes_all.shp")

foxes_resamp_final = foxes_resamp_clean.copy()
foxes_resamp_final.to_file("../data/cleaned_shapefiles/foxes_resamp.shp")

sample_points_clean.reset_index(drop = True)
sample_points_clean.to_file("data/cleaned_shapefiles/sample_points.shp")
print("Done. The cleaned data is now saved.")