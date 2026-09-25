"""Générateur de données synthétiques : soins à domicile, 12 mois.

Produit cinq fichiers CSV dans data/ :
secteurs, employes, usagers, absences et quarts_planifies.

Principe : chaque usager a un plan de services (visites récurrentes). Les
visites sont assignées dans l'ordre chronologique, d'abord aux employés dans
leurs heures de contrat, puis, à défaut, en heures supplémentaires aux seuls
employés volontaires. Une visite que personne ne peut prendre reste
NON_COUVERT. Les bris de service, la concentration des heures
supplémentaires et les longues séquences de travail émergent donc des
contraintes, ils ne sont pas tirés au hasard.

Quelques anomalies sont injectées volontairement pour les contrôles de
qualité ; leur nombre est affiché à la fin de l'exécution.
"""

from __future__ import annotations

import csv
import random
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from pathlib import Path

SEED = 42
DATE_DEBUT = date(2025, 1, 1)
DATE_FIN = date(2025, 12, 31)
DATA_DIR = Path(__file__).parent / "data"

SECTEURS = ["Nord", "Sud", "Est", "Ouest", "Centre"]

# heures de contrat, secteur d'attache, travaille la fin de semaine,
# accepte les heures supplémentaires
EMPLOYES = [
    (40.0, 1, True, True),
    (40.0, 2, True, False),
    (40.0, 3, True, False),
    (37.5, 4, True, True),
    (37.5, 5, True, False),
    (37.5, 1, False, False),
    (35.0, 2, True, True),
    (35.0, 3, False, False),
    (35.0, 4, True, False),
    (35.0, 5, True, False),
    (32.0, 1, True, True),
    (32.0, 2, False, False),
    (32.0, 3, True, False),
    (28.0, 4, True, False),
    (28.0, 5, False, False),
    (24.0, 1, True, True),
    (24.0, 3, True, False),
    (21.0, 5, False, False),
]
EMBAUCHE_TARDIVE = {17: date(2025, 4, 7)}
DEPART = {9: date(2025, 9, 30)}

# Plans de services : (heure de début, durée en heures, jours de la semaine,
# 0 = lundi). Les visites du matin des usagers de niveau Standard et
# Intermédiaire commencent à une heure propre à chaque usager.
TOUS_LES_JOURS = range(7)
SEMAINE = range(5)


def plan_services(niveau: str) -> list[tuple]:
    if niveau == "Standard":
        jours_semaine = sorted(random.sample(range(7), random.randint(2, 4)))
        return [((random.randint(8, 13), 0), 2.0, jours_semaine)]
    if niveau == "Intermédiaire":
        matin = random.choice([(7, 0), (7, 30), (8, 0), (8, 30), (9, 0)])
        return [(matin, 2.0, TOUS_LES_JOURS), ((17, 0), 2.0, SEMAINE)]
    if niveau == "Élevé":
        return [((7, 0), 3.0, TOUS_LES_JOURS), ((12, 0), 1.0, TOUS_LES_JOURS),
                ((16, 0), 3.0, TOUS_LES_JOURS)]
    # Continu : présence 24 h sur 24 en trois quarts de 8 h
    return [((7, 0), 8.0, TOUS_LES_JOURS), ((15, 0), 8.0, TOUS_LES_JOURS),
            ((23, 0), 8.0, TOUS_LES_JOURS)]


NIVEAUX_USAGERS = ["Standard"] * 12 + ["Intermédiaire"] * 9 + ["Élevé"] * 3 + ["Continu"]

LIMITE_HEBDO_SUP = 55.0      # plafond hebdomadaire en heures supplémentaires
REPOS_MIN = timedelta(hours=8)  # sépare deux périodes de travail
MAX_HEURES_PERIODE = 10.0    # dans les heures normales
MAX_AMPLITUDE = timedelta(hours=13)
MAX_HEURES_PERIODE_SUP = 16.0
MAX_BLOC_SUP = 24.0          # enchaînement chez le même usager


@dataclass
class Employe:
    employe_id: int
    contrat: float
    secteur_id: int
    fin_semaine: bool
    volontaire_sup: bool
    date_embauche: date = DATE_DEBUT
    date_fin: date | None = None
    quarts: list = field(default_factory=list)  # (debut, fin, usager_id)
    absences: list = field(default_factory=list)  # (debut, fin)

    def employe_le(self, jour: date) -> bool:
        return self.date_embauche <= jour and (self.date_fin is None or jour <= self.date_fin)

    def absent(self, debut: datetime, fin: datetime) -> bool:
        return any(debut < a_fin and fin > a_debut for a_debut, a_fin in self.absences)


@dataclass
class Usager:
    usager_id: int
    secteur_id: int
    niveau: str
    titulaires: list = field(default_factory=list)


def jours(debut: date, fin: date):
    jour = debut
    while jour <= fin:
        yield jour
        jour += timedelta(days=1)


def creer_employes() -> list[Employe]:
    employes = []
    for i, (contrat, secteur, fds, sup) in enumerate(EMPLOYES, start=1):
        e = Employe(i, contrat, secteur, fds, sup)
        e.date_embauche = EMBAUCHE_TARDIVE.get(i, DATE_DEBUT)
        e.date_fin = DEPART.get(i)
        employes.append(e)
    return employes


def creer_usagers(employes: list[Employe]) -> list[Usager]:
    niveaux = NIVEAUX_USAGERS[:]
    random.shuffle(niveaux)
    usagers = []
    for i, niveau in enumerate(niveaux, start=1):
        secteur = (i - 1) % len(SECTEURS) + 1
        u = Usager(i, secteur, niveau)
        locaux = [e for e in employes if e.secteur_id == secteur and e.date_fin is None]
        u.titulaires = [e.employe_id for e in random.sample(locaux, min(2, len(locaux)))]
        usagers.append(u)
    return usagers


def creer_absences(employes: list[Employe]) -> list[tuple]:
    absences = []

    def ajouter(e: Employe, debut: date, nb_jours: int, motif: str) -> None:
        d = datetime.combine(debut, time())
        f = d + timedelta(days=nb_jours)
        e.absences.append((d, f))
        absences.append((e.employe_id, d, f, motif))

    for e in employes:
        # Deux semaines de vacances, surtout l'été
        if random.random() < 0.75:
            lundi = date(2025, 6, 16) + timedelta(weeks=random.randint(0, 10))
            ajouter(e, lundi, 14, "Vacances")
        else:
            lundi = date(2025, 7, 7) + timedelta(weeks=random.randint(0, 6))
            ajouter(e, lundi, 7, "Vacances")
            ajouter(e, date(2025, 12, 22), 7, "Vacances")
        # Maladie : plus fréquente l'hiver
        for _ in range(random.randint(1, 5)):
            mois = random.choices(range(1, 13), weights=[3, 3, 2, 1, 1, 1, 1, 1, 1, 2, 2, 3])[0]
            debut = date(2025, mois, random.randint(1, 28))
            ajouter(e, debut, random.choice([1, 1, 2, 3, 5]), "Maladie")
        ajouter(e, date(2025, random.choice([3, 5, 10]), random.randint(1, 28)), 1, "Formation")

    return [a for a in absences if a[1].date() <= DATE_FIN]


def creer_demande(usagers: list[Usager]) -> list[tuple]:
    """Retourne les visites (debut, fin, usager) en ordre chronologique."""
    visites = []
    for u in usagers:
        plan = plan_services(u.niveau)
        for jour in jours(DATE_DEBUT, DATE_FIN):
            for (h, m), duree, jours_semaine in plan:
                if jour.weekday() in jours_semaine:
                    debut = datetime.combine(jour, time(h, m))
                    visites.append((debut, debut + timedelta(hours=duree), u))
    visites.sort(key=lambda v: (v[0], v[2].usager_id))
    return visites


def heures(debut: datetime, fin: datetime) -> float:
    return (fin - debut).total_seconds() / 3600


def evaluer(e: Employe, debut: datetime, fin: datetime, u: Usager, heures_sem: float,
            sup: bool) -> bool:
    """Indique si l'employé peut prendre la visite."""
    jour = debut.date()
    if not e.employe_le(jour) or e.absent(debut, fin):
        return False
    if jour.weekday() >= 5 and not e.fin_semaine:
        return False
    duree = heures(debut, fin)
    if sup:
        if not e.volontaire_sup or heures_sem + duree > LIMITE_HEBDO_SUP:
            return False
    elif heures_sem + duree > e.contrat:
        return False

    # Chevauchement, avec un délai de déplacement entre deux domiciles
    for q_debut, q_fin, q_usager in e.quarts[-3:]:
        if q_usager == u.usager_id:
            delai = timedelta(0)
        elif q_usager_secteur(q_usager) == u.secteur_id:
            delai = timedelta(minutes=30)
        else:
            delai = timedelta(hours=1)
        if debut < q_fin + delai and fin + delai > q_debut:
            return False

    # Période de travail courante : quarts séparés par moins de REPOS_MIN
    periode = []
    borne = debut
    for q in reversed(e.quarts):
        if borne - q[1] >= REPOS_MIN:
            break
        periode.append(q)
        borne = q[0]
    travaillees = sum(heures(q[0], q[1]) for q in periode) + duree
    if not sup:
        amplitude = fin - (periode[-1][0] if periode else debut)
        return travaillees <= MAX_HEURES_PERIODE and amplitude <= MAX_AMPLITUDE

    # En heures supplémentaires : enchaînement permis chez le même usager
    bloc = duree
    suivant = debut
    for q in reversed(e.quarts):
        if q[1] != suivant or q[2] != u.usager_id:
            break
        bloc += heures(q[0], q[1])
        suivant = q[0]
    if bloc > duree:
        return bloc <= MAX_BLOC_SUP
    return travaillees <= MAX_HEURES_PERIODE_SUP


_SECTEUR_USAGER: dict[int, int] = {}


def q_usager_secteur(usager_id: int) -> int:
    return _SECTEUR_USAGER[usager_id]


def assigner(visites: list[tuple], employes: list[Employe]) -> list[dict]:
    heures_sem: dict[tuple[int, date], float] = defaultdict(float)
    par_id = {e.employe_id: e for e in employes}
    quarts = []

    for debut, fin, u in visites:
        semaine = debut.date() - timedelta(days=debut.weekday())
        choisi = None
        for sup in (False, True):
            candidats = [e for e in employes
                         if evaluer(e, debut, fin, u, heures_sem[e.employe_id, semaine], sup)]
            if candidats:
                def priorite(e: Employe):
                    en_poste = bool(e.quarts) and e.quarts[-1][1] == debut \
                        and e.quarts[-1][2] == u.usager_id
                    return (
                        not en_poste,
                        e.employe_id not in u.titulaires,
                        e.secteur_id != u.secteur_id,
                        heures_sem[e.employe_id, semaine] / e.contrat,
                        random.random(),
                    )
                choisi = min(candidats, key=priorite)
                break

        remplace = None
        if choisi is not None:
            choisi.quarts.append((debut, fin, u.usager_id))
            heures_sem[choisi.employe_id, semaine] += heures(debut, fin)
            titulaire = par_id[u.titulaires[0]]
            if choisi.employe_id != titulaire.employe_id and titulaire.absent(debut, fin):
                remplace = titulaire.employe_id

        quarts.append({
            "employe_id": choisi.employe_id if choisi else None,
            "usager_id": u.usager_id,
            "debut": debut,
            "fin": fin,
            "type_quart": type_quart(debut),
            "statut": "COUVERT" if choisi else "NON_COUVERT",
            "employe_remplace_id": remplace,
        })
    return quarts


def type_quart(debut: datetime) -> str:
    if 7 <= debut.hour < 15:
        return "JOUR"
    if 15 <= debut.hour < 23:
        return "SOIR"
    return "NUIT"


def injecter_anomalies(quarts: list[dict], employes: list[Employe]) -> dict[str, int]:
    couverts = [q for q in quarts if q["statut"] == "COUVERT" and q["employe_remplace_id"] is None]
    cibles = random.sample(couverts, 8)

    # Employé assigné pendant son absence
    for q in cibles[:4]:
        absents = [e for e in employes if e.absent(q["debut"], q["fin"])]
        while not absents:
            q = random.choice(couverts)
            absents = [e for e in employes if e.absent(q["debut"], q["fin"])]
        q["employe_id"] = random.choice(absents).employe_id

    # Quart après la fin d'emploi
    partant, fin_emploi = next(iter(DEPART.items()))
    apres = [q for q in couverts if q["debut"].date() > fin_emploi and q not in cibles]
    for q in random.sample(apres, 3):
        q["employe_id"] = partant

    # Remplaçant identique au remplacé
    for q in cibles[4:6]:
        q["employe_remplace_id"] = q["employe_id"]

    # Quart couvert sans employé
    for q in cibles[6:8]:
        q["employe_id"] = None

    return {
        "Employé assigné pendant une absence": 4,
        "Quart après la fin d'emploi": 3,
        "Remplaçant identique au remplacé": 2,
        "Quart COUVERT sans employé": 2,
    }


def ecrire(nom: str, entetes: list[str], lignes) -> None:
    with (DATA_DIR / nom).open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(entetes)
        writer.writerows(lignes)


def fmt(valeur) -> str:
    if valeur is None:
        return ""
    if isinstance(valeur, datetime):
        return valeur.isoformat(sep=" ")
    return str(valeur)


def main() -> None:
    random.seed(SEED)
    DATA_DIR.mkdir(exist_ok=True)

    employes = creer_employes()
    usagers = creer_usagers(employes)
    _SECTEUR_USAGER.update({u.usager_id: u.secteur_id for u in usagers})
    absences = creer_absences(employes)
    quarts = assigner(creer_demande(usagers), employes)
    anomalies = injecter_anomalies(quarts, employes)

    ecrire("secteurs.csv", ["secteur_id", "nom"], enumerate(SECTEURS, start=1))
    ecrire("employes.csv",
           ["employe_id", "nom", "secteur_id", "date_embauche", "date_fin_emploi",
            "heures_contrat_semaine"],
           ([e.employe_id, f"Employé {e.employe_id:02d}", e.secteur_id, e.date_embauche,
             fmt(e.date_fin), e.contrat] for e in employes))
    ecrire("usagers.csv", ["usager_id", "nom", "secteur_id", "niveau_soins"],
           ([u.usager_id, f"Usager {u.usager_id:02d}", u.secteur_id, u.niveau] for u in usagers))
    ecrire("absences.csv", ["absence_id", "employe_id", "debut", "fin", "motif"],
           ([i, e, fmt(d), fmt(f), m] for i, (e, d, f, m) in enumerate(absences, start=1)))
    ecrire("quarts_planifies.csv",
           ["quart_id", "employe_id", "usager_id", "debut", "fin", "type_quart", "statut",
            "employe_remplace_id"],
           ([i, fmt(q["employe_id"]), q["usager_id"], fmt(q["debut"]), fmt(q["fin"]),
             q["type_quart"], q["statut"], fmt(q["employe_remplace_id"])]
            for i, q in enumerate(quarts, start=1)))

    non_couverts = sum(q["statut"] == "NON_COUVERT" for q in quarts)
    print(f"Données générées dans {DATA_DIR}")
    print(f"  {len(employes)} employés, {len(usagers)} usagers, {len(absences)} absences")
    print(f"  {len(quarts)} quarts, dont {non_couverts} non couverts "
          f"({100 * non_couverts / len(quarts):.1f} %)")
    print("Anomalies injectées :")
    for libelle, nombre in anomalies.items():
        print(f"  {libelle} : {nombre}")


if __name__ == "__main__":
    main()
