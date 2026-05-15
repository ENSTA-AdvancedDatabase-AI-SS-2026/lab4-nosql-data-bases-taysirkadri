// TP4 - Exercice 1 : Création du graphe UniConnect DZ
// Effacer la base pour partir propre
MATCH (n) DETACH DELETE n;

// ─── 1.1 : Contraintes d'unicité ─────────────────────────────────────────────
CREATE CONSTRAINT etudiant_id IF NOT EXISTS FOR (e:Etudiant) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT cours_code IF NOT EXISTS FOR (c:Cours) REQUIRE c.code IS UNIQUE;
CREATE CONSTRAINT competence_nom IF NOT EXISTS FOR (c:Competence) REQUIRE c.nom IS UNIQUE;

// ─── 1.2 : Créer les compétences ──────────────────────────────────────────────
UNWIND [
  {nom: "Python", categorie: "Programmation"},
  {nom: "Java", categorie: "Programmation"},
  {nom: "SQL", categorie: "Bases de Données"},
  {nom: "NoSQL", categorie: "Bases de Données"},
  {nom: "Machine Learning", categorie: "IA"},
  {nom: "Deep Learning", categorie: "IA"},
  {nom: "React", categorie: "Web"},
  {nom: "Docker", categorie: "DevOps"},
  {nom: "Linux", categorie: "Systèmes"},
  {nom: "Réseaux", categorie: "Infrastructure"}
] AS comp
MERGE (:Competence {nom: comp.nom, categorie: comp.categorie});

// ─── 1.3 : Créer les cours ────────────────────────────────────────────────────
UNWIND [
  {code: "INFO401", intitule: "Bases de Données Avancées", credits: 6, dept: "Informatique"},
  {code: "INFO402", intitule: "Intelligence Artificielle", credits: 6, dept: "Informatique"},
  {code: "INFO403", intitule: "Développement Web", credits: 4, dept: "Informatique"},
  {code: "INFO404", intitule: "Systèmes Distribués", credits: 5, dept: "Informatique"},
  {code: "INFO405", intitule: "Cloud Computing", credits: 4, dept: "Informatique"}
] AS cours
MERGE (:Cours {code: cours.code, intitule: cours.intitule, 
               credits: cours.credits, departement: cours.dept});

// ─── 1.4 : Créer les étudiants ────────────────────────────────────────────────
// 50 étudiants avec données algériennes réalistes
// Universités : USTHB, UMBB, USTO, UMC, UBMA
// Filieres : Informatique, Mathematiques, Electronique, Telecoms, GL

WITH
  ["Ahmed", "Fatima", "Karim", "Yasmina", "Rania", "Mehdi", "Sara", "Youcef",
   "Lina", "Anis", "Nadia", "Samir", "Imane", "Nabil", "Amine", "Salma",
   "Riad", "Meriem", "Bilal", "Hind", "Walid", "Sofiane", "Aya", "Dounia",
   "Ilyes", "Sara", "Hichem", "Amina", "Omar", "Houda", "Rachid", "Selma",
   "Farid", "Lamia", "Issam", "Yasmine", "Khaled", "Nora", "Adel", "Lina",
   "Mourad", "Ines", "Rafik", "Nesrine", "Zahir", "Kenza", "Samia", "Tarek",
   "Amira", "Nassim"] AS prenoms,
  ["Bensalem", "Ouali", "Meziane", "Hamdi", "Belkacem", "Derbal", "Amrani",
   "Cherif", "Boudia", "Haddar", "Benali", "Mansouri", "Bouzid", "Kaci",
   "Toumi", "Saidi", "Rahmani", "Brahimi", "Ziani", "Guerfi"] AS noms,
  ["USTHB", "UMBB", "USTO", "UMC", "UBMA"] AS universites,
  ["Informatique", "Mathematiques", "Electronique", "Telecoms", "GL"] AS filieres,
  ["Alger", "Boumerdes", "Oran", "Constantine", "Annaba"] AS villes
UNWIND range(1, 50) AS i
WITH
  i,
  prenoms[i % size(prenoms)] AS prenom,
  noms[i % size(noms)] AS nom,
  universites[i % size(universites)] AS universite,
  filieres[i % size(filieres)] AS filiere,
  villes[i % size(villes)] AS ville
WITH
  i,
  prenom,
  nom,
  universite,
  filiere,
  ville,
  CASE
    WHEN i < 10 THEN "E00" + toString(i)
    WHEN i < 100 THEN "E0" + toString(i)
    ELSE "E" + toString(i)
  END AS id
MERGE (e:Etudiant {id: id})
SET e.prenom = prenom,
    e.nom = nom,
    e.universite = universite,
    e.filiere = filiere,
    e.annee = 1 + (i % 5),
    e.ville = ville;

// ─── 1.5 : Créer les relations ────────────────────────────────────────────────
// Relations CONNAIT entre étudiants
// Assurer que le graphe est connexe (pas d'etudiants isoles)

UNWIND [
  {nom: "Club IA USTHB", universite: "USTHB", domaine: "IA"},
  {nom: "Club Data UMBB", universite: "UMBB", domaine: "Data"},
  {nom: "Club Cyber USTO", universite: "USTO", domaine: "Securite"},
  {nom: "Club Web UMC", universite: "UMC", domaine: "Web"},
  {nom: "Club Robot UBMA", universite: "UBMA", domaine: "Robotique"}
] AS club
MERGE (:Club {nom: club.nom, universite: club.universite, domaine: club.domaine});

UNWIND [
  {nom: "Sonatrach", secteur: "Energie", ville: "Alger"},
  {nom: "Ooredoo", secteur: "Telecom", ville: "Alger"},
  {nom: "Algex", secteur: "Services", ville: "Oran"},
  {nom: "Cevital", secteur: "Industrie", ville: "Bejaia"}
] AS ent
MERGE (:Entreprise {nom: ent.nom, secteur: ent.secteur, ville: ent.ville});

MATCH (c401:Cours {code: "INFO401"}), (c402:Cours {code: "INFO402"}), (c403:Cours {code: "INFO403"}),
      (c404:Cours {code: "INFO404"}), (c405:Cours {code: "INFO405"}),
      (sql:Competence {nom: "SQL"}), (nosql:Competence {nom: "NoSQL"}),
      (py:Competence {nom: "Python"}), (ml:Competence {nom: "Machine Learning"}),
      (dl:Competence {nom: "Deep Learning"}), (docker:Competence {nom: "Docker"})
MERGE (c401)-[:REQUIERT]->(sql)
MERGE (c401)-[:REQUIERT]->(nosql)
MERGE (c402)-[:REQUIERT]->(py)
MERGE (c402)-[:REQUIERT]->(ml)
MERGE (c402)-[:REQUIERT]->(dl)
MERGE (c403)-[:REQUIERT]->(py)
MERGE (c403)-[:REQUIERT]->(docker)
MERGE (c404)-[:REQUIERT]->(sql)
MERGE (c405)-[:REQUIERT]->(docker);

MATCH (e:Etudiant)
WITH collect(e) AS etudiants
UNWIND range(0, size(etudiants) - 1) AS i
WITH etudiants[i] AS e1, etudiants[(i + 1) % size(etudiants)] AS e2
MERGE (e1)-[:CONNAIT {depuis: 2022, contexte: "Promo"}]->(e2);

MATCH (e:Etudiant)
WITH collect(e) AS etudiants
UNWIND range(0, size(etudiants) - 1) AS i
WITH etudiants[i] AS e1, etudiants[(i + 5) % size(etudiants)] AS e2
MERGE (e1)-[:CONNAIT {depuis: 2023, contexte: "Club"}]->(e2);

// Relations SUIT (etudiant → cours) avec notes

MATCH (e:Etudiant)
WITH e, toInteger(substring(e.id, 1)) AS idx
MATCH (c:Cours)
WITH e, idx, collect(c) AS cours
MERGE (e)-[:SUIT {semestre: 5, note: 10 + (idx % 11)}]->(cours[idx % size(cours)])
MERGE (e)-[:SUIT {semestre: 5, note: 10 + ((idx + 2) % 11)}]->(cours[(idx + 2) % size(cours)]);

// Relations MAITRISE (etudiant → competence) avec niveaux

MATCH (e:Etudiant)
WITH e, toInteger(substring(e.id, 1)) AS idx
MATCH (c:Competence)
WITH e, idx, collect(c) AS competences
MERGE (e)-[:MAITRISE {niveau: 2 + (idx % 3)}]->(competences[idx % size(competences)])
MERGE (e)-[:MAITRISE {niveau: 2 + ((idx + 4) % 3)}]->(competences[(idx + 4) % size(competences)]);

MATCH (e:Etudiant)
WITH e, toInteger(substring(e.id, 1)) AS idx
MATCH (cl:Club)
WITH e, idx, collect(cl) AS clubs
MERGE (e)-[:MEMBRE_DE {role: CASE WHEN idx % 5 = 0 THEN "Responsable" ELSE "Membre" END}]
  ->(clubs[idx % size(clubs)]);

MATCH (e:Etudiant)
WITH e, toInteger(substring(e.id, 1)) AS idx
MATCH (ent:Entreprise)
WITH e, idx, collect(ent) AS ents
WHERE idx % 3 = 0
MERGE (e)-[:A_STAGE_CHEZ {annee: 2024, duree_mois: 2 + (idx % 4)}]
  ->(ents[idx % size(ents)]);

// Vérification
MATCH (n) RETURN labels(n)[0] AS type, count(n) AS total ORDER BY total DESC;
MATCH ()-[r]->() RETURN type(r) AS relation, count(r) AS total ORDER BY total DESC;

// ─── 1.6 : Import depuis CSV (import/students.csv) ───────────────────────────
// Le fichier students.csv est fourni dans le dossier starter/import/
// Ce bloc importe les étudiants, met à jour leurs propriétés si déjà présents
// et crée quelques relations garantissant la connexité.
LOAD CSV WITH HEADERS FROM 'file:///students.csv' AS row
MERGE (e:Etudiant {id: row.id})
SET e.prenom = row.prenom,
    e.nom = row.nom,
    e.universite = row.universite,
    e.filiere = row.filiere,
    e.annee = toInteger(row.annee),
    e.ville = row.ville

// Associer chaque étudiant importé à au moins un cours, une competence et un club
WITH e
MATCH (c:Cours) WITH e, collect(c) AS cours
CALL {
  WITH e, cours
  WITH e, cours[toInteger(substring(e.id,1)) % size(cours)] AS csel
  MERGE (e)-[:SUIT {semestre: 5, note: 12 + (toInteger(substring(e.id,1)) % 9)}]->(csel)
  RETURN null
}
CALL {
  WITH e
  MATCH (comp:Competence)
  WITH e, collect(comp) AS comps
  MERGE (e)-[:MAITRISE {niveau: 2 + (toInteger(substring(e.id,1)) % 3)}]->(comps[toInteger(substring(e.id,1)) % size(comps)])
  RETURN null
}
CALL {
  WITH e
  MATCH (cl:Club)
  WITH e, collect(cl) AS clubs
  MERGE (e)-[:MEMBRE_DE {role: CASE WHEN toInteger(substring(e.id,1)) % 7 = 0 THEN 'Responsable' ELSE 'Membre' END}]->(clubs[toInteger(substring(e.id,1)) % size(clubs)])
  RETURN null
}

// Connecter l'étudiant importé à un pair existant pour éviter l'isolement
WITH e
MATCH (other:Etudiant) WHERE other.id <> e.id
WITH e, other
LIMIT 1
MERGE (e)-[:CONNAIT {depuis: 2024, contexte: 'Import CSV'}]->(other);

