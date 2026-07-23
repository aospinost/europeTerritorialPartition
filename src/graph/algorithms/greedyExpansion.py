"""
GREEDY FRONTIER EXPANSION PARTITION

Description:
    This algorithm implements a deterministic greedy frontier-expansion
    heuristic for graph partitioning over a political geography network.
    Countries iteratively absorb adjacent provinces by maximizing local
    cultural satisfaction while preserving strict territorial contiguity.

Core Mechanics:
    1. Capital Frontier Initialization:
       Every sovereign tag begins in a dormant state with its frontier
       initialized exclusively at its capital node. Provinces remain globally
       unclaimed until explicitly assigned.

    2. Country Priority Evaluation:
       During each iteration, all active frontiers are evaluated.
       Countries are ranked according to:
       - Remaining globally satisfiable population.
       - Current sovereignty status (already founded or dormant).

       This establishes the expansion priority order for the iteration.

    3. Coherent Frontier Claim:
       The algorithm scans countries in priority order searching for the
       first frontier province whose cultural satisfaction ratio exceeds
       a minimum threshold (MIN_SATISFACTION = 0.5).

       Satisfaction is defined as:

       s = accepted population / total province population

       The highest-scoring frontier province for that country is selected
       and immediately assigned.

    4. Global Greedy Fallback:
       If no frontier province satisfies the coherence threshold,
       the algorithm performs a global fallback search across every
       country's frontier and selects the province with the highest
       available satisfaction score regardless of threshold.

    5. Frontier Propagation:
       Once a province is assigned:
       - The node is removed from the global unclaimed pool.
       - The owning country's frontier expands to neighboring provinces.
       - Coastal provinces activate maritime frontier propagation,
         allowing access to all remaining unclaimed coastal nodes.

       The claimed province is simultaneously removed from all competing
       national frontiers.

    6. Cleanup Pass:
       After frontier exhaustion, any remaining orphaned provinces are
       absorbed by the first valid bordering country encountered.

Properties:
    - Complete Determinism: Identical inputs always generate identical 
      territorial partitions.
    - Guaranteed Contiguity: Territorial growth occurs exclusively
      through frontier propagation, preventing disconnected exclaves.
    - Coherence-Driven Expansion: The minimum satisfaction threshold
      threshold biases the algorithm toward culturally compatible
      territorial growth whenever possible.
"""

import networkx as nx
import time

from src.graph.data import (
    LoadCountryMetadata,
    BuildProvincePopulationTable,
    BuildProvinceValueTable
)
from src.graph.partition import Partition

def GreedyExpansionPartition(G: nx.Graph) -> Partition:

    print("\n=== GREEDY PARTITION PARTITION START ===")
    start_time = time.perf_counter()

    metadata = LoadCountryMetadata()
    province_population = BuildProvincePopulationTable()
    province_value = BuildProvinceValueTable()

    partition = Partition()
    unclaimed = set(G.nodes())


    coastal_provinces = {
        p for p in G.nodes()
        if G.nodes[p].get('coastal')
    }

    # BUILD BEST CLAIMANT TABLE
    province_best_owner = {}
    all_provinces = set()

    for tag in province_value:
        all_provinces |= set(
            province_value[tag].keys()
        )

    for province in all_provinces:
        best_tag = None
        best_value = -1
        for tag in province_value:
            value = (
                province_value[tag]
                .get(province, 0)
            )
            if value > best_value:
                best_value = value
                best_tag = tag

        province_best_owner[province] = best_tag

    # COUNTRY STATES
    states = {}

    # INITIALIZATION
    for tag, data in metadata.items():
        capital = data['capital']
        if capital not in G.nodes():
            print(f"[SKIP] {tag} invalid capital")
            continue
        states[tag] = {
            'exists': False,
            'owned': set(),

            # Countries begin only able to claim capital
            'frontier': {capital},
            'capital': capital
        }

        print(
            f"[DORMANT] {tag} "
            f"capital={capital}"
        )

    # MAIN LOOP
    iteration = 0

    while True:
        iteration += 1
        print(f"\n=== ITERATION {iteration} ===")

        evaluation_table = []

        # BUILD COUNTRY EVALUATION TABLE
        for tag, state in states.items():
            frontier = {
                p for p in state['frontier']
                if p in unclaimed
            }

            state['frontier'] = frontier

            if not frontier:
                continue

            # Total remaining satisfiable population
            available_population = 0
            for province in unclaimed:
                available_population += (
                    province_value
                    .get(tag, {})
                    .get(province, 0)
                )

            evaluation_table.append({
                'tag': tag,
                'exists': int(state['exists']),
                'availablePopulation': available_population,
                'availableProvinces': list(frontier)
            })

        # TERMINATION
        if not evaluation_table:
            print("No valid countries remain.")
            break

        # SELECT BEST COUNTRY
        best_country_row = max(
            evaluation_table,
            key=lambda x: (
                x['availablePopulation'],
                x['exists']
            )
        )

        best_tag = best_country_row['tag']

        print(
            f"[COUNTRY] {best_tag} "
            f"availablePopulation="
            f"{best_country_row['availablePopulation']} "
            f"exists="
            f"{best_country_row['exists']}"
        )

        # PROVINCE PRIORITY
        def ProvincePriority(province):
            province_value_score = (
                province_value
                .get(best_tag, {})
                .get(province, 0)
            )

            total_population = province_population.get(province, 0)

            if total_population > 0:
                satisfaction_score = province_value_score / total_population
            else:
                satisfaction_score = 0
            return satisfaction_score, province_value_score

        # INITIAL BEST PROVINCE
        frontier = best_country_row['availableProvinces']

        best_province = max(frontier, key=ProvincePriority)
        best_gain = (
            province_value
            .get(best_tag, {})
            .get(best_province, 0)
        )
        best_population = (
            province_population
            .get(best_province, 0)
        )

        if best_population > 0:
            best_satisfaction = best_gain / best_population
        else:
            best_satisfaction = 0

        MIN_SATISFACTION = 0.5

        # Sort countries by algorithm priority
        sorted_countries = sorted(
            evaluation_table,
            key=lambda x: (
                x['availablePopulation'],
                x['exists']
            ),
            reverse=True
        )

        # Search for first coherent country/province pair
        found_valid_claim = False
        for candidate_country in sorted_countries:
            candidate_tag = candidate_country['tag']
            candidate_frontier = candidate_country['availableProvinces']

            # Skip empty frontier
            if not candidate_frontier:
                continue

            # Province priority for candidate country
            def CandidatePriority(province):
                value = (
                    province_value
                    .get(candidate_tag, {})
                    .get(province, 0)
                )

                population = province_population.get(province, 0)

                if population > 0:
                    score = value / population
                else:
                    score = 0
                return score, value

            candidate_province = max(
                candidate_frontier,
                key=CandidatePriority
            )

            candidate_gain = (
                province_value
                .get(candidate_tag, {})
                .get(candidate_province, 0)
            )

            candidate_population = (
                province_population
                .get(candidate_province, 0)
            )

            if candidate_population > 0:
                candidate_satisfaction = candidate_gain / candidate_population
            else:
                candidate_satisfaction = 0

            # Accept first coherent option
            if candidate_satisfaction >= MIN_SATISFACTION:
                best_tag = candidate_tag
                best_country_row = candidate_country
                best_province = candidate_province
                best_gain = candidate_gain
                best_population = candidate_population
                best_satisfaction = candidate_satisfaction

                found_valid_claim = True

                print(
                    f"[COHERENT] "
                    f"{best_tag} -> "
                    f"{best_province} "
                    f"({best_satisfaction:.3f})"
                )

                break

        if not found_valid_claim:
            print(
                "[FALLBACK] "
                "No coherent claim found"
            )

            fallback_tag = None
            fallback_province = None
            fallback_satisfaction = -1
            fallback_gain = -1
            fallback_population = 0

            for candidate_country in sorted_countries:
                candidate_tag = candidate_country['tag']
                candidate_frontier = candidate_country['availableProvinces']

                if not candidate_frontier:
                    continue
                for province in candidate_frontier:
                    value = (
                        province_value
                        .get(candidate_tag, {})
                        .get(province, 0)
                    )

                    population = province_population.get(province, 0)

                    if population > 0:
                        satisfaction = value / population
                    else:
                        satisfaction = 0

                    # Global best fallback

                    if (satisfaction > fallback_satisfaction
                        or (satisfaction == fallback_satisfaction and value > fallback_gain)):
                        fallback_tag = candidate_tag
                        fallback_province = province
                        fallback_satisfaction = satisfaction
                        fallback_gain = value
                        fallback_population = population

            # Apply fallback
            best_tag = fallback_tag
            best_province = fallback_province
            best_satisfaction = fallback_satisfaction
            best_gain = fallback_gain
            best_population = fallback_population

            print(
                f"[GLOBAL FALLBACK] "
                f"{best_tag} -> {best_province} "
                f"({best_satisfaction:.3f})"
            )

        # CLAIM
        print(
            f"[CLAIM] {best_tag} "
            f"claims {best_province} "
            f"gain={best_gain} "
            f"satisfaction={best_satisfaction:.3f}"
        )

        # COUNTRY FORMATION
        state = states[best_tag]

        if not state['exists']:
            state['exists'] = True
            print(f"[FOUNDED] {best_tag}")

        # ASSIGN PROVINCE
        partition.assign(best_province, best_tag)
        unclaimed.discard(best_province)
        state['owned'].add(best_province)
        state['frontier'].discard(best_province)

        # LAND FRONTIER EXPANSION
        new_frontier = set(G.neighbors(best_province)) & unclaimed

        # COASTAL TELEPORTATION
        if G.nodes[best_province].get('coastal'):
            new_frontier |= coastal_provinces & unclaimed
            print(
                f"[COASTAL] "
                f"{len(coastal_provinces & unclaimed)} "
                f"coastal provinces reachable"
            )

        state['frontier'] |= new_frontier

        # REMOVE CLAIMED PROVINCE
        for other_state in states.values():
            other_state['frontier'].discard(best_province)

    # CLEANUP PASS
    print("\n=== CLEANUP PASS ===")
    for province in list(unclaimed):
        neighbors = set(G.neighbors(province))
        bordering = [
            partition.country_of(n)
            for n in neighbors
            if partition.country_of(n)
            is not None
        ]

        if bordering:
            partition.assign(province, bordering[0])

    print("\n=== GREEDY PARTITION PARTITION COMPLETE ===")
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    print(f"[PERF] GreedyPartition completed in {elapsed_ms:.2f} ms")
    return partition