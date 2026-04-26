"""
**Thème :** Sécurité / Utilitaire

**Description :**
Génère des mots de passe aléatoires selon les critères de l'utilisateur :
    longueur, inclusion de majuscules, minuscules, chiffres, symboles.

**Contraintes :**
- L'utilisateur choisit chaque critère individuellement (oui/non)
- Générer plusieurs mots de passe à la fois (l'utilisateur choisit combien)
- Évaluer et afficher la "force" du mot de passe (faible/moyen/fort/très fort)
- Permettre de copier le mot de passe dans le presse-papier (module `pyperclip` autorisé ici)

**Pistes de réflexion :**
- Quelle est la différence entre `random` et `secrets` pour la génération de nombres ?
- Comment définir les critères d'un "bon" mot de passe ?
- Explore le module `string` (constantes de caractères)

<>
"""

from string import ascii_lowercase, ascii_uppercase, digits, punctuation, Formatter
import secrets, random
from typing import Callable, Any, List
import pyperclip


fmt: Callable[[str, Any], str] = lambda text, *args: Formatter().format(text, args)


def number_input(text) -> int:
    while True:
        try:
            n = int(input(text))
            if n >= 0:
                return n
            print(fmt("Must be greather 0"))
        except ValueError:
            print(fmt("Not a number - retry"))


def choosePwd(n: int, l: int, arr: List[tuple]) -> str:
    while True:
        if not 0 < n <= l:
            print(f"{n} must be between 1 and {l}")

        return arr[n - 1]


def evaluate_force(pwd: str) -> str:
    has_lower = any(p.islower() for p in pwd)
    has_upper = any(p.isupper() for p in pwd)
    has_digits = sum(p.isdigit() for p in pwd)
    has_punct = sum(p in punctuation for p in pwd)

    length: int = len(pwd)
    if length >= 20 and has_lower and has_upper and has_digits >= 3 and has_punct >= 3:
        msg = "Tres fort"
    elif (
        length >= 15 and has_lower and has_upper and has_digits >= 2 and has_punct >= 2
    ):
        msg = "Fort"
    elif length >= 10 and (
        (has_lower and has_upper) or (has_digits >= 1 and has_punct >= 1)
    ):
        msg = "Moyen"
    else:
        msg = "Faible"

    return msg


def welcome() -> None:
    print("#" * 40)
    print("WELCOME TO GENESIA")
    print("#" * 40, end="\n")


def main() -> None:
    welcome()
    while True:

        q1 = number_input("\nDefinir la longueur du mp (0 = No / 1 = Yes) >> ")
        if q1 == 1:
            length = number_input("Votre longueur >> ")
        else:
            length = random.randint(5, 30)

        char = ""

        q2 = number_input("\nContenir des minusclues (0 = No / 1 = Yes) >> ")
        if q2 == 1:
            char += ascii_lowercase

        q3 = number_input("\nContenir des majuscules (0 = No / 1 = Yes) >> ")
        if q3 == 1:
            char += ascii_uppercase

        q4 = number_input("\nContenir des nombres (0 = No / 1 = Yes) >> ")
        if q4 == 1:
            char += digits

        q5 = number_input("\nContenir des ponctuation (0 = No / 1 = Yes) >> ")
        if q5 == 1:
            char += punctuation

        count = number_input("\nGenerer combien de mp ? >> ")

        # generate: List[str] = [(i,"".join(secrets.choice(char) for _ in range(length))) for i in range(1, count + 1)]
        generate: List[str] = [
            "".join(secrets.choice(char) for _ in range(length))
            for _ in range(1, count + 1)
        ]

        print("\n Vos mots de passe")
        for i, p in enumerate(generate, 1):
            res = evaluate_force(p)
            print(f"{i} - {p} >>> {res} ")

        choix = number_input(f"\nchoisir un mp entre de 1 et {count} ? >> ")

        print(f"\nYour choice: {generate[choix -1]}")

        # <>

        break


if __name__ == "__main__":
    main()
