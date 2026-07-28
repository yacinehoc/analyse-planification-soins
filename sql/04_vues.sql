CREATE TABLE IF NOT EXISTS dim_date AS
SELECT
    d::date AS date,
    EXTRACT(YEAR FROM d)::int AS annee,
    EXTRACT(MONTH FROM d)::int AS mois_numero,
    TO_CHAR(d, 'TMMonth') AS mois_nom,
    EXTRACT(WEEK FROM d)::int AS semaine_iso,
    EXTRACT(ISODOW FROM d)::int AS jour_semaine_iso,
    TO_CHAR(d, 'TMDay') AS jour_semaine_nom
FROM GENERATE_SERIES('2025-01-01'::date, '2027-12-31'::date, interval '1 day') d;

CREATE OR REPLACE VIEW vw_couverture_mensuelle AS
SELECT
    DATE_TRUNC('month', debut)::date AS mois,
    secteur_id,
    type_quart,
    COUNT(*) AS quarts_total,
    COUNT(*) FILTER (WHERE statut = 'COUVERT') AS quarts_couverts,
    COUNT(*) FILTER (WHERE statut = 'NON_COUVERT') AS bris_service
FROM quart_planifie
GROUP BY 1, 2, 3;

CREATE OR REPLACE VIEW vw_heures_employe_semaine AS
SELECT
    employe_id,
    DATE_TRUNC('week', debut)::date AS semaine,
    SUM(EXTRACT(EPOCH FROM (fin - debut)) / 3600.0) AS heures_travaillees
FROM quart_planifie
WHERE statut = 'COUVERT'
  AND employe_id IS NOT NULL
GROUP BY 1, 2;
