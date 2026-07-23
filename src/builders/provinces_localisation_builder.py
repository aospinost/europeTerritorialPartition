# ============================================================
# builder.py
# ============================================================
#
# PURPOSE
# ------------------------------------------------------------
#
# Replaces province names in vertex csv
# using parsed localization dataframe.
#
#
# ============================================================
# BEFORE
# ============================================================
#
# province,name
#
# 607,Région Lémanique
#
#
# ============================================================
# AFTER
# ============================================================
#
# vertex csv gets updated:
#
# province,red,green,blue,name,...
#
# 607,...,Région Lémanique,...
#
# ============================================================

import pandas as pd

from src.config import (
    VERTEX_CSV
)

from src.parsers.provinces_localisation_parser import (
    BuildProvinceLocalisations
)


# ============================================================
# APPLY LOCALIZED NAMES
# ============================================================

def ApplyProvinceLocalisations():

    print("\n=== APPLYING LOCALISATIONS ===")

    # --------------------------------------------------------
    # Load existing vertices
    # --------------------------------------------------------

    vertex_df = pd.read_csv(VERTEX_CSV)

    # --------------------------------------------------------
    # Load localization table
    # --------------------------------------------------------

    localisation_df = (
        BuildProvinceLocalisations()
    )

    # --------------------------------------------------------
    # Convert to lookup dictionary
    # --------------------------------------------------------

    localisation_map = dict(

        zip(

            localisation_df['province'],
            localisation_df['name']
        )
    )

    # --------------------------------------------------------
    # Replace names
    # --------------------------------------------------------

    replaced = 0

    for idx, row in vertex_df.iterrows():

        province = row['province']

        if province in localisation_map:

            vertex_df.at[
                idx,
                'name'
            ] = localisation_map[province]

            replaced += 1

    # --------------------------------------------------------
    # Save updated csv
    # --------------------------------------------------------

    vertex_df.to_csv(

        VERTEX_CSV,

        index=False,

        encoding='utf-8-sig'
    )

    print(
        f"[DONE] Replaced "
        f"{replaced} province names"
    )

    return