from shapely.geometry import mapping, Polygon
import geopandas as gpd
from . import pd, folium, Polygon, gpd
from utils.helper import createColorMap, createIndexedDict, convertZeroToNan
from area import area

# Function to create GeoDataFrame
def createAreaGeoDF() -> gpd.GeoDataFrame:
    # Read the CSV file into a DataFrame
    df = pd.read_csv('../data/All Regions_Coordinates.csv')

    # Group by the 'area' column
    grouped = df.groupby('Area')

    # Function to create a Polygon from a group of coordinates
    def create_polygon(group):
        coords = list(zip(group['Longitude'], group['Latitude']))
        return Polygon(coords)

    # Apply the function to each group and create a GeoDataFrame
    polygons = grouped.apply(create_polygon)

    # Convert the Series to a GeoDataFrame
    gdf = gpd.GeoDataFrame(polygons, columns=['geometry'])

    # Reset the index to have the 'area' column back
    gdf = gdf.reset_index()
    return gdf.set_crs(epsg=4326, inplace=True)


# Function to add GeoDataFrame to Folium map
def addPolygonToMap(geo_df: gpd.GeoDataFrame, folium_map: folium.Map) -> folium.Map:
    for _, row in geo_df.iterrows():
        sim_geo = gpd.GeoSeries(row['geometry']).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {
            'color': '#000000',
            "fillColor": "#ffffff",
            "fillOpacity": 0.2,
            "weight": '2'})
        folium.Popup(row['Area']).add_to(geo_j)
        geo_j.add_to(folium_map)
        
    return folium_map
        
        
# Function to add Population to Folium map
def addPopulationHeatmap(geo_df: gpd.GeoDataFrame, folium_map: folium.Map) -> folium.Map:
    colormap = createColorMap(
        geo_df['population_count'].min(), geo_df['population_count'].max(), caption = "Population Density")
    colormap.add_to(folium_map)

    population_dict = createIndexedDict(geo_df, 'population_count')
    color_dict = {key: colormap(
        population_dict[key]) for key in population_dict.keys()}

    geo_json = folium.GeoJson(
        geo_df.to_json(),
        style_function=lambda feature: {
            "fillColor": color_dict[feature['properties']["Area"]],
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 1 if int(feature['properties']['population_count']) > 0 else 0,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["Area", "population_count"],
            aliases=["Area: ", "Population: "],
            localize=True
        ),
    )

    geo_json.add_to(folium_map)
    return folium_map


# Function to add regions with number of PT stops to the map as a heatmap
def createRegionHeatMap(geo_df: gpd.GeoDataFrame, geo_map: folium.Map) -> folium.Map:
    colormap = createColorMap(
        geo_df['total_stops'].min(), geo_df['total_stops'].max(), caption = "PT Stops")
    colormap.add_to(geo_map)

    pt_stops_dict = createIndexedDict(geo_df, 'total_stops')
    color_dict = {key: colormap(
        pt_stops_dict[key]) for key in pt_stops_dict.keys()}

    # print(color_dict)
    # print(geo_df.to_json())   
    geo_json = folium.GeoJson(
        geo_df.to_json(),
        style_function=lambda feature: {
            "fillColor": color_dict[feature['properties']["Area"]],
            "color": "black" if feature['properties']['total_stops'] > 0 else 'none ',
            "weight": 0.5,
            "fillOpacity": 1 if feature['properties']['total_stops'] > 0 else 0,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["Area", "bus_stops_count", "train_stops_count"],
            aliases=["Area: ", "Bus Stops: ", "Train Stops: "],
            localize=True
        ),
    )

    geo_json.add_to(geo_map)
    return geo_map
    
    # geo_df['normalized_stops'] = convertZeroToNan(geo_df, 'normalized_stops')

    # folium.Choropleth(
    #     geo_data=geo_df.to_json(),
    #     name='choropleth',
    #     data=geo_df,
    #     columns=['Area', 'normalized_stops'],
    #     key_on='feature.properties.Area',
    #     fill_color='YlOrRd',
    #     fill_opacity=0.7,
    #     line_weight=1,
    #     line_opacity=0.2,
    #     nan_fill_color="white",
    #     nan_fill_opacity=0.7,
    #     legend_name='Relative Number of Stops per Region',
    #     highlight=True
    # ).add_to(geo_map)

    # return geo_map


# Function to add Population to Folium map
def addDensityHeatmap(geo_df: gpd.GeoDataFrame, folium_map: folium.Map, pt_type: str) -> folium.Map:
    colormap = createColorMap(
        geo_df[f'normalized_{pt_type}_density_discrepancy'].min(), geo_df[f'normalized_{pt_type}_density_discrepancy'].max(), caption=f"Normalized {pt_type.capitalize()} Density Discrepancy")
    colormap.add_to(folium_map)

    density_dict = createIndexedDict(geo_df, f'normalized_{pt_type}_density_discrepancy')
    color_dict = {key: colormap(
        density_dict[key]) for key in density_dict.keys()}

    geo_json = folium.GeoJson(
        geo_df.to_json(),
        style_function=lambda feature: {
            "fillColor": color_dict[feature['properties']["Area"]],
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 1,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["Area", f"normalized_{pt_type}_density_discrepancy"],
            aliases=["Area: ", "Density: "],
            localize=True
        ),
    )

    geo_json.add_to(folium_map)
    return folium_map

# Add the regions to the map with stop counts
def addRegionswithPT(geo_df: gpd.GeoDataFrame, folium_map: folium.Map) -> folium.Map:
    for _, row in geo_df.iterrows():
        sim_geo = gpd.GeoSeries(row['geometry']).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j)
        popup_text = f"Region: {row['Area']}<br>Bus Stops: {row['bus_stops_count']}<br>Train Stops: {row['train_stops_count']}"
        folium.Popup(popup_text).add_to(geo_j)
        geo_j.add_to(folium_map)

    return folium_map

# Process the dataframe to determine the total number of public transport stops in an area
def cleanRegionPTDF(geo_df: gpd.GeoDataFrame, bus_stops_df: gpd.GeoDataFrame, train_stops_df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    # Merge the counts with the regions GeoDataFrame
    regionPT_df = geo_df.merge(bus_stops_df, on='Area', how='left').merge(
        train_stops_df, on='Area', how='left')
    regionPT_df['bus_stops_count'] = regionPT_df['bus_stops_count'].fillna(
        0).astype(int)
    regionPT_df['train_stops_count'] = regionPT_df['train_stops_count'].fillna(
        0).astype(int)

    # Calculate the total number of stops per region
    regionPT_df['total_stops'] = regionPT_df['bus_stops_count'] + \
        regionPT_df['train_stops_count']

    # Normalize the total stops for heatmap
    max_stops = regionPT_df['total_stops'].max()
    regionPT_df['normalized_stops'] = regionPT_df['total_stops'] / max_stops

    return regionPT_df

# Get Land Area based on Geometry column in dataframe
def getLandArea(geo_df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    def calculate_area(geometry):
        # Convert geometry to GeoJSON format
        geojson = mapping(geometry)
        # Calculate the area in square meters
        area_m2 = area(geojson)
        # Convert to square kilometers
        return area_m2 / 1e6

    # Apply the transformation and area calculation to each geometry in the GeoDataFrame
    geo_df['land_area-km2'] = geo_df['geometry'].apply(calculate_area)

    return geo_df
