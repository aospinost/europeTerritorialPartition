import os
import re
import pandas as pd
from collections import defaultdict
from src.config import POP_DIR

def ParsePopFile(filepath):
    """
    Parse a Victoria-style POP file and return:
    province, culture, population
    """

    with open(filepath, 'r', encoding='latin1') as f:
        content = f.read()

    # Find province blocks
    province_blocks = re.findall(
        r'(\d+)\s*=\s*{(.*?)(?=\n\d+\s*=|$)',
        content,
        re.DOTALL
    )

    # Aggregate population
    pop_data = defaultdict(int)

    for province_id, block in province_blocks:

        # Find all culture + size pairs
        matches = re.findall(
            r'culture\s*=\s*(\w+).*?size\s*=\s*(\d+)',
            block,
            re.DOTALL
        )

        for culture, size in matches:
            pop_data[(int(province_id), culture)] += int(size)

    # Convert to dataframe
    rows = [
        {
            'province': province,
            'culture': culture,
            'population': population
        }
        for (province, culture), population in pop_data.items()
    ]

    return pd.DataFrame(rows)

def CallPopulation(province_ids):
    all_dfs = []

    for filename in os.listdir(POP_DIR):

        if filename.endswith(".txt"):

            filepath = os.path.join(POP_DIR, filename)

            try:
                df_temp = ParsePopFile(filepath)

                # Keep only European provinces
                df_temp = df_temp[df_temp['province'].isin(province_ids)]

                all_dfs.append(df_temp)

                print(f"Parsed {filename}")

            except Exception as e:
                print(f"Failed {filename}: {e}")

    # Combine everything
    df_population = pd.concat(all_dfs, ignore_index=True)

    # Merge duplicates
    df_population = (
        df_population
        .groupby(['province', 'culture'], as_index=False)
        ['population']
        .sum()
    )

    return df_population