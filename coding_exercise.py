"""
CSI Coding Exercise script

# This script finds the nearest tall building to each random 
# point specified in gberardinelli's github project.

# This project is written in Python 3, and requires an up-to-date
# installation of geopandas, pandas, and shapely.
"""

"""
# optional set your working directory
# path = "C:/Users/ADD_YOUR_USER_NAME/PycharmProjects/CSI_Coding_Exercise/"; os.chdir(path)
"""

# import needed packages
import geopandas as gpd
import pandas as pd
from shapely.ops import nearest_points
import os


# list the url of the buildings and points csv files.
url_b = 'https://gist.githubusercontent.com/gberardinelli/8567cdbcad220e46b2f8fc4e33a203a0/raw/e9d27e14fbbde4b28a6c09d077b43537310a5b0b/buildings.csv'
url_q = 'https://gist.githubusercontent.com/gberardinelli/8567cdbcad220e46b2f8fc4e33a203a0/raw/e9d27e14fbbde4b28a6c09d077b43537310a5b0b/queries.csv'

# read in the csv files as pandas data frames
buildings = pd.read_csv(url_b, error_bad_lines=False)
points = pd.read_csv(url_q, error_bad_lines=False)

# this function creates Geopandas Geodataframe
# with which you can run spatial operations
def create_gdf(df, x="X", y="Y"):
    return gpd.GeoDataFrame(df,
                            geometry=gpd.points_from_xy(df[y], df[x]),
                            crs={"init": "EPSG:2991"})

# make your Geodataframes
buildings_gdf = create_gdf(buildings)
points_gdf = create_gdf(points)

# Find the nearest building neighbor of each random point
# for more information look at:
# https://shapely.readthedocs.io/en/latest/manual.html
def calculate_nearest(row, destination, val, col="geometry"):
    # create unary union
    dest_unary = destination["geometry"].unary_union
    # find closest point
    nearest_geom = nearest_points(row[col], dest_unary)
    # Find the corresponding geom
    match_geom = destination.loc[destination.geometry
                == nearest_geom[1]]
    # get the corresponding value
    match_value = match_geom[val].to_numpy()[0]
    return match_value

# Use an apply function to add information about the
# neighboring towers to the points_gdf.

# Add the nearest building name
points_gdf["nearest"] = points_gdf.apply(calculate_nearest,
                                                  destination=buildings_gdf,
                                                  val="Name", axis=1)
# add rank
points_gdf["rank"] = points_gdf.apply(calculate_nearest,
                                                  destination=buildings_gdf,
                                                  val="Rank", axis=1)
# add elevation
points_gdf["elev"] = points_gdf.apply(calculate_nearest,
                                                  destination=buildings_gdf,
                                                  val="Elevation", axis=1)
# add height
points_gdf["height"] = points_gdf.apply(calculate_nearest,
                                                  destination=buildings_gdf,
                                                  val="Height", axis=1)
# add number of floors
points_gdf["floors"] = points_gdf.apply(calculate_nearest,
                                                  destination=buildings_gdf,
                                                  val="Floors", axis=1)

####### the output ########

print("The nearest tower to each random point is")
print(pd.concat([points_gdf["Name"], points_gdf["nearest"]], axis=1))

# create output files
buildings_gdf.to_file(driver='ESRI Shapefile', filename='buildings.shp')
points_gdf.to_file(driver='ESRI Shapefile', filename='random_neighbors.shp')

# print the locations of outputs
print(os.getcwd()+"\\random_neighbors.shp created. \n This contains information about \n the nearest building in the attribute table.")
print(os.getcwd()+"\\buildings.shp created. \n This contains the 30 tallest buildings in Portland.")