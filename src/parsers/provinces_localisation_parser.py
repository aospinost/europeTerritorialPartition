# ============================================================
# provinces_localisation_parser.py
# ============================================================
#
# PURPOSE
# ------------------------------------------------------------
#
# Parses province localization names from the
# Europa Universalis style localization file.
#
#
# IMPORTANT FORMAT NOTES
# ------------------------------------------------------------
#
# The file is EXTREMELY inconsistent:
#
# Example:
#
# PROV3274;Svaneti;;;;;;;;;;x;;;;
# PROV2095;Dithakong;;;;;;;;;;x;;;;
#
# Rows have different lengths.
#
# Some rows:
#
# BEL_387;Vlaanderen;;;;;;;;;;;;;;x
#
# should be ignored entirely because they
# are NOT province localizations.
#
#
# ============================================================
# WHAT WE CARE ABOUT
# ============================================================
#
# ONLY:
#
# column 0 -> localization key
# column 1 -> localized name
#
#
# ============================================================
# VALID ROWS
# ============================================================
#
# We ONLY parse rows beginning with:
#
#     PROV<number>
#
#
# ============================================================
# OUTPUT
# ============================================================
#
# Exports dataframe:
#
# province,name
#
# Example:
#
# 3274,Svaneti
# 2095,Dithakong
#
#
# ============================================================
# ENCODING ISSUE
# ============================================================
#
# Visual Studio Code displays weird characters:
#
# R�gion L�manique
#
# because the file is likely encoded in:
#
#     cp1252
#
# or:
#
#     latin-1
#
# instead of UTF-8.
#
# We therefore explicitly read using:
#
#     encoding='cp1252'
#
# which usually fixes EU4 localization files.
#
# ============================================================

import re
import pandas as pd

from src.config import (
    PROVINCES_LOCALISED_NAMES,
    VERTEX_CSV
)


# ============================================================
# BUILD LOCALIZATION DATAFRAME
# ============================================================

def BuildProvinceLocalisations():

    print("\n=== BUILDING PROVINCE LOCALISATIONS ===")

    # --------------------------------------------------------
    # Load valid provinces from vertex csv
    # --------------------------------------------------------

    vertex_df = pd.read_csv(VERTEX_CSV)

    valid_provinces = set(
        vertex_df['province']
    )

    # --------------------------------------------------------
    # Output rows
    # --------------------------------------------------------

    rows = []

    # --------------------------------------------------------
    # Read localization file
    # --------------------------------------------------------
    #
    # cp1252 fixes weird accented characters
    #
    # --------------------------------------------------------

    with open(

        PROVINCES_LOCALISED_NAMES,

        'r',

        encoding='cp1252',

        errors='replace'

    ) as file:

        for line in file:

            line = line.strip()

            # ------------------------------------------------
            # Skip empty rows
            # ------------------------------------------------

            if not line:
                continue

            # ------------------------------------------------
            # Split ONLY first two columns
            # ------------------------------------------------
            #
            # Because csv is wildly inconsistent
            #
            # ------------------------------------------------

            parts = line.split(';', 2)

            if len(parts) < 2:
                continue

            key = parts[0]
            name = parts[1]

            # ------------------------------------------------
            # Match:
            #
            # PROV1234
            #
            # ------------------------------------------------

            match = re.match(
                r'^PROV(\d+)$',
                key
            )

            if not match:
                continue

            province = int(
                match.group(1)
            )

            # ------------------------------------------------
            # Ignore provinces not in vertices
            # ------------------------------------------------

            if province not in valid_provinces:
                continue

            rows.append({

                'province': province,

                'name': name
            })

    localisation_df = pd.DataFrame(rows)

    print(
        f"[DONE] Parsed "
        f"{len(localisation_df)} "
        f"localized province names"
    )

    return localisation_df