import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point

plt.rcParams['font.family'] = 'Times New Roman'

# Read the shapefile
gdf = gpd.read_file('Sheffield_Wards_(Open_Data).shp')

gdf2 = gpd.read_file('Primary_Gritting_Routes_.shp')

# Reproject the shapefile to WGS84 (the coordinate system used by latitudes and longitudes)
gdf = gdf.to_crs(epsg=4326)  # EPSG 4326 is the code for WGS84
gdf2 = gdf2.to_crs(epsg=4326)

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

young_casualties = casualty_data[
    (casualty_data['age_band_of_casualty'] == "16 - 20") |
    (casualty_data['age_band_of_casualty'] == "21 - 25")
]

# Step 2: Create a GeoDataFrame from the CSV data with Point geometries
casualty_geo = gpd.GeoDataFrame(young_casualties,
                                geometry=gpd.points_from_xy(young_casualties.longitude, young_casualties.latitude),
                                crs='EPSG:4326')

casualties_with_wards = gpd.sjoin(casualty_geo, gdf, how='inner', predicate='within')

# Step 4: Group and count casualties for each ward
ward_casualty_counts = casualties_with_wards['objectid'].value_counts().reset_index()
ward_casualty_counts.columns = ['ward_name', 'casualty_count']


# Sort ward_casualty_counts by 'casualty_count' in descending order
ward_casualty_counts = ward_casualty_counts.sort_values(by='casualty_count', ascending=False)

# Reset index to ensure correct merging
ward_casualty_counts.reset_index(drop=True, inplace=True)

# Merge the counts with the ward GeoDataFrame using the 'objectid' as the key
gdf = gdf.merge(ward_casualty_counts, left_on='objectid', right_on='ward_name', how='left')

# Add a new column 'ward_number' with numbers in descending order starting from 1
gdf['ward_number'] = range(1, len(gdf) + 1)

print(gdf)

# Create the first choropleth map
fig, ax = plt.subplots(1, 1, figsize=(20, 12))
plot = gdf.plot(column='casualty_count', cmap='RdYlGn_r', edgecolor='black', linewidth=0.4, ax=ax, legend=True)

# Access the colorbar object
cbar = plot.get_figure().get_axes()[1]

# Set font size for colorbar labels
cbar.tick_params(labelsize=17)

# Add ward labels in bold
for idx, row in gdf.iterrows():
    ax.text(row.geometry.centroid.x, row.geometry.centroid.y, str(row['ward_number']), fontsize=17, color="black", weight='bold')

# Add a legend
ax.set_title('STATS19 2016-2022 Total Casualties by Ward Ages 16-25', fontsize=28)
ax.set_axis_off()

plt.savefig('casualty_map_high_dpi.png', dpi=400, bbox_inches='tight')

plt.show()
