# HELPER FUNCTIONS
from . import pd, gpd
import re
from typing import List
import branca.colormap as cm

# Public Transport Analysis

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
def createIndexedDict(dataframe: pd.DataFrame) -> pd.DataFrame:
    return dataframe.set_index("Area")["Count"]

# Create a colour map
def createColorMap(geo_df: gpd.GeoDataFrame):
    colormap = cm.LinearColormap(
        colors=["#78777d", "#ac172b"], 
        vmin=geo_df['Count'].min(), 
        vmax=geo_df['Count'].max())
    colormap.caption = "Population Density"

    return colormap
