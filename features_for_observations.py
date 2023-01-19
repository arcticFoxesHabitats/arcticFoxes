'''
Functions unsed in EDA_obseervsations.

Gathering addidtional information from the data and performing transformations
'''



from datetime import datetime, timedelta
from shapely.geometry import Point, Polygon, MultiPolygon
import numpy as np
import pandas as pd
import geopandas as gpd

''' 
Function to get an array of diffs in seconds between time stamps of subsequent rows of a DataFrame.

Input:
df: DataFrame containing column of time stamps
df_time_col: name of column with time stamps
id: identifier for which time steps are calculated

Returns:
Array of float, representing seconds passed since preceding entry in DataFrame.
NaN if there is no preceeding row for the same id
'''

def get_time_diffs(df, df_time_col = "t_", id = "id"):
    fmt = '%Y-%m-%d-%H:%M:%S'
    time_diff = []
    for i, _ in enumerate(df.t_):
        if i > 0 and df.iloc[i-1][id] == df.iloc[i][id] :
            time_1 = datetime.strptime(df.iloc[i-1][df_time_col], fmt)
            time_2 = datetime.strptime(df.iloc[i][df_time_col], fmt)
            time_diff.append((time_2 - time_1).total_seconds())
        else:
            time_diff.append(np.nan)
    return time_diff



''' 
Function to get an array of distance in seconds between coords of subsequent rows of a DataFrame.

Input:
df: DataFrame containing column of coords
df_time_col: name of column with coords
id: identifier for which coords are calculated

Returns:
Array of float, representing seconds passed since preceding entry in DataFrame.
NaN if there is no preceeding row for the same id
'''

def get_distance(df, x = "x_", y= "y_", id = "id"): 
  travel_distance = []
  for i, _ in enumerate(df.t_):
    if i > 0 and df[id].iloc[i-1] == df[id].iloc[i]:
      x_diff = df[x].iloc[i-1] - df[x].iloc[i]
      y_diff = df[y].iloc[i-1] - df[y].iloc[i]
      tot_diff = np.sqrt(np.square(x_diff) + np.square(y_diff) )
      travel_distance.append(int(tot_diff))
    else:
      travel_distance.append(np.nan)
  return travel_distance




''' 
Function to convert a shapely Polygon object into a GeoJson.
As GeoJson requires CRS4326, input will be transformed unless it also is in this format

Input:
poly: shapely Polygon object
in_crs: crs system of coords in poly

Returns:
GeoJson object representing poly
'''

def polygon_to_geojson(poly, in_crs = 3006):
    poly_coords = poly.boundary.coords.xy    
    s= pd.DataFrame( [Point(x,y) for x,y in zip( poly_coords[0], poly_coords[1])])
    s.columns = ["geometry"]
    gdf = gpd.GeoDataFrame(s, crs=in_crs)
    if in_crs != 4326:
        gdf = gdf.to_crs(epsg= 4326)
    geojson = {'type':'Polygon', 'coordinates':[]}
    f  = []
    for point in gdf.geometry:
        f.append([point.x, point.y])
    geojson['coordinates'].append(f)
    return geojson

#def dataframe_convert_coords(df, coord_in = 3006, coord_out = 4326):
 #   gdf = gpd.GeoDataFrame(df, crs=coord_in)
  #  return gdf.to_crs(epsg= coord_out)


''' 
Function to calculate the distance between a point, and the farthest point of a shapely Polygon

Input:
point: shapely Point object
point: shapely Polygon object

Returns:
distance between point and farthest point of poly
'''
def max_dist_point_poly(point, poly):
    max_dist = 0
    poly_coords = poly.boundary.coords.xy
    for point_poly in [Point(x,y) for x,y in zip( poly_coords[0], poly_coords[1])]:
        if point.distance(point_poly) > max_dist:
            max_dist = point.distance(point_poly)
    return max_dist


''' 
Function to turn a DataFrame with columns for coords and an timestamp into a GeoJson object
representing a trip in Kepler Gl

Input:
df: DataFrame
properties: List of properties to be associated with each trip
lat: name of the column with latitude coords
lon: name of the column with longitude coords
elev: name of the column with elevation above sea level
time: name of the column with time stamp
id: name of the column with id by which to group together for a

Returns:
distance between point and farthest point of poly
'''
def df_to_geojson_trip(df, properties, lat='geo_kepler_lat', lon='geo_kepler_lon', elev = 'elev', time = 'timestamp', id = 'id'):
    geojson = {'type':'FeatureCollection', 'features':[]}
    for fox_id in df[id].unique():
        i =0
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':{'type':'LineString',
                               'coordinates':[]}}
        for _, row in df.query('id == @fox_id').iterrows():        
       #     feature['geometry']['coordinates'].append([row[lon], row[lat], row[elev],  int(row[time])])
            feature['geometry']['coordinates'].append([row[lon], row[lat], row[elev], 1564184363 + 10 * i])# row[time]])
            i += 1
        for prop in properties:
            feature['properties'][prop] = row[prop]
        geojson['features'].append(feature)
    return geojson


''' 
Function to get an array of diffs in seconds between time stamps of subsequent rows of a DataFrame.

Input:
df: DataFrame containing column of time stamps
df_time_col: name of column with time stamps
id: identifier for which time steps are calculated

Returns:
Array of float, representing seconds passed since preceding entry in DataFrame.
NaN if there is no preceeding row for the same id
'''

def get_time_diffs(df, df_time_col = "t_", id = "id"):
    fmt = '%Y-%m-%d-%H:%M:%S'
    time_diff = []
    for i, _ in enumerate(df.t_):
        if i > 0 and df.iloc[i-1][id] == df.iloc[i][id] :
            time_1 = datetime.strptime(df.iloc[i-1][df_time_col], fmt)
            time_2 = datetime.strptime(df.iloc[i][df_time_col], fmt)
            time_diff.append((time_2 - time_1).total_seconds())
        else:
            time_diff.append(np.nan)
    return time_diff



''' 
Function to get an array of distance in seconds between coords of subsequent rows of a DataFrame.

Input:
df: DataFrame containing column of coords
df_time_col: name of column with coords
id: identifier for which coords are calculated

Returns:
Array of float, representing seconds passed since preceding entry in DataFrame.
NaN if there is no preceeding row for the same id
'''

def get_distance(df, x = "x_", y= "y_", id = "id"): 
  travel_distance = []
  for i, _ in enumerate(df.t_):
    if i > 0 and df[id].iloc[i-1] == df[id].iloc[i]:
      x_diff = df[x].iloc[i-1] - df[x].iloc[i]
      y_diff = df[y].iloc[i-1] - df[y].iloc[i]
      tot_diff = np.sqrt(np.square(x_diff) + np.square(y_diff) )
      travel_distance.append(int(tot_diff))
    else:
      travel_distance.append(np.nan)
  return travel_distance

''' 
Function to convert a shapely Polygon object into a GeoJson.
As GeoJson requires CRS4326, input will be transformed unless it also is in this format

Input:
poly: shapely Polygon object
in_crs: crs system of coords in poly

Returns:
GeoJson object representing poly
'''

def polygon_to_geojson(poly, in_crs = 3006):
    poly_coords = poly.boundary.coords.xy    
    s= pd.DataFrame( [Point(x,y) for x,y in zip( poly_coords[0], poly_coords[1])])
    s.columns = ["geometry"]
    gdf = gpd.GeoDataFrame(s, crs=in_crs)
    if in_crs != 4326:
        gdf = gdf.to_crs(epsg= 4326)
    geojson = {'type':'Polygon', 'coordinates':[]}
    f  = []
    for point in gdf.geometry:
        f.append([point.x, point.y])
    geojson['coordinates'].append(f)
    return geojson

#def dataframe_convert_coords(df, coord_in = 3006, coord_out = 4326):
 #   gdf = gpd.GeoDataFrame(df, crs=coord_in)
  #  return gdf.to_crs(epsg= coord_out)


''' 
Function to calculate the distance between a point, and the farthest point of a shapely Polygon

Input:
point: shapely Point object
point: shapely Polygon object

Returns:
distance between point and farthest point of poly
'''
def max_dist_point_poly(point, poly):
    max_dist = 0
    poly_coords = poly.boundary.coords.xy
    for point_poly in [Point(x,y) for x,y in zip( poly_coords[0], poly_coords[1])]:
        if point.distance(point_poly) > max_dist:
            max_dist = point.distance(point_poly)
    return max_dist


''' 
Function to turn a DataFrame with columns for coords and an timestamp into a GeoJson object
representing a trip in Kepler Gl

Input:
df: DataFrame
properties: List of properties to be associated with each trip
lat: name of the column with latitude coords
lon: name of the column with longitude coords
elev: name of the column with elevation above sea level
time: name of the column with time stamp (if it is an empty string, timestamps will be invented)
id: name of the column with id by which to group together for a trip

Returns:
distance between point and farthest point of poly
'''
def df_to_geojson_trip(df, properties, lat='geo_kepler_lat', lon='geo_kepler_lon', elev = 'elev', time = 'timestamp', id = 'id'):
    geojson = {'type':'FeatureCollection', 'features':[]}
    for fox_id in df[id].unique():
        i =0
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':{'type':'LineString',
                               'coordinates':[]}}
        for _, row in df.query('id == @fox_id').iterrows():        
            if time == "":
                feature['geometry']['coordinates'].append([row[lon], row[lat], row[elev], 1564184363 + 10 * i])
            else:
                feature['geometry']['coordinates'].append([row[lon], row[lat], row[elev],  int(row[time])])
            
            i += 1
        for prop in properties:
            feature['properties'][prop] = row[prop]
        geojson['features'].append(feature)
    return geojson

