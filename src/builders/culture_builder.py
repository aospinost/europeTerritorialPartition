from src.config import CULTURE_KEY_CSV
from src.parsers.culture_parser import *

def ExportCulturesKey(df_cultures):
    # Export
    df_cultures.to_csv(
        CULTURE_KEY_CSV,
        index=False
    )

    print(f"Exported {len(df_cultures)} cultures.")

    return