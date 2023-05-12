import geopandas as gpd
from shapely.geometry import MultiLineString, LineString
from pyproj import CRS

from unit_conversions import *

def line_length_in_miles(shapefile_path):
    '''Calculate the total length of all lines in a shapefile, in miles'''''
    # Read the shapefile into a GeoDataFrame
    gdf = gpd.read_file(shapefile_path)

    total_length = 0

    # If the CRS is geographic (i.e., in degrees), reproject each feature to its UTM zone
    if gdf.crs.is_geographic:
        # Determine the UTM zone for each feature
        gdf['utm_zone'] = gdf['geometry'].centroid.to_crs('EPSG:4326').map(lambda coord: 
                    int((coord.x + 180) / 6) + 1).astype(int)

        # For each UTM zone present in the data
        for zone in gdf['utm_zone'].unique():
            # Create a subset of the data in this UTM zone
            gdf_zone = gdf[gdf['utm_zone'] == zone]
            
            # Reproject to the appropriate UTM zone
            gdf_zone = gdf_zone.to_crs(f'EPSG:326{str(zone).zfill(2)}')

            # Iterate over the rows in the GeoDataFrame
            for index, row in gdf_zone.iterrows():
                geometry = row['geometry']

                # If it's a LineString, just add the length
                if isinstance(geometry, LineString):
                    total_length += geometry.length

                # If it's a MultiLineString, iterate over each part and add the length
                elif isinstance(geometry, MultiLineString):
                    for line in geometry:
                        total_length += line.length

                else:
                    print(f"Unsupported geometry type at index {index}")
                    exit()
    else:
        # Iterate over the rows in the GeoDataFrame
        for index, row in gdf.iterrows():
            geometry = row['geometry']

            # If it's a LineString, just add the length
            if isinstance(geometry, LineString):
                total_length += geometry.length

            # If it's a MultiLineString, iterate over each part and add the length
            elif isinstance(geometry, MultiLineString):
                for line in geometry:
                    total_length += line.length

            else:
                print(f"Unsupported geometry type at index {index}")
                exit()

    # Get the units of the CRS
    units = CRS(gdf.crs).axis_info[0].unit_name

    if units == 'metre':
        total_length = meters_to_international_feet(total_length)
        units = 'ft'
    elif units == 'US survey foot':
        units = 'ft'
    elif units == 'foot':
        total_length = total_length * 0.999998 # convert from international feet to US survey feet
        units = 'ft'
    elif units == 'degree': # if the CRS is originally geographic, the program converts it on the fly to UTM
        total_length = meters_to_international_feet(total_length)
    else:
        print("The input shapefile is in an unsupported CRS. Exiting...")
        exit()

    #convert to miles and display
    total_length = round(total_length / 5280, 3)
    print("Input shapefile's total length is: " + str(total_length) + " miles")

    return total_length