import pandas as pd
import re
from src.config import POPULATION_CSV, CULTURES_FILE

def CreateCulturesKey():

    # -----------------------------
    # LOAD CULTURES OF INTEREST
    # -----------------------------

    pop_df = pd.read_csv(POPULATION_CSV)

    target_cultures = set(pop_df['culture'].unique())

    # -----------------------------
    # LOAD CULTURES FILE
    # -----------------------------

    with open(
        CULTURES_FILE,
        'r',
        encoding='latin1'
    ) as f:

        content = f.read()

    # -----------------------------
    # FIND CULTURE BLOCKS
    # -----------------------------

    # Matches:
    # north_german = {
    #     color = { 90 60 60 }

    pattern = re.compile(
        r'(\w+)\s*=\s*{[^{}]*?color\s*=\s*{\s*(\d+)\s+(\d+)\s+(\d+)\s*}',
        re.DOTALL
    )

    rows = []

    for match in pattern.finditer(content):

        culture = match.group(1)

        if culture in target_cultures:

            rows.append({
                'culture': culture,
                'red': int(match.group(2)),
                'green': int(match.group(3)),
                'blue': int(match.group(4))
            })

    # -----------------------------
    # CREATE DATAFRAME
    # -----------------------------

    df_cultures = pd.DataFrame(rows)

    # Optional sorting
    df_cultures = df_cultures.sort_values('culture')

    return df_cultures