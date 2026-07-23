"""
SEQUENTIAL DEPTH-FIRST SEARCH (DFS) PARTITION

Description:
    This algorithm implements a structured, stateful "Baton-Passing" sequence 
    modeled on a Depth-First Search (DFS)  expansion to divide a graph into
    contiguous national subgraphs (tags). Instead of a global, parallel race condition,
    countries are arranged in a strict queue and take turns expanding their borders one
    at a time using a single localized exploration stack.

Core Mechanics:
    1. Queue Assembly & Pre-shuffling:
       Determines processing order using an input priority tag queue configuration. 
       Any remaining countries not specified in the custom configuration are 
       sorted alphabetically and appended to the back of the queue. Nodes are 
       deterministically sorted to strip out hidden processing sequence artifacts.
    2. Sovereignty Railguards & Capital Seeding:
       When a country receives the "baton," the algorithm checks if its designated 
       capital node is unassigned. If its capital was already consumed by a 
       prior country's expansion phase, the country is immediately skipped and 
       cannot form. If free, the capital is assigned and seeds the local DFS stack.
    3. Dedicated DFS Snake Expansion Loop:
       The active country expands using a stateful stack framework that checks three 
       hierarchical routing directives at every step:
       - Rule A (Snaking): Prioritizes adjacent unassigned land neighbors that 
         possess a positive cultural extraction score (value > 0).
       - Rule B (Maritime Leaps): If landlocked options are completely exhausted 
         but the current node is coastal, the country triggers a maritime jump, 
         scanning the entire global map for unassigned coastal nodes matching its culture.
    4. Hybrid Domino Cleanup Pass:
       Once the baton queue runs dry, any remaining orphaned unassigned nodes 
       undergo an iterative cleanup pass. Nodes are absorbed by the first valid 
       bordering nation found via standard land connections, cascading across 
       the maritime coastal matrix if dealing with isolated islands.

Properties:
    - Highly Concentrated Territorials: Creates long, snake-like continuous strips 
      of territory resembling historical migration/expansion paths.
    - Strong First-Mover Advantage: Nations placed early in the baton queue possess 
      massive territorial advantages, capable of trapping later nations inside 
      their own capitals or even claiming their capitals preventing spawn.
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

def DFSPartition(G: nx.Graph, priority_tags: list[str] = None) -> Partition:
    print("\n=== STRICT SEQUENTIAL BATON DFS START ===")
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
        # Sanitize to ensure user inputs exist in your valid tag dataset
        for tag in priority_tags:
            if tag in all_unique_tags and tag not in allowed_tags:
                allowed_tags.append(tag)
                
    # Append the remaining tags sorted alphabetically behind the priority list
    remaining_tags = sorted([t for t in all_unique_tags if t not in allowed_tags])
    allowed_tags.extend(remaining_tags)
    partition = Partition()
    unclaimed = sorted(list(G.nodes()))
    coastal_provinces = sorted([p for p in G.nodes() if G.nodes[p].get('coastal')])
    
    dfs_history_rows = []
    iteration = 0

    # 2. Sequential Country Processing
    for tag in allowed_tags:
        if tag not in metadata:
            continue
            
        capital = metadata[tag]['capital']
        
        # CRITICAL FIX: A country can ONLY exist if it controls its capital.
        # If the capital is already claimed by a previous country, this tag is skipped.
        if capital not in unclaimed:
            print(f"[BATON] Country {tag} cannot exist (Capital {capital} already claimed). Skipping.")
            continue

        # Initialize the stack at the valid capital
        stack = [capital]
        partition.assign(capital, tag)
        unclaimed.remove(capital)
        
        dfs_history_rows.append({
            'step_id': len(dfs_history_rows) + 1,
            'iteration': iteration,
            'tag': tag,
            'action_type': 'INITIALIZE_BATON',
            'province': capital,
            'is_coastal': int(G.nodes[capital].get('coastal', False)),
            'stack_depth': 1,
            'priority_score': 0.0
        })

        # 3. Dedicated DFS Snake Loop
        while stack and unclaimed:
            # Secondary Guard: Double-check we still own our capital 
            # (Strict adherence to the metadata rule)
            if partition.country_of(capital) != tag:
                print(f"[BATON] Country {tag} lost control of its capital {capital}! Freezing expansion.")
                break
                
            iteration += 1
            current_province = stack[-1]
            
            # Isolate neighbors and shuffle to break structural ID bias
            land_neighbors = sorted([n for n in G.neighbors(current_province) if n in unclaimed])
            if land_neighbors:
                np.random.shuffle(land_neighbors)
            
            # Filter culturally matching land targets
            cultural_land = [p for p in land_neighbors if province_value.get(tag, {}).get(p, 0) > 0]
            
            next_province = None
            is_leap_step = False
            
            # Rule A: Prioritize immediate cultural expansion (Snaking)
            if cultural_land:
                next_province = cultural_land[0]
                
            # Rule B: Maritime jumps if stuck on a coast
            elif G.nodes[current_province].get('coastal'):
                unclaimed_coastal = [p for p in coastal_provinces if p in unclaimed]
                cultural_coastal = sorted([p for p in unclaimed_coastal if province_value.get(tag, {}).get(p, 0) > 0])
                
                if cultural_coastal:
                    np.random.shuffle(cultural_coastal)
                    next_province = cultural_coastal[0]
                    is_leap_step = True
                
            # Execute Step or Backtrack
            if next_province is not None:
                partition.assign(next_province, tag)
                unclaimed.remove(next_province)
                stack.append(next_province)
                
                dfs_history_rows.append({
                    'step_id': len(dfs_history_rows) + 1,
                    'iteration': iteration,
                    'tag': tag,
                    'action_type': 'MARITIME_LEAP' if is_leap_step else 'CLAIM_LAND',
                    'province': next_province,
                    'is_coastal': int(G.nodes[next_province].get('coastal', False)),
                    'stack_depth': len(stack),
                    'priority_score': 1.0
                })
            else:
                popped_province = stack.pop()
                
                dfs_history_rows.append({
                    'step_id': len(dfs_history_rows) + 1,
                    'iteration': iteration,
                    'tag': tag,
                    'action_type': 'BACKTRACK',
                    'province': popped_province,
                    'is_coastal': int(G.nodes[popped_province].get('coastal', False)),
                    'stack_depth': len(stack),
                    'priority_score': 0.0
                })
        
        print(f"[BATON] Country {tag} finished its expansion phase.")

    # 4. FIXED: Hybrid Land-Maritime Domino Cleanup Sweep
    if unclaimed:
        print(f"[CLEANUP] Mopping up {len(unclaimed)} orphaned provinces using land & maritime proximity.")
        
        while True:
            claimed_in_this_pass = 0
            for province in list(unclaimed):
                assigned_neighbor_tag = None
                
                # Step A: Check standard land neighbors first
                for neighbor in sorted(list(G.neighbors(province))):
                    nbr_country = partition.country_of(neighbor)
                    if nbr_country is not None:
                        assigned_neighbor_tag = nbr_country
                        break
                
                # Step B: If it's a coastal island with no claimed land neighbors, look across the water
                if assigned_neighbor_tag is None and G.nodes[province].get('coastal'):
                    # Find all claimed coastal provinces currently on the map
                    claimed_coastal = [p for p in coastal_provinces if partition.country_of(p) is not None]
                    
                    if claimed_coastal:
                        # Fallback to the closest claimed coastal landmass using your graph architecture 
                        # or sorting by ID as a stable tiebreaker.
                        # (If your graph has sea-lane connections built-in, use those; otherwise, grab the first available coastal neighbor)
                        assigned_neighbor_tag = partition.country_of(claimed_coastal[0])
                
                # If we found a valid homeland anchor via land or sea, capture it
                if assigned_neighbor_tag is not None:
                    partition.assign(province, assigned_neighbor_tag)
                    unclaimed.remove(province)
                    claimed_in_this_pass += 1
                    
                    dfs_history_rows.append({
                        'step_id': len(dfs_history_rows) + 1,
                        'iteration': iteration,
                        'tag': assigned_neighbor_tag,
                        'action_type': 'CLEANUP_SWEEP',
                        'province': province,
                        'is_coastal': int(G.nodes[province].get('coastal', False)),
                        'stack_depth': -1,
                        'priority_score': 0.0  
                    })
            
            if claimed_in_this_pass == 0:
                break
    
    print("=== SEQUENTIAL BATON DFS COMPLETE ===")
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    print(f"[PERF] DFSPartition completed in {elapsed_ms:.2f} ms")
    return partition