import os
import re
import pandas as pd
from src.config import VERTEX_CSV, CULTURE_KEY_CSV, COUNTRY_HISTORY_DIR, VALID_COUNTRIES_CSV, REJECTED_COUNTRIES_CSV

def FindValidCountries():

    # -----------------------------
    # EUROPE DATA
    # -----------------------------

    vertex_df = pd.read_csv(VERTEX_CSV)
    culture_df = pd.read_csv(CULTURE_KEY_CSV)

    europe_provinces = set(vertex_df['province'])
    europe_cultures = set(culture_df['culture'])

    valid_rows = []
    rejected = []

    folder = COUNTRY_HISTORY_DIR

    for filename in os.listdir(folder):

        if not filename.endswith(".txt"):
            continue

        match = re.match(r'([A-Z]{3})\s*-\s*(.*)\.txt', filename)
        if not match:
            continue

        tag = match.group(1)
        name = match.group(2)

        filepath = os.path.join(folder, filename)

        with open(filepath, 'r', encoding='latin1') as f:
            content = f.read()

        # -----------------------------
        # CAPITAL
        # -----------------------------

        cap_match = re.search(r'capital\s*=\s*(\d+)', content)

        capital = int(cap_match.group(1)) if cap_match else None

        capital_valid = capital in europe_provinces

        # -----------------------------
        # CULTURES
        # -----------------------------

        cultures = set()

        cultures.update(
            re.findall(r'primary_culture\s*=\s*(\w+)', content)
        )

        cultures.update(
            re.findall(r'culture\s*=\s*(\w+)', content)
        )

        culture_valid = len(cultures.intersection(europe_cultures)) > 0

        # -----------------------------
        # FINAL DECISION
        # -----------------------------

        if capital_valid and culture_valid:

            valid_rows.append({
                'tag': tag,
                'country_name': name,
                'capital': capital,
                'cultures': ",".join(sorted(cultures))
            })

        else:

            rejected.append({
                'tag': tag,
                'country_name': name,
                'capital_valid': capital_valid,
                'culture_valid': culture_valid,
                'cultures': ",".join(sorted(cultures))
            })

    valid_df = pd.DataFrame(valid_rows)
    rejected_df = pd.DataFrame(rejected)

    valid_df.to_csv(VALID_COUNTRIES_CSV, index=False)
    rejected_df.to_csv(REJECTED_COUNTRIES_CSV, index=False)

    print(f"Valid countries: {len(valid_df)}")
    print(f"Rejected countries: {len(rejected_df)}")

    return valid_df, rejected_df