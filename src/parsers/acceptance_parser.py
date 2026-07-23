import os
import re
import pandas as pd
from src.config import POPULATION_CSV, COUNTRY_HISTORY_DIR

def CreateCountryAcceptance():

    # -----------------------------
    # TARGET CULTURES
    # -----------------------------

    pop_df = pd.read_csv(POPULATION_CSV)

    target_cultures = set(pop_df['culture'].unique())

    # -----------------------------
    # COUNTRY FILES
    # -----------------------------

    folder = COUNTRY_HISTORY_DIR

    rows = []

    represented_cultures = set()

    for filename in os.listdir(folder):

        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(folder, filename)

        # FRA - France.txt
        match = re.match(
            r'([A-Z]{3})\s*-\s*(.*)\.txt',
            filename
        )

        if not match:
            continue

        tag = match.group(1)

        with open(filepath, 'r', encoding='latin1') as f:
            content = f.read()

        cultures = set()

        # primary culture
        cultures.update(
            re.findall(
                r'primary_culture\s*=\s*(\w+)',
                content
            )
        )

        # accepted cultures
        cultures.update(
            re.findall(
                r'culture\s*=\s*(\w+)',
                content
            )
        )

        # Keep only relevant cultures
        cultures = cultures.intersection(target_cultures)

        # Track represented cultures
        represented_cultures.update(cultures)

        for culture in cultures:

            rows.append({
                'tag': tag,
                'accepted_culture': culture
            })

    df_acceptance = pd.DataFrame(rows)

    df_acceptance = df_acceptance.sort_values(
        ['tag', 'accepted_culture']
    )
    missing_cultures = sorted(
        target_cultures - represented_cultures
    )

    missing_df = pd.DataFrame({
        'culture': missing_cultures
    })

    return df_acceptance, missing_df