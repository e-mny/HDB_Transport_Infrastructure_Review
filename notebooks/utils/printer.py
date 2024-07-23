from . import pd

def printTopUnderservedAreas(df: pd.DataFrame, pt_type: str, num_rows: int = 5) -> None:
    print(f"Top {num_rows} Areas Needing More {pt_type.capitalize()} Stops:")
    print(df[['Area', f'{pt_type}_density_discrepancy']].head(num_rows))
    print()
