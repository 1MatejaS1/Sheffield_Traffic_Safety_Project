import geopandas as gpd
import os
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams['font.family'] = 'Times New Roman'

# Directory containing the shapefiles
shapefile_dir = r'C:\Users\matej\Desktop\Shapefile plotting\Ward_Road_Shapefiles'

# Directory to save the plots
output_folder = r'C:\Users\matej\Desktop\Plots'

# Check if the output folder exists, if not, create it
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Read the city ward boundaries shapefile
gdf = gpd.read_file('Sheffield_Wards_(Open_Data).shp')
gdf = gdf.to_crs(epsg=4326)

# Read the casualty data
data = pd.read_csv('combined_data(2).csv')

# Filter data for each type of casualty
casualty_data = data[(~data['casualty_type'].isin(['Cyclist', 'Pedestrian']))]
cyclist_data = data[data['casualty_type'] == "Cyclist"]
pedestrian_data = data[data['casualty_type'] == "Pedestrian"]

# Convert latitude/longitude to GeoDataFrame for each dataset
geometry_casualty = gpd.points_from_xy(casualty_data['longitude'], casualty_data['latitude'])
casualty_gdf = gpd.GeoDataFrame(casualty_data, geometry=geometry_casualty, crs='EPSG:4326')

geometry_cyclist = gpd.points_from_xy(cyclist_data['longitude'], cyclist_data['latitude'])
cyclist_gdf = gpd.GeoDataFrame(cyclist_data, geometry=geometry_cyclist, crs='EPSG:4326')

geometry_pedestrian = gpd.points_from_xy(pedestrian_data['longitude'], pedestrian_data['latitude'])
pedestrian_gdf = gpd.GeoDataFrame(pedestrian_data, geometry=geometry_pedestrian, crs='EPSG:4326')

# Initialise an empty GeoDataFrame to store all road segments
all_road_segments_casualties = gpd.GeoDataFrame()
all_road_segments_cyclist = gpd.GeoDataFrame()
all_road_segments_pedestrian = gpd.GeoDataFrame()

# Iterate over each ward
for index, row in gdf.iterrows():
    ward_name = row['admin_name']
    
    # Get the path for the specific shapefile of road segments
    specific_shapefile = os.path.join(shapefile_dir, f'{ward_name}_road_segments.shp')

    # Read the specific shapefile and ensure a consistent CRS
    gdf_road_segments = gpd.read_file(specific_shapefile).to_crs('EPSG:4326')
    
    # Define buffer size for each ward (you can adjust this based on your requirements)
    buffer_size = 0.0008  # Adjust this value based on your data
    
    # Create a buffer around the road segments for this ward
    buffered_segments = gdf_road_segments.geometry.buffer(buffer_size)
    
    # Plot road segments with colors based on casualties count for this ward
    casualties_within_buffer_casualties = gpd.sjoin(casualty_gdf, gdf_road_segments.assign(geometry=buffered_segments), predicate='within')
    casualties_per_segment_casualties = casualties_within_buffer_casualties.groupby('index_right').size()
    gdf_road_segments['casualties_count_casualties'] = gdf_road_segments.index.map(lambda x: casualties_per_segment_casualties.get(x, 0))
    all_road_segments_casualties = pd.concat([all_road_segments_casualties, gdf_road_segments])

    casualties_within_buffer_cyclist = gpd.sjoin(cyclist_gdf, gdf_road_segments.assign(geometry=buffered_segments), predicate='within')
    casualties_per_segment_cyclist = casualties_within_buffer_cyclist.groupby('index_right').size()
    gdf_road_segments['casualties_count_cyclist'] = gdf_road_segments.index.map(lambda x: casualties_per_segment_cyclist.get(x, 0))
    all_road_segments_cyclist = pd.concat([all_road_segments_cyclist, gdf_road_segments])

    casualties_within_buffer_pedestrian = gpd.sjoin(pedestrian_gdf, gdf_road_segments.assign(geometry=buffered_segments), predicate='within')
    casualties_per_segment_pedestrian = casualties_within_buffer_pedestrian.groupby('index_right').size()
    gdf_road_segments['casualties_count_pedestrian'] = gdf_road_segments.index.map(lambda x: casualties_per_segment_pedestrian.get(x, 0))
    all_road_segments_pedestrian = pd.concat([all_road_segments_pedestrian, gdf_road_segments])



# Plot the combined road segments with colors based on casualty intensity for each dataset
fig, axs = plt.subplots(1, 3, figsize=(25, 10), gridspec_kw={'width_ratios': [1, 1, 1.09]})  # Create a figure with 3 subplots

import matplotlib.colors as mcolors

# Plot wards on all subplots
for ax in axs:
    gdf.plot(ax=ax, color='gray', alpha=0.67, edgecolor='white', linewidth=0.3)

# Plot road segments with casualty intensity for each type of casualty
casualties_plot = all_road_segments_casualties.plot(column='casualties_count_casualties', cmap='RdYlGn_r', linewidth=1.2, legend=False, ax=axs[0])
cyclist_plot = all_road_segments_cyclist.plot(column='casualties_count_cyclist', cmap='RdYlGn_r', linewidth=1.2, legend=False, ax=axs[1])
pedestrian_plot = all_road_segments_pedestrian.plot(column='casualties_count_pedestrian', cmap='RdYlGn_r', linewidth=1.2, legend=False, ax=axs[2])


# Set titles and labels
axs[0].set_title('Vehicle Casualty Intensity Performance', fontsize=23)
axs[0].set_xlabel('Longitude', fontsize=18)
axs[0].set_ylabel('Latitude', fontsize=18)
axs[1].set_title('Cyclist Casualty Intensity Performance', fontsize=23)
axs[1].set_xlabel('Longitude', fontsize=18)
axs[2].set_title('Pedestrian Casualty Intensity Performance', fontsize=23)
axs[2].set_xlabel('Longitude', fontsize=18)

# Increase size of x-axis and y-axis numbers
for ax in axs:
    ax.tick_params(axis='x', labelsize=15)
    ax.tick_params(axis='y', labelsize=15)

# Create a custom color bar legend
cmap = plt.cm.RdYlGn_r
norm = mcolors.Normalize(vmin=0, vmax=1)  # adjust the vmin and vmax as needed
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])  # fake up the array
cbar = plt.colorbar(sm, ax=axs[2], aspect=10, fraction=0.0645, pad=0.02, orientation='vertical')
cbar.ax.tick_params(labelsize=18)
cbar.set_label('Performance index', fontsize=18)

# Only show ticks at the low and high ends
cbar.set_ticks([0, 1])
cbar.set_ticklabels(['Good', 'Poor'])

plt.tight_layout()

# Save the figure with high DPI
plt.savefig(os.path.join(output_folder, 'casualty_comparison.png'), dpi=600)  # Adjust DPI as needed

# Show the plot
plt.show()
