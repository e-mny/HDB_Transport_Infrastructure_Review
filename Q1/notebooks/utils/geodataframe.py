from . import pd, folium, Polygon, gpd
from utils.helper import createColorMap, createIndexedDict

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
    return gdf


# Function to add GeoDataFrame to Folium map
def add_polygon_to_map(geo_df: gpd.GeoDataFrame, folium_map: folium.Map) -> folium.Map:
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
        
        
# Function to add GeoDataFrame to Folium map
def add_heatmap_to_map(geo_df: gpd.GeoDataFrame, folium_map: folium.Map) -> folium.Map:
    colormap = createColorMap(geo_df)
    colormap.add_to(folium_map)

    population_dict = createIndexedDict(geo_df)
    color_dict = {key: colormap(
        population_dict[key]) for key in population_dict.keys()}

    geo_json = folium.GeoJson(
        geo_df.to_json(),
        style_function=lambda feature: {
            "fillColor": color_dict[feature['properties']["Area"]],
            "color": "black",
            "weight": 1,
            "dashArray": "5, 5",
            "fillOpacity": 0.75,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["Area", "Count"],
            aliases=["Area: ", "Population: "],
            localize=True
        ),
    )

    geo_json.add_to(folium_map)
    return folium_map
