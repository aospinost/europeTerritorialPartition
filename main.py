# ESTE FUE EL ARCHIVO EN EL QUE FUI TRABAJANDO.
# AQUI ESTA LA CARGA DE DATOS, LA EXPORTACION Y CUANDO
# CORRI LOS ALGORITMOS. NO TOCAR ESTE MAIN.

from src.builders.vertex_builder import *
from src.builders.edge_builder import *
from src.builders.pop_builder import *
from src.builders.country_builder import *
from src.builders.acceptance_builder import *
from src.builders.culture_builder import *
from src.imageGenerators.image_generator import *


'''
vertices = CreateVertices()
european_provinces = CallEuropeanProvinces()
ExportVertices(vertices, european_provinces)

edges_vertices = CreateProvinceEdges(vertices, european_provinces)
ExportEdges(edges_df)

df_population = CallPopulation(european_provinces)
ExportPopulation(df_population)

country_metadata = CreateCountryMetadata()
ExportCountryMetadata(country_metadata)

accepted, missing = CreateCountryAcceptance()
ExportAcceptedCultures(accepted, missing)

df_cultures = CreateCulturesKey()
ExportCulturesKey(df_cultures)
'''

'''
from src.cleaning.find_valid_countries import *
from src.cleaning.generate_delete_manifests import *
from src.cleaning.delete_irrelevant_countries import *

valid, invalid = FindValidCountries()
#GenerateCountryRemovalManifest(invalid)
DeleteIrrelevantCountries()
'''

'''
from src.builders.provinces_localisation_builder import *

ApplyProvinceLocalisations()
'''

from src.graph.graph import *
from src.graph.algorithms.greedyExpansion import *
from src.graph.algorithms.dfs import *
from src.graph.algorithms.bfs import *
from src.graph.algorithms.multistart import *
from src.graph.algorithms.globalCoreRegion import *
from src.graph.show import *

base_graph = LoadGeographicGraph()

#ShowGeographicGraph(base_graph)

'''
vertices = ImportVertices()
from src.builders.ownership1836_builder import *

european_provinces = CallEuropeanProvinces()
partition = Build1836Partition(european_provinces)

partition = Partition.create_from_csv("1836imputated.csv")
ShowMapWithColoring(vertices, partition, save_path = "1836imputated.bmp")
ShowMapWithSatisfaction(vertices, partition, base_graph, save_path = "1836imputated.bmp")
'''

'''
vertices = ImportVertices()

partition = Partition.create_from_csv("1836.csv")
#ShowMapWithColoring(vertices, partition, save_path = "1836.bmp")
#ShowMapWithSatisfaction(vertices, partition, base_graph, save_path = "1836.bmp")

partition = Partition.create_from_csv("1836imputated.csv")
#ShowMapWithColoring(vertices, partition, save_path = "1836imputated.bmp")
#ShowMapWithSatisfaction(vertices, partition, base_graph, save_path = "1836imputated.bmp")

partition = GreedyExpansionPartition(base_graph)
partition.export_csv("greedyExpansionPartition.csv")
partition.export_stats_csv("greedyExpansionPartition.csv", base_graph)
#ShowMapWithColoring(vertices, partition, save_path = "greedyExpansionPartition.bmp")
#ShowMapWithSatisfaction(vertices, partition, base_graph, save_path = "greedyExpansionPartition.bmp")

partition = DFSPartition(base_graph)
partition.export_csv("DFSPartition.csv")
partition.export_stats_csv("DFSPartition.csv", base_graph)
#ShowMapWithColoring(vertices, partition, save_path = "DFSPartition.bmp")
#ShowMapWithSatisfaction(vertices, partition, base_graph, save_path = "DFSPartition.bmp")

partition = BFSPartition(base_graph)
partition.export_csv("BFSPartition.csv")
partition.export_stats_csv("BFSPartition.csv", base_graph)
#ShowMapWithColoring(vertices, partition, save_path = "BFSPartition.bmp")
#ShowMapWithSatisfaction(vertices, partition, base_graph, save_path = "BFSPartition.bmp")

partition = DFSPartition(base_graph, priority_tags=["LAT","BYE","NOR","LIT","MON","NET","SLV","SLO","UKR","POL","ROM","HUN","DEN","RUS","GER","FRA","TUR","ITA","SPA"])
partition.export_csv("DFSPartitionOrdered.csv")
partition.export_stats_csv("DFSPartitionOrdered.csv", base_graph)
#ShowMapWithColoring(vertices, partition, save_path = "DFSPartitionOrdered.bmp")
#ShowMapWithSatisfaction(vertices, partition, base_graph, save_path = "DFSPartitionOrdered.bmp")

partition = BFSPartition(base_graph, priority_tags=["BUL","GEO","LAT","EST","KDS","BYE","NOR","LIT","MON","NET","SLV","SLO","UKR","POL","ROM","HUN","DEN","GER","FRA","TUR","ITA","SPA"])
partition.export_csv("BFSPartitionOrdered.csv")
partition.export_stats_csv("BFSPartitionOrdered.csv", base_graph)
#ShowMapWithColoring(vertices, partition, save_path = "BFSPartitionOrdered.bmp")
#ShowMapWithSatisfaction(vertices, partition, base_graph, save_path = "BFSPartitionOrdered.bmp")

partition = MultistartPartition(base_graph, iterations = 1000)
partition.export_csv("multistartPartition.csv")
partition.export_stats_csv("multistartPartition.csv", base_graph)
#ShowMapWithColoring(vertices, partition, save_path = "multistartPartition.bmp")
#ShowMapWithSatisfaction(vertices, partition, base_graph, save_path = "multistartPartition.bmp")

partition = GlobalCoreRegionPartition(base_graph)
partition.export_csv("globalCoreRegionPartition.csv")
partition.export_stats_csv("globalCoreRegionPartition.csv", base_graph)
#ShowMapWithColoring(vertices, partition, save_path = "globalCoreRegionPartition.bmp")
#ShowMapWithSatisfaction(vertices, partition, base_graph, save_path = "globalCoreRegionPartition.bmp")
'''
#partition = GlobalCoreRegionPartition(base_graph)
#'''
partition = Partition.create_from_csv("multistartPartition.csv")
vertices = ImportVertices()
#ShowGeographicGraph(base_graph)
#ShowMapWithCulture(base_graph, vertices)
#partition = GlobalCoreRegionPartition(base_graph)
#partition.export_csv("globalCoreRegionPartition.csv")
#partition.export_stats_csv("globalCoreRegionPartition.csv", base_graph)
#ShowMapWithColoring(vertices, partition, save_path = "globalCoreRegionPartition.bmp")
#ShowMapWithSatisfaction(vertices, partition, base_graph, save_path = "globalCoreRegionPartition.bmp")

#partition = GlobalCoreRegionPartition(base_graph)
#partition.export_csv("globalCoreRegionPartition.csv")
#partition.export_stats_csv("globalCoreRegionPartition.csv", base_graph)

#partition = GlobalCoreRegionPartition(base_graph)
partitioned_graph = LoadPartitionedGraph(base_graph, partition)

#ShowPartitionedGraph(partitioned_graph, show_labels = False)
#ShowCulturalMap(partitioned_graph)
#ShowPartitionedGraph(partitioned_graph)
#ShowSatisfactionMap(partitioned_graph)

#partition = Partition.create_from_csv("heuristicPartition.csv")
#partitioned_graph = LoadPartitionedGraph(base_graph, partition)
#ShowGeographicGraph(base_graph)
#ShowPartitionedGraph(partitioned_graph, show_labels = False)

#ShowCulturalMap(partitioned_graph, show_labels = False)

#vertices = ImportVertices()
#ShowMapWithSelectedVerticesOnTop(vertices, european_provinces)
#ShowGeographicGraph(base_graph)
#ShowMapWithColoring(vertices, partition)
#'''