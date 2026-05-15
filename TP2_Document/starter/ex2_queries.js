/**
 * TP2 - Exercice 2 : Requêtes de base
 * Script mongo shell exécutant les requêtes demandées
 */

use("medical_db");

// Date seuil pour 50 ans
const date50 = new Date();
date50.setFullYear(date50.getFullYear() - 50);

print('=== 2.1 : Patients diabétiques >50 ans à Alger ===');
const q21 = {
  "adresse.wilaya": "Alger",
  antecedents: { $in: ["Diabete type 2", "Diabete"] },
  dateNaissance: { $lte: date50 }
};
printjson(db.patients.find(q21, { cin: 1, nom: 1, prenom: 1, dateNaissance: 1 }).toArray());

print('\n=== 2.2 : Patients allergiques à la Pénicilline avec >=3 consultations ===');
const q22 = {
  allergies: "Penicilline",
  $expr: { $gte: [{ $size: "$consultations" }, 3] }
};
printjson(db.patients.find(q22, { cin: 1, nom: 1, prenom: 1, consultations: 1 }).toArray());

print('\n=== 2.3 : Projection : Nom, prénom, et dernière consultation ===');
const proj23 = db.patients.aggregate([
  { $project: { nom: 1, prenom: 1, lastConsultation: { $arrayElemAt: ["$consultations", -1] } } },
  { $limit: 50 }
]).toArray();
printjson(proj23);

print('\n=== 2.4 : Patients sans antécédents et tension systolique > 140 en dernière consultation ===');
const q24 = [
  { $addFields: { lastConsultation: { $arrayElemAt: ["$consultations", -1] } } },
  { $match: { $or: [{ antecedents: { $exists: false } }, { antecedents: { $size: 0 } }], "lastConsultation.tension.systolique": { $gt: 140 } } },
  { $project: { cin: 1, nom: 1, prenom: 1, "lastConsultation.tension": 1 } }
];
printjson(db.patients.aggregate(q24).toArray());

print('\n=== 2.5 : Recherche textuelle sur les diagnostics (exemple : "Hypertension") ===');
// Assurez-vous que l'index text a été créé (voir ex4_indexes.js)
printjson(db.patients.find({ $text: { $search: "Hypertension" } }, { score: { $meta: "textScore" }, nom: 1, prenom: 1 }).sort({ score: { $meta: "textScore" } }).toArray());
