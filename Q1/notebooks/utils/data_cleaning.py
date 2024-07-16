from utils.helper import removeDepots, dropRows, getCentroid, loadMRTJSON, split_slash, split_alphanumeric, prepare_area_list, determine_area
from . import pd


def cleanTrainStationDF(dataframe: pd.DataFrame) -> pd.DataFrame:
    trainStation_coords_new = dataframe[dataframe.apply(
        removeDepots, axis=1)]
    trainStation_df = dropRows(trainStation_coords_new)
    trainStation_df = trainStation_df.rename(columns={
        'TYP_CD_DES': 'TYPE',
        'STN_NAM_DE': 'STN_NAME',
        'geometry': 'GEOMETRY'
    })

    # Apply the function to the GeoDataFrame
    trainStation_df['COORDINATES'] = trainStation_df['GEOMETRY'].apply(
        getCentroid)

    # Merge the STN_NAME and STN_NO
    mrtJSONDF = loadMRTJSON()
    new_df = pd.merge(trainStation_df, mrtJSONDF, on="STN_NAME", how="inner")
    new_df = new_df.drop_duplicates(subset="STN_NAME", keep='last')

    # Duplicate rows that are interchanges
    # Apply the function to the DataFrame and explode the list
    df_expanded = new_df['STN_NO'].apply(split_slash).explode()
    df_expanded = df_expanded.rename('STN_NO')
    df_expanded = df_expanded.to_frame()

    # Merge with the original DataFrame to retain other columns
    df_expanded = df_expanded.merge(new_df.drop(
        columns=['STN_NO']), left_index=True, right_index=True).reset_index(drop=True)
    # print(df_expanded)

    # Split into Line column and Station Number column
    df_expanded[['LINE', 'NUM']] = df_expanded['STN_NO'].apply(
        lambda x: pd.Series(split_alphanumeric(x)))
    df_expanded['NUM'] = pd.to_numeric(df_expanded['NUM'], errors='coerce')
    df_expanded['NUM'].fillna(0, inplace=True)
    df_expanded['NUM'] = df_expanded['NUM'].astype(int)

    # Sort according to Station Number
    new_df = df_expanded.sort_values(by=['LINE', 'NUM'])

    return new_df.reset_index(drop=True)


# Preprocess HDB Population Data
def cleanHDBDF(dataframe: pd.DataFrame) -> pd.DataFrame:
    # Remove entries that have 0 HSE
    df = dataframe[dataframe['HSE'] != 0]

    area_list = prepare_area_list()

    # Apply function to create 'MRT' column
    df['Area'] = df.apply(lambda row: determine_area(row, area_list), axis=1)
    # print(df.to_string())

    # Group by MRT Area
    # Sum the total number of HSE (Dwelling count)
    # Combine the TOD (Type of Dwelling)
    new_df = df.groupby('Area').agg({
        'HSE': 'sum',
        'PA': lambda x: list(dict.fromkeys(x)),
        'SZ': lambda x: list(dict.fromkeys(x)),
        'TOD': lambda x: ', '.join(x),
        'Time': 'max'
    }).reset_index()

    new_df = new_df.rename(columns={
        "SZ": "HDBSubzone",
        "TOD": "Type",
        "HSE": "Count"
    })

    return new_df
