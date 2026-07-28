-- Heures par employé et semaine
WITH heures AS (
    SELECT
        employe_id,
        DATE_TRUNC('week', debut)::date AS semaine,
        SUM(EXTRACT(EPOCH FROM (fin - debut)) / 3600.0) AS heures_travaillees
    FROM quart_planifie
    WHERE statut = 'COUVERT'
      AND employe_id IS NOT NULL
    GROUP BY 1, 2
)
SELECT
    h.*,
    e.heures_contrat_semaine,
    GREATEST(h.heures_travaillees - e.heures_contrat_semaine, 0) AS heures_supplementaires
FROM heures h
JOIN employe e USING (employe_id)
ORDER BY semaine, employe_id;

-- Détection des blocs consécutifs de 24 heures ou plus
WITH ordonnes AS (
    SELECT
        q.*,
        LAG(fin) OVER (PARTITION BY employe_id ORDER BY debut, fin) AS fin_precedente
    FROM quart_planifie q
    WHERE statut = 'COUVERT'
      AND employe_id IS NOT NULL
),
marques AS (
    SELECT *, CASE WHEN fin_precedente = debut THEN 0 ELSE 1 END AS nouveau_bloc
    FROM ordonnes
),
groupes AS (
    SELECT *,
        SUM(nouveau_bloc) OVER (
            PARTITION BY employe_id
            ORDER BY debut, fin
            ROWS UNBOUNDED PRECEDING
        ) AS bloc_id
    FROM marques
)
SELECT
    employe_id,
    bloc_id,
    MIN(debut) AS debut_bloc,
    MAX(fin) AS fin_bloc,
    EXTRACT(EPOCH FROM (MAX(fin) - MIN(debut))) / 3600.0 AS duree_heures
FROM groupes
GROUP BY employe_id, bloc_id
HAVING EXTRACT(EPOCH FROM (MAX(fin) - MIN(debut))) / 3600.0 >= 24
ORDER BY duree_heures DESC;
