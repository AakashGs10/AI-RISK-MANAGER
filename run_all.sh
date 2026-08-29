#!/bin/bash
echo "[1/4] Generating synthetic transaction data and fraud rings..."
python data/generate.py

echo "[2/4] Building Cross-Merchant Federated Graph & Epidemic Models..."
python graph_engine/build_graph.py

echo "[3/4] Training XGBoost Fraud-Spike Classifier..."
python ml/train.py

echo "[4/4] Starting FastAPI Gateway..."
echo "API live at http://localhost:8000"
uvicorn backend.app:app --reload --port 8000
