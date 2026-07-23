from src.config import POPULATION_CSV
from src.parsers.pop_parser import *

def ExportPopulation(df_population):
    df_population.to_csv(POPULATION_CSV, index=False)
    print(f"Exported {len(df_population)} rows of population.")
    return