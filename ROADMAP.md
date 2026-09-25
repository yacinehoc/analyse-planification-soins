# Feuille de route

La semaine 1 (fondations) fournit la base : schéma, générateur, chargement.
Les semaines 2 à 10 sont le travail d'analyse : **chaque requête SQL et
chaque visuel Power BI doivent être écrits par l'auteur du dépôt.** Les
fichiers `sql/` actuels sont des brouillons à réécrire au fil des semaines.

Règle pour chaque semaine : une fonctionnalité n'est « terminée » que si
elle respecte son critère d'acceptation **et** si l'auteur peut refaire la
requête sans notes et expliquer chaque ligne.

## Modèle de données

| Table | Contenu |
|---|---|
| `secteur` | 5 secteurs géographiques |
| `employe` | 18 employés : contrat hebdomadaire, secteur d'attache, embauche et départ |
| `usager` | 25 usagers : secteur et niveau de soins (Standard, Intermédiaire, Élevé, Continu) |
| `quart_planifie` | environ 12 000 visites en 2025 : usager, employé (NULL si non couvert), statut, remplacement |
| `absence` | vacances, maladie et formation |

Les visites durent de 1 à 8 h (2,6 h en moyenne) : c'est ce qui rend
réaliste le volume de 12 000 quarts pour 18 employés. Une semaine commence
le lundi, comme `DATE_TRUNC('week', ...)` dans PostgreSQL.

---

## Semaine 1 — Fondations (fait)

- Schéma PostgreSQL, générateur Python, script de chargement.
- **Critère** : après `chargement.sql`, `SELECT COUNT(*) FROM quart_planifie;`
  retourne environ 12 000 lignes, dont environ 7 % non couvertes.

## Semaine 2 — Qualité des données

Fichier : `sql/01_qualite_donnees.sql`, puis `notes/qualite.md`.

- Volumétrie par table ; plage de dates des quarts.
- Contrôles d'intégrité : employé assigné pendant une absence, quart hors de
  la période d'emploi, remplaçant identique au remplacé, statut incohérent
  avec l'employé (COUVERT sans employé, NON_COUVERT avec employé),
  chevauchement de deux quarts pour un même employé.
- Documenter chaque anomalie dans `notes/qualite.md` : définition, nombre,
  impact sur les indicateurs, règle retenue (exclure, corriger, signaler).
- **Critère** : chaque contrôle retrouve exactement le nombre d'anomalies
  affiché par le générateur. Le contrôle de chevauchement retourne 0 ligne
  hors anomalies injectées.
- **À savoir expliquer** : pourquoi la condition `a.debut < b.fin AND
  a.fin > b.debut` détecte tous les chevauchements.

## Semaine 3 — Couverture des quarts

Fichier : `sql/02_couverture.sql`.

- Taux de couverture global, par mois, par secteur, par niveau de soins, par
  type de quart (JOUR, SOIR, NUIT) et par jour de la semaine.
- Classement des usagers les plus touchés par les bris de service.
- Part des quarts couverts par un remplaçant.
- **Critère** : les totaux par dimension se recoupent avec le total global
  (même nombre de quarts, même nombre de bris).
- **À savoir expliquer** : `COUNT(*) FILTER (WHERE ...)` contre
  `SUM(CASE ...)`, et pourquoi `NULLIF` dans une division.

## Semaine 4 — Heures supplémentaires et fatigue

Fichier : `sql/03_heures_fatigue.sql`.

- Heures travaillées par employé et par semaine, comparées au contrat.
- Concentration : part des heures supplémentaires totales portée par les
  3 employés qui en font le plus (fonctions de fenêtre, cumul).
- Fatigue :
  - blocs de quarts enchaînés sans interruption (méthode « gaps and
    islands » : `LAG`, marqueur de nouveau bloc, `SUM` cumulée) ; seuils de
    16 h et de 24 h ;
  - jours de travail consécutifs ;
  - repos de moins de 11 h entre deux journées de travail.
- **Critère** : les blocs de 24 h existent (plusieurs dizaines) et
  concernent un petit nombre d'employés ; résultat identique en réécrivant
  la requête avec une autre approche (par exemple sous-requête corrélée).
- **À savoir expliquer** : chaque étape de la méthode « gaps and islands »,
  au tableau, sur 5 lignes d'exemple.

## Semaine 5 — Couche de présentation

Fichier : `sql/04_vues.sql` (à réécrire : l'ancienne version fait
référence à `quart_planifie.secteur_id`, qui n'existe plus).

- Modèle en étoile pour Power BI : une vue de faits (un quart par ligne,
  durée en heures, indicateur de bris, date) et des dimensions (date,
  employé, usager avec secteur, type de quart).
- Vue des heures par employé et par semaine, et vue des blocs de fatigue.
- **Critère** : chaque vue se charge dans Power BI sans transformation
  Power Query autre que le typage ; la table de dates couvre toute la
  période des faits.

## Semaine 6 — Power BI : modèle et page Couverture

- Connexion PostgreSQL, relations entre faits et dimensions, table de dates
  marquée comme telle.
- Mesures DAX : quarts, bris, taux de couverture, taux de remplacement.
- Page Couverture : tendance mensuelle, carte de chaleur jour × type de
  quart, classement des usagers.
- **Critère** : le taux de couverture de Power BI est identique à celui du
  SQL, au global et pour chaque mois.

## Semaine 7 — Power BI : pages Heures supplémentaires et Fatigue

- Page Heures supplémentaires : heures par employé comparées au contrat,
  graphique de Pareto de la concentration.
- Page Fatigue : liste des blocs de 16 h et de 24 h, employés concernés,
  évolution mensuelle.
- Segments communs (mois, secteur) et info-bulles.
- **Critère** : chaque chiffre affiché peut être retrouvé par une requête SQL.

## Semaine 8 — Mise en forme du dépôt

- Captures d'écran du tableau de bord dans `images/`.
- README : contexte, questions d'affaires, captures, méthode, limites.
- Relecture des fichiers SQL : commentaires utiles, noms cohérents.
- **Critère** : une personne extérieure reproduit l'installation en suivant
  seulement le README.

## Semaine 9 — Constats et recommandations

Fichier : `CONSTATS.md`.

- Trois à cinq constats chiffrés, chacun appuyé par une requête ou un visuel.
- Recommandations opérationnelles liées à chaque constat.
- Limites : données synthétiques, règles de génération connues.
- **Critère** : aucun constat sans chiffre ni source dans le dépôt.

## Semaine 10 — Publication

- Mettre à jour le CV **seulement avec ce qui existe dans le dépôt**.
- Préparer une démonstration de 3 minutes : question d'affaires, une requête
  expliquée en direct, le tableau de bord, un constat.
- **Critère** : refaire, sans notes, la requête des blocs consécutifs et le
  calcul du taux de couverture.
