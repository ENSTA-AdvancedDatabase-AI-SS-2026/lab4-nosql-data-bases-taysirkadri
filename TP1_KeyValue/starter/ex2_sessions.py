"""
TP1 - Exercice 2 : Sessions utilisateur (sliding TTL)
Fonctions : create_session, get_session, renew_session, delete_session
"""
import redis
import uuid
import time
from typing import Optional

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def create_session(r, user_id: str, data: dict = None, ttl_seconds: int = 1800) -> str:
    """Créer une session et retourner le token (UUID)."""
    token = str(uuid.uuid4())
    key = f"session:{token}"
    payload = {"user_id": user_id, "created_at": str(int(time.time()))}
    if data:
        for k, v in data.items():
            payload[k] = v

    r.hset(key, mapping=payload)
    r.expire(key, ttl_seconds)
    return token


def get_session(r, token: str) -> Optional[dict]:
    """Retourner le dict stocké pour la session ou None."""
    key = f"session:{token}"
    data = r.hgetall(key)
    return data if data else None


def renew_session(r, token: str, ttl_seconds: int = 1800) -> bool:
    """Renouveler la TTL (sliding expiration). Retourne True si la session existait."""
    key = f"session:{token}"
    if r.exists(key):
        r.expire(key, ttl_seconds)
        return True
    return False


def delete_session(r, token: str) -> bool:
    """Supprimer la session. Retourne True si supprimée."""
    key = f"session:{token}"
    return r.delete(key) == 1


if __name__ == "__main__":
    # petit test manuel
    r.flushdb()
    token = create_session(r, "user:42", {"role": "buyer"}, ttl_seconds=60)
    print("token:", token)
    print("get:", get_session(r, token))
    print("renew:", renew_session(r, token, 120))
    print("delete:", delete_session(r, token))
