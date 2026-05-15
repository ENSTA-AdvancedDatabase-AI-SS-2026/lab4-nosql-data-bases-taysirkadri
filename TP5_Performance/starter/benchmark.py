"""
TP5 - Benchmark Comparatif NoSQL
Mesurer les performances de Redis, MongoDB, Cassandra, Neo4j
"""
import time
import statistics
import json
from typing import Callable, List, Tuple
import redis
from pymongo import MongoClient, InsertOne
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, BatchType
from neo4j import GraphDatabase
import os

# Container for accumulated results (exported at end)
RESULTS_STORE = []

# ─── Utilitaires de mesure ────────────────────────────────────────────────────

def measure_latency(fn: Callable, iterations: int = 1000) -> dict:
    """
    Exécuter fn iterations fois et retourner les statistiques
    """
    latencies = []
    for _ in range(iterations):
        start = time.perf_counter()
        fn()
        latencies.append((time.perf_counter() - start) * 1000)  # en ms
    
    latencies.sort()
    return {
        "mean_ms": statistics.mean(latencies),
        "p50_ms": latencies[int(0.50 * len(latencies))],
        "p95_ms": latencies[int(0.95 * len(latencies))],
        "p99_ms": latencies[int(0.99 * len(latencies))],
        "max_ms": max(latencies),
        "throughput_rps": 1000 / statistics.mean(latencies)
    }


def print_results(name: str, results: dict):
    print(f"\n{'='*50}")
    print(f" {name}")
    print(f"{'='*50}")
    for k, v in results.items():
        print(f"  {k:20s}: {v:.2f}")
    # Persist results for later export
    try:
        RESULTS_STORE.append({"name": name, **results})
    except NameError:
        pass


# ─── Ex1 : Benchmark Écriture ─────────────────────────────────────────────────

def benchmark_write_redis(n: int = 100_000):
    """Insérer n enregistrements dans Redis et mesurer le débit"""
    r = redis.Redis(host='localhost', port=6379)
    pipeline = r.pipeline()
    start = time.perf_counter()
    for i in range(n):
        pipeline.set(f"bench:{i}", json.dumps({"id": i, "payload": f"value-{i}"}))
    pipeline.execute()
    elapsed = time.perf_counter() - start
    results = {
        "count": n,
        "total_s": elapsed,
        "throughput_rps": n / elapsed if elapsed else 0
    }
    print_results("Redis Write", results)


def benchmark_write_mongodb(n: int = 100_000):
    """Insérer n documents dans MongoDB et mesurer le débit"""
    client = MongoClient("mongodb://admin:admin123@localhost:27017/")
    db = client["benchmark"]
    collection = db["items"]
    collection.drop()

    start = time.perf_counter()
    batch = []
    batch_size = 1000
    for i in range(n):
        batch.append(InsertOne({"_id": i, "payload": f"value-{i}", "ts": time.time()}))
        if len(batch) >= batch_size:
            collection.bulk_write(batch, ordered=False)
            batch = []
    if batch:
        collection.bulk_write(batch, ordered=False)

    elapsed = time.perf_counter() - start
    results = {
        "count": n,
        "total_s": elapsed,
        "throughput_rps": n / elapsed if elapsed else 0
    }
    print_results("MongoDB Write", results)


def benchmark_write_cassandra(n: int = 100_000):
    """Insérer n rows dans Cassandra et mesurer le débit"""
    cluster = Cluster(["localhost"])
    session = cluster.connect()
    session.execute(
        """
        CREATE KEYSPACE IF NOT EXISTS benchmark
        WITH replication = { 'class': 'NetworkTopologyStrategy', 'datacenter1': 1 }
        """
    )
    session.set_keyspace("benchmark")
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS kv (
          id int PRIMARY KEY,
          payload text
        )
        """
    )

    prepared = session.prepare("INSERT INTO kv (id, payload) VALUES (?, ?)")
    start = time.perf_counter()
    batch = BatchStatement(batch_type=BatchType.UNLOGGED)
    batch_size = 50
    for i in range(n):
        batch.add(prepared, (i, f"value-{i}"))
        if len(batch) >= batch_size:
            session.execute(batch)
            batch = BatchStatement(batch_type=BatchType.UNLOGGED)
    if len(batch) > 0:
        session.execute(batch)

    elapsed = time.perf_counter() - start
    results = {
        "count": n,
        "total_s": elapsed,
        "throughput_rps": n / elapsed if elapsed else 0
    }
    print_results("Cassandra Write", results)
    cluster.shutdown()


# ─── Ex2 : Benchmark Lecture ─────────────────────────────────────────────────

def benchmark_read_redis():
    """Point lookup, range (ZRANGE), complex (pipeline multi-get)"""
    r = redis.Redis(host='localhost', port=6379)
    keys = [f"bench:{i}" for i in range(1000)]
    for i, key in enumerate(keys):
        r.set(key, json.dumps({"id": i, "payload": f"value-{i}"}))

    def point_lookup():
        r.get("bench:500")

    r.zadd("bench:zset", {str(i): i for i in range(2000)})

    def range_query():
        r.zrange("bench:zset", 100, 200)

    def complex_query():
        pipe = r.pipeline()
        for k in keys[:50]:
            pipe.get(k)
        pipe.execute()

    print_results("Redis Read - point", measure_latency(point_lookup, 1000))
    print_results("Redis Read - range", measure_latency(range_query, 1000))
    print_results("Redis Read - pipeline", measure_latency(complex_query, 500))


def benchmark_read_mongodb():
    """find_one, find avec range, aggregate pipeline"""
    client = MongoClient("mongodb://admin:admin123@localhost:27017/")
    db = client["benchmark"]
    collection = db["items"]

    if collection.count_documents({}) < 1000:
        collection.drop()
        collection.insert_many(
            {"_id": i, "payload": f"value-{i}", "ts": time.time() + i}
            for i in range(2000)
        )
        collection.create_index("ts")

    def point_lookup():
        collection.find_one({"_id": 1000})

    def range_query():
        list(collection.find({"ts": {"$gte": time.time(), "$lte": time.time() + 500}}))

    def complex_query():
        list(collection.aggregate([
            {"$match": {"_id": {"$gte": 0, "$lt": 1000}}},
            {"$group": {"_id": None, "count": {"$sum": 1}}}
        ]))

    print_results("MongoDB Read - point", measure_latency(point_lookup, 1000))
    print_results("MongoDB Read - range", measure_latency(range_query, 200))
    print_results("MongoDB Read - aggregate", measure_latency(complex_query, 200))


# ─── Ex3 : Charge concurrente ─────────────────────────────────────────────────

def benchmark_concurrent(db_fn: Callable, n_clients: int = 50, requests_per_client: int = 200):
    """
    Lancer n_clients threads simultanés
    Chaque thread effectue requests_per_client requêtes
    Mesurer les latences globales et la dégradation vs single client
    """
    import threading
    latencies = []
    lock = threading.Lock()

    def worker():
        for _ in range(requests_per_client):
            start = time.perf_counter()
            db_fn()
            elapsed = (time.perf_counter() - start) * 1000
            with lock:
                latencies.append(elapsed)

    threads = [threading.Thread(target=worker) for _ in range(n_clients)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    latencies.sort()
    results = {
        "mean_ms": statistics.mean(latencies) if latencies else 0,
        "p95_ms": latencies[int(0.95 * len(latencies))] if latencies else 0,
        "p99_ms": latencies[int(0.99 * len(latencies))] if latencies else 0,
        "total_requests": len(latencies)
    }
    print_results("Concurrent Load", results)


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀 Benchmark NoSQL - Comparatif des 4 technologies")
    print("="*60)
    
    N = 10_000  # Réduire pour les tests, 100_000 pour la production
    
    print(f"\n📝 Benchmark Écriture ({N:,} enregistrements)")
    benchmark_write_redis(N)
    benchmark_write_mongodb(N)
    benchmark_write_cassandra(N)
    
    print(f"\n📖 Benchmark Lecture (1,000 requêtes)")
    benchmark_read_redis()
    benchmark_read_mongodb()
    
    print(f"\n⚡ Test Charge Concurrente (50 clients)")
    # benchmark_concurrent(...)
    
    print("\n✅ Benchmark terminé ! Consultez RAPPORT.md pour l'analyse.")
    # Export collected results to a JSON file for easy inclusion in RAPPORT.md
    try:
        out_path = os.path.join(os.path.dirname(__file__), 'benchmark_results.json')
        with open(out_path, 'w', encoding='utf-8') as fh:
            json.dump(RESULTS_STORE, fh, indent=2)
        print(f"\nSaved results to {out_path}")
    except Exception as exc:
        print(f"Could not write results file: {exc}")
