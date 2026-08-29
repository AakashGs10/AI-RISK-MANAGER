from mcp.server.fastmcp import FastMCP
import httpx
import uuid
import asyncio

mcp = FastMCP("Sentinel Agentic Guardrail")
API_BASE = "http://localhost:8000"

@mcp.tool()
async def process_payment(amount: float, item: str, user_prompt: str) -> str:
    """Process a payment on behalf of the user. Pass the RAW natural language prompt as `user_prompt`."""
    payload = {
        "order_id": "", "user_id": "user_mcp_" + uuid.uuid4().hex[:8],
        "device_id": "dev_chatgpt_mcp", "ip": "127.0.0.1", "card_or_upi": "upi_mcp",
        "amount": amount, "new_payee": True, "geo_mismatch": False, "agent_prompt": user_prompt
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{API_BASE}/api/pay", json=payload, timeout=10.0)
            data = resp.json()
            if data.get("decision") == "BLOCK": return f"BLOCKED. Reason: {data.get('reasons')}"
            elif data.get("decision") == "STEP_UP": return f"STEP_UP REQUIRED. Reason: {data.get('reasons')}"
            return f"APPROVED. Txn ID: {data.get('txn_id')}"
        except Exception as e: return f"Error: {e}"

@mcp.tool()
async def evaluate_risk(amount: float, ip_address: str, device_id: str) -> str:
    """Perform a pre-authorization risk check without moving money."""
    payload = {
        "order_id": "", "user_id": "user_mcp", "device_id": device_id, "ip": ip_address,
        "card_or_upi": "upi_test", "amount": amount, "new_payee": True, "geo_mismatch": False, "agent_prompt": ""
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{API_BASE}/api/evaluate_risk", json=payload, timeout=10.0)
            data = resp.json()
            return f"Score: {data.get('risk_score')}/100. Decision: {data.get('decision')}."
        except Exception as e: return f"Error: {e}"

@mcp.tool()
async def generate_dispute_evidence(txn_id: str) -> str:
    """Generate a legal evidence template for a chargeback dispute."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{API_BASE}/api/dispute/{txn_id}", timeout=10.0)
            if resp.status_code == 404: return "Transaction not found."
            return f"EVIDENCE:\n{resp.json().get('evidence_packet')}"
        except Exception as e: return f"Error: {e}"

@mcp.tool()
async def get_recent_transactions() -> str:
    """Fetch the latest transactions processed by the Sentinel engine."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{API_BASE}/api/transactions", timeout=10.0)
            txns = resp.json()
            return f"Retrieved {len(txns)} transactions. Latest: {txns[-5:] if len(txns)>5 else txns}"
        except Exception as e: return f"Error: {e}"

@mcp.tool()
async def get_active_fraud_rings() -> str:
    """Fetch all currently detected botnets and fraud rings in the graph network."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{API_BASE}/api/alerts", timeout=10.0)
            rings = resp.json()
            if not rings: return "No active fraud rings detected."
            return f"DETECTED RINGS:\n{rings}"
        except Exception as e: return f"Error: {e}"

@mcp.tool()
async def submit_fraud_feedback(txn_id: str, is_fraud: bool, source: str) -> str:
    """Submit ground-truth labels for a past transaction to improve the continuous learning model."""
    payload = {"txn_id": txn_id, "confirmed_label": "fraud" if is_fraud else "legit", "source": source}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{API_BASE}/api/feedback", json=payload, timeout=10.0)
            return resp.json().get("status", "Unknown response")
        except Exception as e: return f"Error: {e}"

@mcp.tool()
async def trigger_model_retraining() -> str:
    """Trigger the XGBoost model to incrementally retrain on newly submitted feedback data."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{API_BASE}/api/retrain", timeout=15.0)
            return resp.json().get("status", "Unknown response")
        except Exception as e: return f"Error: {e}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
