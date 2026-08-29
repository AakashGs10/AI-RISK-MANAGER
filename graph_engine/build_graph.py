import pandas as pd
import networkx as nx
import community.community_louvain as community_louvain
from sklearn.linear_model import LogisticRegression
import argparse
import os
import numpy as np

def calculate_epidemic_decay(timestamps, current_time, decay_rate=0.01):
    # SIS Model: Risk decays exponentially since last exposure
    # timestamps: list of unix times this node transacted with a risky node
    if not timestamps: return 1.0
    time_since_last_exposure = (current_time - max(timestamps)) / 3600.0 # hours
    return np.exp(-decay_rate * time_since_last_exposure)

def run_aggregator():
    data_dir = "data/output"
    out_dir = "graph_engine/output"
    os.makedirs(out_dir, exist_ok=True)
    
    print("[Aggregator] Loading edges and tabular data for cross-merchant alignment...")
    edges_df = pd.read_csv(os.path.join(data_dir, "graph_edges.csv"))
    labels_df = pd.read_csv(os.path.join(data_dir, "node_labels.csv"))
    tabular_df = pd.read_csv(os.path.join(data_dir, "tabular_features.csv"))
    
    # 1. Simulate Local Merchant Graphs (they miss the big picture)
    merchants = tabular_df['merchant_id'].unique()
    local_graphs = {}
    for m in merchants:
        merchant_txns = tabular_df[tabular_df['merchant_id'] == m]['txn_id']
        local_edges = edges_df[(edges_df['edge_type'] != 'transaction') | (edges_df['weight'].isin(merchant_txns))]
        G_local = nx.from_pandas_edgelist(local_edges, 'source', 'target', ['edge_type', 'weight'])
        local_graphs[m] = G_local
    
    # 2. Build the Federated Global Graph (Aggregator Level)
    print("[Aggregator] Building Global Federated Graph using shared identifiers...")
    G_global = nx.from_pandas_edgelist(edges_df, 'source', 'target', ['edge_type', 'weight'])
    
    print("[Aggregator] Running Louvain community detection on global graph...")
    partition = community_louvain.best_partition(G_global)
    
    print("[Aggregator] Calculating PageRank & Louvain Centrality Embeddings...")
    degree = dict(G_global.degree())
    pagerank = nx.pagerank(G_global, alpha=0.85)
    
    features = []
    current_sim_time = tabular_df['timestamp'].max()
    
    for uid in labels_df['user_id']:
        if uid not in G_global:
            features.append({'user_id': uid, 'graph_risk_score': 0.0, 'community_id': -1, 'counterfactual_drop': 0.0})
            continue
            
        deg = degree[uid]
        pr = pagerank[uid]
        comm = partition[uid]
        
        # 3. Epidemic Risk Propagation (SIS)
        # Find risky neighbors (nodes sharing IP/Device)
        neighbors = list(G_global.neighbors(uid))
        shared_resource_edges = [n for n in neighbors if str(n).startswith('1') or len(str(n)) < 30] # IP/Devices
        
        # Simulate epidemic decay
        user_txns = tabular_df[tabular_df['user_id'] == uid]
        if not user_txns.empty:
            last_txn_time = user_txns['timestamp'].max()
            epidemic_multiplier = calculate_epidemic_decay([last_txn_time], current_sim_time)
        else:
            epidemic_multiplier = calculate_epidemic_decay([current_sim_time - 86400], current_sim_time) # simplified simulation
        
        # Base risk calculation
        risk_score = min(1.0, (deg * 0.05 + pr * 100) * epidemic_multiplier)
        
        # 4. Counterfactual Generation for Compliance
        # "If this account hadn't shared devices with X, its score would drop by Y"
        counterfactual_drop = 0.0
        if risk_score > 0.7 and len(shared_resource_edges) > 0:
            # Perturb graph
            G_temp = G_global.copy()
            for n in shared_resource_edges:
                if G_temp.has_edge(uid, n):
                    G_temp.remove_edge(uid, n)
            try:
                pr_cf = nx.pagerank(G_temp, alpha=0.85, max_iter=50)[uid]
                risk_cf = min(1.0, ((deg - len(shared_resource_edges)) * 0.05 + pr_cf * 100) * epidemic_multiplier)
                counterfactual_drop = risk_score - risk_cf
            except:
                pass
                
        features.append({
            'user_id': uid,
            'graph_risk_score': risk_score,
            'community_id': comm,
            'counterfactual_drop': round(counterfactual_drop, 3),
            'epidemic_decay_factor': round(epidemic_multiplier, 3),
            'federated_ring_detected': int(risk_score > 0.7)
        })
        
    out_df = pd.DataFrame(features)
    out_df.to_csv(os.path.join(out_dir, "graph_risk_scores.csv"), index=False)
    
    print(f"[Aggregator] Found {len(out_df[out_df['federated_ring_detected'] == 1])} highly suspicious cross-merchant accounts.")
    print("[Aggregator] Federated Embeddings and Counterfactuals saved.")

if __name__ == "__main__":
    run_aggregator()
