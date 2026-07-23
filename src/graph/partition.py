import networkx as nx
import pandas as pd
from src.graph.data import LoadCountryMetadata
from src.graph.metrics import ApplySatisfactionScores
from src.config import (
    PARTITIONS_DIR,
    PARTITIONS_STATS_DIR
)

class Partition:
    def __init__(self) -> None:
        self.assignment = {}
        return

    def assign(self, province: int, country: str) -> None:
        self.assignment[province] = country
        return

    def country_of(self, province: int) -> str | None:
        return self.assignment.get(province)

    def provinces_of(self, country: str) -> list[int]:
        return [
            p for p, c in self.assignment.items()
            if c == country
        ]

    def countries(self) -> set[str]:
        return set(self.assignment.values())
    
    def apply(self, G: nx.Graph) -> None:
        metadata = LoadCountryMetadata()
        for province, country_tag in self.assignment.items():
            if province not in G.nodes():
                continue

            G.nodes[province]['country_tag'] = country_tag
            G.nodes[province]['country'] = metadata.get(country_tag, {}).get('name')
        return

    def copy(self) -> "Partition":
        new_partition = Partition()
        new_partition.assignment = self.assignment.copy()
        return new_partition
    
    def export_csv(self, filename: str) -> None:
        rows = []
        for province, tag in self.assignment.items():
            rows.append({'province': province,'tag': tag})

        df = pd.DataFrame(rows)
        output_path = PARTITIONS_DIR / filename

        df.to_csv(output_path, index=False)
        return
    
    def export_stats_csv(self, filename: str, G: nx.Graph) -> None:

        # TEMPORARY GRAPH COPY
        H = G.copy()

        # COUNTRY METADATA
        metadata = LoadCountryMetadata()

        # APPLY PARTITION OWNERSHIP
        for province, country_tag in self.assignment.items():
            if province not in H.nodes(): continue

            H.nodes[province]['country_tag'] = country_tag

            H.nodes[province]['country'] = (
                metadata.get(country_tag,{}).get('name')
            )

        # COMPUTE SATISFACTION
        ApplySatisfactionScores(H)

        # EXPORT ROWS
        rows = []
        for province in H.nodes():
            node = H.nodes[province]
            rows.append({
                'province_id': province,
                'province_name': node.get('name'),
                'country_tag': node.get('country_tag'),
                'country_name': node.get('country'),
                'population': node.get('total_population',0),
                'satisfied_population': node.get('satisfied_population',0),
                'satisfaction_score': node.get('satisfaction',0)
            })

        df = pd.DataFrame(rows)
        stats_filename = 'stats_' + filename
        output_path = PARTITIONS_STATS_DIR/ stats_filename

        df.to_csv(output_path,index=False)
        return

    @classmethod
    def create_from_csv(cls, filename: str) -> "Partition":
        path = PARTITIONS_DIR / filename
        df = pd.read_csv(path)
        partition = cls()

        for _, row in df.iterrows():
            partition.assign(
                row['province'],
                row['tag']
            )

        return partition