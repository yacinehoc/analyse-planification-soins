CREATE TABLE IF NOT EXISTS employe (
    employe_id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    date_embauche DATE NOT NULL,
    date_fin_emploi DATE,
    heures_contrat_semaine NUMERIC(5,2) NOT NULL CHECK (heures_contrat_semaine >= 0)
);

CREATE TABLE IF NOT EXISTS secteur (
    secteur_id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS quart_planifie (
    quart_id SERIAL PRIMARY KEY,
    employe_id INTEGER REFERENCES employe(employe_id),
    secteur_id INTEGER NOT NULL REFERENCES secteur(secteur_id),
    debut TIMESTAMP NOT NULL,
    fin TIMESTAMP NOT NULL,
    type_quart VARCHAR(20) NOT NULL,
    niveau_soins VARCHAR(50),
    statut VARCHAR(20) NOT NULL,
    employe_remplace_id INTEGER REFERENCES employe(employe_id),
    CHECK (fin > debut)
);

CREATE TABLE IF NOT EXISTS absence (
    absence_id SERIAL PRIMARY KEY,
    employe_id INTEGER NOT NULL REFERENCES employe(employe_id),
    debut TIMESTAMP NOT NULL,
    fin TIMESTAMP NOT NULL,
    motif VARCHAR(100),
    CHECK (fin > debut)
);
