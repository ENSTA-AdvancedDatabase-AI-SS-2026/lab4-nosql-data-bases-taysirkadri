# TP5 - Rapport Benchmark

## 1) Objectif et protocole
But : comparer Redis, MongoDB, Cassandra et Neo4j sur workloads représentatifs (écriture intensive, lecture point lookup, range queries, requêtes complexes). Protocole :
- dataset : 100k enregistrements par SGBD
- scénarios : écriture bulk, lectures point lookup (10k requêtes), range queries (10k), charge concurrente (50 clients)
- métriques : débit (ops/s), latence P50/P95/P99, utilisation CPU/RAM

## 2) Résultats (exemple — remplacer par mesures réelles)

NOTE: The values below are SIMULATED EXAMPLE RESULTS. Replace them with measurements from `benchmark_results.json` after you run the benchmark.

- Écriture (100k) :
	- Redis: total_s=0.83s, throughput=120,482 ops/s (simulated)
	- MongoDB: total_s=4.80s, throughput=20,833 ops/s (simulated)
	- Cassandra: total_s=3.20s, throughput=31,250 ops/s (simulated)
	- Neo4j: total_s=30.00s, throughput=3,333 ops/s (simulated)

- Lecture (10k) :

	- Point lookup (Redis): P50=0.20ms, P95=0.60ms, P99=1.20ms (simulated)
	- Range query (Redis ZRANGE): P50=0.80ms, P95=2.00ms (simulated)
	- Complex query (MongoDB aggregate): P50=5.0ms, P95=12.0ms, P99=25.0ms (simulated)

- Charge concurrente (50 clients) : mean=12.5ms, p95=48ms, p99=120ms (simulated)

## 3) Tableau synthétique
| Critère | Redis | MongoDB | Cassandra | Neo4j |
|---|---:|---:|---:|---:|
| Débit écriture | 120k ops/s (simulé) — Très élevé | 20.8k ops/s (simulé) — Élevé | 31.2k ops/s (simulé) — Élevé | 3.3k ops/s (simulé) — Faible |
| Débit lecture (point) | P50=0.20ms (excellente) | P50≈1.2ms (bonne) | P50≈1.5ms (bonne) | P50≈5-10ms (moyen) |
| Requêtes complexes | Limité (pas adapté) | Très bonne (agrégations) | Moyenne (modélisation requise) | Excellente (traversals & GDS) |
| Scalabilité | Haute (cluster, sharding possible) | Haute (sharding) | Très haute (conçu pour scale-out) | Moyenne (scale-out mais sharding limité) |
| Use case idéal | Cache, counters, sessions | Documents / APIs | Ingestion massive / time-series | Graph traversals & analyses |

## 4) Recommandation
- Si priorité latence lecture simple : utiliser Redis en front (cache) devant la base durable.
- Pour documents et requêtes complexes : MongoDB.
- Pour ingestion massives et time-series : Cassandra.
- Pour problèmes de graphe : Neo4j.

--

Exécutez les scripts de benchmark fournis (`TP5_Performance/starter/benchmark.py`) et complétez les tableaux avec les valeurs mesurées.

Commandes recommandées (pré-requis : Docker Compose démarré via `docker-compose up -d`)

1. Installer les dépendances Python dans un environnement virtuel :

	python -m venv .venv
	.venv\Scripts\activate   # Windows PowerShell
	python -m pip install -r requirements.txt

2. Lancer le benchmark (exécution complète, écrit `benchmark_results.json` dans le dossier starter) :

	python TP5_Performance/starter/benchmark.py

3. Après exécution, inspecter `TP5_Performance/starter/benchmark_results.json` et coller les chiffres dans la section 2.

Notes utiles pour la notation :
- Capturez aussi l'utilisation CPU/RAM pendant les insertions (par ex. `docker stats`) et joignez les captures.
- Pour la lecture (Ex2) exécutez d'abord l'écriture pour remplir les collections/tables, puis lancez la section lecture du script.
- Le script exporte les métriques principales ; pour des mesures plus précises, exécuter plusieurs runs et prendre la médiane.

Fichier de sortie exemple : `TP5_Performance/starter/benchmark_results.json`

{
  "name": "Redis Write",
  "count": 10000,
  "total_s": 1.23,
  "throughput_rps": 8129.0
}

Remplissez la section 2 avec vos valeurs mesurées et joignez `benchmark_results.json` et des captures d'écran à votre soumission.
