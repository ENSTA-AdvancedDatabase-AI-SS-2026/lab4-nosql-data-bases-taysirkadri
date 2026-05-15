# TP4 - Rapport Neo4j

## 1) Schéma et modélisation
- Labels : `:Etudiant`, `:Cours`, `:Club`, `:Entreprise`, `:Competence`.
- Relations et propriétés :
	- `(:Etudiant)-[:CONNAIT {depuis}]->(:Etudiant)`
	- `(:Etudiant)-[:SUIT {semestre, note}]->(:Cours)`
	- `(:Etudiant)-[:MEMBRE_DE {role}]->(:Club)`

Schéma choisi pour favoriser requêtes de voisinage et algorithmes GDS.

## 2) Algorithmes et résultats attendus
- Louvain (communautés) : permettre d'identifier groupes d'étudiants fortement interconnectés — rapporter le nombre de communautés et tailles.
- Centralité de degré : lister top-N étudiants par degré.
- ShortestPath : afficher chemin et longueur entre deux étudiants.

Exemple de commande pour Louvain (GDS) :
```cypher
CALL gds.graph.create('g',{Etudiant: 'Etudiant'},{CONNAIT: {type: 'CONNAIT', orientation: 'UNDIRECTED'}});
CALL gds.louvain.stream('g') YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).prenom AS prenom, communityId LIMIT 20;
```

## 3) Comparaison SQL vs Cypher (exemple)
- Requête : trouver amis d'amis non-connectés directement.
- SQL : plusieurs JOINs récursifs ou CTEs complexes et coûteux.
- Cypher : `MATCH (a:Etudiant {id:...})-[:CONNAIT*2]-(b) WHERE NOT (a)-[:CONNAIT]-(b) RETURN b` — plus expressif et performant pour graph traversal.

## 4) Recommandations et livrables
- Inclure capture Neo4j Browser du graphe, commandes GDS exécutées, et interprétation des communautés.

## 4) Recommandations et livrables
- Inclure capture Neo4j Browser du graphe, commandes GDS exécutées, et interprétation des communautés.

## 5) Commandes d'exécution (pour le correcteur)
Prérequis : Docker Compose (services Neo4j/Cassandra/Mongo/Redis) démarrés via `docker-compose up -d`.

1. Ouvrir un shell dans le container Neo4j (nom du service : `nosql_neo4j` dans le compose) :

	docker compose exec nosql_neo4j bash

2. Copier `starter/import/students.csv` dans le dossier `import/` du container ou monter le dossier starter/import comme volume.

3. Exécuter le script d'import et de création du graphe :

	cypher-shell -u neo4j -p neo4j "$(cat /var/lib/neo4j/import/ex1_create_graph.cypher)"

	OU (depuis l'hôte si `neo4j-admin import`/`cypher-shell` sont disponibles) :

	cat TP4_Graph/starter/ex1_create_graph.cypher | docker compose exec -T nosql_neo4j cypher-shell -u neo4j -p neo4j

4. Lancer les requêtes des exercices :

	- ex2 (requêtes de base) : cat TP4_Graph/starter/ex2_basic_queries.cypher | docker compose exec -T nosql_neo4j cypher-shell -u neo4j -p neo4j
	- ex3 (algorithmes GDS) : cat TP4_Graph/starter/ex3_graph_algorithms.cypher | docker compose exec -T nosql_neo4j cypher-shell -u neo4j -p neo4j
	- ex4 (requêtes avancées) : cat TP4_Graph/starter/ex4_advanced.cypher | docker compose exec -T nosql_neo4j cypher-shell -u neo4j -p neo4j

5. Capturer les sorties (STDOUT) et joindre les captures ou `COPY` de l'output (.txt) dans l'archive de soumission.

## 6) Points à fournir pour attribution de la note maximale
- les scripts `.cypher` présents dans `TP4_Graph/starter/` (ex1..ex4) doivent s'exécuter et produire des résultats lisibles
- captures d'écran du Neo4j Browser montrant la visualisation et les sorties GDS
- un court commentaire interprétant les résultats (top communities, central nodes, recommandations)

Complétez avec captures d'écran, fichiers d'output et interprétations pour la soumission.
