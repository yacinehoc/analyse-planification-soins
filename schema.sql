-- Schéma de la base. Le script recrée les tables : les données existantes
-- et les vues qui en dépendent sont supprimées.

DROP TABLE IF EXISTS quart_planifie, absence, usager, employe, secteur CASCADE;

CREATE TABLE secteur (
    secteur_id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE employe (
    employe_id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    secteur_id INTEGER NOT NULL REFERENCES secteur(secteur_id),
    date_embauche DATE NOT NULL,
    date_fin_emploi DATE,
    heures_contrat_semaine NUMERIC(5,2) NOT NULL CHECK (heures_contrat_semaine >= 0)
);

CREATE TABLE usager (
    usager_id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    secteur_id INTEGER NOT NULL REFERENCES secteur(secteur_id),
    niveau_soins VARCHAR(50) NOT NULL
);

CREATE TABLE quart_planifie (
    quart_id SERIAL PRIMARY KEY,
    employe_id INTEGER REFERENCES employe(employe_id),
    usager_id INTEGER NOT NULL REFERENCES usager(usager_id),
    debut TIMESTAMP NOT NULL,
    fin TIMESTAMP NOT NULL,
    type_quart VARCHAR(20) NOT NULL CHECK (type_quart IN ('JOUR', 'SOIR', 'NUIT')),
    statut VARCHAR(20) NOT NULL CHECK (statut IN ('COUVERT', 'NON_COUVERT')),
    employe_remplace_id INTEGER REFERENCES employe(employe_id),
    CHECK (fin > debut)
);

CREATE TABLE absence (
    absence_id SERIAL PRIMARY KEY,
    employe_id INTEGER NOT NULL REFERENCES employe(employe_id),
    debut TIMESTAMP NOT NULL,
    fin TIMESTAMP NOT NULL,
    motif VARCHAR(100),
    CHECK (fin > debut)
);

CREATE INDEX idx_quart_debut ON quart_planifie (debut);
CREATE INDEX idx_quart_employe_debut ON quart_planifie (employe_id, debut);
CREATE INDEX idx_quart_usager ON quart_planifie (usager_id);
CREATE INDEX idx_absence_employe ON absence (employe_id, debut);
