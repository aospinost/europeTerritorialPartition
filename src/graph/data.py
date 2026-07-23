import pandas as pd
from src.config import (
    ALLOWED_COUNTRY_ACCEPTANCE_CSV,
    COUNTRY_METADATA_CSV,
    CULTURE_KEY_IMPUTATED,
    POPULATION_CSV
)

def LoadCountryMetadata() -> dict[str, dict]:
    df = pd.read_csv(COUNTRY_METADATA_CSV)
    metadata = {}
    for _, row in df.iterrows():
        metadata[row['tag']] = {
            'name': row['name'],
            'capital': row['capital'],
            'color': (
                row['red'] / 255,
                row['green'] / 255,
                row['blue'] / 255
            )
        }

    return metadata

def LoadCultureColors() -> dict[str, tuple[float, float, float]]:
    df = pd.read_csv(CULTURE_KEY_IMPUTATED)
    culture_colors = {}
    for _, row in df.iterrows():
        culture_colors[row['culture']] = (
            row['red'] / 255,
            row['green'] / 255,
            row['blue'] / 255
        )

    return culture_colors

def LoadAllowedAcceptanceMap() -> dict[str, set[str]]:
    df = pd.read_csv(ALLOWED_COUNTRY_ACCEPTANCE_CSV)
    acceptance = {}
    for tag, group in df.groupby('tag'):
        acceptance[tag] = set(group['accepted_culture'])
    return acceptance

def BuildProvincePopulationTable():
    df = pd.read_csv(POPULATION_CSV)
    province_population = {}
    for _, row in df.iterrows():
        province = row['province']
        population = row['population']
        province_population[province] = province_population.get(province, 0) + population
    return province_population

def BuildProvinceValueTable():
    population_df = pd.read_csv(POPULATION_CSV)
    accepted = LoadAllowedAcceptanceMap()
    province_value = {}

    for tag in accepted:
        province_value[tag] = {}

    for _, row in population_df.iterrows():
        province = row['province']
        culture = row['culture']
        population = row['population']

        for tag, cultures in accepted.items():
            if culture in cultures:
                province_value[tag][province] = province_value[tag].get(province, 0) + population

    return province_value