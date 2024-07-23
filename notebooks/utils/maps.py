from utils.constants import TRAIN_COLOURS
from . import pd, folium, gpd
from folium.plugins import FastMarkerCluster

# Function to create Singapore map
def createSingaporeMap() -> folium.Map:
    return folium.Map(
        location=[1.3521, 103.8198],
        zoom_start=11.45,
        max_bounds=True
    )

# Add bus stop markers
def addBusStopMarkers(df: pd.DataFrame, geo_map: folium.Map) -> folium.Map:

    bus_stops_layer = folium.FeatureGroup(name='Bus Stops', show=False)
    for index, point in df.iterrows():
        folium.Marker(
            location=[point['Latitude'], point['Longitude']],
            tooltip=point['Description'],
            icon=folium.Icon(
                color='purple',
                icon="bus",
                prefix="fa")
        ).add_to(bus_stops_layer)
    bus_stops_layer.add_to(geo_map)

    return geo_map

# Add bus stop clusters within its region
def addBusStopClusters(df: pd.DataFrame, geo_map: folium.Map, regions_gdf: gpd.GeoDataFrame) -> folium.Map:
    
    bus_stops_layer = folium.FeatureGroup(name='Bus Stops Clusters', show=False)

    # Convert DataFrame to GeoDataFrame
    gdf_bus_stops = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.Longitude, df.Latitude),
        crs="EPSG:4326"
    )

    # Perform spatial join to associate each bus stop with its region
    bus_stops_in_area = gpd.sjoin(gdf_bus_stops, regions_gdf, how='inner')

    # Group bus stops by region
    grouped = bus_stops_in_area.groupby('Area')

    # Create clusters for each region and add them to the map
    for area, group in grouped:
        lat_long_pairs = list(zip(group.geometry.y, group.geometry.x))
        cluster = FastMarkerCluster(
            data=lat_long_pairs, name=f"Bus Stops in {area}")
        cluster.add_to(bus_stops_layer)

    bus_stops_layer.add_to(geo_map)

    return geo_map

# Add train station lines
def addTrainLines(df: pd.DataFrame, geo_map: folium.Map) -> folium.Map:
    for code, colour in TRAIN_COLOURS.items():
        filtered_gdf = df[df['LINE'].str.contains(code)]
        coordinates = [[point.y, point.x]
                       for point in filtered_gdf['COORDINATES']]
        folium.PolyLine(coordinates,
                        color=colour,
                        weight=3,
                        tooltip=f"{code}L").add_to(geo_map)

    return geo_map

# Add train station markers
def addTrainStopMarkers(df: pd.DataFrame, geo_map: folium.Map) -> folium.Map:
    """
    red, blue, green, purple, orange, darkred, lightred, beige, darkblue, darkgreen, cadetblue, darkpurple, white, pink, lightblue, lightgreen, gray, black, lightgray
    """
    
    TRAIN_ICON_COLOURS = {
        "NS": "red",
        "EW": "green",
        "CG": "green",
        "DT": "darkblue",
        "TE": "orange",
        "CC": "lightred",
        "CE": "lightred",
        "NE": "purple",
        "BP": "gray",
        "SW": "gray",
        "SE": "gray",
        "PW": "gray",
        "PE": "gray",
        "PTC": "gray",
        "STC": "gray"
    }
    
    train_stops_layer = folium.FeatureGroup(name='Train Stops')
    for index, point in df.iterrows():
        folium.Marker(
            location=[point['COORDINATES'].y, point['COORDINATES'].x],
            tooltip=point['STN_NAME'],
            icon=folium.Icon(
                color=TRAIN_ICON_COLOURS[point['LINE']],
                icon="train",
                prefix="fa")

        ).add_to(train_stops_layer)
        
    train_stops_layer.add_to(geo_map)

    return geo_map
