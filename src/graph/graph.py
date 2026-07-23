import networkx as nx
import pandas as pd
from src.graph.data import LoadCountryMetadata
from src.graph.metrics import ApplySatisfactionScores
from src.graph.partition import Partition
from src.config import (
    IMPUTATED_VERTEX_CSV,
    EDGE_CSV,
    POPULATION_CSV,
)

def LoadGeographicGraph() -> nx.Graph:
    vertex_df = pd.read_csv(IMPUTATED_VERTEX_CSV)
    edges_df = pd.read_csv(EDGE_CSV)
    population_df = pd.read_csv(POPULATION_CSV)

    G = nx.Graph()

    # NODES
    for _, row in vertex_df.iterrows():
        G.add_node(
            row['province'],
            name=row['name'],
            base_color=(
                row['red'] / 255,
                row['green'] / 255,
                row['blue'] / 255
            ),
            color=(
                row['red'] / 255,
                row['green'] / 255,
                row['blue'] / 255
            ),
            pos=(row['unit_x'], row['unit_y']),
            coastal=row['coastal']
        )

    # EDGES
    for _, row in edges_df.iterrows():
        G.add_edge(row['province_1'],row['province_2'])

    # POPULATION DATA
    province_pops = {}
    for province, group in population_df.groupby('province'):
        pops = []
        for _, row in group.iterrows():
            pops.append((row['culture'], row['population']))
        province_pops[province] = pops

    # Attach directly to graph
    for province in G.nodes():
        G.nodes[province]['population'] = (
            province_pops.get(province, [])
        )
    
    return G

def LoadPartitionedGraph(base_graph: nx.Graph, partition: Partition) -> nx.Graph:
    G = base_graph.copy()

    country_metadata = LoadCountryMetadata()

    # APPLY COUNTRY DATA
    for province in G.nodes():
        # Get the 3-letter tag from your partition object
        tag = partition.country_of(province) 
        
        # Keep the tag on the node just in case you need it for keys/lookups
        G.nodes[province]['country_tag'] = tag 
        
        if tag in country_metadata:
            meta = country_metadata[tag]
            # Standardized: 'country' attribute is the human-readable name
            G.nodes[province]['country'] = meta['name'] 
            G.nodes[province]['color'] = meta['color']
        else:
            # Fallback if tag is missing from metadata sheet
            G.nodes[province]['country'] = tag
    
    # REMOVE INTERNATIONAL EDGES
    edges_to_remove = []
    for u, v in G.edges():
        country_u = G.nodes[u].get('country_tag')
        country_v = G.nodes[v].get('country_tag')
        if country_u != country_v:
            edges_to_remove.append((u, v))

    G.remove_edges_from(edges_to_remove)

    # SATISFACTION METRICS
    ApplySatisfactionScores(G)

    return G