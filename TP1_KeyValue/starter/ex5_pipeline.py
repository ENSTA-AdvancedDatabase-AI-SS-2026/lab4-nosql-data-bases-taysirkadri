"""
TP1 - Exercice 5 : Pipeline & Transactions
Fonctions : bulk_insert_products, atomic_purchase (WATCH + MULTI/EXEC)
"""
import redis
from typing import List, Dict

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

LEADERBOARD_KEY = "leaderboard:sales"


def bulk_insert_products(r, products: List[Dict], chunk_size: int = 100):
    """Insérer en bulk une liste de products via pipeline.
    Chaque product doit être un dict avec au moins 'id' et autres champs.
    Retourne le nombre d'items insérés.
    """
    inserted = 0
    for i in range(0, len(products), chunk_size):
        chunk = products[i:i+chunk_size]
        pipe = r.pipeline()
        for p in chunk:
            pid = p.get("id")
            if pid is None:
                continue
            key = f"product:{pid}"
            pipe.hset(key, mapping={k: str(v) for k, v in p.items() if k != "id"})
        pipe.execute()
        inserted += len(chunk)
    return inserted


def atomic_purchase(r, user_id: str, product_id: int, quantity: int = 1) -> bool:
    """Tentative d'achat atomique : décrémente le stock si disponible,
    ajoute au panier et incrémente le leaderboard. Utilise WATCH + MULTI/EXEC.
    Retourne True si transaction réussie, False sinon.
    """
    product_key = f"product:{product_id}"
    cart_key = f"cart:{user_id}"

    while True:
        try:
            pipe = r.pipeline()
            pipe.watch(product_key)
            stock = pipe.hget(product_key, "stock")
            if stock is None:
                pipe.unwatch()
                return False
            stock_int = int(stock)
            if stock_int < quantity:
                pipe.unwatch()
                return False

            pipe.multi()
            pipe.hincrby(product_key, "stock", -quantity)
            pipe.hincrby(cart_key, str(product_id), quantity)
            pipe.zincrby(LEADERBOARD_KEY, quantity, str(product_id))
            pipe.execute()
            return True
        except redis.WatchError:
            # conflit, réessayer
            continue


if __name__ == "__main__":
    # test manuel
    r.flushdb()
    bulk_insert_products(r, [
        {"id": 1, "name": "Phone", "price": "50000", "stock": "10"},
        {"id": 2, "name": "Mouse", "price": "2000", "stock": "50"},
    ])
    print("purchase ok:", atomic_purchase(r, "user:1", 1, 2))
    print("stock after:", r.hget("product:1", "stock"))
