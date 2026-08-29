# Abuse-Ring Sentinel

**Zero-Trust AI Security Proxy for Agentic Payments**

> AI Buildathon 2026 — AI Risk Manager Track

---

## Fraud Detection Engine
*This is the core, deeply measured architecture designed to stop one specific class of loss: Coordinated Payment Fraud.*

**Module 1: Fraud-Spike Detector (Layer 1)**
A low-latency XGBoost classifier trained to detect anomalous transaction bursts based on device history, IP velocity, and financial Z-scores.

**Module 2: Abuse-Ring Sentinel (Layer 2)**
A NetworkX graph engine running Louvain community detection to identify money-mule rings (Stars, Cycles, Bipartite graphs) based on shared underlying resources, entirely without target leakage.

*(See **Metrics** below for the rigorous held-out test set evaluation of this core engine).*

## Extended Capabilities (Built on the Shared Backbone)
*These modules reuse the telemetry and graph backbone of the Core Engine to solve adjacent merchant problems. Note: These are functional demonstrations of the architecture's flexibility, and are not benchmarked with the same strict held-out PR/AUC rigor as the Fraud Engine above.*

**Module 3: Return-Risk Scorer**
A lightweight heuristic model that isolates return risk (a merchant policy signal) from fraud risk (a blockable offense).

**Module 4: Chargeback Evidence Responder**
An automated, template-constrained system that generates dispute packets entirely from logged telemetry facts—defense only.

**Module 5: Agentic Payment Guardrail**
Differentiates AI agents from human users to enforce strict, progressive Trust Budgets on autonomous transactions.

## The Problem We Solved

AI Agents (ChatGPT, Claude, Gemini) are beginning to execute financial transactions autonomously via MCP tool calls. This introduces three attack vectors that traditional fraud models cannot handle:

1. **Prompt Injection** — Hackers trick the agent into diverting payments (OWASP LLM01)
2. **Excessive Agency** — The agent calls financial tools it shouldn't have access to (OWASP LLM08)
3. **Coordinated Mule Rings** — Fraudsters use networks of compromised accounts sharing devices/IPs to launder money

We built a **Zero-Trust Gatekeeper** that intercepts every AI agent tool call before it reaches the payment API, running it through three defensive layers in under 100ms.

## Architecture

```
Agent Prompt ──→ [Semantic Firewall] ──→ [Graph ML Engine] ──→ [Decision] ──→ Payment API
                  (OWASP LLM01)         (XGBoost + Louvain)    ALLOW/BLOCK
                       │                        │
                  Keyword scan            Pre-computed graph
                  Deterministic           risk scores via cache
                  0ms latency             2ms lookup
```

### Why Three Layers (AI Judgment)

| Layer | Tool Used | Why This Tool | What We Chose NOT to Use |
|---|---|---|---|
| Semantic Firewall | Keyword matching | Deterministic, 0ms, no hallucination | LLM-based classifier (50ms latency, probabilistic) |
| Transaction Scoring | XGBoost | Outperforms DNNs on tabular data ([Grinsztajn, NeurIPS 2022](https://arxiv.org/abs/2207.08815)), 2ms inference | Neural networks (slower, worse on tabular) |
| Graph Analysis | Louvain + Logistic Regression | O(n log n), interpretable communities | GraphSAGE (requires GPU, overkill for MVP) |
| Velocity Checks | Rule-based counter | Arithmetic operation, not a learning problem | ML-based anomaly detection (unnecessary complexity) |
| Audit Trails | Deterministic hashing | PII masking is a crypto problem, not an AI problem | Generative AI summarization |
| Threshold Selection | Cost-curve analysis | Business decision, not a pattern recognition problem | AutoML threshold optimization |

## Quick Start

```bash
pip install -r requirements.txt
python run.py
```

Then open: **http://localhost:3000** (after starting the frontend server)

```bash
# Start frontend server
python -m http.server 3000 --directory frontend
```

### Step by Step

```bash
pip install -r requirements.txt

python data/generate.py              # Generate synthetic fraud data
python graph_engine/build_graph.py   # Build graph, compute risk scores
python ml/train.py                   # Train XGBoost with GridSearchCV
uvicorn backend.app:app --port 8000  # Start API server
python -m http.server 3000 --directory frontend  # Serve UI
```

## Metrics (Honest, Held-Out Test Set)

All metrics are computed on a **strict 30% chronological test split** that the model never saw during training or tuning. The graph engine also only uses training-period edges (no data leakage).

| Metric | Value |
|---|---|
| Precision | 0.9783 |
| Recall | 1.0000 |
| F1 Score | 0.9890 |
| AUC-PR | 0.9995 |
| False Positives | 1 out of 3,042 test transactions |
| Optimal Threshold | 0.25 (cost-optimized, not default 0.5) |

### Financial Impact

| Metric | Value |
|---|---|
| False Positive Cost | ₹750 (1 blocked legit × ₹750/FP) |
| Fraud Prevented | 45 transactions (₹112,500 saved) |
| **Net Merchant Savings** | **₹111,750** |
| Cost Assumptions | AOV=₹2,500, Margin=10%, Churn Penalty=₹500/FP |

## Failure Recovery Log

> "What broke, and what you did about it"

| What Broke | Root Cause | How We Fixed It |
|---|---|---|
| Semantic Firewall crashed with `NameError` on every prompt injection | Referenced `decision` variable before it was computed; duplicate dict key | Removed the forward-reference, added `secondary_threat` field |
| MCP Server crashed with `AttributeError` | Typo: `json.json.dumps` instead of `json.dumps` | Fixed the typo |
| Graph engine had **data leakage** | Built the NetworkX graph from ALL edges including future test data | Filtered edges to only include training-period users. AUC-PR dropped from 1.000 to 0.9995 (more honest) |
| `dry_run=True` caused `KeyError` for new users | `USER_FIRST_SEEN[user_id]` accessed before being set when `dry_run` was active | Added safe initialization for new users during dry runs |
| Frontend buttons stopped working (non-interactive) | A regex replacement accidentally swallowed JavaScript functions | Completely rebuilt the script block from scratch |
| Rupee symbol (₹) rendered as `?` | PowerShell encoding corrupted UTF-8 characters during file merging | Rewrote with explicit UTF-8 encoding |

## Regulatory Compliance (India 2026)

| Framework | Implementation |
|---|---|
| RBI KYC Three-Tier | Every transaction auto-classified as SDD/CDD/EDD based on risk |
| DoT FRI | Fraud Risk Indicator field returned in every API response |
| PMLA/FIU-IND | Automatic STR flag for blocked transactions |
| RBI April 2026 Auth | Step-up authentication beyond standard 2FA for medium-risk |
| NIST AI RMF | Map, Measure, Manage, Govern — displayed on dashboard |
| OWASP Top 10 LLMs | LLM01 (Prompt Injection) and LLM08 (Excessive Agency) mitigated |

## Project Structure

```
abuse-ring-sentinel/
├── run.py                      # One-command pipeline launcher
├── requirements.txt
├── docker-compose.yml
│
├── data/
│   ├── generate.py             # Synthetic fraud ring generator (Star/Cycle/Bipartite)
│   └── output/                 # Generated CSVs (10K+ transactions)
│
├── graph_engine/
│   ├── build_graph.py          # Louvain community detection (train-only, no leakage)
│   └── output/                 # Graph risk scores per user
│
├── ml/
│   ├── train.py                # XGBoost + GridSearchCV + SHAP + cost-sensitive threshold
│   └── output/                 # model.json, metrics.json, SHAP plots, cost curve
│
├── backend/
│   ├── app.py                  # FastAPI: Semantic Firewall + ML Gatekeeper + WebSockets
│   ├── redis_client.py         # Redis with graceful in-memory fallback
│   └── mcp_server.py           # Model Context Protocol server (3 tools)
│
└── frontend/
    └── index.html              # Unified SPA: Landing + Simulator + Dashboard
```

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/evaluate_risk` | POST | Pre-auth risk check (Semantic Firewall + ML) |
| `/api/pay` | POST | Full transaction scoring with SHAP explanation |
| `/api/simulate_ring` | POST | Fire 20 coordinated mule transactions |
| `/api/metrics` | GET | Offline held-out test metrics + financials |
| `/api/explain/{txn_id}` | GET | SHAP feature attribution for any decision |
| `/ws/feed` | WS | Real-time transaction + ring alert stream |

## Tech Stack

- **Backend:** Python 3.11, FastAPI, WebSockets, Uvicorn
- **ML:** XGBoost (GridSearchCV tuned), scikit-learn, SHAP
- **Graph:** NetworkX, python-louvain (Louvain community detection)
- **Cache:** Redis (with graceful in-memory fallback)
- **Frontend:** HTML/JS, TailwindCSS (CDN), Single Page Application
- **Security:** MCP Server, Semantic Firewall, PII-masked Audit Traces

## What's Real vs. Simulated

| Component | Status |
|---|---|
| XGBoost inference with SHAP explainability | ✅ Real trained model |
| GridSearchCV hyperparameter tuning | ✅ Real 3-fold CV |
| Cost-sensitive threshold optimization | ✅ Real cost curve analysis |
| Graph-based Louvain community detection | ✅ Real algorithm |
| Semantic Firewall (prompt injection detection) | ✅ Real keyword scanner |
| WebSocket real-time streaming | ✅ Real FastAPI WebSockets |
| MCP Server (3 tools) | ✅ Real stdio MCP protocol |
| Ring detection via shared device/IP clustering | ✅ Real algorithm |
| Redis caching layer | ✅ Real (with in-memory fallback) |
| Payment processing | 🔶 Simulated (no real money) |
| Transaction data | 🔶 Synthetic (calibrated to FATF typologies) |
