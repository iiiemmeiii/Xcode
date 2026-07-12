"""
### Projet 12 — Calculateur IMC & Santé

**Thème :** Santé / Calcul

**Description :**
Calcule l'IMC (Indice de Masse Corporelle IMC = Poids (kg) ÷ Taille² (m)) à partir du poids et de la taille. 
Affiche la catégorie OMS correspondante et des informations générales.

**Contraintes :**
- Accepter les données en unités métriques
- Afficher une barre de progression ASCII indiquant où se situe l'IMC
- Calculer et afficher le poids idéal selon la formule de Lorentz 
    - PI = T – 100 – [(T- 150)/2,5)]  -> homme
    - PI = T – 100 – [(T- 150)/4)] -> Femme
- Sauvegarder un historique des mesures (date + IMC) dans un fichier CSV

**Pistes de réflexion :**
- Explore le module `csv` pour écrire dans un fichier CSV
- Comment afficher une barre de progression avec des caractères ASCII ?
- Quelle est la différence entre IMC et composition corporelle ?
"""

#############################################################################################
# IMPORT
#############################################################################################
import sys
from typing import Dict, Tuple, List, Callable, Any
from pyfiglet import Figlet
from tabulate import tabulate
from pathlib import Path
import csv
from datetime import datetime
#############################################################################################
# PROGRAMM GLOBALS VARIABLES
#############################################################################################
type Key = Tuple[float, float]
type Value = Dict[str, str]

IMC_FORMULA = "Weight (kg) ÷ Height (m))"
IMC_DATA: Dict[Key, Value] = {
    (0, 16.0): {"classification": "Maigreur sévère", "risque": "Élevé (dénutrition)"},
    (16.0, 16.9): {"classification": "Maigreur modérée", "risque": "Modéré"},
    (17.0, 18.4): {"classification": "Maigreur légère", "risque": "Faible"},
    (18.5, 24.9): {"classification": "Poids normal", "risque": "Faible (référence)"},
    (25.0, 29.9): {"classification": "Surpoids (préobésité)", "risque": "Accru"},
    (30.0, 34.9): {"classification": "Obésité classe I (modérée)", "risque": "Élevé"},
    (35.0, 39.9): {"classification": "Obésité classe II (sévère)", "risque": "Très élevé"},
    (40.0, float('inf')): {"classification": "Obésité classe III (morbide)", "risque": "Extrêmement élevé"},
}

MENU = ["Get IMC", "Exit"]
FONT = "mono9"
CSV_FILE = Path("imc.csv")
#############################################################################################
# FILE
#############################################################################################


def write_csv(filename: Path, fields: List[str], datas: List[Value]) -> None:
    try:
        with open(filename, 'w', newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(datas)
    except (IOError, csv.Error) as e:
        print(e)


def load_history() -> List[Value]:
    if not CSV_FILE.exists():
        return []
    try:
        with open(CSV_FILE, mode="r", encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            return list(csv_reader)
    except (IOError, csv.Error) as e:
        print(e)
        return []


def save_history(datas: List[Value], name: str, sex: str, imc: float, ideal_weight: float) -> None:
    fields = ["NUM", "DATETIME", "NAME", "SEX", "IMC", "IDEALWEIGHT"]
    newdata: Value = {
        "NUM": str(len(datas) + 1),
        "DATETIME": datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
        "NAME": name,
        "SEX": sex,
        "IMC": f"{imc:.2f}",
        "IDEALWEIGHT": f"{ideal_weight:.2f}"
    }
    datas.append(newdata)
    write_csv(CSV_FILE, fields, datas)
#############################################################################################
# PROGRAMM INPUT
#############################################################################################


def fields_input(prompt: str, valid_field: Callable[[str], Any]) -> Any:
    while True:
        try:
            value = input(prompt)
            return valid_field(value)
        except ValueError as e:
            print(f"\n> Erreur : {e}")


def valid_name_field(name: str) -> str:
    if not name.isalpha():
        raise ValueError("Name must be only alpha chars")
    return name.capitalize()


def valid_sex_field(sex: str) -> str:
    if sex.upper() not in ("M", "F"):
        raise ValueError("Sex must be F or M")
    return sex.capitalize()


def valid_positive_field(value: str) -> float:
    res = float(value)
    if res <= 0:
        raise ValueError("Value must be positive and greather than zero")
    return res


def valid_menu_field(value: str) -> int:
    res = int(value)
    if not 1 <= res <= len(MENU):
        raise ValueError(f"Value must be between 1-{len(MENU)}")
    return res


def valid_confirmation_field(value: str) -> bool:
    res = int(value)
    if res not in (0, 1):
        raise ValueError("Value must be between 0-1")
    return bool(res)

#############################################################################################
# PROGRAMM UTILS FUNCTIONS
#############################################################################################


def get_imc(weight: float, height: float) -> float:
    return weight / (height ** 2)


def observation(imc: float) -> Value:
    for (m, M), v in IMC_DATA.items():
        if m <= imc <= M:
            return v
    return {"classification": "Inconnue", "risque": "Inconnu"}


def imc_ideal_weight(sex: str, height_m: float) -> float:
    height_cm = height_m * 100
    if sex == "M":
        return height_cm - 100 - ((height_cm - 150) / 2.5)
    return height_cm - 100 - ((height_cm - 150) / 4)


def display_progression(imc: float) -> None:
    start, end = 10, 40
    bar_length = 30
    current = max(start, min(imc, end))
    ecart = current - start
    plage = end - start
    position = int((ecart / plage) * bar_length)
    bar = ["="] * bar_length
    if 0 <= position < bar_length:
        bar[position] = "X"

    print(f"{start} [{''.join(bar)}] {end} (Votre IMC: {imc:.2f})")

#############################################################################################
# PROGRAMM LOGIC
#############################################################################################


def imc_calulator_handler(datas):
    name = fields_input("Enter name > ", valid_name_field)
    sex = fields_input("Enter sex (M, F) > ", valid_sex_field)
    weight = fields_input("Enter weight > ", valid_positive_field)
    height = fields_input("Enter height > ", valid_positive_field)

    print("\n=== RÉSUMÉ DES DONNÉES INSERÉES ===")
    print(tabulate([{"Nom": name, "Sexe": sex, "Poids (kg)": weight,
          "Taille (m)": height}], headers="keys", tablefmt="grid"))

    imc = get_imc(weight, height)
    obs = observation(imc)
    ideal_weight = imc_ideal_weight(sex, height)

    print("\n=== RÉSULTATS ===")
    print(tabulate([{
        "IMC": f"{imc:.2f}",
        "Classification": obs["classification"],
        "Risque": obs["risque"],
        "Poids Idéal (Lorentz)": f"{ideal_weight:.2f} kg"
    }], headers="keys", tablefmt="grid"))

    print("\nBARRE DE PROGRESSION IMC :")
    display_progression(imc)

    save_conf = fields_input("Save data ? > ", valid_confirmation_field)
    if save_conf:
        save_history(datas, name, sex, imc, ideal_weight)


#############################################################################################
# PROGRAMM DISPLAY
#############################################################################################


def welcome() -> None:
    f = Figlet(font=FONT, width=80)
    print(f.renderText("IMC"))


def display_menu(menu: List[str]) -> None:
    print("\nCHOOSE AN OPERATION")
    print("-"*20)
    for i, v in enumerate(menu, start=1):
        print(f"{i} > {v}")
    print("-"*20)


#############################################################################################
# MAIN PROGRAMM
#############################################################################################


def main():
    datas = load_history()
    welcome()
    #
    while True:
        display_menu(MENU)
        choice = fields_input(
            f"\nEnter choice (1-{len(MENU)}) > ", valid_menu_field)
        print(f"\n== {MENU[choice - 1]} ==\n")
        #
        if choice == 1:
            imc_calulator_handler(datas)
        else:
            if fields_input("\nAre sur to exit programm ? > ", valid_confirmation_field):
                print("\n GOODBYE...")
                sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nUSER EXITS PROGRAM VIA [CTRL-C]...\n ")
        sys.exit(0)
