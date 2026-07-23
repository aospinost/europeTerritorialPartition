from pathlib import Path

RANDOM_SEED = 123

# ROOTS

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT / "data"
RAW_DATA = DATA_ROOT / "raw" / "dataSourceAlternative"
PROCESSED_DATA = DATA_ROOT / "processed"
BACKUP_DATA = DATA_ROOT / "backup"
INTERNAL = DATA_ROOT / "internal"
DIST = PROJECT_ROOT / "dist"

# RAW PATHS

MAP_DIR = RAW_DATA / "map"
POP_DIR = RAW_DATA / "history" / "pops" / "1836.1.1"
COUNTRY_HISTORY_DIR = RAW_DATA / "history" / "countries"
PROVINCES_HISTORY_DIR = RAW_DATA / "history" / "provinces"
COMMON_DIR = RAW_DATA / "common"
LOCALISATION_DIR = RAW_DATA / "localisation"
COUNTRIES_FILE = COMMON_DIR / "countries.txt"
CULTURES_FILE = COMMON_DIR / "cultures.txt"
COMMON_COUNTRY_DIR = COMMON_DIR / "countries"
PARTITIONS_DIR = DATA_ROOT / "partitions"
PARTITIONS_STATS_DIR = PARTITIONS_DIR / "stats"
IMPUTATED_DIR = DATA_ROOT / "imputated"

# MAP FILES

DEFINITION_CSV = MAP_DIR / "definition.csv"
POSITIONS_FILE = MAP_DIR / "positions.txt"
CONTINENT_FILE = MAP_DIR / "continent.txt"
PROVINCES_BMP = IMPUTATED_DIR / "imp_provinces.bmp"
PROVINCES_BMP_ORIGINAL = MAP_DIR / "provinces.bmp"

# OUTPUT FILES

VERTEX_CSV = PROCESSED_DATA / "europe_vertex.csv"
EDGE_CSV = PROCESSED_DATA / "europe_edges.csv"
POPULATION_CSV = PROCESSED_DATA / "europe_population.csv"
CULTURE_KEY_CSV = PROCESSED_DATA / "culture_key.csv"
COUNTRY_ACCEPTANCE_CSV = PROCESSED_DATA / "country_acceptance.csv"
COUNTRY_METADATA_CSV = PROCESSED_DATA / "country_metadata.csv"

# IMPUTATED FILES

IMPUTATED_VERTEX_CSV = IMPUTATED_DIR / "europe_vertex.csv"
IMPUTATED_COUNTRY_ACCEPTANCE_CSV = IMPUTATED_DIR / "country_acceptance.csv"
ALLOWED_COUNTRY_ACCEPTANCE_CSV = IMPUTATED_DIR / "allowed_country_acceptance.csv"
CULTURE_KEY_IMPUTATED = IMPUTATED_DIR/ "culture_key.csv"

# INTERNAL FILES

MISSING_CULTURES_CSV = INTERNAL / "missing_cultures.csv"
VALID_COUNTRIES_CSV = INTERNAL / "valid_countries.csv"
REJECTED_COUNTRIES_CSV = INTERNAL / "rejected_countries.csv"
REMOVE_COUNTRIES_TXT = INTERNAL / "remove_common_countries.txt"
REMOVE_HISTORIES_TXT = INTERNAL / "remove_history_files.txt"

# BACKUPS

HISTORY_COUNTRIES_BACKUP = BACKUP_DATA / "history_countries"
COMMON_COUNTRIES_TXT_BACKUP = BACKUP_DATA / "countries.txt"
COMMON_COUNTRIES_BACKUP = BACKUP_DATA / "countries"

# LOCALISATION

PROVINCES_LOCALISED_NAMES = LOCALISATION_DIR / "00_HPM_map.csv"

# EXPORTS

MISSING_CULTURES_CSV = INTERNAL / "missing_cultures.csv"
VALID_COUNTRIES_CSV = INTERNAL / "valid_countries.csv"
REJECTED_COUNTRIES_CSV = INTERNAL / "rejected_countries.csv"
REMOVE_COUNTRIES_TXT = INTERNAL / "remove_common_countries.txt"
REMOVE_HISTORIES_TXT = INTERNAL / "remove_history_files.txt"
PARALLEL_DFS_RECORD = INTERNAL / "parallel_dfs_record.csv"
PURE_DFS_RECORD = INTERNAL / "pure_dfs_record.csv"
PURE_BFS_RECORD = INTERNAL / "pure_bfs_record.csv"

# DIST

COLORED_MAPS = DIST / "coloredMaps"
SAT_MAPS = DIST / "satMaps"