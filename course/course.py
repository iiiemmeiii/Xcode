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
import sys
from typing import List, Dict


def Create_File(filename: str) -> None:
    with open(filename, "w") as file:
        file.write("{}")


def Read_File(filename: str) -> str:
    try:
        with open(filename, "r") as file:
            return file.read()
    except FileNotFoundError:
        print("FILE NOT FOUND")


def Handle_Json_File() -> dict:
    filename: str = "data.json"
    try:
        path = p.Path(filename)

        if not path.exists():
            Create_File(filename=filename)
        data = Read_File(filename=filename)
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


def Add_Dict_Keys(data: Dict[str, List[str]], category: str) -> None:
    keys = list(data.keys())
    if len(keys) == 0:
        keys.append(category)
    if keys.count(category) > 0:
        print("CATEGORY ALREADY EXIST")
    return keys


def Add_Category(data: Dict[str, List[str]]) -> None:
    print("1",data)
    while True:
        choice = Binary_Input("Add caterory ? (0 = NO / 1 = Yes) >>> ")

        if choice:
            category = String_Input("Set category name >>> ")
            if category in data:
                print("CATEGORY ALREADY EXIST - RETRY")
                continue
            data[category] = []
            json.dumps(data)
            
            break

    print(data)

def main() -> None:
    data = Handle_Json_File()
    print(data, type(dict(data)))
    # Add_Category(data)


if __name__ == "__main__":
    main()
