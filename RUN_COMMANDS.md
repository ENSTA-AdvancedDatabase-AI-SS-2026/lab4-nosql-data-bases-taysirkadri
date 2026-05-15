# Step-by-step Commands to Run (Local Setup)

## Prerequisites
Make sure all 4 services are installed and running:
- Redis: `redis-server` (default port 6379)
- MongoDB: `mongod --dbpath "C:\data\db"` (default port 27017, user: admin/admin123)
- Cassandra: `cassandra.bat` (default port 9042)
- Neo4j: `neo4j start` (default port 7474 web, 7687 bolt)

---

## TP1: Redis (ex1, ex3, ex4)

### Command
```powershell
cd c:\Users\taysir\lab4-nosql-data-bases-taysirkadri\TP1_KeyValue\starter

# Ensure Redis is running (in another terminal)
# redis-server

# Run tests
python -m pytest tests\test_ex1.py -v

# Run ex4 leaderboard
python ex4_leaderboard.py

# Run ex3 cache benchmark
python ex3_cache.py
```

### Expected output
- All tests pass (PASSED)
- Cache benchmark shows HIT/MISS latencies
- Leaderboard shows top 5 products

---

## TP2: MongoDB (ex1, ex3, ex4)

### Prerequisites
MongoDB must be running with auth setup. On first run, create admin user:
```powershell
mongosh --eval "use admin; db.createUser({user: 'admin', pwd: 'admin123', roles: ['root']})"
```

Or in mongosh interactive shell:
```javascript
use admin
db.createUser({user: 'admin', pwd: 'admin123', roles: ['root']})
```

### Commands
```powershell
cd c:\Users\taysir\lab4-nosql-data-bases-taysirkadri\TP2_Document\starter

# Connect to MongoDB with auth
mongosh -u admin -p admin123 --authenticationDatabase admin

# Inside mongosh, run each script
load("ex1_modelisation.js")
// Wait for output: ✅ Modélisation terminée...

load("ex3_aggregation.js")
// Shows aggregation results

load("ex4_indexes.js")
// Shows BEFORE/AFTER index performance

exit()
```

### Expected output
- ex1: 20 patients + analyses inserted ✓
- ex3: aggregation pipelines execute and show results
- ex4: BEFORE index shows high totalDocsExamined, AFTER shows low (index working)

---

## TP3: Cassandra (ex1, ex2)

### Prerequisites
Cassandra must be running. Create keyspace first:

```powershell
cqlsh
```

Inside cqlsh:
```cql
CREATE KEYSPACE IF NOT EXISTS smartgrid
WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': 1 };
```

### Commands
```powershell
# Apply schema
cqlsh -f c:\Users\taysir\lab4-nosql-data-bases-taysirkadri\TP3_ColumnFamily\starter\ex1_schema.cql

# Run ingestion (may take a few minutes with 10,000 sensors × 5 min)
cd c:\Users\taysir\lab4-nosql-data-bases-taysirkadri\TP3_ColumnFamily\starter
python ex2_ingestion.py
```

### Expected output
```
Démarrage ingestion : 10000 capteurs × 5 min
✅ 50,000 mesures insérées en X.Xs
   Débit : Y,ZZZ mesures/seconde
```

---

## TP4: Neo4j (ex1, ex3)

### Prerequisites
Neo4j must be running. Access at http://localhost:7474, login with neo4j / password123 (first time, change it to something else or keep default).

### Commands
```powershell
# Run Cypher scripts
cypher-shell -u neo4j -p password123 < c:\Users\taysir\lab4-nosql-data-bases-taysirkadri\TP4_Graph\starter\ex1_create_graph.cypher

cypher-shell -u neo4j -p password123 < c:\Users\taysir\lab4-nosql-data-bases-taysirkadri\TP4_Graph\starter\ex3_graph_algorithms.cypher

# Or interactive
cypher-shell -u neo4j -p password123
```

Inside cypher-shell, copy-paste the Cypher queries.

### Expected output
- ex1: "Constraints created", "Competences created", "50 Etudiant nodes", relations created
- ex3: shortestPath results, degree centrality top 10, Louvain communities, recommendations

---

## TP5: Benchmark (full suite)

### Prerequisites
All 4 services running.

### Commands
```powershell
cd c:\Users\taysir\lab4-nosql-data-bases-taysirkadri\TP5_Performance\starter

# Run benchmarks (takes ~10 minutes for 100k writes, 10k reads)
python benchmark.py

# Or reduced for quick test (modify N = 10_000 in the script)
python benchmark.py
```

### Expected output
```
Redis Write: throughput_rps: 50000
MongoDB Write: throughput_rps: 5000
Cassandra Write: throughput_rps: 10000
Redis Read - point: mean_ms: 0.05
...
```

---

## Quick Summary - Run This Order

1. Start all 4 services in separate terminals
2. Run TP1 tests: `cd TP1_KeyValue\starter && python -m pytest tests\ -v`
3. Run TP2 scripts: mongosh shell with load() commands
4. Run TP3: `python ex2_ingestion.py` in TP3 folder
5. Run TP4: `cypher-shell` with Cypher scripts
6. Run TP5: `python benchmark.py` in TP5 folder

All commands are in this file for copy-paste.
