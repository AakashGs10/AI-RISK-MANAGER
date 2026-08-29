# Abuse-Ring Sentinel
**Zero-Trust AI Security Proxy for Agentic Payments**
> Razorpay AI Buildathon 2026 — AI Risk Manager Track

Abuse-Ring Sentinel intercepts every payment — human or AI-agent-initiated — before it reaches the payment API, running it through four defensive layers in under 100ms. Modern fraud rings spread mule accounts across multiple merchants specifically to stay under any single merchant's radar; this system is built around the idea that only an aggregator (like Razorpay, sitting across many merchants) can see the full ring.

## Architecture

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
