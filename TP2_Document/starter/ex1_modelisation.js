/**
 * TP2 - Exercice 1 : Modélisation MongoDB
 * Use Case : HealthCare DZ - Dossiers Médicaux
 */

// Se connecter à la base médicale
use("medical_db");

// ─── 1.1 : Créer la collection avec validation ────────────────────────────────
db.createCollection("patients", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["cin", "nom", "prenom", "dateNaissance", "sexe", "adresse", "consultations"],
      properties: {
        cin: { bsonType: "string", minLength: 12, maxLength: 12 },
        nom: { bsonType: "string" },
        prenom: { bsonType: "string" },
        dateNaissance: { bsonType: "date" },
        sexe: { enum: ["M", "F"] },
        adresse: {
          bsonType: "object",
          required: ["wilaya", "commune"],
          properties: {
            wilaya: { bsonType: "string" },
            commune: { bsonType: "string" }
          }
        },
        groupeSanguin: { bsonType: "string" },
        antecedents: { bsonType: "array", items: { bsonType: "string" } },
        allergies: { bsonType: "array", items: { bsonType: "string" } },
        consultations: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["id", "date", "medecin", "diagnostic"],
            properties: {
              id: { bsonType: "binData" },
              date: { bsonType: "date" },
              medecin: {
                bsonType: "object",
                required: ["nom", "specialite"],
                properties: {
                  nom: { bsonType: "string" },
                  specialite: { bsonType: "string" }
                }
              },
              diagnostic: { bsonType: "string" },
              tension: {
                bsonType: "object",
                properties: {
                  systolique: { bsonType: "int" },
                  diastolique: { bsonType: "int" }
                }
              },
              medicaments: {
                bsonType: "array",
                items: {
                  bsonType: "object",
                  required: ["nom", "dosage"],
                  properties: {
                    nom: { bsonType: "string" },
                    dosage: { bsonType: "string" },
                    duree: { bsonType: "string" }
                  }
                }
              },
              notes: { bsonType: "string" }
            }
          }
        }
      }
    }
  }
});

// ─── 1.2 : Insérer des patients avec données algériennes ──────────────────────
// 20 patients, wilayas variees, pathologies courantes

const prenoms = [
  "Ahmed", "Fatima", "Karim", "Yasmina", "Rania", "Mehdi", "Sara", "Youcef",
  "Lina", "Anis", "Nadia", "Samir", "Imane", "Nabil", "Amine", "Salma",
  "Riad", "Meriem", "Bilal", "Hind", "Walid", "Sofiane", "Aya", "Dounia"
];
const noms = [
  "Bensalem", "Ouali", "Meziane", "Hamdi", "Belkacem", "Derbal", "Amrani",
  "Cherif", "Boudia", "Haddar", "Benali", "Mansouri", "Bouzid", "Kaci"
];
const wilayas = [
  { wilaya: "Alger", communes: ["Bab Ezzouar", "Hydra", "El Harrach"] },
  { wilaya: "Oran", communes: ["Bir El Djir", "Es Senia", "Arzew"] },
  { wilaya: "Constantine", communes: ["El Khroub", "Ain Smara"] },
  { wilaya: "Annaba", communes: ["El Bouni", "Seraidi"] },
  { wilaya: "Blida", communes: ["Boufarik", "Larbaa"] }
];
const groupes = ["O+", "A+", "B+", "AB+", "O-"];
const antecedentsPool = ["Diabete type 2", "HTA", "Asthme", "Anemie", "Obesite"];
const diagnostics = [
  "Hypertension arterielle", "Diabete", "Asthme", "Grippe", "RGO",
  "Hypercholesterolemie", "Anemie"
];
const medicaments = [
  { nom: "Amlodipine", dosage: "5mg" },
  { nom: "Metformine", dosage: "500mg" },
  { nom: "Salbutamol", dosage: "2 bouffees" },
  { nom: "Paracetamol", dosage: "1g" },
  { nom: "Atorvastatine", dosage: "20mg" }
];
const medecins = [
  { nom: "Dr. Mansouri", specialite: "Cardiologie" },
  { nom: "Dr. Zeroual", specialite: "Endocrinologie" },
  { nom: "Dr. Bouzid", specialite: "Pneumologie" },
  { nom: "Dr. Lounes", specialite: "Medecine generale" }
];

function pick(list, i) {
  return list[i % list.length];
}

function randomDateBack(daysBack) {
  const d = new Date();
  d.setDate(d.getDate() - daysBack);
  return d;
}

function buildConsultations(i) {
  const count = 2 + (i % 3);
  const result = [];
  for (let j = 0; j < count; j += 1) {
    const med = pick(medecins, i + j);
    const diag = pick(diagnostics, i + j * 2);
    const medoc = pick(medicaments, i + j * 3);
    result.push({
      id: UUID(),
      date: randomDateBack(30 + i * 10 + j * 20),
      medecin: med,
      diagnostic: diag,
      tension: { systolique: 120 + (i % 5) * 5, diastolique: 75 + (j % 4) * 3 },
      medicaments: [
        { nom: medoc.nom, dosage: medoc.dosage, duree: "30 jours" }
      ],
      notes: "Suivi clinique et conseils d hygiene de vie"
    });
  }
  return result;
}

const patients = [];
for (let i = 0; i < 20; i += 1) {
  const w = pick(wilayas, i);
  const cin = `198${(i % 9) + 1}0101${(2300 + i).toString()}`;
  const antecedents = [pick(antecedentsPool, i)];
  if (i % 4 === 0) antecedents.push("HTA");

  patients.push({
    cin,
    nom: pick(noms, i),
    prenom: pick(prenoms, i + 2),
    dateNaissance: new Date(1965 + (i % 30), (i % 12), (i % 28) + 1),
    sexe: i % 2 === 0 ? "M" : "F",
    adresse: { wilaya: w.wilaya, commune: pick(w.communes, i) },
    groupeSanguin: pick(groupes, i),
    antecedents,
    allergies: i % 5 === 0 ? ["Penicilline"] : [],
    consultations: buildConsultations(i)
  });
}

const insertResult = db.patients.insertMany(patients);

// ─── 1.3 : Collection analyses (référencée) ───────────────────────────────────
// Types : "Glycemie", "NFS", "Lipidogramme", "Creatinine", "ECG"

const analyseTypes = ["Glycemie", "NFS", "Lipidogramme", "Creatinine", "ECG"];
const analyses = [];

Object.values(insertResult.insertedIds).forEach((patientId, idx) => {
  for (let j = 0; j < 2; j += 1) {
    const type = pick(analyseTypes, idx + j);
    analyses.push({
      patient_id: patientId,
      date: randomDateBack(15 + idx * 5 + j * 12),
      type,
      resultats: {
        valeur: 0.8 + ((idx + j) % 6) * 0.2,
        unite: type === "ECG" ? "score" : "g/L"
      },
      laboratoire: "Labo Central Alger",
      valide: true
    });
  }
});

db.analyses.insertMany(analyses);

print("✅ Modélisation terminée. Patients insérés:", db.patients.countDocuments());
print("✅ Analyses insérées:", db.analyses.countDocuments());
