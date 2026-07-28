"""Générateur de données synthétiques pour le projet."""

from pathlib import Path
import csv
import random
from datetime import datetime, timedelta

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
random.seed(42)


def generate_employes(n: int = 100) -> None:
    path = DATA_DIR / "employes.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["employe_id", "nom", "date_embauche", "date_fin_emploi", "heures_contrat_semaine"])
        for i in range(1, n + 1):
            writer.writerow([i, f"Employé {i}", "2024-01-01", "", random.choice([24, 32, 35, 37.5, 40])])


def generate_secteurs() -> None:
    secteurs = ["Nord", "Sud", "Est", "Ouest", "Centre"]
    path = DATA_DIR / "secteurs.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["secteur_id", "nom"])
        for i, nom in enumerate(secteurs, start=1):
            writer.writerow([i, nom])


def generate_quarts(n: int = 12000) -> None:
    path = DATA_DIR / "quarts_planifies.csv"
    start = datetime(2025, 1, 1, 7, 0)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["quart_id", "employe_id", "secteur_id", "debut", "fin", "type_quart", "niveau_soins", "statut", "employe_remplace_id"])
        for i in range(1, n + 1):
            debut = start + timedelta(hours=8 * i)
            duree = random.choice([8, 8, 8, 12])
            statut = random.choices(["COUVERT", "NON_COUVERT"], weights=[92, 8])[0]
            employe_id = random.randint(1, 100) if statut == "COUVERT" else ""
            writer.writerow([
                i,
                employe_id,
                random.randint(1, 5),
                debut.isoformat(sep=" "),
                (debut + timedelta(hours=duree)).isoformat(sep=" "),
                "NUIT" if debut.hour >= 19 or debut.hour < 7 else "JOUR",
                random.choice(["Standard", "Intermédiaire", "Élevé"]),
                statut,
                "",
            ])


def main() -> None:
    generate_employes()
    generate_secteurs()
    generate_quarts()
    print("Données générées dans le dossier data/")


if __name__ == "__main__":
    main()
