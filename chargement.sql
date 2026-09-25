-- Chargement des CSV produits par generation_donnees.py.
-- À lancer depuis la racine du dépôt :
--   psql -d analyse_planification_soins -f chargement.sql

\set ON_ERROR_STOP on
SET client_encoding = 'UTF8';

TRUNCATE quart_planifie, absence, usager, employe, secteur RESTART IDENTITY CASCADE;

\copy secteur (secteur_id, nom) FROM 'data/secteurs.csv' WITH (FORMAT csv, HEADER true)
\copy employe (employe_id, nom, secteur_id, date_embauche, date_fin_emploi, heures_contrat_semaine) FROM 'data/employes.csv' WITH (FORMAT csv, HEADER true)
\copy usager (usager_id, nom, secteur_id, niveau_soins) FROM 'data/usagers.csv' WITH (FORMAT csv, HEADER true)
\copy absence (absence_id, employe_id, debut, fin, motif) FROM 'data/absences.csv' WITH (FORMAT csv, HEADER true)
\copy quart_planifie (quart_id, employe_id, usager_id, debut, fin, type_quart, statut, employe_remplace_id) FROM 'data/quarts_planifies.csv' WITH (FORMAT csv, HEADER true)

-- Les identifiants viennent des CSV : on réaligne les séquences
SELECT setval(pg_get_serial_sequence('secteur', 'secteur_id'), MAX(secteur_id)) FROM secteur;
SELECT setval(pg_get_serial_sequence('employe', 'employe_id'), MAX(employe_id)) FROM employe;
SELECT setval(pg_get_serial_sequence('usager', 'usager_id'), MAX(usager_id)) FROM usager;
SELECT setval(pg_get_serial_sequence('absence', 'absence_id'), MAX(absence_id)) FROM absence;
SELECT setval(pg_get_serial_sequence('quart_planifie', 'quart_id'), MAX(quart_id)) FROM quart_planifie;

ANALYZE;
