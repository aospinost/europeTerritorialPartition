import networkx as nx
import pandas as pd
from src.config import IMPUTATED_COUNTRY_ACCEPTANCE_CSV
from typing import Optional

def LoadAcceptanceMap() -> dict[str, set[str]]:
    df = pd.read_csv(IMPUTATED_COUNTRY_ACCEPTANCE_CSV)
    acceptance = {}
    for tag, group in df.groupby('tag'):
        acceptance[tag] = set(
            group['accepted_culture']
        )
    return acceptance

def ApplySatisfactionScores(G: nx.Graph) -> None:
    acceptance = LoadAcceptanceMap()
    for province in G.nodes():
        node = G.nodes[province]
        country = node.get('country_tag')
        populations = node.get(
            'population',
            []
        )

        # TOTAL POPULATION
        total_population = sum(pop for _, pop in populations)


        # ACCEPTED CULTURES
        accepted_cultures = acceptance.get(country, set())

        # SATISFIED POPULATION
        satisfied_population = 0
        for culture, pop in populations:
            if culture in accepted_cultures:
                satisfied_population += pop

        # NORMALIZED SCORE
        if total_population > 0:
            satisfaction = satisfied_population / total_population
        else:
            satisfaction = 0

        # STORE ON GRAPH

        node['satisfied_population'] = satisfied_population
        node['total_population'] = total_population
        node['satisfaction'] = satisfaction

    return

def GlobalSatisfaction(G: nx.Graph, tags: Optional[str | list[str]] = None) -> tuple[int, int, float]:
    if tags is not None:
        if isinstance(tags, str):
            tags = {tags}
        else:
            tags = set(tags)

    total_population = 0
    total_satisfied_population = 0

    for province in G.nodes():
        node = G.nodes[province]
        if tags is not None:
            country = node.get('country_tag')
            if country not in tags:
                continue

        total_population += node.get('total_population', 0)
        total_satisfied_population += node.get('satisfied_population', 0)

    # NORMALIZED SCORE

    if total_population > 0:
        satisfaction_score = total_satisfied_population / total_population

    else:
        satisfaction_score = 0

    return (total_population, total_satisfied_population, satisfaction_score)