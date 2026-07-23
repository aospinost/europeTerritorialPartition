import os
import re
import pandas as pd

from src.config import PROVINCES_HISTORY_DIR


def Parse1836Ownership():

    rows = []

    # -----------------------------------
    # WALK ALL REGION SUBFOLDERS
    # -----------------------------------

    for root, _, files in os.walk(PROVINCES_HISTORY_DIR):

        for filename in files:

            if not filename.endswith(".txt"):
                continue

            # -----------------------------------
            # EXTRACT PROVINCE ID
            # -----------------------------------

            match = re.match(
                r'(\d+)\s*-\s*.*\.txt',
                filename
            )

            if not match:
                continue

            province_id = int(match.group(1))

            filepath = os.path.join(root, filename)

            # -----------------------------------
            # READ FILE
            # -----------------------------------

            with open(filepath, 'r', encoding='latin1') as f:

                content = f.read()

            # -----------------------------------
            # REMOVE HISTORY BLOCKS
            # -----------------------------------

            split_match = re.split(
                r'\d{4}\.\d{1,2}\.\d{1,2}\s*=\s*\{',
                content,
                maxsplit=1
            )

            prehistory = split_match[0]

            # -----------------------------------
            # EXTRACT OWNER
            # -----------------------------------

            owner_match = re.search(
                r'owner\s*=\s*([A-Z]{3})',
                prehistory
            )

            if not owner_match:
                continue

            owner = owner_match.group(1)

            rows.append({
                'province': province_id,
                'tag': owner
            })

    # -----------------------------------
    # DATAFRAME
    # -----------------------------------

    df = pd.DataFrame(rows)

    df = df.sort_values('province')

    return df