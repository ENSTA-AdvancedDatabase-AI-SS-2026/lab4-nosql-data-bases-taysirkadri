/**
 * TP2 - Exercice 5 : $lookup et données référencées
 * Scripts pour joindre patients et analyses et réaliser statistiques
 */

use("medical_db");

print('=== 5.1 : Dossier complet d\'un patient (par CIN) ===');
const cinToFetch = "1981010112300"; // ajuster selon données insérées
const dossier = db.patients.aggregate([
  { $match: { cin: cinToFetch } },
  { $lookup: { from: "analyses", localField: "_id", foreignField: "patient_id", as: "analyses" } },
  { $limit: 1 }
]).toArray();
printjson(dossier);

print('\n=== 5.2 : Patients dont la glycémie > 1.26 g/L ===');
const glyPatients = db.analyses.aggregate([
  { $match: { type: "Glycemie", "resultats.valeur": { $gt: 1.26 } } },
  { $group: { _id: "$patient_id" } },
  { $lookup: { from: "patients", localField: "_id", foreignField: "_id", as: "patient" } },
  { $unwind: "$patient" },
  { $project: { "patient.cin": 1, "patient.nom": 1, "patient.prenom": 1 } }
]).toArray();
printjson(glyPatients);

print('\n=== 5.3 : Taux d\'analyses anormales par wilaya ===');
// Définition simple d\'anormal : resultats.valeur > 1.26 (pour glycemie)
const statsWilaya = db.analyses.aggregate([
  { $lookup: { from: "patients", localField: "patient_id", foreignField: "_id", as: "patient" } },
  { $unwind: "$patient" },
  { $project: { wilaya: "$patient.adresse.wilaya", type: 1, valeur: "$resultats.valeur" } },
  { $group: { _id: "$wilaya", total: { $sum: 1 }, abnormal: { $sum: { $cond: [{ $gt: ["$valeur", 1.26] }, 1, 0] } } } },
  { $project: { wilaya: "$_id", total: 1, abnormal: 1, abnormalRate: { $multiply: [{ $divide: ["$abnormal", "$total"] }, 100] } } }
]).toArray();
printjson(statsWilaya);
