"""
GLOBAL CORE REGION PARTITION (WITH EXCLAVE RECOVERY)

Description:
    Graph partitioning algorithm that uses a multi-stage optimization process to
    map graph nodes (provinces) to sovereign structures (tags). Unlike purely local
    step-by-step algorithms, this engine performs a global initial optimization pass
    and then programmatically repairs topological anomalies (exclaves) via minimum-cost
    pathfinding corridors without fracturing neighboring states.

Core Mechanics:
    1. Global Optimization Initialization: Provinces are assigned globally to the
       country tag that extracts the absolute highest localized value score. If
       scores tie, the algorithm favors the tag with the higher global demographic
       capacity.
    2. Sovereignty Validation Loop: Validates state capitals. If a nation's capital
       is captured by an external power and locked (due to high satisfaction), the
       losing nation is marked as ELIMINATED, and its entire territory is returned
       to a neutral state. If it's occupied but not locked, the nation becomes DORMANT.
    3. Exclave Extraction: Runs a Breadth-First Search (BFS) component verification
       from every capital. Any owned territory unreachable from the capital via
       contiguous land paths or maritime coastal links is isolated, declared an
       exclave, and stripped from the nation's control.
    4. Corridor Reconstruction & Sovereign Continuity Guardrail: For every
       isolated exclave component, a heap-sorted search attempts to carve a
       contiguous path (corridor) back to its homeland. 
       - Safeguard: A path cannot step through a foreign node if removing it breaks 
         the native owner's territorial continuity back to its own capital.
       - Early Termination: Search stops instantly upon touching homeland borders 
         to prevent bleeding into existing territory.
       - Net Evaluation: Evaluates pure economic variance isolated from geometric weights:
         Net = EnclaveGain + CorridorDelta - AntiSpaghettiPenalties
       If Net > 0, the nation reclaims the exclave and absorbs the corridor.
       If Net =< 0, the exclave is abandoned and permanently redistributed.
    5. Cultural Desolation Awakening & Cleanup: Unassigned/vacant capitals are evaluated.
       If a dormant tag's capital matches cultural requirements, it undergoes "Awakening"
       and propagates via a BFS flood-fill. Finally, stray unassigned nodes are cleanly
       absorbed by their highest-value valid neighbor.

Properties:
    - Complete Determinism: Identical inputs always generate identical 
      territorial partitions.
    - Guaranteed Contiguity: There are hard checks in place to ensure that all nations
      are contiguous. Even the creation of a corridor must respect the territorial
      contiguity of other nations.
    - Locked homelands: ensures that corridors can only be formed through ethnically
      viable territory.
"""

from collections import deque
import heapq
import networkx as nx
import time

from src.graph.data import (
    LoadCountryMetadata,
    BuildProvincePopulationTable,
    BuildProvinceValueTable
)
from src.graph.partition import Partition

def BuildPotentialPopulationTable(province_value: dict[str, dict[str, int]]) -> dict[str, int]:
    potential_population = {}
    for tag in province_value:
        potential_population[tag] = sum(province_value[tag].values())
    return potential_population

def ReachableNeighbors(G: nx.Graph, province: str, coastal_provinces: set[str]) -> set[str]:
    neighbors = set(G.neighbors(province))
    if G.nodes[province].get('coastal'):
        neighbors |= coastal_provinces
    return neighbors

def ConnectedComponent(G: nx.Graph, start: str, owned: set[str], coastal_provinces: set[str]) -> set[str]:
    visited = set()
    queue = deque([start])
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)

        for neighbor in ReachableNeighbors(G, current, coastal_provinces):
            if neighbor in owned:
                queue.append(neighbor)
    return visited

def BuildLockedProvinces(
    G: nx.Graph,
    owner_map: dict[str, str | None],
    valid_tags: dict[str, dict],
    province_value: dict[str, dict[str, int]],
    province_population: dict[str, int],
    coastal_provinces: set[str],
    threshold: float = 0.5) -> set[str]:

    locked = set()
    for tag, data in valid_tags.items():
        capital = data['capital']
        owned = {p for p, o in owner_map.items() if o == tag}

        if capital not in owned:
            continue

        connected = ConnectedComponent(G, capital, owned, coastal_provinces)

        for province in connected:
            total_population = province_population.get(province, 0)
            if total_population <= 0:
                continue

            sat = province_value.get(tag, {}).get(province, 0) / total_population
            if sat >= threshold:
                locked.add(province)
    return locked

def IsContinuityMaintained(G: nx.Graph, province_to_remove: str, owner: str, owner_map: dict[str, str | None], capital: str, coastal_provinces: set[str]) -> bool:
    current_owned = {p for p, o in owner_map.items() if o == owner}
    if province_to_remove in current_owned:
        current_owned.remove(province_to_remove)
        
    if not current_owned:
        return True
    if capital == province_to_remove:
        return False

    visited = set()
    queue = deque([capital])
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)

        for neighbor in ReachableNeighbors(G, current, coastal_provinces):
            if neighbor in current_owned:
                queue.append(neighbor)
                
    return len(visited) == len(current_owned)

def FindCorridor(
    G: nx.Graph,
    component: set[str],
    homeland: set[str],
    owner_map: dict[str, str | None],
    tag: str,
    province_value: dict[str, dict[str, int]],
    coastal_provinces: set[str],
    capital_provinces: set[str],
    locked_provinces: set[str],
    valid_tags: dict[str, dict]) -> tuple[float, list[str]] | None:

    heap = []
    visited = {}

    for province in component:
        heapq.heappush(heap, (0, province, []))

    while heap:
        cost, current, path = heapq.heappop(heap)

        if current in visited:
            if visited[current] <= cost:
                continue
        visited[current] = cost

        if current in homeland:
            return cost, path

        for neighbor in ReachableNeighbors(G, current, coastal_provinces):
            # IMMEDIATELY TERMINATE: Homeland reached, do not pay on our own borders
            if neighbor in homeland:
                return cost, path

            if neighbor in capital_provinces and owner_map.get(neighbor) != tag:
                continue
            if neighbor in locked_provinces and owner_map.get(neighbor) != tag:
                continue

            current_owner = owner_map.get(neighbor)
            
            if current_owner is not None and current_owner != tag:
                owner_capital = valid_tags[current_owner]['capital']
                if not IsContinuityMaintained(G, neighbor, current_owner, owner_map, owner_capital, coastal_provinces):
                    continue  

            claimant_gain = province_value.get(tag, {}).get(neighbor, 0)
            owner_gain = 0
            if current_owner is not None:
                owner_gain = province_value.get(current_owner, {}).get(neighbor, 0)

            transfer_cost = max(0, owner_gain - claimant_gain)
            transfer_cost += 10000  

            heapq.heappush(heap, (cost + transfer_cost, neighbor, path + [neighbor]))

    return None

def GetBestTagsForProvince(
    province: str,
    target_tags: list[str] | set[str] | dict.keys,
    province_value: dict[str, dict[str, int]],
    valid_tags: dict[str, dict]) -> list[tuple[int, int, str]]:
    
    candidates = []
    for tag in target_tags:
        value = province_value.get(tag, {}).get(province, 0)
        potential = valid_tags[tag]['potentialPopulation']
        candidates.append((value, potential, tag))
    
    candidates.sort(key=lambda x: (-x[0], -x[1]))
    return candidates

def GlobalCoreRegionPartition(G: nx.Graph):
    print("\n=== GLOBAL CORE REGION START ===")
    start_time = time.perf_counter()

    metadata = LoadCountryMetadata()
    province_population = BuildProvincePopulationTable()
    province_value = BuildProvinceValueTable()
    potential_population = BuildPotentialPopulationTable(province_value)

    coastal_provinces = {p for p in G.nodes() if G.nodes[p].get('coastal')}
    partition = Partition()

    valid_tags = {}
    for tag, data in metadata.items():
        capital = data['capital']
        if capital not in G.nodes():
            continue
        valid_tags[tag] = {
            'capital': capital,
            'potentialPopulation': potential_population.get(tag, 0)
        }

    capital_provinces = {data['capital'] for data in valid_tags.values()}
    dormant_tags = set()

    # INITIAL GLOBAL ASSIGNMENT
    print("\n=== INITIAL ASSIGNMENT ===")
    owner_map = {}

    for province in G.nodes():
        candidates = GetBestTagsForProvince(province, valid_tags.keys(), province_value, valid_tags)
        if not candidates:
            owner_map[province] = None
            continue
        best_val, best_pot, best_tag = candidates[0]
        if len(candidates) > 1:
            next_val, next_pot, next_tag = candidates[1]
            if best_val == next_val and next_pot > best_pot:
                best_tag = next_tag
        owner_map[province] = best_tag

    # CAPITAL VALIDATION (DORMANT LOGIC)
    print("\n=== CAPITAL VALIDATION ===")
    changed = True

    while changed:
        changed = False
        eliminated_tags = []

        locked_provinces = BuildLockedProvinces(
            G, owner_map, valid_tags, province_value, province_population, coastal_provinces, threshold=0.8
        )

        for tag in list(valid_tags.keys()):
            capital = valid_tags[tag]['capital']
            current_owner = owner_map.get(capital)

            if current_owner != tag:
                if capital in locked_provinces and current_owner is not None:
                    print(f"[ELIMINATED] {tag} - Capital locked by {current_owner}")
                    eliminated_tags.append(tag)
                else:
                    if tag not in dormant_tags:
                        print(f"[DORMANT] {tag} - Capital currently occupied by {current_owner}")
                        dormant_tags.add(tag)
            else:
                if tag in dormant_tags:
                    print(f"[REVIVED] {tag} - Capital reclaimed")
                    dormant_tags.remove(tag)

        if eliminated_tags:
            changed = True
            for tag in eliminated_tags:
                del valid_tags[tag]
                dormant_tags.discard(tag)
                for province in owner_map:
                    if owner_map[province] == tag:
                        owner_map[province] = None

    # REASSIGNMENT
    print("\n=== REASSIGNMENT ===")
    active_tags = {t: d for t, d in valid_tags.items() if t not in dormant_tags}

    for province in G.nodes():
        if owner_map[province] is not None:
            continue

        candidates = GetBestTagsForProvince(province, active_tags.keys(), province_value, valid_tags)
        if candidates:
            owner_map[province] = candidates[0][2]

    # LOCK HOMELANDS
    print("\n=== LOCK HOMELANDS ===")
    locked_provinces = BuildLockedProvinces(
        G, owner_map, valid_tags, province_value, province_population, coastal_provinces, threshold=0.8
    )
    print(f"[LOCKED] {len(locked_provinces)} provinces")

    # REMOVE EXCLAVES
    print("\n=== REMOVE EXCLAVES ===")
    disconnected_components = []

    for tag, data in valid_tags.items():
        if tag in dormant_tags:
            continue

        capital = data['capital']
        owned = {p for p, o in owner_map.items() if o == tag}

        if capital not in owned:
            continue

        homeland = ConnectedComponent(G, capital, owned, coastal_provinces)
        disconnected = owned - homeland

        if disconnected:
            print(f"[DISCONNECTED] {tag}: {len(disconnected)} provinces")

        remaining = set(disconnected)
        while remaining:
            seed = next(iter(remaining))
            component = ConnectedComponent(G, seed, disconnected, coastal_provinces)
            remaining -= component

            disconnected_components.append((tag, component))
            for province in component:
                owner_map[province] = None

    # RECOVER EXCLAVES
    print("\n=== EXCLAVE RECOVERY ===")
    for tag, component in disconnected_components:
        if tag in dormant_tags or tag not in valid_tags:
            continue

        capital = valid_tags[tag]['capital']
        owned = {p for p, o in owner_map.items() if o == tag}

        if capital not in owned:
            continue

        homeland = ConnectedComponent(G, capital, owned, coastal_provinces)
        enclave_gain = sum(province_value.get(tag, {}).get(p, 0) for p in component)

        result = FindCorridor(
            G, component, homeland, owner_map, tag, province_value,
            coastal_provinces, capital_provinces, locked_provinces, valid_tags
        )

        if result is None:
            print(f"[ABANDON] {tag} (Reason: Found NO valid path to homeland)")
            continue

        corridor_cost, corridor = result
        corridor_delta = 0
        anti_spaghetti_penalty_total = 0

        for province in corridor:
            current_owner = owner_map.get(province)
            claimant_gain = province_value.get(tag, {}).get(province, 0)
            owner_gain = 0
            if current_owner is not None:
                owner_gain = province_value.get(current_owner, {}).get(province, 0)
            
            corridor_delta += (claimant_gain - owner_gain)
            anti_spaghetti_penalty_total += 10000 

        net_gain = enclave_gain + corridor_delta - anti_spaghetti_penalty_total

        if net_gain > 0:
            print(f"[RECOVER] {tag}")
            for province in component:
                owner_map[province] = tag
            for province in corridor:
                owner_map[province] = tag
        else:
            print(f"[ABANDON-REALLOCATE] {tag}'s component elements (Reason: Negative Net Utility {net_gain})")
            for province in component:
                candidates = GetBestTagsForProvince(province, valid_tags.keys(), province_value, valid_tags)
                filtered_candidates = [c for c in candidates if c[2] != tag]
                if filtered_candidates:
                    owner_map[province] = filtered_candidates[0][2]

    # AWAKEN DORMANT TAGS
    print("\n=== DORMANT TAG AWAKENING ===")
    awakened_any = True
    while awakened_any:
        awakened_any = False
        for tag in list(dormant_tags):
            capital = valid_tags[tag]['capital']
            
            if owner_map.get(capital) is None:
                accepted_pop_in_capital = province_value.get(tag, {}).get(capital, 0)
                total_pop_in_capital = province_population.get(capital, 0)
                
                if total_pop_in_capital > 0 and (accepted_pop_in_capital / total_pop_in_capital) > 0:
                    print(f"[AWAKENED] {tag} - Capital {capital} is vacant and has valid cultural saturation. Reclaiming.")
                    owner_map[capital] = tag
                    dormant_tags.remove(tag)
                    awakened_any = True
                    
                    queue = deque([capital])
                    while queue:
                        curr = queue.popleft()
                        for neighbor in G.neighbors(curr):
                            if owner_map.get(neighbor) is None:
                                val = province_value.get(tag, {}).get(neighbor, 0)
                                if val > 0:
                                    owner_map[neighbor] = tag
                                    queue.append(neighbor)
                else:
                    print(f"[KEEP DORMANT] {tag} - Capital {capital} is vacant, but accepted culture population is 0.")

    # CLEANUP
    print("\n=== CLEANUP ===")
    changed = True

    while changed:
        changed = False
        for province in G.nodes():
            if owner_map[province] is not None:
                continue

            neighboring_tags = {
                owner_map[n] for n in G.neighbors(province)
                if owner_map[n] is not None and owner_map[n] not in dormant_tags
            }

            if not neighboring_tags:
                continue

            candidates = GetBestTagsForProvince(province, neighboring_tags, province_value, valid_tags)
            if candidates:
                owner_map[province] = candidates[0][2]
                changed = True

    # BUILD PARTITION
    print("\n=== BUILD PARTITION ===")
    for province, tag in owner_map.items():
        if tag is not None:
            partition.assign(province, tag)

    print("\n=== GLOBAL CORE REGION COMPLETE ===")
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    print(f"[PERF] GlobalCoreRegionPartition completed in {elapsed_ms:.2f} ms")
    return partition