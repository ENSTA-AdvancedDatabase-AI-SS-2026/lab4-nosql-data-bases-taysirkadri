-- TP3 - Exercice 4 : Compaction et Maintenance
USE smartgrid;

-- 4.1 Choix recommandé : TWCS pour mesures (time series), STCS/LCS pour tables différentes
-- 4.2 Configurer TWCS pour mesures_par_capteur
ALTER TABLE mesures_par_capteur WITH compaction = {
  'class' : 'TimeWindowCompactionStrategy',
  'compaction_window_unit' : 'DAYS',
  'compaction_window_size' : 1
};

-- 4.3 Vérifier l'utilisation des TTL : compter lignes expirant bientôt
-- (Cassandra ne fournit pas direct expire-time, mais on peut estimer via write_time)
SELECT capteur_id, timestamp, WRITETIME(puissance_kw) FROM mesures_par_capteur LIMIT 10;

-- 4.4 Analyser une partition hot : utiliser nodetool and tracing
-- Exemples :
-- nodetool tpstats
-- nodetool cfstats smartgrid mesures_par_capteur
-- Pour corriger une partition hot : inclure date dans partition key, ajouter bucketing (hash modulo)
