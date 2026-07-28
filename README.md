# Analyse de la planification des soins

Projet de portfolio en analyse de données portant sur la couverture des quarts, les bris de service, les heures supplémentaires et les risques de fatigue dans un contexte de planification des soins.

## Objectifs

- Construire une base PostgreSQL structurée et reproductible
- Contrôler la qualité des données
- Produire des indicateurs de couverture et de main-d'œuvre
- Détecter les blocs de travail consécutifs de 24 h ou plus
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
├── schema.sql
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

## Installation

```bash
git clone https://github.com/yacinehoc/analyse-planification-soins.git
cd analyse-planification-soins
python -m venv .venv
pip install -r requirements.txt
python generation_donnees.py
createdb analyse_planification_soins
psql -d analyse_planification_soins -f schema.sql
```

## Critère d’acceptation — semaine 1

```sql
SELECT COUNT(*) FROM quart_planifie;
```

La requête doit retourner environ 12 000 lignes.

## Feuille de route

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
