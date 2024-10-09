import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point

population_data = pd.DataFrame([
    ['0', 2108], ['1', 2412], ['2', 284], ['3', 1495], ['4', 1684], ['5', 1419], ['6', 3309], ['7', 3700],
    ['8', 3299], ['9', 4277], ['10', 2437], ['11', 2943], ['12', 1093], ['13', 2711], ['14', 185],
    ['15', 3959], ['16', 7423], ['17', 4229], ['18', 4504], ['19', 5918], ['20', 5008], ['21', 4142],
    ['22', 6942], ['23', 5984], ['24', 4655], ['25', 4358], ['26', 2585], ['27', 518]
], columns=['ward_name', 'population'])

# Read the shapefile
gdf = gpd.read_file('Sheffield_Wards_(Open_Data).shp')

# Reproject the shapefile to WGS84 (the coordinate system used by latitudes and longitudes)
gdf = gdf.to_crs(epsg=4326)  # EPSG 4326 is the code for WGS84

# Create a dictionary to store coordinates for each ward
ward_coordinates = {}

for ward_name, geometry in zip(gdf['objectid'], gdf['geometry']):
    if geometry.geom_type == 'Polygon':
        # For Polygon geometries
        coords = list(geometry.exterior.coords)
        ward_coordinates[ward_name] = coords
    elif geometry.geom_type == 'MultiPolygon':
        # For MultiPolygon geometries
        ward_coords = []
        for polygon in geometry:
            coords = list(polygon.exterior.coords)
            ward_coords.append(coords)
        ward_coordinates[ward_name] = ward_coords

# Load the Sheffield ward boundaries shapefile
gdf = gpd.read_file('Sheffield_Wards_(Open_Data).shp')
gdf = gdf.to_crs(epsg=4326)

# Step 1: Read the CSV file containing casualty data
casualty_data = pd.read_csv('combined_data(2).csv')

# Step 2: Create a GeoDataFrame from the CSV data with Point geometries
casualty_geo = gpd.GeoDataFrame(casualty_data, 
                                geometry=gpd.points_from_xy(casualty_data.longitude, casualty_data.latitude),
                                crs='EPSG:4326')

casualties_with_wards = gpd.sjoin(casualty_geo, gdf, how='inner', predicate='within')

# Step 4: Group and count casualties for each ward
ward_casualty_counts = casualties_with_wards['objectid'].value_counts().reset_index()
ward_casualty_counts.columns = ['ward_name', 'casualty_count']

# Now, the ward_casualty_counts DataFrame contains the count of casualties for each ward.
print(ward_casualty_counts)

# Merge the counts with the ward GeoDataFrame using the 'objectid' as the key
gdf = gdf.merge(ward_casualty_counts, left_on='objectid', right_on='ward_name', how='left')

print(gdf)

# Calculate casualties per population ratio
gdf['casualty_per_population'] = gdf['casualty_count'] / population_data['population']/8*100

# Create the choropleth map with normalized data
fig, ax = plt.subplots(1, 1, figsize=(12, 8))
gdf.plot(column='casualty_per_population', cmap='RdYlGn_r', linewidth=0.8, ax=ax, legend=True)

# Add a legend
ax.set_title('Casualties normalised to population density (yearly average per 100 people)')
ax.set_axis_off()

plt.show()


