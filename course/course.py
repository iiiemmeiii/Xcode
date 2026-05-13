"""
### Projet 7 — Liste de Courses Intelligente

**Thème :** Gestion de données / Fichiers

**Description :**
Une application CLI pour gérer une liste de courses.
L'utilisateur peut
    - ajouter
    - supprimer,
    - cocher des articles,
    - voir la liste
    - sauvegarder/charger depuis un fichier.

**Contraintes :**
- Persistance des données dans un fichier `JSON`
- Regrouper les articles par catégorie (Fruits, Légumes, Épicerie…)
- Afficher la liste avec des cases cochées/non cochées en ASCII (`[x]` / `[ ]`)
- Possibilité d'exporter la liste en `.txt` formaté

**Pistes de réflexion :**
- Pourquoi JSON est-il préférable à un simple `.txt` pour ce cas ?
- Explore `json.load()` et `json.dump()`
- Comment gérer l'absence du fichier au premier lancement ?
 <>
"""

import pathlib as p
import json
from typing import List, Dict


def Dump_in_File(filename: str, init_data: dict = None) -> None:
    if init_data is None:
        init_data = {}

    with open(filename, "w") as file:
        json.dump(init_data, file, indent=3)


def Load_from_File(filename: str) -> dict:
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print("INVALID JSON FILE")
    except IOError:
        print("FILE NOT FOUND")


def Handle_Json_File() -> dict:
    filename: str = "data.json"
    try:
        path = p.Path(filename)

        if not path.exists():
            Dump_in_File(filename)
        data = Load_from_File(filename)
        return data
    except IOError:
        print("ERROR LORS DE WRITE/READ DE FILE")


def Binary_Input(text: str) -> bool:
    try:
        while True:
            value = int(input(text).strip())
            if not 0 <= value <= 1:
                print("INPUT INVALID (0/1)")
            if value == 0:
                return bool(value)
            return bool(value)
    except ValueError:
        print("ENTER VALID INPUT")


def String_Input(text: str) -> str:
    while True:
        value = input(text).strip().capitalize()
        if value == "":
            print("EMPTY INPUT: RETRY")
            continue
        return value


def Add_Category(data: dict, filename: str = "data.json") -> None:

    # data = Handle_Json_File()

    while True:
        choice = Binary_Input("Add caterory ? (0 = NO / 1 = Yes) >>> ")

        if choice:
            while True:
                category = String_Input("Set category name >>> ")
                if category in data:
                    print("CATEGORY ALREADY EXIST - RETRY")
                    continue
                break
        data[category] = []

        print(f"Category [{category}] added...")

        Dump_in_File(filename, data)
        categories = sorted(list(data.keys()))

        return categories


def Display_Items(items:  List[str]) -> None:
    for index, item in enumerate(items, start=1):
        print(f"{index} - {item}")


def Delete_Item(item:  str) -> None:
    pass


def Edit_Category(item:  str) -> None:
    pass

def welcome() -> None :
    print("#"*40)
    print(f"{"COURSES PLANNER":>25}")
    print("#"*40)

def main() -> None:
    try:
        welcome()
        data = Handle_Json_File()
        categories = Add_Category(data)
        Display_Items(categories)

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")


if __name__ == "__main__":
    main()
