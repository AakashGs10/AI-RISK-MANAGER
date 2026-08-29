import json
import os
import logging
import csv

logger = logging.getLogger(__name__)

class RiskStore:
    """Graph risk score store. Tries Redis; falls back to in-memory dict."""

    def __init__(self, redis_url: str = None):
        self._redis = None
        self._fallback: dict[str, dict] = {}
        url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        try:
            import redis as redis_lib
            self._redis = redis_lib.from_url(url, decode_responses=True)
            self._redis.ping()
            logger.info('Connected to Redis at %s', url)
        except Exception as e:
            logger.warning('Redis unavailable (%s) — using in-memory fallback', e)
            self._redis = None

    @property
    def connected(self) -> bool:
        return self._redis is not None

    def get_graph_risk(self, user_id: str) -> dict:
        """Returns {score, ring_type, community_id}. Defaults to score=0.5 on miss."""
        default = {'score': 0.5, 'ring_type': 'unknown', 'community_id': -1}
        try:
            if self._redis:
                raw = self._redis.get(f'user:{user_id}:graph_risk')
                if raw:
                    return json.loads(raw)
            elif user_id in self._fallback:
                return self._fallback[user_id]
        except Exception:
            pass
        return default

        # ==============================================================================
    # ARCHITECTURE CONSTRAINT: FEEDBACK LOOP SAFEGUARD
    # ==============================================================================
    # ALLOWED — only these two write paths may touch graph_risk_score:
    #   1. /api/feedback with an analyst-confirmed or chargeback-confirmed label
    #   2. the offline batch job using ground-truth `is_fraud` from your
    #      synthetic data generator (in the demo/training context)
    #
    # NEVER ALLOWED:
    #   - using `decision` or `risk_score` from /api/pay as if it were a label
    #   - any code path where a BLOCK decision gets treated as `label=1`
    #     without a human or confirmed-outcome step in between
    # ==============================================================================
    def set_graph_risk(self, user_id: str, score: float,
                       ring_type: str = 'none', community_id: int = -1,
                       ttl: int = 900):
        data = {'score': score, 'ring_type': ring_type, 'community_id': community_id}
        try:
            if self._redis:
                self._redis.setex(f'user:{user_id}:graph_risk', ttl, json.dumps(data))
            else:
                self._fallback[user_id] = data
        except Exception:
            self._fallback[user_id] = data

    def load_from_csv(self, csv_path: str) -> int:
        """Bulk-load graph risk scores from CSV. Returns count loaded."""
        if not os.path.exists(csv_path):
            logger.warning('Graph risk CSV not found at %s', csv_path)
            return 0
        count = 0
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.set_graph_risk(
                    user_id=row['user_id'],
                    score=float(row['graph_risk_score']),
                    ring_type=row.get('detected_ring_type', 'none'),
                    community_id=int(row.get('community_id', -1)),
                )
                count += 1
        logger.info('Loaded %d graph risk scores from %s', count, csv_path)
        return count
