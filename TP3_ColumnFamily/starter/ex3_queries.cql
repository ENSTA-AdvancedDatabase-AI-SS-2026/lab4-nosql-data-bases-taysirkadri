-- TP3 - Exercice 3 : Requêtes CQL
USE smartgrid;

-- 3.1 Mesures d'un capteur spécifique sur les dernières 6 heures
-- Remplacer <capteur_uuid> et <date_jour>/<ts_seuil> avant exécution
SELECT * FROM mesures_par_capteur
WHERE capteur_id = <capteur_uuid> AND date_jour = <date_jour> AND timestamp >= <ts_seuil>;

-- 3.2 Dernière mesure de chaque capteur d'une wilaya
-- (Approche : table dédiée ou requête LIMIT 1 par capteur ; ici exemple via table existante)
-- Exemple : sélectionner capteurs d'une wilaya pour un jour donné, puis récupérer la première ligne (timestamp DESC)
SELECT * FROM mesures_par_capteur
WHERE capteur_id = <capteur_uuid> AND date_jour = <date_jour>
LIMIT 1;

-- 3.3 Capteurs en alerte dans la wilaya "Alger" aujourd'hui
SELECT * FROM alertes_par_wilaya
WHERE wilaya = 'Alger' AND date_jour = toDate(now());

-- 3.3b Compter les alertes d'aujourd'hui pour Alger
SELECT count(*) FROM alertes_par_wilaya WHERE wilaya = 'Alger' AND date_jour = toDate(now());

-- 3.4 Consommation totale par heure sur une journée (dashboard)
-- Exemple d'agrégation pré-calculée depuis agregats_horaires
SELECT date_heure, puissance_moy_kw, nb_capteurs FROM agregats_horaires
WHERE wilaya = 'Alger' AND date_jour = toDate(now())
ORDER BY date_heure DESC LIMIT 24;

-- 3.5 Détection d'anomalie : tension < 200V ou > 240V dans les 30 dernières minutes
-- Requête cible : nécessite table adaptée ou scanner partitions pertinentes
-- Exemple pour un capteur donné
SELECT * FROM mesures_par_capteur
WHERE capteur_id = <capteur_uuid> AND date_jour = <date_jour> AND timestamp >= <ts_seuil>
AND (tension_v < 200 OR tension_v > 240);

-- 3.6 Top 10 capteurs les plus actifs cette semaine
-- Cette requête nécessite une table d'agrégats par semaine ou Materialized View
-- Exemple (si table agregats_horaires contient nb_capteurs ou compte par capteur) :
-- SELECT capteur_id, sum(count) FROM mesures_par_capteur_aggregated WHERE week = <week> GROUP BY capteur_id LIMIT 10;

-- 3.7 ALLOW FILTERING : éviter en production car full scan des partitions
-- Exemple d'alternative : créer une table secondaire conçue pour la requête souhaitée.
