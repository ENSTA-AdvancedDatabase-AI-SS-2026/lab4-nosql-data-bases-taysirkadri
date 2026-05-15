# TP3 - Rapport Cassandra

## 1) Contexte et objectif
But : modéliser des tables Cassandra pour des séries temporelles et supporter un fort débit d'ingestion (milliers d'événements/s).

## 2) Schéma proposé (extraits)
- `mesures_par_capteur` :
```sql
CREATE TABLE mesures_par_capteur (
	wilaya text,
	capteur_id uuid,
	date date,
	ts timestamp,
	tension float,
	courant float,
	puissance float,
	PRIMARY KEY ((wilaya, date), capteur_id, ts)
) WITH CLUSTERING ORDER BY (capteur_id ASC, ts DESC);
```
- `alertes_par_wilaya` :
```sql
CREATE TABLE alertes_par_wilaya (
	wilaya text,
	jour date,
	ts timestamp,
	capteur_id uuid,
	niveau float,
	PRIMARY KEY ((wilaya, jour), ts)
);
```
- `agregats_horaires` (pré-agrégats) :
```sql
CREATE TABLE agregats_horaires (
	wilaya text,
	date date,
	heure int,
	consommation_avg double,
	PRIMARY KEY ((wilaya, date), heure)
);
```

## 3) Hot partitions — risques et mitigation
- Risque : partitioning trop grossière (ex: uniquement `wilaya`) crée des partitions « hot ».
- Mitigation : inclure `date` dans la partition key, sharding par capteur ou par bucket (ajouter hash mod N) pour haut débit, écrire en batch bien dimensionné.

## 4) ALLOW FILTERING
- Pourquoi éviter : force Cassandra à scanner partitions qui dégradent performance et brisent scalabilité.
- Alternative : créer une table dédiée adaptée à la requête (duplicate data for query patterns). Exemple : pour rechercher capteurs en alerte par critère, maintenir `alertes_par_wilaya` indexée par jour.

## 5) Compaction — choix et justification
- Séries temporelles → `TimeWindowCompactionStrategy (TWCS)` recommandé pour données append-only, permet compactions efficaces sur fenêtres temporelles.
- Tables d'agrégats statiques → `SizeTieredCompactionStrategy` ou `LeveledCompactionStrategy` selon besoin.

## 6) Tests et métriques
- Mesurer : ingestion rate (rows/s), latence d'insert, latence des requêtes cibles. Utiliser `cassandra-stress` ou scripts Python (`cassandra-driver`).

## 7) Bonus — Materialized Views
- MV utiles pour requêtes alternatives mais attention à coûts d'écriture et incohérences temporaires ; préférer écriture double (denormalisation explicite) pour plus de contrôle.

--

Complétez avec vos mesures d'ingestion et les résultats des requêtes cibles.
--

Complétez avec les choix de schéma, examples de requêtes et mesures.
