from src.parsers.country_parser import *
from src.config import COUNTRY_METADATA_CSV

def ExportCountryMetadata(df_metadata):
    df_metadata.to_csv(
        COUNTRY_METADATA_CSV,
        index=False
    )

    return