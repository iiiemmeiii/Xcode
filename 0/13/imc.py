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

Nom -

"""

#############################################################################################
# IMPORT
#############################################################################################
import sys
from typing import Dict, Tuple, TypeAlias, List, Any
from pyfiglet import Figlet
from tabulate import tabulate
from pathlib import Path
import csv
from datetime import datetime
#############################################################################################
# PROGRAMM GLOBALS VARIABLES
#############################################################################################
Key: TypeAlias = Tuple[float, float]
Value: TypeAlias = Dict[str, str]
imc: TypeAlias = Dict[Key, Value]

IMC_FORMULA = "Weight (kg) ÷ Height (m))"
IMC_DATA: imc = {
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

#############################################################################################
# FILE
#############################################################################################


def write_csv(*args):
    # writing to csv file
    file = f"{args[0]}.{args[1]}"
    with open(file, 'w', newline="") as f:
        # creating a csv dict writer object
        writer = csv.DictWriter(f, fieldnames=args[2])
        # writing headers (field names)
        writer.writeheader()
        # writing data rows
        writer.writerows(args[3])


def read_csv(*args) -> List[Any]:
    try:
        file = f"{args[0]}.{args[1]}"
        with open(file, mode=args[2]) as f:
            reader = csv.DictReader(f)
            data = []
            for row in reader:
                data.append(row)
        return data
    except FileNotFoundError as e:
        print(e)
        return []


def load_csv(*args) -> List[Any]:
    file = f"{args[0]}.{args[1]}"
    path = Path(file)
    if not path.exists():
        with open(file, "w") as f:
            f.write("")

    return read_csv(args[0], args[1], args[2])

#############################################################################################
# PROGRAMM INPUT
#############################################################################################


def name_input(text: str) -> str:
    while True:
        value = input(text).strip()
        if value.isalpha():
            return value.capitalize()
        print(f"\n> {value} must only contain alpha char")


def sex_input(text: str) -> str:
    while True:
        value = input(text).strip().lower()
        if value in ("m", "f"):
            return value.upper()
        print(f"\n> Expected value : M or F")


def number_input(text: str) -> float:
    while True:
        try:
            value = float(input(text))
            if value > 0:
                return value
            print(f"\nValue must be > 0")
        except ValueError as e:
            print(f"\n{e} > retry...")


def menu_input(text: str, l: int) -> int:
    while True:
        try:
            value = int(input(text))
            if 1 <= value <= l:
                return value
            print(f"\nValue must be between (1-{l})")
        except ValueError as e:
            print(f"\n{e} > retry...")


def confirmation(text: str) -> bool:
    while True:
        try:
            value = int(input(text))
            if value in (0, 1):
                return bool(value)
            print(f"\nValue must be between (0-1)")
        except ValueError as e:
            print(f"\n{e} > retry...")

#############################################################################################
# PROGRAMM LOGIC
#############################################################################################


def get_imc(*args):
    return float(args[0] / args[-1]**2)


def save_data(data: List[Value], *args):
    """
    scan current rep
    if find file.csv 
    print found and statitic
    write now data in the file
    """
    newdata: Value = {
        "NUM": str(len(data) + 1),
        "DATETIME": datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
        "NAME": args[0],
        "SEX": args[1],
        "IMC": f"{args[2]:.2f}",
        "IDEALWEIGHT": f"{args[3]:.2f}"
    }
    fields = ["NUM", "DATETIME", "NAME", "SEX", "IMC", "IDEALWEIGHT"]
    data.append(newdata)
    write_csv("imc", "csv", fields, data)

#############################################################################################
# PROGRAMM UTILS FUNCTIONS
#############################################################################################


def observation(imc: float) -> Value:
    value = {}
    for (m, M), v in IMC_DATA.items():
        if m <= imc <= M:
            value = {**v}
    return value


def poids_ideal(*args) -> float:
    """- PI = T – 100 – [(T- 150)/2,5)]  -> homme
    - PI = T – 100 – [(T- 150)/4)] -> Femme"""
    sex, height = args[0], args[-1] * 100
    return height - 100 - ((height - 150) / 2.5) if sex == "M" else height - 100 - ((height - 150) / 4)


def progression(imc: float) -> None:
    for i in range(41):
        p = "="
        if i == 0:
            p = str(i)
        elif i == 40:
            p = str(i)
        elif i == int(imc):
            p = "X"
        sys.stdout.write(p)
        sys.stdout.flush()
    print("")


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


def resume_data(**kwargs) -> None:
    print("\nRESUME DATA")
    print("-"*15)
    print(tabulate(kwargs, headers="keys", tablefmt="grid"))

#############################################################################################
# MAIN PROGRAMM
#############################################################################################


def main():
    data = load_csv("imc", "csv", "r")
    welcome()
    name = name_input("Entrer Name > ")
    sex = sex_input("Entrer Sex > ")
    weight = number_input("Entrer weight (kg) > ")
    height = number_input("Entrer height (m)> ")
    #
    resume_data(Name=[name], Sex=[sex], Weight=[weight], Height=[height])
    #
    while True:
        display_menu(MENU)
        choice = menu_input(f"\nEnter choice (1-{len(MENU)}) > ", len(MENU))
        print(f"\nChoice {choice} : [ {MENU[choice - 1]} ]\n")
        #
        if choice == 1:
            print(f"IMC {IMC_FORMULA}= ")
            imc = get_imc(weight, height)
            observ = observation(imc)
            ideal = poids_ideal(sex, height)
            resume_data(
                IMC=[f"{imc:.2f}"], Classification=[observ["classification"]], Risk=[observ["risque"]], Ideal_weight=[f"{ideal:.2f}"])
            print("\nIMC PROGRESS BAR")
            progression(imc)
            save_conf = confirmation("\nSave this data (0=No - 1=yes) ? > ")
            if save_conf:
                save_data(data, name, sex, imc, ideal)
                print("\nAll data have been saved successfully...")
                sys.exit(0)
        else:
            conf = confirmation("Are you sure to exit (0=No - 1=yes) ? > ")
            if conf:
                print("\n GOODBYE...")
                sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nUSER EXITS PROGRAM VIA [CTRL-C]...\n ")
        sys.exit(0)
