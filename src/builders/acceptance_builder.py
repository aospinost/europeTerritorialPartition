from src.parsers.acceptance_parser import *
from src.config import COUNTRY_ACCEPTANCE_CSV, MISSING_CULTURES_CSV

def ExportAcceptedCultures(df_acceptance, missing_df):
    # -----------------------------
    # EXPORT ACCEPTANCE
    # -----------------------------

    df_acceptance.to_csv(
        COUNTRY_ACCEPTANCE_CSV,
        index=False
    )

    print(f"Exported {len(df_acceptance)} acceptance rows.")

    if missing_df is None: return

    missing_df.to_csv(
        MISSING_CULTURES_CSV,
        index=False
    )

    print(f"Missing cultures: {len(missing_df)}")
    return