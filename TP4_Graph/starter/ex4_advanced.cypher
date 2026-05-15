// TP4 - Exercice 4 : Requêtes avancées

// 4.1 Trouver un tuteur : Etudiant en Master qui maîtrise Python et note >14 en BDD
MATCH (t:Etudiant)-[m:MAITRISE]->(comp:Competence {nom: 'Python'})
MATCH (t)-[s:SUIT]->(c:Cours {code: 'INFO401'})
WHERE t.annee >= 4 AND s.note > 14
RETURN t.prenom, t.nom, t.universite, s.note LIMIT 10;

// 4.2 Réseau alumni dans une entreprise (jusqu'à 3 sauts)
MATCH (me:Etudiant {prenom: 'Ahmed'})-[*1..3]-(x:Etudiant)-[:A_STAGE_CHEZ]->(ent:Entreprise {nom: 'Sonatrach'})
RETURN DISTINCT x.prenom AS prenom, x.nom AS nom, ent.nom AS entreprise LIMIT 50;

// 4.3 Détection de ponts (nodes avec high betweenness or articulation points)
// Approche pratique : utiliser GDS to compute betweenness centrality and list top nodes
CALL gds.betweenness.stream('reseau_social') YIELD nodeId, score
RETURN gds.util.asNode(nodeId).prenom AS prenom, score
ORDER BY score DESC LIMIT 10;

// 4.4 Analyse temporelle : nouvelles connexions par mois
MATCH ()-[r:CONNAIT]->() WHERE exists(r.depuis)
RETURN r.depuis AS annee, count(r) AS connexions ORDER BY r.depuis DESC LIMIT 24;

// 4.5 Score de similarité (Jaccard) : étudiants les plus similaires à Ahmed
MATCH (a:Etudiant {prenom: 'Ahmed'})
MATCH (b:Etudiant) WHERE b <> a
WITH a, b,
  size((a)-[:SUIT]->()<-[:SUIT]-(b)) AS cours_communs,
  size((a)-[:MAITRISE]->()<-[:MAITRISE]-(b)) AS comp_communs
RETURN b.prenom AS prenom, (cours_communs + comp_communs) AS score
ORDER BY score DESC LIMIT 10;
