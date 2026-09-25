# Analyse de la planification des soins

Projet de portfolio en analyse de données portant sur la couverture des quarts, les bris de service, les heures supplémentaires et les risques de fatigue dans un contexte de planification des soins.

## Objectifs

- Construire une base PostgreSQL structurée et reproductible
- Contrôler la qualité des données
- Produire des indicateurs de couverture et de main-d'œuvre
- Mesurer la concentration des heures supplémentaires
- Détecter les blocs de travail consécutifs de 16 h et de 24 h
- Créer un tableau de bord Power BI
- Formuler des constats et recommandations opérationnelles

## Technologies

- PostgreSQL
- Python
- SQL
- Power BI
- Git / GitHub

## Structure du dépôt

```text
analyse-planification-soins/
├── README.md
├── ROADMAP.md
├── schema.sql
├── chargement.sql
├── generation_donnees.py
├── requirements.txt
├── sql/
│   ├── 01_qualite_donnees.sql
│   ├── 02_couverture.sql
│   ├── 03_heures_fatigue.sql
│   └── 04_vues.sql
├── notes/
│   └── qualite.md
├── images/
├── data/
├── CONSTATS.md
├── .gitignore
└── LICENSE
```

## Données

Données entièrement synthétiques, produites par `generation_donnees.py`
(graine fixe, résultat reproductible) :

- 12 mois (année 2025), 5 secteurs, 18 employés, 25 usagers ;
- environ 12 000 visites à domicile de 1 à 8 h, dont environ 7 % non couvertes ;
- des absences (vacances, maladie, formation).

Les visites sont assignées selon des règles (heures de contrat, disponibilité
la fin de semaine, heures supplémentaires réservées aux volontaires, délais de
déplacement). Les bris de service et les heures supplémentaires découlent donc
de ces contraintes plutôt que d'un tirage au hasard. Quelques anomalies sont
injectées volontairement pour les contrôles de qualité ; le générateur en
affiche le nombre.

## Installation

```bash
git clone https://github.com/yacinehoc/analyse-planification-soins.git
cd analyse-planification-soins
python generation_donnees.py
createdb analyse_planification_soins
psql -d analyse_planification_soins -f schema.sql
psql -d analyse_planification_soins -f chargement.sql
```

Le générateur n'utilise que la bibliothèque standard de Python.
`chargement.sql` doit être lancé depuis la racine du dépôt (chemins relatifs
vers `data/`). `schema.sql` recrée les tables : il efface les données
existantes.

## Critère d’acceptation — semaine 1

```sql
SELECT statut, COUNT(*) FROM quart_planifie GROUP BY statut;
```

Environ 12 000 quarts au total, dont environ 7 % `NON_COUVERT`.

## Feuille de route

Le détail semaine par semaine, avec les critères d'acceptation, est dans [ROADMAP.md](ROADMAP.md).

1. Fondations
2. Qualité des données
3. Couverture des quarts
4. Heures et fatigue
5. Couche de présentation
6. Tableau de bord Power BI
7. Tableau de bord Power BI
8. Mise en forme du dépôt
9. Constats et recommandations
10. Publication

## Auteur

Yacine Salah Eddine Hocini
