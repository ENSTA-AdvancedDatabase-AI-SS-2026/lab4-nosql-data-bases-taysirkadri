/**
 * TP2 - Exercice 4 : Index et Optimisation
 */

use("medical_db");

// ─── 4.1 : Créer les index appropriés ────────────────────────────────────────

// Index 1 : Recherche fréquente par wilaya + antécédents
// Index composé pour wilaya + antecedents
// db.patients.createIndex({ "adresse.wilaya": 1, antecedents: 1 });

// Index 2 : Recherche par date de consultation
// db.patients.createIndex({ "consultations.date": -1 });

// Index 3 : Texte sur diagnostics pour recherche full-text
// db.patients.createIndex({ "consultations.diagnostic": "text", "consultations.notes": "text" });

// Index 4 : Analyses par patient (lookup)
// db.analyses.createIndex({ patient_id: 1 });


// ─── 4.2 : Comparer avec explain() ────────────────────────────────────────────

// Requête de test
const requeteTest = {
  "adresse.wilaya": "Alger",
  antecedents: "Diabete type 2"
};

function printExplainStats(stats) {
  const exec = stats.executionStats;
  printjson({
    nReturned: exec.nReturned,
    totalDocsExamined: exec.totalDocsExamined,
    executionTimeMillis: exec.executionTimeMillis
  });
}

print("=== AVANT index ===");
const beforeStats = db.patients.find(requeteTest).explain("executionStats");
printExplainStats(beforeStats);

print("\n=== APRÈS index ===");
db.patients.createIndex({ "adresse.wilaya": 1, antecedents: 1 });
db.patients.createIndex({ "consultations.date": -1 });
db.patients.createIndex({ "consultations.diagnostic": "text", "consultations.notes": "text" });
db.analyses.createIndex({ patient_id: 1 });

const afterStats = db.patients.find(requeteTest).explain("executionStats");
printExplainStats(afterStats);

// ─── 4.4 : Index TTL pour archivage ───────────────────────────────────────────
// Index TTL sur analyses.date pour expirer après 5 ans
db.analyses.createIndex(
  { date: 1 },
  { expireAfterSeconds: 60 * 60 * 24 * 365 * 5 }
);
