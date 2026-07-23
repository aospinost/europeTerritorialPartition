import os
import shutil
from src.config import REMOVE_HISTORIES_TXT, REMOVE_COUNTRIES_TXT, COUNTRY_HISTORY_DIR, COUNTRIES_FILE
from src.config import HISTORY_COUNTRIES_BACKUP, COMMON_DIR, COMMON_COUNTRIES_TXT_BACKUP, COMMON_COUNTRY_DIR, COMMON_COUNTRIES_BACKUP

def DeleteIrrelevantCountries():
    # -----------------------------
    # LOAD MANIFESTS
    # -----------------------------

    with open(
        REMOVE_HISTORIES_TXT,
        'r',
        encoding='utf8'
    ) as f:

        history_files = [
            line.strip()
            for line in f
            if line.strip()
        ]

    with open(
        REMOVE_COUNTRIES_TXT,
        'r',
        encoding='utf8'
    ) as f:
        common_lines_to_remove = set(
            line.strip()
            for line in f
            if line.strip()
        )

    # -----------------------------
    # HISTORY FILE DELETION
    # -----------------------------
    os.makedirs(
        HISTORY_COUNTRIES_BACKUP,
        exist_ok=True
    )

    deleted_files = 0

    for filename in history_files:

        source_path = os.path.join(
            COUNTRY_HISTORY_DIR,
            filename
        )

        if os.path.exists(source_path):

            # Backup first
            shutil.copy2(
                source_path,
                os.path.join(
                    HISTORY_COUNTRIES_BACKUP,
                    filename
                )
            )

            # Delete
            os.remove(source_path)

            deleted_files += 1

    print(
        f"Deleted {deleted_files} history files."
    )

    # -----------------------------
    # COMMON COUNTRIES TXT CLEANING
    # -----------------------------

    # Backup
    shutil.copy2(
        COUNTRIES_FILE,
        COMMON_COUNTRIES_TXT_BACKUP
    )

    # Read lines
    with open(
        COUNTRIES_FILE,
        'r',
        encoding='latin1'
    ) as f:

        lines = f.readlines()

    # Filter lines
    cleaned_lines = []

    removed_lines = 0

    for line in lines:

        if line.strip() in common_lines_to_remove:

            removed_lines += 1
            continue

        cleaned_lines.append(line)

    # Rewrite file
    with open(
        COUNTRIES_FILE,
        'w',
        encoding='latin1'
    ) as f:

        f.writelines(cleaned_lines)

    print(
        f"Removed {removed_lines} entries "
        f"from common/countries.txt"
    )

    # -----------------------------
    # COMMON COUNTRY FILE DELETION
    # -----------------------------

    os.makedirs(
        COMMON_COUNTRIES_BACKUP,
        exist_ok=True
    )

    deleted_common_files = 0

    for filename in common_lines_to_remove:

        source_path = os.path.join(
            COMMON_COUNTRY_DIR,
            filename
        )

        if os.path.exists(source_path):

            # Backup first
            shutil.copy2(
                source_path,
                os.path.join(
                    COMMON_COUNTRIES_BACKUP,
                    filename
                )
            )

            # Delete
            os.remove(source_path)

            deleted_common_files += 1

    print(
        f"Deleted {deleted_common_files} "
        f"common/countries files."
    )

    print("Backups created in ./data/backup/")