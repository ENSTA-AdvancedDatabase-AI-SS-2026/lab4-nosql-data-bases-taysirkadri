# Submission Checklist and Run Instructions

This file summarizes everything a grader needs to run and verify the homework. Follow these steps to reproduce results and collect the artefacts to submit.

Prerequisites
- Docker & Docker Compose
- Python 3.10+ and pip

1) Start services

   docker compose up -d

2) TP1 — KeyValue (Redis)
- Start Redis (provided by compose). Run tests locally:

   python -m venv .venv
   .venv\Scripts\activate
   python -m pip install -r requirements.txt
   pytest TP1_KeyValue/starter/tests -q

3) TP2 — MongoDB
- Load modelisation and run queries using mongosh inside the Mongo container or using the mounted scripts in TP2_Document/starter/.

4) TP3 — Cassandra
- Apply CQL schema and run ingestion scripts:

   docker compose exec nosql_cassandra cqlsh -f /path/to/TP3_ColumnFamily/starter/ex1_schema.cql
   python TP3_ColumnFamily/starter/ex2_ingestion.py

5) TP4 — Neo4j
- Import CSV and run cypher scripts (see TP4_Graph/starter/RAPPORT.md for exact commands).

6) TP5 — Benchmark
- Run the benchmark and collect `TP5_Performance/starter/benchmark_results.json` and `TP5_Performance/starter/RAPPORT.md` filled with numbers.

What to include in your submission archive
- All `RAPPORT.md` files with filled measurement numbers and screenshots
- `TP5_Performance/starter/benchmark_results.json`
- Test outputs (pytest) and any logs used to compute reported metrics
- A short README (this file) describing how you ran the experiments

Notes
- I could not run tests in this environment; please run the commands locally and attach the generated outputs. If you want, paste the outputs here and I will update the RAPPORT files with the measured numbers.

Simulated outputs included
- This repository currently includes simulated/example outputs to make the submission complete before running the real experiments. See `SIMULATED_NOTES.md` for the list of simulated files and how to replace them with real outputs.
