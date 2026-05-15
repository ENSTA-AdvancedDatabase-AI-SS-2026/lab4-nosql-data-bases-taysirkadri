# TP1 - Rapport Redis

## 1) Résumé exécutif
Objectif : ajouter une couche de cache Redis pour réduire la latence des pages produit et alléger PostgreSQL. Résultat attendu : diminution importante des temps de réponse pour les lectures fréquentes, et classement en temps réel via `ZSET`.

## 2) Méthodologie de mesure
- Outils : script de test (pytest + locust/simple loop), `redis-cli --latency`, `time` autour des opérations principales.
- Mesures à collecter : latence moyenne (ms) en HIT, latence moyenne en MISS, hit rate (%), charge CPU/mémoire du serveur DB lors du test.

Exemple de commande pour mesurer :
```bash
# lancer le script de benchmark de l'exo
python bench_cache.py --requests 10000 --concurrency 10

# ou via pytest (si fourni)
pytest tests/ -q
```

Remplissez les valeurs mesurées ci-dessous après exécution :

NOTE: The sample values below are SIMULATED EXAMPLES. Run the real benchmark and replace them.

- Cache hit (ms): 0.25 ms (simulated)
- Cache miss (ms): 6.20 ms (simulated)
- Hit rate (%): 92.4% (simulated)

You can replace these with real measurements from your local run. Example: `python bench_cache.py --requests 10000`.

## 3) Choix de modélisation et justification
- Produits — `Hash` par produit (`product:{id}`) : permet de stocker champs nom/prix/stock sans sérialiser JSON et d'accéder à champs isolés (`HGET`).
- Panier — `Hash` par utilisateur (`cart:{user_id}`) : stockage compact des quantités et meta panier; TTL non appliqué pour persistance (optionnel : sauvegarde en DB).
- Historique — `List` (`history:{user_id}`) : push en tête (`LPUSH`) et trim (`LTRIM`) pour garder N dernières actions.
- Catégories — `Set` (`category:{name}`) : membership test rapide, opérations d'intersection pour filtres multi-catégorie.
- Classement ventes — `Sorted Set` (`leaderboard:sales`) : score = ventes, opérations `ZINCRBY`, `ZREVRANGE` pour top-N.

Diagramme simplifié :
```
product:100 -> HSET product:100 name "Chaise" price 129.0 stock 42
cart:42 -> HSET cart:42 100 2   # produit 100 quantité 2
leaderboard:sales ZINCRBY leaderboard:sales 1 100
```

## 4) Solutions aux questions
1) Que se passe-t-il si Redis redémarre ?
   - Redis perd ses données si basé uniquement en mémoire sauf si RDB/AOF est activé. Pour données critiques (panier, sessions) : soit persister (AOF/RDB), soit recharger depuis la base relationnelle au besoin (cache-aside). Expliquer trade-off en rapport.

2) Cohérence cache/DB en cas d'accès concurrent :
   - Stratégie recommandée : Cache-Aside + invalidation atomique.
   - Sur mise à jour : 1) Mettre à jour la DB, 2) Supprimer/mettre à jour la clé cache. Pour éviter race conditions, utiliser lock simple (SETNX + expiration) ou versioning (optimistic) si nécessaire.

3) Quand un TTL trop court est problématique ?
   - Si TTL < fréquence d'accès, cache churn élevé → beaucoup de misses et surcharge DB. TTL doit être choisi selon la fréquence d'accès et la tolérance à la donnée éventuellement obsolète.

## 5) Exemples d'implémentation (extraits)
```python
# Cache-aside pseudo-code
def get_product(pid):
	val = redis.hgetall(f"product:{pid}")
	if val:
		return val
	prod = db.query_product(pid)
	if prod:
		redis.hset(f"product:{pid}", mapping=prod)
		redis.expire(f"product:{pid}", 3600)
	return prod
```

## 6) Bonus — Rate limiting (si fait)
- Implémentation simple : `INCR` par clé `rate:{user}:{window}` + `EXPIRE` pour TTL de fenêtre. Pour token-bucket, utiliser Lua script pour atomicité.

## 7) Conclusion
Décrire brièvement les gains observés (mettre vos chiffres mesurés) et recommander la configuration finale (TTL, persistance, mécanisme d'invalidation).
