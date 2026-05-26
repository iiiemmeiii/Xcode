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

 Le programme doit memoriser l'etat et se souvenir lors de lexec
"""

import pathlib as p
from json import JSONDecodeError, dump, load
from typing import List, Dict
import pysnooper

############################################################################

# Global variable
filename: str = "data.json"
menu: List[str] = ["Display shopping", "Add new catergory", "Add article",
                   "Delete a category", "Delete all categories", "Check Article", "Delete article", "Exit program"]
article_key: tuple[str] = ("name", "check")
# Global Type
type data_type = Dict[str, List[Dict[str, bool]]]

############################################################################
# File handler function


def dump_into_file(filename: str, data: data_type = None) -> None:
    if data is None:
        data = {}

    with open(filename, "w") as file:
        dump(data, file, indent=3)


def load_from_file(filename: str) -> data_type:
    try:
        with open(filename, "r") as file:
            return load(file)
    except JSONDecodeError as e:
        print("INVALID JSON FILE")
    except IOError:
        print("FILE NOT FOUND")

# this function check if file exist write it if not


def handle_file(filename: str) -> None:
    try:
        path = p.Path(filename)

        if not path.exists():
            dump_into_file(filename)
    except IOError:
        print("\nFile IOError")

############################################################################


def bool_input(text: str, nim: int = 0, xam: int = 1) -> bool:
    try:
        while True:
            value = int(input(text))
            if not nim <= value <= xam:
                print(f"\nError: [{value}] wrong answer.. expected -> (0/1)")
                continue
            if value == 0:
                return bool(value)
            return bool(value)
    except ValueError:
        print("\nValueError: integer number expected -> (0/1)")


def number_input(text: str, nim: int = 1) -> int:
    try:
        while True:
            value = int(input(text))
            if not value >= nim:
                print(f"\nError: [{value}] must be greather than 0)")
                continue
            return value
    except ValueError:
        print("\nValueError: integer number only")


def string_input(text: str) -> str:
    while True:
        value = input(text).strip().capitalize()
        if not value:
            print("\nNot empty string: eg[fruit, drink...]")
            continue
        return value
###################################################################################
# UTILS


def target_item(index: int, items: list[str], nim: int = 0, decr: int = 1) -> str:
    index -= decr
    if not nim <= index < len(items):
        print("\nCategory id is invalid")
        return
    return items[index]


def category_list(data: data_type) -> list[str]:
    return [cat for cat in data.keys() if cat]

##################################################################################


def add_category(data: data_type) -> data_type:
    while True:
        category = string_input("\nSet category name >>> ")
        if category in data:
            print("\nCategory already exist - retry")
            continue

        data[category] = []
        print(f"\nCategory [{category}] added...")
        return data


def delete_single_category(data: data_type) -> data_type:
    categories = category_list(data)
    if not categories:
        print("There is any category set...")
        return
    while True:
        try:
            index: int = number_input("\nEnter category id >>> ")
            category: str = target_item(index, categories)
            if not category:
                continue
            print(f"\nCategory [{category}] delete successfully ...\n")
            data.pop(category)
        except TypeError:
            print(f"\nError : Try to enter valid categorie id -> (int) \n")
        


def delete_all_category(data: dict) -> dict:
    if not data:
        print("\nCategories base is empty")
        return
    data.clear()
    print("\nAll Categories delete successfully ...\n")
    return data


"""
Article function
"""


def add_article(data: data_type) -> data_type:
    categories: List[str] = category_list(data)
    if not categories:
        print("There is any category set...")
        return
    while True:
        try:
            index = number_input("\nSelect Caterory: Id >>> ")
            category = target_item(index, categories)
            if not category:
                continue
            print(f"\nAdd article into category [{category}]")
            article_name = string_input("\nSet article name >>> ")
            if not article_name:
                continue
            article_obj = {
                article_key[0]: article_name,
                article_key[1]: False
            }
            data[category].append(article_obj)
        except TypeError:
            print("Add aritcle typeError")
        except IndexError:
            print("\nArticle Add : Category id is invalid")
        else:
            return data

# @pysnooper.snoop()


def delete_article(data: data_type):
    categories = category_list(data)
    if not categories:
        print("There is any category set...")
        return
    while True:
        try:
            index: int = number_input("\nEnter category id >>> ")
            # Target category
            category = target_item(index, categories)

            if not category:
                continue
            print(category)
            # Target article in category
            index2 = number_input("\nEnter article id >>> ")
            if not index2:
                continue
            article = target_item(index2, data[category])
            if not article:
                continue
            data[category].remove(article)
        except TypeError:
            print("TypeError")
        except IndexError:
            print("\nArticle Add : Category id is invalid")
        else:
            return data


@pysnooper.snoop()
def cocher_article(data: data_type):
    categories = category_list(data)
    if not data:
        print("\nCategories base is empty")
        return
    while True:
        try:
            index = number_input("\nEnter category id >>> ")
            if not index:
                continue
            category = target_item(index, categories)

            index2 = number_input("\nEnter article id >>> ")
            if not index2:
                continue
            article = target_item(index2, data[category])
            article[article_key[1]] = not article[article_key[1]]
        except TypeError:
            print("TypeError")
        else :
            return data


###################################################################################


def display_menu(menu) -> None:
    print("")
    for index, item in enumerate(menu, start=1):
        print(f"[{index}] - {item}")


def display_article(data: data_type) -> None:
    print("")

    categories: list[tuple[int, str]] = [(x, c)
                                         for x, c in enumerate(data, start=1)]
    for cat in categories:
        index = cat[0]
        category = cat[1]
        print(f"[{index}] - {category}")
        articles: list[tuple[int, dict[str, str | bool]]] = [
            (y, a) for y, a in enumerate(data[category], start=1)]
        for article in articles:
            check: str = " " if not article[1]["check"] else "X"
            print(f"\t {article[0]} | [{check}] - {article[1]["name"]}")


def Welcome() -> None:
    print("#"*40)
    print(f"{"COURSES PLANNER":>25}")
    print("#"*40)


def main() -> None:

    handle_file(filename)

    data = load_from_file(filename)

    Welcome()

    while True:
        display_menu(menu)
        data = load_from_file(filename)
        enumeration = "/".join(str(i) for i in range(1, len(menu) + 1))
        option = number_input(f"Choose option ({enumeration}) >>> ")

        if option == 1:
            if not data:
                print("\nNothing to show > Set catergory (2)")
                continue
            else:

                display_article(data)

        elif option == 2:
            data = add_category(data)
            # creer la memoire du programme
            dump_into_file(filename, data)

        elif option == 3:
            display_article(data)
            data = add_article(data)
            dump_into_file(filename, data)

        elif option == 4:
            data = delete_single_category(data)

            dump_into_file(filename, data)

        elif option == 5:
            delete_all_category(data)
            dump_into_file(filename, data)
        elif option == 6:
            data = cocher_article(data)
            dump_into_file(filename, data)
        elif option == 7:
            data = delete_article(data)
            # data = delete_article(data)
            dump_into_file(filename, data)

        elif option == 8:
            confirmation = bool_input("\nAre you show to exist ? (0/1) >>> ")
            if confirmation:
                print("\nGoodbye: see you next ...\n")
                exit(0)
            else:
                continue


if __name__ == "__main__":
    try:

        main()
    except KeyboardInterrupt:
        print("\n\nUser existing program by ctrl-c")
