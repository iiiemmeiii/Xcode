"""
### Projet 4 — Convertisseur d'Unités

**Thème :** Sciences / Utilitaire

**Description :**
Un convertisseur d'unités en ligne de commande qui prend en charge : températures (°C, °F, K), distances (km, miles, nm), poids (kg, lb, g).

**Contraintes :**
- Menu principal avec 3 catégories, puis sous-menu par catégorie
- Toutes les conversions dans les deux sens
- Arrondir les résultats à 4 décimales
- Ne pas utiliser de bibliothèque externe (tout calculer manuellement)
**Pistes de réflexion :**
- Comment structurer un programme avec plusieurs niveaux de menus ?
- Explore les `dictionaries` pour stocker les formules de conversion
"""

"""_summary_
    function that describe the conversion formula
Returns:
    _type_: float
"""
from typing import Dict, List
import math

"""_summary_
    < >
    function that describe the conversion formula
Returns:
    _type_: float
"""


#
formulaData: Dict[str, Dict[str, Dict[str, float | int]]] = {
    "Temperature": {
        "celcius": {
            "celcuis_to_kelvin": lambda v: round(v + 237.15, 4),
            "celcuis_to_farhrenheit": lambda v: round(((v * 1.8) - 459.67), 4),
        },
        "kelvin": {
            "kelvin_to_celcuis": lambda v: round((v - 237.15), 4),
            "kelvin_to_farhrenheit": lambda v: round(((v * 1.8) - 459.67), 4),
        },
        "farhrenheit": {
            "farhrenheit_to_celcuis": lambda v: round(((v - 32) / 1.8), 4),
            "farhrenheit_to_kelvin": lambda v: round(((v + 459.67) / 1.8), 4),
        },
    },
    "Mass": {
        "kg": {
            "kg_to_livre": lambda v: round((v * 2.20462), 4),
            "kg_to_gramme": lambda v: round((v * 1000), 4),
        },
        "livre": {
            "livre_to_kg": lambda v: round((v / 2.20462), 4),
            "livre_to_gramme": lambda v: round((v / (2.20462 / 1000)), 4),
        },
        "gramme": {
            "gramme_to_kg": lambda v: round((v / 1000), 4),
            "gramme_to_livre": lambda v: round((v * (2.20462 / 1000)), 4),
        },
    },
    "Distance": {
        "km": {
            "km_to_miles": lambda v: round((v * 0.621371), 4),
            "km_to_nm": lambda v: round((v / 1.852), 4),
        },
        "miles": {
            "miles_to_km": lambda v: round((v / 0.621371), 4),
            "miles_to_nm": lambda v: round((v / 1.15078), 4),
        },
        "nautique_miles": {
            "nm_to_km": lambda v: round((v * 1.852), 4),
            "nm_to_mile": lambda v: round((v * 1.15078), 4),
        },
    },
}


"""
Choisir type de conversion :  temperature
choisir sous type : kelvin
choisir sous sous type ; k_t_k
entrer valeur
affichier resulat
continue

"""


def setCategories() -> dict:
    categories = {i: v for i, v in enumerate(formulaData, start=1)}
    while True:
        try:
            choice: int = int(input("Choisir une categorie de conversion >>> "))
            if not choice in categories.keys():
                print("choix compris: 1 ou 2 ou 3")
                continue
            print(f"\nChoisir Sous Categories : ")
            for i, v in enumerate(formulaData[categories[choice]], 1):
                print(f"{i} > {v} ")
            print()
            return {1: choice, 2: categories}
            # print(formulaData[categories[choice]][c[sub_choice]].keys())
        except ValueError:
            print("Enter valid choice for categories")


def setSubCategories(data: dict):
    categories: dict = data[2]
    choice: int = data[1]
    while True:
        try:
            SS_CATEGORY = {
                i: v for i, v in enumerate(formulaData[categories[choice]], 1)
            }

            ss_choice = int(input("Entrer votre sous categorie de conversion >>> "))

            if ss_choice not in SS_CATEGORY.keys():
                print("sous choix compris: 1 ou 2 ou 3")
                continue
            print("\nchoisir la conversion : ")
            for i, v in enumerate(
                formulaData[categories[choice]][SS_CATEGORY[ss_choice]], 1
            ):
                print(f"{i} > {v} ")

            # print(list(formulaData[categories[choice]][SS_CATEGORY[ss_choice]].keys()))
            return {1: ss_choice, 2: SS_CATEGORY, 3: categories, 4: choice}
        except:
            print("Enter valid choice for sub categories")


def setConvertionType(data: dict):

    ss_choice = data[1]
    SS_CATEGORY = data[2]
    categories = data[3]
    choice = data[4]

    while True:
        try:
            conv_choice = int(input("Entrer votre choix de conversion >>> "))
            CONVERT = {
                i: v
                for i, v in enumerate(
                    formulaData[categories[choice]][SS_CATEGORY[ss_choice]], 1
                )
            }
            if conv_choice not in CONVERT.keys():
                print("choice convert type between 1 or 2")
                continue
            print(formulaData[categories[choice]][SS_CATEGORY[ss_choice]][CONVERT[conv_choice]])
            break
        except:
            print("Enter valid choice for convertion types")


def main():
    l = setCategories()
    c = setSubCategories(l)
    setConvertionType(c)
    # pass


if __name__ == "__main__":
    main()
