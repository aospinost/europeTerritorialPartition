"""
SEQUENTIAL BREADTH-FIRST SEARCH (BFS) PARTITION

Description:
    This algorithm implements a structured "Baton-Passing" graph partitioning
    heuristic leveraging Breadth-First Search (BFS) mechanics. Instead of building
    narrow, snake-like structures typical of a DFS approach, this engine expands 
    outward radially from sovereign roots. It generates highly cohesive, compact, 
    and block-shaped territorial subgraphs by advancing layer-by-layer.

Core Mechanics:
    1. Synchronous Layer 0 Spawning:
       All valid national capitals are placed onto the map simultaneously at the 
       beginning of execution. This forms a structural anchor for every active tag 
       and initializes their respective First-In, First-Out (FIFO) tracking queues. 
       If a country's capital has already been claimed, it is barred from spawning.
    2. Turn-Based Radial Expansion Loop:
       Nations process sequentially based on a customized priority baton queue. When 
       a tag receives the baton, it exhausts its active FIFO queue layer by layer. 
       For every popped node, it executes a two-phase expansion routing procedure:
       - Phase A (Standard Radial Flow): It checks all unassigned immediate land 
         neighbors. Those with a positive cultural value score (value > 0) 
         are captured and appended to the tail of the country's local queue.
       - Phase B (Native Maritime Island Jumping): If the current evaluation node 
         is flagged as coastal, the tag scans the global network map for all 
         unclaimed coastal nodes matching its cultural preferences. These target 
         islands are annexed instantly and injected into the queue to serve as 
         new outward-radiating nodes.
    3. Structural Capitulation Check:
       Before any country is permitted to execute its expansion phase, the algorithm 
       verifies capital ownership. If a competitor has managed to encircle or 
       occupy the tag's starting capital node, the nation's expansion freeze-locks.
    4. Proximity Domino Cleanup Pass:
       Once the baton queue has run its course, any remaining unassigned land scraps 
       undergo a multi-pass cleanup loop. These orphan nodes are cleanly absorbed 
       by the first valid contiguous country neighbor found.
Properties:
    - High Compactness Ratio: Naturally minimizes perimeter-to-area ratios, yielding 
      well-rounded, compact geographic clusters rather than scattered shapes.
    - Front-Loaded Congestion Protection: Simultaneous capital placement prevents 
      early-turn nations from completely suffocating later nations at step zero.
"""

import networkx as nx
import numpy as np
import pandas as pd
import time

from src.config import ALLOWED_COUNTRY_ACCEPTANCE_CSV
from src.graph.data import (
    BuildProvinceValueTable,
    LoadCountryMetadata
)
from src.graph.partition import Partition

def BFSPartition(G: nx.Graph, priority_tags: list[str] = None) -> Partition:
    print("\n=== STRICT SEQUENTIAL BATON BFS START ===")
    start_time = time.perf_counter()
    
    # 1. Load railguards
    allowed_df = pd.read_csv(ALLOWED_COUNTRY_ACCEPTANCE_CSV)
    province_value = BuildProvinceValueTable()   
    metadata = LoadCountryMetadata()
    
    # Extract unique valid tags from your dataframe
    all_unique_tags = set(allowed_df['tag'].unique())
    
    # Build the customized baton queue order
    allowed_tags = []
    if priority_tags is not None:
        for tag in priority_tags:
            if tag in all_unique_tags and tag not in allowed_tags:
                allowed_tags.append(tag)
                
    # Append the remaining tags sorted alphabetically behind the priority list
    remaining_tags = sorted([t for t in all_unique_tags if t not in allowed_tags])
    allowed_tags.extend(remaining_tags)
    
    partition = Partition()
    unclaimed = sorted(list(G.nodes()))
    coastal_provinces = sorted([p for p in G.nodes() if G.nodes[p].get('coastal')])
    
    bfs_history_rows = []
    iteration = 0
    
    # Track the active FIFO expansion queue for each tag dynamically
    queues = {}

    # 2. Spawn ALL Valid Capitals Simultaneously (Layer 0 Initialization)
    for tag in allowed_tags:
        if tag not in metadata:
            continue
            
        capital = metadata[tag]['capital']
        
        if capital not in unclaimed:
            print(f"[BATON] Country {tag} cannot exist (Capital {capital} already claimed). Skipping.")
            continue
            
        partition.assign(capital, tag)
        unclaimed.remove(capital)
        queues[tag] = [capital]
        
        bfs_history_rows.append({
            'step_id': len(bfs_history_rows) + 1,
            'iteration': iteration,
            'tag': tag,
            'action_type': 'INITIALIZE_BATON',
            'province': capital,
            'is_coastal': int(G.nodes[capital].get('coastal', False)),
            'queue_depth': 1,
            'priority_score': 0.0
        })

    # 3. Dedicated BFS Expansion Loops (Iterating Layer-by-Layer)
    for tag in allowed_tags:
        if tag not in queues:
            continue
            
        capital = metadata[tag]['capital']
        if partition.country_of(capital) != tag:
            print(f"[BATON] Country {tag} lost control of its capital {capital}! Freezing expansion.")
            continue

        while queues[tag] and unclaimed:
            iteration += 1
            current_province = queues[tag].pop(0)
            
            # --- PHASE A: Standard Land Contiguous Expansion ---
            land_neighbors = sorted([n for n in G.neighbors(current_province) if n in unclaimed])
            if land_neighbors:
                np.random.shuffle(land_neighbors)
                
            cultural_targets = [p for p in land_neighbors if province_value.get(tag, {}).get(p, 0) > 0]
            
            for next_province in cultural_targets:
                if next_province in unclaimed:
                    partition.assign(next_province, tag)
                    unclaimed.remove(next_province)
                    queues[tag].append(next_province)
                    
                    bfs_history_rows.append({
                        'step_id': len(bfs_history_rows) + 1,
                        'iteration': iteration,
                        'tag': tag,
                        'action_type': 'CLAIM_LAND',
                        'province': next_province,
                        'is_coastal': int(G.nodes[next_province].get('coastal', False)),
                        'queue_depth': len(queues[tag]),
                        'priority_score': 1.0
                    })
            
            # --- PHASE B: NATIVE MARITIME ISLAND JUMPING ---
            # If the current node we are expanding from is coastal, check for core islands
            if G.nodes[current_province].get('coastal'):
                # Find all unclaimed coastal nodes anywhere on the map that match this country's culture
                unclaimed_coastal = [p for p in coastal_provinces if p in unclaimed]
                cultural_islands = sorted([p for p in unclaimed_coastal if province_value.get(tag, {}).get(p, 0) > 0])
                
                # Snatch up these core islands immediately during initial expansion
                for island in cultural_islands:
                    if island in unclaimed:
                        partition.assign(island, tag)
                        unclaimed.remove(island)
                        queues[tag].append(island)  # Drop into queue so the island group expands internally!
                        
                        bfs_history_rows.append({
                            'step_id': len(bfs_history_rows) + 1,
                            'iteration': iteration,
                            'tag': tag,
                            'action_type': 'MARITIME_LEAP',
                            'province': island,
                            'is_coastal': 1,
                            'queue_depth': len(queues[tag]),
                            'priority_score': 1.0
                        })
                    
        print(f"[BATON] Country {tag} finished its expansion phase.")

    # 4. Cleanup Sweep (Now only mopping up true contiguous land scraps)
    if unclaimed:
        print(f"[CLEANUP] Mopping up {len(unclaimed)} remaining contiguous land scraps.")
        
        while True:
            claimed_in_this_pass = 0
            for province in list(unclaimed):
                assigned_neighbor_tag = None
                
                for neighbor in sorted(list(G.neighbors(province))):
                    nbr_country = partition.country_of(neighbor)
                    if nbr_country is not None:
                        assigned_neighbor_tag = nbr_country
                        break
                
                if assigned_neighbor_tag is not None:
                    partition.assign(province, assigned_neighbor_tag)
                    unclaimed.remove(province)
                    claimed_in_this_pass += 1
                    
                    bfs_history_rows.append({
                        'step_id': len(bfs_history_rows) + 1,
                        'iteration': iteration,
                        'tag': assigned_neighbor_tag,
                        'action_type': 'CLEANUP_SWEEP',
                        'province': province,
                        'is_coastal': int(G.nodes[province].get('coastal', False)),
                        'queue_depth': -1,
                        'priority_score': 0.0  
                    })
            
            if claimed_in_this_pass == 0:
                break

    print("=== SEQUENTIAL BATON BFS COMPLETE ===")
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    print(f"[PERF] BFSPartition completed in {elapsed_ms:.2f} ms")
    return partition