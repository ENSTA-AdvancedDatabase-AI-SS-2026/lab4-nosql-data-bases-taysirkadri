# TP2 - Rapport MongoDB

## 1) Résumé et objectifs
But : modéliser des dossiers médicaux lisibles et performants. On privilégie l'embedding pour données fréquemment lues ensemble (consultations), et le referencing pour collections volumineuses (analyses).

## 2) Choix de schéma et justification
- Patients : document principal `patients` contenant informations identifiantes et tableau `consultations` (embedding) car on lit souvent le dossier complet.
- Analyses : collection séparée `analyses` (referencing) — volume élevé, accès ciblé, TTL possible.
- Avantages : accès simple au dossier patient en un seul `find`. Inconvénient : document volumineux → envisager découpage si > 16MB.

Validation schema (extrait) :
```javascript
db.createCollection("patients", {
	validator: { $jsonSchema: {
		bsonType: "object",
		required: ["cin","nom","prenom","dateNaissance"],
		properties: {
			cin: { bsonType: "string" },
			dateNaissance: { bsonType: "date" }
		}
	}}
});
```

## 3) Requêtes, agrégation et optimisations
- Pipeline exemple (diagnostics les plus fréquents par wilaya) :
```javascript
db.patients.aggregate([
	{ $unwind: "$consultations" },
	{ $group: { _id: { wilaya: "$adresse.wilaya", diag: "$consultations.diagnostic" }, count: { $sum: 1 } } },
	{ $sort: { "count": -1 } },
	{ $limit: 10 }
])
```

Optimisations :
- Créer index composé sur `{ "adresse.wilaya": 1, "consultations.diagnostic": 1 }` si usage fréquent.
- Utiliser `projection` pour limiter data transférée.

## 4) Index recommandés
- Index 1 : `{ "adresse.wilaya": 1 }` — filtrage par région.
- Index 2 : `{ "consultations.date": -1 }` — retrouver dernières consultations.
- Index 3 : `text` index sur champ `consultations.diagnostic` pour recherche texte.
- Index 4 : `{ "analyses.patient_id": 1 }` sur la collection `analyses`.

Expliquer avec `explain()` : comparer `executionStats` avant/après et reporter `nReturned`, `totalDocsExamined`, `executionTimeMillis`.

## 5) Transactions multi-documents
- Utiliser les transactions MongoDB si vous devez écrire atomiquement dans `patients` et `analyses` (replica set requis). Exemple :
```javascript
const session = client.startSession();
session.startTransaction();
try {
	await patients.insertOne(docPatient, { session });
	await analyses.insertOne(docAnalyse, { session });
	await session.commitTransaction();
} catch (e) {
	await session.abortTransaction();
}
```

## 6) Résultats attendus et livrables
- Renseigner les parties suivantes après exécution des scripts : exemples `explain()` avant/après index, durée d'insertion, capture des documents générés.

--

Complétez ce rapport avec les captures `explain()` et les chiffres mesurés lors de vos tests.
--

Complétez les rubriques ci-dessus avec les résultats et captures `explain()`.
