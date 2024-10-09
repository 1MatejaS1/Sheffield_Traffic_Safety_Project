import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point

# Read the shapefile for Sheffield wards
wards_gdf = gpd.read_file('Sheffield_Wards_(Open_Data).shp')

# Reproject the shapefile to WGS84 (the coordinate system used by latitudes and longitudes)
wards_gdf = wards_gdf.to_crs(epsg=4326)  # EPSG 4326 is the code for WGS84

# Step 1: Read the CSV file containing casualty data
casualty_data = pd.read_csv('Combined_data_improved.csv')

# Step 2: Create a GeoDataFrame from the CSV data with Point geometries
geometry = [Point(xy) for xy in zip(casualty_data['longitude'], casualty_data['latitude'])]
crs = {'init': 'epsg:4326'}  # Coordinate Reference System (CRS) for lat/lon
casualty_geo = gpd.GeoDataFrame(casualty_data, crs=crs, geometry=geometry)

# Step 3: Perform a spatial join to assign wards to each casualty
casualties_with_wards = gpd.sjoin(casualty_geo, wards_gdf, how='left', op='within')

# Step 4: Group and count casualties for each ward and year
ward_casualty_counts = casualties_with_wards.groupby(['admin_name', 'accident_year']).size().unstack(fill_value=0)

# Display the resulting DataFrame
print(ward_casualty_counts)

