# Abuse-Ring Sentinel
**Zero-Trust AI Security Proxy for Agentic Payments**
> Razorpay AI Buildathon 2026 — AI Risk Manager Track

Abuse-Ring Sentinel intercepts every payment — human or AI-agent-initiated — before it reaches the payment API, running it through four defensive layers in under 100ms. Modern fraud rings spread mule accounts across multiple merchants specifically to stay under any single merchant's radar; this system is built around the idea that only an aggregator (like Razorpay, sitting across many merchants) can see the full ring.


## The Plain-English Pitch
**The Problem:** In the future, AI agents (like ChatGPT) will be making purchases and moving money automatically on our behalf. But what happens when a fraudster hacks an AI, or sets up a massive network of bots to steal money? Traditional security systems are built to catch human thieves, not autonomous AI swarms. Furthermore, modern scammers hide by spreading their fake accounts across dozens of different stores. Because each store only sees a tiny piece of the puzzle, the scammers slip right through.

**Our Solution:** We built the **Abuse-Ring Sentinel**. It is a "Zero-Trust" gatekeeper that sits in front of the payment button and acts like a hyper-intelligent security guard. It runs every single transaction through 4 layers of defense in less than a tenth of a second.

**1. The "Too Perfect" Trap (Synthetic Identity)**
Most security systems look for anomalies—like someone typing too fast or buying too much. We do the opposite. Fraudsters who create fake accounts often use automated scripts that are statistically *too perfect*. If an account has absolutely zero variance, perfect timing, and zero friction, we flag it as a bot. Real humans are messy; perfection is suspicious.

**2. The Hard Trust Boundary**
If we detect that an AI agent is making the purchase, we don't rely on guessing. We enforce a hard limit (e.g., ₹10,000). If the AI tries to move more than that, we block it immediately. We believe that when dealing with autonomous AI, safety rules should be written in stone, not left up to a machine learning algorithm.

**3. The Cross-Merchant Map**
Since scammers spread out across multiple stores, we act as a massive aggregator. We safely stitch together the data from multiple merchants by connecting the dots between shared devices and IP addresses. Even if a scammer only buys one item at Store A, and one item at Store B, our system sees the massive web connecting them and shuts the entire ring down. 

**4. The "Infection" Model**
We don't just give an account a static risk score. We treat fraud like a virus. If a clean account interacts with a known scammer, it gets "infected" and its risk score spikes. But just like a real virus, that risk decays over time as long as they don't interact with scammers again. 

**5. AI Investigating AI**
Finally, when a transaction is blocked, our system mathematically proves *why* it was blocked so that regulators (like the RBI) are happy. We then expose this entire system to Claude, turning Claude into our own autonomous Fraud Investigator. It can read our graphs, spot the scammers, and write legal chargeback evidence in seconds.

## Architecture

```mermaid
flowchart TD
    %% Input Layer
    classDef input fill:#111827,stroke:#3b82f6,stroke-width:2px,color:#fff
    A1[Human Transaction]:::input --> Gateway
    A2[Agentic Transaction via MCP]:::input --> Gateway

    Gateway[FastAPI Gateway /api/pay]:::core
    
    %% Pre-ML Filter Layer
    subgraph PreFilter[Layer 1: Pre-ML Guardrails]
        SG[Semantic Firewall
Intercepts 'IGNORE PREVIOUS']:::guard
        AG[Agentic Velocity Limits
Blocks Autonomous Txn > ₹10k]:::guard
        SI[Synthetic Identity 'Too Clean' Detector
Flags zero-variance perfect accounts]:::guard
    end
    
    Gateway --> SG
    SG --> AG
    AG --> SI
    
    %% Shared Backbone
    subgraph Backbone[Shared Backbone]
        RE[Rolling Feature Extractor
IP Velocity, Device Age, Z-Scores]:::data
        RC[(Redis Cache
Graph Centrality, Community IDs)]:::data
    end
    
    SI --> RE
    RE --> RC
    
    %% Core ML Engines
    subgraph CoreML[Layer 2 & 3: The ML Engines]
        XGB[XGBoost Layer 1
Fraud-Spike Detection]:::ml
        FGA[Cross-Merchant Graph Stitching
Topology & Community Detection]:::ml
        SIS[Epidemiological SIS Model
Time-Decaying Risk Propagation]:::ml
    end
    
    RC --> XGB
    RC --> FGA
    FGA --> SIS
    
    %% Explanation & Compliance
    subgraph Compliance[Layer 4: Compliance & Explanations]
        CF[Counterfactual Generator
Graph Perturbation Proofs]:::comp
        AT[Adaptive Threshold Engine
MCC & Contextual Adjustments]:::comp
    end
    
    XGB --> AT
    SIS --> CF
    CF --> AT
    
    %% Decision Routing
    DR{Decision Router}:::router
    AT --> DR
    
    DR -- "Score > 85.0" --> BLOCK[BLOCK]:::block
    DR -- "Score > 75.0" --> STEP[STEP-UP / 2FA]:::warn
    DR -- "Score < 75.0" --> ALLOW[ALLOW]:::allow
    
    %% MCP SOC Analyst Integration
    subgraph MCP[Model Context Protocol Server]
        Claude[Claude Desktop App
(Tier-3 SOC Analyst)]:::mcp
        T1[get_active_fraud_rings]:::mcp
        T2[generate_dispute_evidence]:::mcp
        T3[evaluate_risk]:::mcp
    end
    
    Claude <--> T1
    Claude <--> T2
    Claude <--> T3
    T1 -.-> FGA
    T2 -.-> CF
    
    %% Styling
    classDef core fill:#0f172a,stroke:#10b981,stroke-width:2px,color:#fff
    classDef guard fill:#7f1d1d,stroke:#ef4444,stroke-width:2px,color:#fff
    classDef data fill:#1e293b,stroke:#94a3b8,stroke-width:2px,color:#fff
    classDef ml fill:#312e81,stroke:#6366f1,stroke-width:2px,color:#fff
    classDef comp fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#fff
    classDef router fill:#050810,stroke:#f59e0b,stroke-width:3px,color:#fff
    classDef block fill:#991b1b,color:#fff,font-weight:bold
    classDef warn fill:#b45309,color:#fff,font-weight:bold
    classDef allow fill:#166534,color:#fff,font-weight:bold
    classDef mcp fill:#4c1d95,stroke:#a78bfa,stroke-width:2px,color:#fff
```




### Layer 1 — Pre-ML Guardrails
* **Semantic firewall:** scans the raw agent prompt for injection/bypass patterns before any ML runs.
* **Agentic velocity limits:** autonomous AI-driven transactions over ₹10,000 hit a hard trust boundary and are blocked outright — this line is intentionally not ML-adjustable.
* **Synthetic identity ("too clean") detector:** inverts the usual anomaly-hunting paradigm. Real humans are messy; fabricated accounts are often statistically too perfect (zero amount variance, exactly one IP hit, no geo mismatch, suspiciously round session durations). Flags before ML is even evaluated.

### Layer 2 — Fraud-Spike Detector
XGBoost classifier trained on rolling features (IP velocity, device age, amount z-score, graph risk score, etc.). See Model Performance for real numbers.

### Layer 3 — Cross-Merchant Graph Aggregator
A single merchant only sees its own transaction graph — a ring spread across four merchants looks like four harmless accounts. This layer stitches merchant graphs together using shared hashed identifiers (device ID, IP, card hash), then runs:
* **PageRank + Louvain community detection** for cross-merchant ring/cluster discovery
* **Epidemiological (SIS) risk decay** — an account's risk score decays exponentially since its last exposure to a risky neighbor, rather than resetting to zero the moment it goes quiet.

### Layer 4 — Compliance & Explanations
* **Counterfactual generator:** for any flagged ring, perturbs the graph in memory (severs the suspected shared-resource edges) and recomputes PageRank, producing a concrete, defensible statement: *"If this account had not shared a device with these nodes, its risk score would drop by X."* This is what RBI/compliance teams need to actually freeze an account — not a black-box score.
* **Adaptive threshold engine:** block/step-up thresholds shift based on business context (stricter for high-risk MCCs, looser for groceries/utilities; extra penalty for Account-Takeover signatures).

## Repo Structure
```text
.
├── backend/
│   ├── app.py                 FastAPI gateway — /api/pay, /api/evaluate_risk, /api/feedback, etc.
│   ├── mcp_server.py          MCP server exposing the system to Claude Desktop
│   ├── evidence_responder.py  Builds chargeback/dispute evidence packets
│   └── redis_client.py        Graph-risk store (Redis with in-memory fallback)
├── data/
│   ├── generate.py            Synthetic transaction + fraud-ring generator
│   └── output/                Generated CSVs (edges, node labels, tabular features)
├── ml/
│   ├── train.py                Trains the XGBoost fraud-spike model
│   └── output/                 model.json, feature_names.json, metrics.json, SHAP/threshold plots
├── graph_engine/
│   ├── build_graph.py          Cross-merchant graph aggregation, epidemic decay, counterfactuals
│   └── output/                 graph_risk_scores.csv
├── frontend/
│   ├── index.html               Landing/overview page
│   ├── dashboard.html           Live transaction + fraud-ring dashboard
│   └── checkout.html            Demo checkout flow that calls /api/pay
├── demo_attack.py               Adversarial evasion demo (cross-merchant mule ring)
├── requirements.txt
├── .env.example
└── README.md
```

## Setup
```bash
git clone <your-repo-url>
cd abuse-ring-sentinel
pip install -r requirements.txt
cp .env.example .env        # fill in Razorpay test keys — never commit real keys
```

## Running the Pipeline
The stages have a real dependency order — each one reads output the previous stage wrote:

```bash
# 1. Generate synthetic transactions + injected fraud rings
python data/generate.py

# 2. Train the XGBoost fraud-spike model on the generated tabular features
python ml/train.py

# 3. Build the cross-merchant graph, compute PageRank/Louvain + epidemic decay + counterfactuals
python graph_engine/build_graph.py

# 4. Start the API (loads model.json + graph_risk_scores.csv on startup)
uvicorn backend.app:app --reload --port 8000
```
*Optional — run the adversarial evasion demo against a live server:*
```bash
python demo_attack.py
```
Open `frontend/dashboard.html` to watch transactions and ring alerts stream in via the `/ws/feed` WebSocket.

## MCP Server (Claude Desktop Integration)
`backend/mcp_server.py` exposes the system to Claude Desktop as a Tier-3 SOC analyst via 7 tools:
* `process_payment`: Execute a payment on the user's behalf (subject to all 4 layers)
* `evaluate_risk`: Pre-auth risk check without moving money
* `generate_dispute_evidence`: Generate a chargeback evidence packet for a transaction
* `get_recent_transactions`: Pull the live audit trail
* `get_active_fraud_rings`: Query currently detected rings/clusters
* `submit_fraud_feedback`: Confirm ground-truth label for a past transaction
* `trigger_model_retraining`: Kick off incremental XGBoost retraining

Run it with `python backend/mcp_server.py` and point Claude Desktop's MCP config at it.

## Model Performance
Evaluated on a strict chronological 30% test split:
* **Precision:** 0.591
* **Recall:** 1.000
* **F1 Score:** 0.743
* **AUC-PR:** 0.716

*Cost-sensitive analysis (AOV ₹2,500, 10% margin, ₹500 LTV-churn penalty per false positive, ₹2,500 chargeback cost per false negative):*
* **False positive cost:** ₹13,500 (18 blocked-legit txns)
* **Fraud prevented:** 26 transactions, ₹65,000
* **Net savings:** ₹51,500

These numbers are intentionally not "too good to be true" — recall is prioritized (catch every fraud case) at the cost of some false positives.

## Known Limitations & Security Notes
* **Graph layer uses classical centrality, not a GNN.** `build_graph.py` computes PageRank + Louvain community detection, not GraphSAGE.
* **Epidemic decay** falls back to a simplified constant for users with no transaction history in the current dataset window, rather than a true per-neighbor exposure timeline.
* **Security:** Never commit real API keys. If you cloned this after a prior version had hardcoded test keys in `app.py`, those keys have already been exposed and should be rotated.
