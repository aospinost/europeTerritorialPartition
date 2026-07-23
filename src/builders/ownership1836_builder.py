from src.graph.partition import Partition
from src.parsers.ownership1836_parser import *


def Build1836Partition(provinces_list):

    df = Parse1836Ownership()

    # -----------------------------------
    # FILTER TO EUROPE
    # -----------------------------------

    df = df[
        df['province'].isin(provinces_list)
    ]

    # -----------------------------------
    # BUILD PARTITION
    # -----------------------------------

    partition = Partition()

    for _, row in df.iterrows():

        partition.assign(
            row['province'],
            row['tag']
        )

    return partition