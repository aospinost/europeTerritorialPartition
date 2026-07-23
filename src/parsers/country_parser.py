import os
import re
import pandas as pd
from src.config import COUNTRY_HISTORY_DIR, COUNTRIES_FILE, COMMON_DIR, COUNTRY_ACCEPTANCE_CSV

def CreateCountryMetadata():
    # -----------------------------
    # ACCEPTED TAGS
    # -----------------------------
    acceptance_df = pd.read_csv(
        COUNTRY_ACCEPTANCE_CSV
    )

    valid_tags = set(
        acceptance_df['tag'].unique()
    )

    # -----------------------------
    # CAPITALS
    # -----------------------------

    history_folder = COUNTRY_HISTORY_DIR

    capital_map = {}

    ### MODIFIED

    name_map = {}

    for filename in os.listdir(history_folder):

        if not filename.endswith(".txt"):
            continue

        match = re.match(
            r'([A-Z]{3})\s*-\s*(.*)\.txt',
            filename
        )

        if not match:
            continue

        tag = match.group(1)
        #### MODIFIED
        country_name = match.group(2).strip()

        if tag not in valid_tags:
            continue

        filepath = os.path.join(
            history_folder,
            filename
        )

        with open(filepath, 'r', encoding='latin1') as f:
            content = f.read()

        capital_match = re.search(
            r'capital\s*=\s*(\d+)',
            content
        )

        if capital_match:
            capital_map[tag] = int(
                capital_match.group(1)
            )
        ### MODIFIED
        name_map[tag] = country_name

    # -----------------------------
    # COUNTRY COLOR FILE LINKS
    # -----------------------------

    master_file = (
        COUNTRIES_FILE
    )

    with open(master_file, 'r', encoding='latin1') as f:
        content = f.read()

    rows = []

    for tag in valid_tags:

        # Example:
        # FRA = "countries/France.txt"

        match = re.search(
            rf'\b{tag}\b\s*=\s*"([^"]+)"',
            content
        )

        if not match:
            continue

        relative_path = match.group(1)

        country_file = os.path.join(
            COMMON_DIR,
            relative_path
        )

        if not os.path.exists(country_file):
            continue

        with open(country_file, 'r', encoding='latin1') as f:
            country_content = f.read()

        color_match = re.search(
            r'color\s*=\s*{\s*(\d+)\s+(\d+)\s+(\d+)\s*}',
            country_content
        )

        if not color_match:
            continue

        rows.append({
            'tag': tag,
            ### MODIFIED
            'name': name_map.get(tag, tag),
            'capital': capital_map.get(tag, None),
            'red': int(color_match.group(1)),
            'green': int(color_match.group(2)),
            'blue': int(color_match.group(3))
        })

    # -----------------------------
    # EXPORT
    # -----------------------------

    df_metadata = pd.DataFrame(rows)

    df_metadata = df_metadata.sort_values('tag')
    
    return df_metadata