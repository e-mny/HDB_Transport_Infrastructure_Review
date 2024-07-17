# HELPER FUNCTIONS
from . import pd, gpd
import re
from typing import List
import branca.colormap as cm
import requests
import numpy as np

# Public Transport Analysis
def getRes(api_link: str, acc_key: str):
    return requests.get(api_link, headers={"AccountKey": acc_key})

def getJSON(response):
    return response.json()['value']

def getDataframe(jsonList: list) -> pd.DataFrame:
    return pd.DataFrame(jsonList)

def getAllRecords(api_link: str, acc_key: str) -> list:
    listRecords = []
    curNum = 0

    while True:
        # print(curNum)
        new_api_link = api_link + f"?$skip={curNum}"
        if getJSON(getRes(new_api_link, acc_key)): # List
            listRecords.extend(getJSON(getRes(new_api_link, acc_key)))
        else:
            break
        curNum += 500
    # print(listRecords)
    return listRecords


# Train depots are not considered public transportation as commuters do not have access
def removeDepots(row):
    return 'depot' not in row['STN_NAM_DE'].lower()

# Drop unnecessary rows
def dropRows(dataframe: pd.DataFrame) -> pd.DataFrame:
    return dataframe.drop(['TYP_CD', 'STN_NAM', 'ATTACHEMEN'], axis=1)

# Get the centre of the polygon to find the location of the station
def getCentroid(polygon):
    return polygon.centroid

# Load JSON containing MRT station coordinates (except TEL)
def loadMRTJSON() -> pd.DataFrame:
    return pd.read_json("../data/MRTLRTStnPtt.json")

# Function to extract alphabetical and numerical parts
def split_alphanumeric(station):
    match = re.match(r'([a-zA-Z]+)(\d*)', station)
    if match:
        letters = match.group(1)
        numbers = match.group(2) if match.group(2) else None
        return letters, numbers
    return None, None

# Function to split rows with slashes into multiple rows
def split_slash(station) -> List:
    if '/' in station:
        parts = station.split('/')
        return [part for part in parts]
    return [station]

# Function to create MRT List
def prepare_mrt_list():
    mrt_df = pd.read_json("../data/MRTLRTStnPtt.json")

    def remove_and_lowercase(text):
        words = text.split()[:-2]  # Remove last two words
        # lowercase each word for case insensitivity
        lowercase_words = [word.lower() for word in words]
        return ' '.join(lowercase_words)

    mrt_df['STN_NAME'] = mrt_df['STN_NAME'].apply(remove_and_lowercase)
    return mrt_df['STN_NAME']

# Function to create Area List (in lowercase)
def prepare_area_list() -> list:
    area_list = pd.read_csv(
        '../data/All Regions_Coordinates.csv')['Area'].to_list()

    area_list = list(set(area_list))
    area_list_lower = [str(area).lower() for area in area_list]

    return area_list_lower

# Function to capitalize a phrase of words
def capitalize(words: list) -> str:
    words_list = words.split()  # Split the input string into a list of words
    capitalized_words = [word.capitalize()
                         for word in words_list]  # Capitalize each word
    # Join the capitalized words back into a single string
    return ' '.join(capitalized_words)

# Function to strip location names that do not alter the area
def strip_key_words(word: str) -> str:
    key_words = ['North', 'South', 'East', 'West', 'Central', 'Rise',
                 'Drive', 'Way', 'Station', 'Kampong', '1', '2', 'Place']
    for key_word in key_words:
        word = word.replace(key_word.lower(), '')
    return word.strip()

# Function to determine mrt based on Subzone column
def determine_mrt(row, mrt_list: list):
    sz_value = row['SZ'].lower()

    # Check if SZ value is in MRT name list
    if any(sz_value == mrt_name for mrt_name in mrt_list):
        return next((capitalize(mrt_name) for mrt_name in mrt_list if sz_value == mrt_name), row['PA'])

    # Strip directional words and check again
    stripped_value = strip_key_words(sz_value)
    if any(stripped_value == mrt_name for mrt_name in mrt_list):
        return next((capitalize(mrt_name) for mrt_name in mrt_list if stripped_value == mrt_name), row['PA'])

    # Default to 'PA' if no match found
    return row['PA']

# Function to determine area based on Subzone column
def determine_area(row, area_list: list):
    sz_value = row['SZ'].lower()

    # Check if SZ value is in MRT name list
    if any(sz_value == area_name for area_name in area_list):
        return next((capitalize(area_name) for area_name in area_list if sz_value == area_name), row['PA'])

    # Strip directional words and check again
    stripped_value = strip_key_words(sz_value)
    if any(stripped_value == area_name for area_name in area_list):
        return next((capitalize(area_name) for area_name in area_list if stripped_value == area_name), row['PA'])

    # Default to 'PA' if no match found
    return row['PA']

# Population Analysis

# Create a Dataframe indexed on Area
def createIndexedDict(dataframe: pd.DataFrame, col_name: str) -> pd.DataFrame:
    return dataframe.set_index("Area")[col_name]

# Create a colour map
def createColorMap(minvalue: int, maxvalue: int, caption: str) -> cm.LinearColormap:
    colormap = cm.LinearColormap(
        colors=["#78777d", "#ac172b"], 
        vmin=minvalue, 
        vmax=maxvalue)
    colormap.caption = caption

    return colormap


# Convert all 0 values to be NaN
def convertZeroToNan(df: gpd.GeoDataFrame, col_name: str) -> gpd.GeoDataFrame:
    return df[col_name].replace(0, np.nan)

# Create a new dataframe that determines the number of public transport stops within a region   
def createPTStopsDF(geo_df: gpd.GeoDataFrame, pt_stops_gdf: gpd.GeoDataFrame, pt_type: str) -> gpd.GeoDataFrame:
    print(geo_df.crs)
    print(pt_stops_gdf.crs)
    pt_stops_in_region = gpd.sjoin(geo_df, pt_stops_gdf, how='inner')
    pt_stops_count = pt_stops_in_region.groupby(
        'Area').size().reset_index(name=f'{pt_type}_stops_count')

    return pt_stops_count


# Normalize Dataframe column
def normalizeColumn(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    df[f"normalized_{col_name}"] = (df[col_name] - df[col_name].min()) / (df[col_name].max() - df[col_name].min())
    return df

# Get Density Discrepancy dataframe, sorted from highest to lowest
def getDensityDiscrepancyDF(df: pd.DataFrame, pt_type: str) -> pd.DataFrame:
    areas_needing_more_stops = df[df[f'{pt_type}_density_discrepancy'] > 0]
    underserved_areas_df = areas_needing_more_stops.sort_values(by=f"{pt_type}_density_discrepancy", ascending=False).reset_index(drop=True)

    return underserved_areas_df