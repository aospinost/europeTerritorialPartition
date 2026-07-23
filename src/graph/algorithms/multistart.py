"""
MULTISTART GRAPH PARTITIONING

Description:
    This module implements a randomized metaheuristic partitioning algorithm 
    designed to segment a political geography graph G into distinct national 
    territories (tags) while strictly maximizing cultural satisfaction.

Core Mechanism:
    1. Seed Initialization: Active sovereign tags are instantiated at their 
       defined capital nodes. Unclaimed provinces form the initial global pool.
    2. Frontier Expansion: Each sovereign maintains separate land and maritime 
       frontier sets. Territorial growth strictly prioritizes contiguous land 
       expansion. Maritime expansion activates only when no valid land frontier 
       remains, allowing island and overseas territories to remain reachable 
       without destabilizing continental border coherence.
    3. Softmax Soft-Growth (Stochastic Loop): Nations are selected randomly to 
       expand. The selection of which frontier node to absorb is weighted via
       demographic satisfaction.
    4. Multistart Metaheuristic: Because single runs can converge into sub-optimal 
       local minima, The algorithm wraps the growth loop inside an independent 
       multistart framework. It repeats the randomized partition process N times, 
       evaluates global satisfaction scores, and saves the global maximum.

Properties:
    - Guaranteed Contiguity: Nodes are exclusively absorbed through a running 
      frontier set, eliminating the risk of broken, floating land exclaves.
"""

import networkx as nx
import numpy as np
import time

from src.config import RANDOM_SEED
from src.graph.data import (
    LoadCountryMetadata,
    LoadAllowedAcceptanceMap
)
from src.graph.metrics import (
    ApplySatisfactionScores,
    GlobalSatisfaction
)
from src.graph.partition import Partition

# Set reproducibility seed
np.random.seed(RANDOM_SEED)

ACCEPTANCE = LoadAllowedAcceptanceMap()

def ProvinceSatisfaction(G: nx.Graph, province: str, tag: str) -> float:
    node = G.nodes[province]
    populations = node.get('population', [])
    accepted = ACCEPTANCE.get(tag, set())

    total_population = 0
    satisfied_population = 0

    for culture, pop in populations:
        total_population += pop
        if culture in accepted:
            satisfied_population += pop

    if total_population == 0:
        return 0.0

    return satisfied_population

def RandomConnectedPartition(G: nx.Graph) -> Partition:
    metadata = LoadCountryMetadata()
    allowed_tags = set(ACCEPTANCE.keys())
    partition = Partition()

    # Pre-aggregate sea-lane node indices for instant lookup
    coastal_provinces = {p for p in G.nodes() if G.nodes[p].get('coastal')}
    
    states = {}
    unclaimed = set(G.nodes())

    # 1. Initialize Country Capitals
    for tag, data in metadata.items():
        if tag not in allowed_tags:
            continue

        capital = data['capital']
        if capital not in G.nodes() or capital not in unclaimed:
            continue

        partition.assign(capital, tag)
        unclaimed.discard(capital)

        states[tag] = {
            'owned': {capital},
            'land_frontier': set(),
            'sea_frontier': set()
        }

    # 2. Build Initial Frontiers
    for tag, state in states.items():

        capital = next(iter(state['owned']))

        # --------------------------------------------
        # Land frontier
        # --------------------------------------------

        land_frontier = set(
            G.neighbors(capital)
        ) & unclaimed

        state['land_frontier'] = land_frontier

        # --------------------------------------------
        # Sea frontier
        # --------------------------------------------

        if G.nodes[capital].get('coastal'):

            sea_frontier = (
                coastal_provinces
                & unclaimed
            )

            state['sea_frontier'] = sea_frontier

    # 3. Stochastic Optimization Loop
    while unclaimed:
        valid_countries = [
            tag
            for tag, state in states.items()
            if (
                state['land_frontier']
                or state['sea_frontier']
            )
        ]
        
        if not valid_countries:
            # Graph contains disconnected subgraphs unreachable from any capital
            break

        # Select expanding tag with uniform probability
        tag = np.random.choice(valid_countries)
        state = states[tag]
        # Prioritize land expansion.
        # Sea expansion only activates when
        # no land frontier remains.

        if state['land_frontier']:
            frontier = list(state['land_frontier'])

        else:
            frontier = list(state['sea_frontier'])

        # Calculate exponential Softmax weights across frontier targets
        weights = []
        for province in frontier:
            satisfaction = ProvinceSatisfaction(G, province, tag)
            weight = satisfaction
            weights.append(weight)

        weights = np.array(weights)
        if weights.sum() == 0:
            weights = np.ones(len(weights)) / len(weights)
        else:
            weights = weights / weights.sum()

        # Stochastic selection of node
        province = np.random.choice(frontier, p=weights)

        # Commit node allocation
        partition.assign(province, tag)
        unclaimed.discard(province)
        state['owned'].add(province)
        state['land_frontier'].discard(province)
        state['sea_frontier'].discard(province)

        # Propagate land frontier
        new_land_frontier = (
            set(G.neighbors(province))
            & unclaimed
        )

        state['land_frontier'] |= new_land_frontier

        # Propagate sea frontier
        if G.nodes[province].get('coastal'):

            new_sea_frontier = (
                coastal_provinces
                & unclaimed
            )

            state['sea_frontier'] |= new_sea_frontier

        # Evict newly claimed province from all competing national frontiers
        for other_state in states.values():
            other_state['land_frontier'].discard(province)
            other_state['sea_frontier'].discard(province)

    return partition

def MultistartPartition(
    G: nx.Graph, 
    iterations: int = 100, 
    verbose: bool = True) -> Partition:

    print("\n=== MULTISTART PARTITION START ===")
    start_time = time.perf_counter()
    
    best_partition = None
    best_score = -1.0

    for iteration in range(iterations):
        # Generate independent candidate
        partition = RandomConnectedPartition(G)

        # Mutate graph state to evaluate fitness
        partition.apply(G)
        ApplySatisfactionScores(G)
        _, _, score = GlobalSatisfaction(G)

        if verbose:
            print(f"[{iteration + 1}/{iterations}] score={score:.6f}")

        # Keep running global maximum configuration
        if score > best_score:
            best_score = score
            best_partition = partition.copy()
            print(f"[NEW BEST] {best_score:.6f}")

    print("\n=== MULTISTART COMPLETE ===")
    print(f"BEST SCORE = {best_score:.6f}")
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    print(f"[PERF] MultistartPartition completed in {elapsed_ms:.2f} ms")
    return best_partition