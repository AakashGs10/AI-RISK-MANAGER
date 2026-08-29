import argparse
import os
import random
import uuid
import numpy as np
import pandas as pd
import networkx as nx

def generate_data(num_users, num_rings, seed, output_dir):
    random.seed(seed)
    np.random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate legitimate users using Barabási-Albert graph
    print(f"Generating {num_users} legitimate users...")
    G_legit = nx.barabasi_albert_graph(num_users, 3, seed=seed)
    legit_users = [f"u_{i}" for i in range(num_users)]
    
    # Assign resources
    devices = [f"dev_{uuid.uuid4().hex[:8]}" for _ in range(num_users)]
    ips = [f"ip_{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}" for _ in range(num_users)]
    cards = [f"card_{uuid.uuid4().hex[:8]}" for _ in range(num_users)]
    
    user_devices = {u: d for u, d in zip(legit_users, devices)}
    user_ips = {u: i for u, i in zip(legit_users, ips)}
    user_cards = {u: c for u, c in zip(legit_users, cards)}
    user_bins = {u: c[:9] + str(random.randint(100, 120)) for u, c in user_cards.items()} # 20 fake BINs
    user_agents = {u: f"agent_{uuid.uuid4().hex[:8]}" if random.random() < 0.20 else "agent_none" for u in legit_users}


    
    # Simulate sharing (5% device, 3% IP)
    num_dev_share = int(num_users * 0.05)
    num_ip_share = int(num_users * 0.03)
    
    for _ in range(num_dev_share):
        u1, u2 = random.sample(legit_users, 2)
        user_devices[u1] = user_devices[u2]
        
    for _ in range(num_ip_share):
        u1, u2 = random.sample(legit_users, 2)
        user_ips[u1] = user_ips[u2]
        
    # Generate Legitimate Transactions
    print("Generating legitimate transactions...")
    txns = []
    edges = list(G_legit.edges())
    if len(edges) > 10000:
        edges = random.sample(edges, 10000)
    
    start_time = 1700000000.0
    end_time = start_time + 30 * 24 * 3600
    
    for u_idx, v_idx in edges:
        sender = legit_users[u_idx]
        receiver = legit_users[v_idx]
        if random.random() > 0.5:
            sender, receiver = receiver, sender
            
        amt = np.random.lognormal(mean=7.5, sigma=1.0)
        amt = np.clip(amt, 100, 200000)
        
        ts = random.uniform(start_time, end_time)
        txns.append({
            'txn_id': f"txn_{uuid.uuid4().hex[:12]}",
            'timestamp': ts,
            'user_id': sender,
            'target_user_id': receiver,
            'amount': amt,
            'ip': user_ips[sender],
            'device_id': user_devices[sender],
            'agent_id': user_agents.get(sender, 'agent_none'),
            'card_hash': user_cards[sender], 'card_bin': user_bins[sender], 'attempt_status': 'approved' if random.random() < 0.90 else 'declined', 'card_bin': user_bins[sender], 'attempt_status': 'approved' if random.random() < 0.97 else 'declined',
            'geo_mismatch': 1 if random.random() < 0.05 else 0,
            'session_duration': random.uniform(2, 600),
            'hour_of_day': int((ts % 86400) / 3600),
            'label': 0
        })
        
    node_labels = [{'user_id': u, 'is_fraud': 0, 'ring_type': 'none', 'ring_id': -1} for u in legit_users]
    
    # Generate Fraud Rings
    print(f"Generating {num_rings} fraud rings...")
    ring_types = ['star'] * (num_rings // 4) + ['cycle'] * (num_rings // 4) + ['bipartite'] * (num_rings // 4) + ['agent_hijack'] * ((num_rings - 3*(num_rings // 4))//2) + ['card_testing'] * ((num_rings - 3*(num_rings // 4)) - (num_rings - 3*(num_rings // 4))//2)
    
    fraud_uid_counter = num_users
    for ring_idx, rtype in enumerate(ring_types):
        if rtype == 'star':
            n_senders = random.randint(8, 15)
            n_collectors = random.randint(1, 2)
            senders = [f"u_{fraud_uid_counter+i}" for i in range(n_senders)]
            collectors = [f"u_{fraud_uid_counter+n_senders+i}" for i in range(n_collectors)]
            fraud_uid_counter += n_senders + n_collectors
            
            ring_devices = [f"dev_{uuid.uuid4().hex[:8]}" for _ in range(3)]
            ring_ips = [f"ip_{random.randint(1,255)}.F.F.F" for _ in range(2)]
            
            for u in senders + collectors:
                user_devices[u] = random.choice(ring_devices)
                user_ips[u] = random.choice(ring_ips)
                user_cards[u] = f"card_{uuid.uuid4().hex[:8]}"
                user_bins[u] = user_cards[u][:9] + str(random.randint(100, 120))
                node_labels.append({'user_id': u, 'is_fraud': 1, 'ring_type': rtype, 'ring_id': ring_idx})
                
            for s in senders:
                c = random.choice(collectors)
                ts = random.uniform(start_time, end_time)
                amt = random.uniform(500, 5000)
                txns.append({
                    'txn_id': f"txn_{uuid.uuid4().hex[:12]}",
                    'timestamp': ts,
                    'user_id': s,
                    'target_user_id': c,
                    'amount': amt,
                    'ip': user_ips[s],
                    'device_id': user_devices[s],
                    'agent_id': user_agents.get(s, 'agent_none'),
            'card_hash': user_cards[s],
                    'geo_mismatch': 1 if random.random() < 0.40 else 0,
                    'session_duration': random.uniform(3, 20),
                    'hour_of_day': int((ts % 86400) / 3600),
                    'label': 1
                })
                
        elif rtype == 'cycle':
            n_nodes = random.randint(5, 10)
            nodes = [f"u_{fraud_uid_counter+i}" for i in range(n_nodes)]
            fraud_uid_counter += n_nodes
            
            ring_devices = [f"dev_{uuid.uuid4().hex[:8]}" for _ in range(2)]
            
            for u in nodes:
                user_devices[u] = random.choice(ring_devices)
                user_ips[u] = f"ip_{random.randint(1,255)}.C.C.C"
                user_cards[u] = f"card_{uuid.uuid4().hex[:8]}"
                user_bins[u] = user_cards[u][:9] + str(random.randint(100, 120))
                node_labels.append({'user_id': u, 'is_fraud': 1, 'ring_type': rtype, 'ring_id': ring_idx})
                
            base_amt = random.uniform(5000, 20000)
            ts = random.uniform(start_time, end_time - 3600)
            for i in range(n_nodes):
                s = nodes[i]
                c = nodes[(i+1)%n_nodes]
                ts += random.uniform(10, 60)
                amt = base_amt * (0.9 ** i)
                txns.append({
                    'txn_id': f"txn_{uuid.uuid4().hex[:12]}",
                    'timestamp': ts,
                    'user_id': s,
                    'target_user_id': c,
                    'amount': amt,
                    'ip': user_ips[s],
                    'device_id': user_devices[s],
                    'agent_id': user_agents.get(s, 'agent_none'),
            'card_hash': user_cards[s],
                    'geo_mismatch': 1 if random.random() < 0.40 else 0,
                    'session_duration': random.uniform(3, 20),
                    'hour_of_day': int((ts % 86400) / 3600),
                    'label': 1
                })
                
        elif rtype == 'bipartite':
            n_senders = random.randint(10, 20)
            n_cashouts = random.randint(2, 3)
            senders = [f"u_{fraud_uid_counter+i}" for i in range(n_senders)]
            cashouts = [f"u_{fraud_uid_counter+n_senders+i}" for i in range(n_cashouts)]
            fraud_uid_counter += n_senders + n_cashouts
            
            ring_devices = [f"dev_{uuid.uuid4().hex[:8]}" for _ in range(3)]
            
            for u in senders + cashouts:
                user_devices[u] = random.choice(ring_devices)
                user_ips[u] = f"ip_{random.randint(1,255)}.B.B.B"
                user_cards[u] = f"card_{uuid.uuid4().hex[:8]}"
                user_bins[u] = user_cards[u][:9] + str(random.randint(100, 120))
                node_labels.append({'user_id': u, 'is_fraud': 1, 'ring_type': rtype, 'ring_id': ring_idx})
                
            for s in senders:
                c = random.choice(cashouts)
                ts = random.uniform(start_time, end_time)
                amt = random.uniform(100, 2000)
                txns.append({
                    'txn_id': f"txn_{uuid.uuid4().hex[:12]}",
                    'timestamp': ts,
                    'user_id': s,
                    'target_user_id': c,
                    'amount': amt,
                    'ip': user_ips[s],
                    'device_id': user_devices[s],
                    'agent_id': user_agents.get(s, 'agent_none'),
            'card_hash': user_cards[s],
                    'geo_mismatch': 1 if random.random() < 0.40 else 0,
                    'session_duration': random.uniform(3, 20),
                    'hour_of_day': int((ts % 86400) / 3600),
                    'label': 1
                })
                
    df = pd.DataFrame(txns)
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    print("Computing rolling features...")
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    
    # ip_velocity
    vel_list = []
    decline_rates = []
    distinct_cards_list = []
    bin_divs = []
    avg_amts = []
    for i in range(len(df)):
        row = df.iloc[i]
        window_start = row['timestamp'] - 60
        window = df.iloc[max(0, i-200):i]
        vel = len(window[(window['ip'] == row['ip']) & (window['timestamp'] >= window_start)])
        vel_list.append(vel)
    df['ip_velocity'] = vel_list
    
    # device_age_hours
    first_seen = df.groupby('device_id')['timestamp'].min().to_dict()
    df['device_age_hours'] = (df['timestamp'] - df['device_id'].map(first_seen)) / 3600.0
    
    # is_new_account
    user_first_seen = df.groupby('user_id')['timestamp'].min().to_dict()
    dataset_start = df['timestamp'].min()
    df['is_new_account'] = df['user_id'].map(lambda u: 1 if (user_first_seen[u] - dataset_start) <= 168 * 3600 else 0)
    df['is_new_payee'] = [random.choice([0, 1]) for _ in range(len(df))]
    df['agentic_behavior_score'] = df['session_duration'].apply(lambda x: 0.9 if x < 2.0 else 0.1)
    
    # amount_zscore
    df['amount_zscore'] = 0.0
    df['rolling_mean'] = df.groupby('user_id')['amount'].transform(lambda x: x.shift().expanding().mean())
    df['rolling_std'] = df.groupby('user_id')['amount'].transform(lambda x: x.shift().expanding().std())
    zscores = (df['amount'] - df['rolling_mean']) / df['rolling_std'].replace(0, 1.0)
    df['amount_zscore'] = zscores.fillna(0.0)
    
    columns_order = [
        'txn_id', 'timestamp', 'user_id', 'target_user_id', 'amount', 'ip', 'device_id', 'card_hash',
        'ip_velocity', 'device_age_hours', 'geo_mismatch', 'session_duration', 'hour_of_day',
        'is_new_account', 'is_new_payee', 'agentic_behavior_score', 'amount_zscore', 'label'
    ]
    df = df[columns_order]
    
    # Create graph edges
    print("Creating graph edges...")
    edge_list = []
    
    for _, row in df.iterrows():
        edge_list.append({'source': row['user_id'], 'target': row['target_user_id'], 'edge_type': 'transaction', 'weight': row['amount'], 'timestamp': row['timestamp']})
        
    device_to_users = {}
    ip_to_users = {}
    card_to_users = {}
    for u, d in user_devices.items(): device_to_users.setdefault(d, []).append(u)
    for u, i in user_ips.items(): ip_to_users.setdefault(i, []).append(u)
    for u, c in user_cards.items(): card_to_users.setdefault(c, []).append(u)
        
    def add_shared_edges(resource_dict, e_type):
        for res, users in resource_dict.items():
            if len(users) > 1:
                for i in range(len(users)):
                    for j in range(i+1, len(users)):
                        edge_list.append({'source': users[i], 'target': users[j], 'edge_type': e_type, 'weight': 1.0, 'timestamp': 0.0})
                        
    add_shared_edges(device_to_users, 'shared_device')
    add_shared_edges(ip_to_users, 'shared_ip')
    add_shared_edges(card_to_users, 'shared_card')
    

    agent_to_users = {}
    for u, a in user_agents.items(): 
        if a != 'agent_none': agent_to_users.setdefault(a, []).append(u)
    
    for users in agent_to_users.values():
        for i in range(len(users)):
            for j in range(i+1, len(users)):
                edge_list.append({'source': users[i], 'target': users[j], 'edge_type': 'shared_agent', 'weight': 1.0, 'timestamp': 0.0})


    # Track resource first used for Idea 2
    resource_first_used = {}
    for i, row in enumerate(sorted(txns, key=lambda x: x['timestamp'])):

        u = row['user_id']
        t = row['timestamp']
        for res in [row['device_id'], row['ip'], row['card_hash']]:
            key = (res, u)
            if key not in resource_first_used:
                resource_first_used[key] = t
                
    timeline_data = [{'resource': res, 'user_id': u, 'first_used_timestamp': t} for (res, u), t in resource_first_used.items()]
    pd.DataFrame(timeline_data).to_csv(os.path.join(output_dir, 'resource_timeline.csv'), index=False)

    df_edges = pd.DataFrame(edge_list)
    df_labels = pd.DataFrame(node_labels)
    
    df.to_csv(os.path.join(output_dir, 'tabular_features.csv'), index=False)
    df_edges.to_csv(os.path.join(output_dir, 'graph_edges.csv'), index=False)
    df_labels.to_csv(os.path.join(output_dir, 'node_labels.csv'), index=False)
    
    print(f"\n--- Generation Summary ---")
    print(f"Total Transactions: {len(df)}")
    print(f"Fraud Rate: {(df['label'].mean() * 100):.2f}%")
    print(f"Total Rings: {num_rings}")
    print(f"Total Users: {len(df_labels)}")
    print(f"Files saved to: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--users", type=int, default=5000)
    parser.add_argument("--rings", type=int, default=12)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=str, default="data/output")
    args = parser.parse_args()
    
    generate_data(args.users, args.rings, args.seed, args.output_dir)
