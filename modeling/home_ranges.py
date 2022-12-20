import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as geopd
import seaborn as sns

from scipy.spatial import ConvexHull

import pyreadr


def hr_mean(xy, n_drop):
    '''
    Function to calculate the homerange using the arithmetic mean of all points.
    
    Input:
    xy: Series with the positional data
    n_drop: amount of positions that should be removed

    To remove the positions, the mean of all positions is calculated. 
    The positions with the biggest distance to this mean are deleted.
    
    Returns:
    Array with the reduced amount of positions.
    '''
    #sort points by distance to mean
    ind_list = np.linalg.norm(xy - np.mean(xy, axis = 0, keepdims=True), axis = 1).argsort()
    xy_sorted = xy[ind_list, :]

    #drop last n-drop values, calculate hull
    xy_hr = xy_sorted[:-n_drop,...]
    hull = ConvexHull(xy_hr)
    
    return xy_hr

def hr_min_volume(xy, n_drop):
    '''
    Function to calculate the homerange using the minimum volume.

    Input: 
    xy: Series with the positional data 
    n_drop: amount of positions that should be removed.

    The total amount of positions is reduced in a way such 
    that the volume of the ConvexHull is as small as possible.
    
    Returns:
    Array with the reduced amount of positions.
    '''
    #loop for every row that will be dropped:
    for k in range(n_drop):
        #create lists
        vol = []
        index = []
        #get points that make up the ConvexHull and store them in points
        #these are the points that could be dropped to reduce the volume
        hull = ConvexHull(xy)
        points = hull.vertices
        #loop over points: drop each one and store both the resulting volume and the index of the point in a list
        for i in points:
            xy_drop = np.delete(xy, i, 0)
            hull = ConvexHull(xy_drop)
            vol.append(hull.volume)
            index.append(i)
        #find the smallest volume and the corresponding index
        smallest = min(vol)
        index_smallest = vol.index(smallest)
        del_index = index[index_smallest]
        #drop the row with this index from the array
        xy = np.delete(xy,del_index,0)
    return xy

def hr_proportion(data, proportion = 0.95):
    '''
    Main function to calculate the homerange.

    Input: 
    data: Dataframe where the x- and y- values of the position are stored
    in the first two columns
    proportion: proportion of positions that should be used for the homerange.

    The function calls the two functions homerange_plot_mean to calculate
    the proportion of points that are then used in the homerange calculation.
    
    Returns: 
    xy: Array with two columns: 0: x values, 1: y values. Includes all points
    xy_proportion: Array with two columns: 0: x values, 1: y values. Includes
    only the specified proportion of points
    '''
    #create array out of input data
    xy = np.array(data.iloc[:,0:2].to_numpy())
    #estimate how many rows need to be dropped
    n_drop = int(np.ceil(xy.shape[0]*(1-proportion)))

    #distribute n_drop between the two functions
    if (proportion < 0.97):
        n_drop_min_volume = int(np.ceil(xy.shape[0]*0.03))
    else:
        n_drop_min_volume = n_drop-1
    n_drop_mean = n_drop - n_drop_min_volume

    # use homerange_plot_min_volume and homerange_plot_mean to build
    # the data frame including only the points used to build the 
    # home range
    xy_new = hr_min_volume(xy, n_drop_min_volume)
    xy_proportion = hr_mean(xy_new, n_drop_mean)

    return xy, xy_proportion

def hr_plot(data, proportion = 0.95):
    '''
    Function to plot the home ranges. 
    
    Input:
    data: should include an x and y column at first and second place
    proportion: the proportion of points that should be used to build
    the home ranges

    Uses the homerange_proportion() function to create new array only
    including the proportion of points of the input data frame that was
    specified. It then calculates the hull and plots it.

    Returns:
    hull object
    '''
    # get the data into the needed format for the plot
    # xy: Array with all data points with x as column 0 and y as column 1
    # xy_new: array only including the set proportion of x and y coordinates
    xy, xy_new = hr_proportion(data, proportion)

    # creating the hull from the set proportion of data points
    hull = ConvexHull(xy_new)

    # creating the plot
    f, ax = plt.subplots()
    # first, all data points are plotted
    ax.plot(xy[:,0], xy[:,1], 'o')
    # next, the hull is plotted
    for simplex in hull.simplices:
        ax.plot(xy_new[simplex, 0], xy_new[simplex, 1], 'k-')
    # and last the axis are set to invisible to preserve the secrecy of
    # the gps coordinates
    ax.axes.get_xaxis().set_visible(False)
    ax.axes.get_yaxis().set_visible(False)
    plt.show()


def hr_geometry_df(data, proportion = 0.95):
    '''
    Function to build a data frame including the geometry out of the 
    output of homerange_proportion(). 
    
    Input:
    data: dataframe where the x- and y- values of the position are stored
    in the first two columns
    proportion: proportion of positions that should be used for the homerange.

    The function calls the homerange_proportion function and uses the return 
    to build the convex hull of the data points. 

    Returns:
    xy_df: data frame including the point geometry and the id of the input data
    '''

    # get the data into the needed format for the plot
    # xy: Array with all data points with x as column 0 and y as column 1
    # we do not need this here, but hr_proportion gives out 2 variables, 
    # so we have to define two
    # xy_new: array only including the set proportion of x and y coordinates
    xy, xy_new = hr_proportion(data, proportion)
    hull = ConvexHull(xy_new)

    # building the geo data frame later used for analysis
    xy_df = geopd.GeoDataFrame(xy_new, geometry=geopd.points_from_xy(xy_new[:,0], xy_new[:,1]), columns = ["x", "y"])
    # adding the id again
    xy_df["id"] = data["id"][data["id"].first_valid_index()]
    # adding the area of the hull
    xy_df["area"] = hull.volume
    # dropping the x and y coordinate columns, as we already have them in the
    # original data frame, with which we will merge this data frame later
    xy_df = xy_df.drop(["x","y"], axis = 1)

    return xy_df

def hr_area(data, proportion = 0.95):
    '''
    Main function to calculate the polygons of the home ranges.

    Input: 
    data: dataframe where the x- and y- values of the position are stored
    in the first two columns
    proportion: proportion of positions that should be used for the homerange.
    proportion of positions that should be used for the homerange.

    The function calls the homerange_proportion function.

    Returns:
    xy_geometry: convex hull of the input geometry
    '''
    # xy_new: data frame only including the set proportion of x and y coordinates
    # includes id of the foxes, area of the home range and geometry of the points

    xy_new = hr_geometry_df(data, proportion)

    xy_geometry = xy_new.unary_union.convex_hull

    return xy_geometry