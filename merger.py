import pandas as pd
from constants import *
import os

nodes = pd.read_csv(os.path.join(RESULTS_PATH, "nodes_major.csv"))
edges = pd.read_csv(os.path.join(RESULTS_PATH, "edges_major.csv"))

nodes_groupped_degree = nodes.groupby("group", as_index=False)["Degree"].sum()
nodes_groupped_degree = nodes_groupped_degree.reset_index().rename({"index": "id"}, axis=1)

for i, edge in edges.iterrows():
    source_group = nodes.loc[nodes['id'] == edge['source']]["group"].item()
    target_group = nodes.loc[nodes['id'] == edge['target']]["group"].item()
    new_source_id = nodes_groupped_degree.loc[nodes_groupped_degree["group"] == source_group]["id"].item()
    new_target_id = nodes_groupped_degree.loc[nodes_groupped_degree["group"] == target_group]["id"].item()
    edges.at[i, "source"] = new_source_id
    edges.at[i, "target"] = new_target_id

edges_groupped_weight = edges.groupby(["source", "target"], as_index=False)["Weight"].sum()

nodes_groupped_degree.to_csv(os.path.join(RESULTS_PATH, "nodes_major_aggregated.csv"), index=False)
edges_groupped_weight.to_csv(os.path.join(RESULTS_PATH, "edges_major_aggregated.csv"), index=False)


