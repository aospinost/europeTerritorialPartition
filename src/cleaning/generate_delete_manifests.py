import re
from src.config import COUNTRIES_FILE, REMOVE_COUNTRIES_TXT, REMOVE_HISTORIES_TXT

def GenerateCountryRemovalManifest(irrelevant_df):
    tags_to_remove = set(
        irrelevant_df['tag']
    )

    # -----------------------------
    # COMMON COUNTRIES ENTRIES
    # -----------------------------

    common_file = (
        COUNTRIES_FILE
    )

    with open(common_file, 'r', encoding='latin1') as f:
        lines = f.readlines()

    removal_lines = []

    for line in lines:

        print("\nRAW LINE:")
        print(repr(line))

        match = re.match(
            r'\s*([A-Z]{3})\s*=\s*"countries/(.+\.txt)"',
            line
        )

        if match:

            print("MATCHED")

            tag = match.group(1)
            filename = match.group(2)

            print(f"TAG: {tag}")
            print(f"FILENAME: {filename}")

            in_remove = tag in tags_to_remove

            print(f"IN REMOVE SET: {in_remove}")
            
            if in_remove:

                removal_lines.append(filename)

                print("APPENDED")

        else:

            print("NO MATCH")

    # Export manifest
    with open(
        REMOVE_COUNTRIES_TXT,
        'w',
        encoding='utf8'
    ) as f:

        for line in removal_lines:
            f.write(line + '\n')

    print(
        f"Manifested {len(removal_lines)} "
        f"common/countries entries."
    )

    # -----------------------------
    # HISTORY FILES
    # -----------------------------

    with open(
        REMOVE_HISTORIES_TXT,
        'w',
        encoding='utf8'
    ) as f:

        for _, row in irrelevant_df.iterrows():

            filename = (
                f"{row['tag']} - "
                f"{row['country_name']}.txt"
            )

            f.write(filename + '\n')

    print("Generated deletion manifests.")