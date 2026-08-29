def build_evidence_packet(txn: dict, user_history: list) -> dict:
    device_matches = sum(1 for t in user_history if t.get("device_id") == txn.get("device_id"))
    ip_matches = sum(1 for t in user_history if t.get("ip") == txn.get("ip"))
    
    device_consistency = f"{device_matches} out of {len(user_history)} prior transactions used this device" if user_history else "No prior history"
    ip_consistency = f"{ip_matches} out of {len(user_history)} prior transactions used this IP" if user_history else "No prior history"
    
    features = txn.get("features", {})
    account_age_days = features.get("device_age_hours", 0) / 24
    
    top_factors = txn.get("reasons", [])
    top_factors_text = ", ".join(top_factors) if top_factors else "No explicit SHAP factors"
    
    import datetime
    dt_str = datetime.datetime.fromtimestamp(txn.get("timestamp", 0)).strftime('%Y-%m-%d %H:%M:%S') if txn.get("timestamp") else "UNKNOWN"
    
    packet = {
        "transaction_id": txn.get("txn_id"),
        "timestamp": dt_str,
        "amount": txn.get("amount", 0),
        "decision_at_time": txn.get("decision", "UNKNOWN"),
        "risk_score_at_time": txn.get("risk_score", 0.0),
        "device_consistency_text": device_consistency,
        "ip_consistency_text": ip_consistency,
        "prior_transaction_count": len(user_history),
        "account_age_days": round(account_age_days, 1),
        "top_factors_text": top_factors_text
    }
    return packet

def generate_evidence_prose(packet: dict) -> str:
    TEMPLATE = """
This transaction (ID: {transaction_id}, amount: {amount}) was processed on
{timestamp} and evaluated at a risk score of {risk_score_at_time}/100,
resulting in a system decision of {decision_at_time}.

Account history: {prior_transaction_count} prior transactions from this
account. Device fingerprint: {device_consistency_text}. IP address:
{ip_consistency_text}.

Primary risk factors considered at time of transaction: {top_factors_text}.

**Auto-drafted from logged transaction data — requires human review before submission.**
"""
    return TEMPLATE.format(**packet).strip()
