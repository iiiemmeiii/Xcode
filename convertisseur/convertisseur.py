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

categories = {i: v for i, v in enumerate((list(formulaData.keys())), start=1)}

# convertMode = {i:v for i, v in enumerate(1)}


def setCategories() -> int:
    while True:
        try:
            choice = int(input("Choisir categorie >>> "))
            if not choice in categories:
                print("choix compris: 1 ou 2 ou 3")
            return choice

        except ValueError:
            print("Entrer valid choix")


def setlabelConv(choice: int):
    pass


def setConversion(choice: int) -> int:
    while True:
        try:
            setlabelConv(choice)

            conv = int(input("choisir une conversion >>> "))

        except ValueError:
            pass


# d = {i: v for i, v in enumerate((list(formulaData[categories.values()])), start=1)}
d = list(formulaData.keys())
c = {}


def con(l):
    for i in d:
        for v in formulaData[i].keys():
            print(v)


con()
