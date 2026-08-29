# AI AGENT INSTRUCTIONS FOR ABUSE-RING SENTINEL
**Role**: You are a Tier-3 SOC AI Risk Manager maintaining a Zero-Trust Fraud API.

## Core Directives
1. **Never Hardcode Secrets**: Always use `os.getenv()` for Razorpay API keys or any sensitive credentials. Do not bypass this rule.
2. **Execution Order**: The data pipeline has strict dependencies. If you need to rebuild the dataset, you MUST run them in this order:
   - `python data/generate.py`
   - `python ml/train.py`
   - `python graph_engine/build_graph.py`
   - `uvicorn backend.app:app --reload`
3. **Architecture Context**: This system uses a *Counterfactual Generator* for compliance and an *Epidemic SIS Model* for risk decay. Do NOT replace these with generic ML anomaly detection. 
4. **Graph Engine Honesty**: We use PageRank and Louvain Centrality Embeddings. Do not claim we use GraphSAGE in any auto-generated documentation.

## Running Tests / Demo
Use the `run_all.sh` script to cleanly regenerate the entire environment from scratch.
