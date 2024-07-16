from utils.mrt_colours import TRAIN_COLOURS
from . import pd, folium
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
    for index, point in df.iterrows():
        folium.Marker(
            location=[point['Latitude'], point['Longitude']],
            tooltip=point['Description'],
            icon=folium.Icon(
                color='purple',
                icon="bus",
                prefix="fa")
        ).add_to(geo_map)
    
    
    return geo_map

# Add bus stop clusters
def addBusStopClusters(df: pd.DataFrame, geo_map: folium.Map) -> folium.Map:
    lat = [row['Latitude'] for _, row in df.iterrows()]
    long = [row['Longitude'] for _, row in df.iterrows()]
    FastMarkerCluster(
        data = list(zip(lat, long))
        ).add_to(geo_map)
    
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
    
    for index, point in df.iterrows():
        folium.Marker(
            location=[point['COORDINATES'].y, point['COORDINATES'].x],
            tooltip=point['STN_NAME'],
            icon=folium.Icon(
                color=TRAIN_ICON_COLOURS[point['LINE']],
                icon="train",
                prefix="fa")

        ).add_to(geo_map)

    return geo_map