import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

from pyfiglet import Figlet
from tabulate import tabulate

# Variables globales et configurations
IMC_DATA: Dict[Tuple[float, float], Dict[str, str]] = {
    (0.0, 16.0): {"classification": "Maigreur sévère", "risque": "Élevé (dénutrition)"},
    (16.0, 17.0): {"classification": "Maigreur modérée", "risque": "Modéré"},
    (17.0, 18.5): {"classification": "Maigreur légère", "risque": "Faible"},
    (18.5, 25.0): {"classification": "Poids normal", "risque": "Faible (référence)"},
    (25.0, 30.0): {"classification": "Surpoids (préobésité)", "risque": "Accru"},
    (30.0, 35.0): {"classification": "Obésité classe I (modérée)", "risque": "Élevé"},
    (35.0, 40.0): {"classification": "Obésité classe II (sévère)", "risque": "Très élevé"},
    (40.0, float('inf')): {"classification": "Obésité classe III (morbide)", "risque": "Extrêmement élevé"},
}

CSV_FILE = Path("imc.csv")
CSV_FIELDS = ["NUM", "DATETIME", "NAME", "SEX", "IMC", "IDEALWEIGHT"]

#############################################################################################
# GESTION DES FICHIERS
#############################################################################################

def load_history() -> List[Dict[str, str]]:
    """Charge l'historique depuis le fichier CSV. Le crée s'il n'existe pas."""
    if not CSV_FILE.exists():
        return []
    try:
        with open(CSV_FILE, mode="r", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except (IOError, csv.Error) as e:
        print(f"\n[Erreur] Impossible de lire l'historique : {e}")
        return []

def save_history(history: List[Dict[str, str]], name: str, sex: str, imc_val: float, ideal_w: float) -> None:
    """Ajoute une nouvelle entrée et sauvegarde l'historique complet."""
    new_entry = {
        "NUM": str(len(history) + 1),
        "DATETIME": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "NAME": name,
        "SEX": sex,
        "IMC": f"{imc_val:.2f}",
        "IDEALWEIGHT": f"{ideal_w:.2f}"
    }
    history.append(new_entry)
    
    try:
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(history)
        print("\n> Données sauvegardées avec succès.")
    except IOError as e:
        print(f"\n[Erreur] Impossible d'écrire dans le fichier : {e}")

#############################################################################################
# LOGIQUE ET CALCULS
#############################################################################################

def calculate_imc(weight: float, height: float) -> float:
    return weight / (height ** 2)

def calculate_ideal_weight(sex: str, height_m: float) -> float:
    height_cm = height_m * 100
    if sex == "M":
        return height_cm - 100 - ((height_cm - 150) / 2.5)
    return height_cm - 100 - ((height_cm - 150) / 4.0)

def get_observation(imc_val: float) -> Dict[str, str]:
    for (low, high), info in IMC_DATA.items():
        if low <= imc_val < high:
            return info
    return {"classification": "Inconnue", "risque": "Inconnu"}

def display_progression(imc_val: float) -> None:
    """Affiche une barre de progression ASCII propre et bornée."""
    min_scale, max_scale = 10, 40
    bar_length = 30
    
    # On borne la valeur pour éviter que le curseur sorte de la barre
    current = max(min_scale, min(imc_val, max_scale))
    position = int((current - min_scale) / (max_scale - min_scale) * bar_length)
    
    bar = ["="] * bar_length
    if 0 <= position < bar_length:
        bar[position] = "X"
        
    print(f"{min_scale} [{''.join(bar)}] {max_scale} (Votre IMC: {imc_val:.2f})")

#############################################################################################
# ENTRÉES UTILISATEUR
#############################################################################################

def get_input_input(prompt: str, validation_func) -> Any:
    while True:
        try:
            value = input(prompt).strip()
            return validation_func(value)
        except ValueError as e:
            print(f"> Erreur : {e}")

def validate_name(val: str) -> str:
    if not val.isalpha(): raise ValueError("Le nom doit contenir uniquement des lettres.")
    return val.capitalize()

def validate_sex(val: str) -> str:
    if val.upper() not in ("M", "F"): raise ValueError("Le sexe doit être M ou F.")
    return val.upper()

def validate_positive_float(val: str) -> float:
    res = float(val)
    if res <= 0: raise ValueError("La valeur doit être supérieure à 0.")
    return res

def validate_menu_choice(val: str) -> int:
    res = int(val)
    if res not in (1, 2): raise ValueError("Choix invalide (1 ou 2).")
    return res

def validate_confirmation(val: str) -> bool:
    if val not in ("0", "1"): raise ValueError("Entrez 0 pour Non ou 1 pour Oui.")
    return val == "1"

#############################################################################################
# FLUX PRINCIPAL
#############################################################################################

def run_imc_calculator(history: List[Dict[str, str]]) -> None:
    name = get_input_input("Entrer Nom > ", validate_name)
    sex = get_input_input("Entrer Sexe (M/F) > ", validate_sex)
    weight = get_input_input("Entrer poids (kg) > ", validate_positive_float)
    height = get_input_input("Entrer taille (m) > ", validate_positive_float)

    print("\n=== RÉSUMÉ DES DONNÉES INSERÉES ===")
    print(tabulate([{"Nom": name, "Sexe": sex, "Poids (kg)": weight, "Taille (m)": height}], headers="keys", tablefmt="grid"))

    imc_val = calculate_imc(weight, height)
    obs = get_observation(imc_val)
    ideal_w = calculate_ideal_weight(sex, height)

    print("\n=== RÉSULTATS ===")
    print(tabulate([{
        "IMC": f"{imc_val:.2f}",
        "Classification": obs["classification"],
        "Risque": obs["risque"],
        "Poids Idéal (Lorentz)": f"{ideal_w:.2f} kg"
    }], headers="keys", tablefmt="grid"))

    print("\nBARRE DE PROGRESSION IMC :")
    display_progression(imc_val)

    if get_input_input("\nSauvegarder ces données (0=Non - 1=Oui) ? > ", validate_confirmation):
        save_history(history, name, sex, imc_val, ideal_w)

def main():
    history = load_history()
    f = Figlet(font="mono9", width=80)
    print(f.renderText("IMC HEALTH"))

    while True:
        print("\nCHOOSE AN OPERATION\n" + "-"*20 + "\n1 > Get IMC\n2 > Exit\n" + "-"*20)
        choice = get_input_input("Entrez votre choix (1-2) > ", validate_menu_choice)

        if choice == 1:
            run_imc_calculator(history)
        elif choice == 2:
            if get_input_input("Êtes-vous sûr de vouloir quitter (0=Non - 1=Oui) ? > ", validate_confirmation):
                print("\nAU REVOIR...")
                sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPROGRAMME INTERROMPU PAR L'UTILISATEUR.")
        sys.exit(0)