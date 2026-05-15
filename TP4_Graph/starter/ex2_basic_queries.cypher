// TP4 - Exercice 2 : Requêtes de base
// 2.1 Trouver tous les amis d'Ahmed (1 saut)
MATCH (a:Etudiant {prenom: 'Ahmed'})-[:CONNAIT]->(ami)
RETURN ami.prenom AS prenom, ami.universite AS universite LIMIT 50;

// 2.2 Trouver les amis d'amis d'Ahmed qui ne sont pas déjà ses amis
MATCH (a:Etudiant {prenom: 'Ahmed'})-[:CONNAIT]->()-[:CONNAIT]->(fof)
WHERE NOT (a)-[:CONNAIT]->(fof) AND fof <> a
RETURN DISTINCT fof.prenom AS suggestion, fof.universite AS universite LIMIT 50;

// 2.3 Étudiants qui suivent le même cours que Fatima mais ne la connaissent pas
MATCH (fatima:Etudiant {prenom: 'Fatima'})-[:SUIT]->(c:Cours)<-[:SUIT]-(p:Etudiant)
WHERE NOT (fatima)-[:CONNAIT]-(p) AND p <> fatima
RETURN DISTINCT p.prenom AS prenom, p.universite AS universite LIMIT 50;

// 2.4 Clubs les plus populaires (par nombre de membres)
MATCH (cl:Club)<-[:MEMBRE_DE]-(m:Etudiant)
RETURN cl.nom AS club, count(m) AS membres
ORDER BY membres DESC LIMIT 10;

// 2.5 Profil complet d'un étudiant : amis, cours, compétences, clubs
MATCH (e:Etudiant {prenom: 'Ahmed'})
OPTIONAL MATCH (e)-[:CONNAIT]->(amis)
OPTIONAL MATCH (e)-[:SUIT]->(cours)
OPTIONAL MATCH (e)-[:MAITRISE]->(comp)
OPTIONAL MATCH (e)-[:MEMBRE_DE]->(club)
RETURN e.prenom AS prenom, collect(DISTINCT amis.prenom) AS amis,
       collect(DISTINCT cours.intitule) AS cours, collect(DISTINCT comp.nom) AS competences,
       collect(DISTINCT club.nom) AS clubs LIMIT 1;
