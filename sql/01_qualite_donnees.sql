-- Contrôles de qualité des données

SELECT 'employe' AS table_name, COUNT(*) AS nombre_lignes FROM employe
UNION ALL
SELECT 'secteur', COUNT(*) FROM secteur
UNION ALL
SELECT 'quart_planifie', COUNT(*) FROM quart_planifie
UNION ALL
SELECT 'absence', COUNT(*) FROM absence;

-- Quarts assignés à un employé absent
SELECT q.*
FROM quart_planifie q
JOIN absence a
  ON a.employe_id = q.employe_id
 AND q.debut < a.fin
 AND q.fin > a.debut;

-- Quarts hors période d'emploi
SELECT q.*
FROM quart_planifie q
JOIN employe e ON e.employe_id = q.employe_id
WHERE q.debut::date < e.date_embauche
   OR (e.date_fin_emploi IS NOT NULL AND q.fin::date > e.date_fin_emploi);

-- Remplaçant identique au remplacé
SELECT *
FROM quart_planifie
WHERE employe_id IS NOT NULL
  AND employe_remplace_id = employe_id;
