-- Taux de couverture global
SELECT
    COUNT(*) AS quarts_total,
    COUNT(*) FILTER (WHERE statut = 'COUVERT') AS quarts_couverts,
    ROUND(100.0 * COUNT(*) FILTER (WHERE statut = 'COUVERT') / NULLIF(COUNT(*), 0), 2) AS taux_couverture_pct
FROM quart_planifie;

-- Taux de couverture par mois
SELECT
    DATE_TRUNC('month', debut)::date AS mois,
    COUNT(*) AS quarts_total,
    COUNT(*) FILTER (WHERE statut = 'NON_COUVERT') AS bris_service,
    ROUND(100.0 * COUNT(*) FILTER (WHERE statut = 'COUVERT') / NULLIF(COUNT(*), 0), 2) AS taux_couverture_pct
FROM quart_planifie
GROUP BY 1
ORDER BY 1;
