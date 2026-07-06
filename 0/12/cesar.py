"""
### Projet 11 — Traducteur de César

**Thème :** Cryptographie / Algorithmique

**Description :**
Implémente le chiffre de César : décale chaque lettre de l'alphabet 
d'une valeur N choisie par l'utilisateur. Encode et décode des messages.

**Contraintes :**
- Préserver la casse (majuscules restent majuscules)
- Ignorer les chiffres et symboles (les laisser inchangés)
- Proposer un mode "force brute" qui teste tous les décalages possibles (0–25) 
  et affiche les résultats
- Afficher la table de correspondance lettre → lettre pour le décalage choisi

**Pistes de réflexion :**
- Qu'est-ce que `ord()` et `chr()` ? Comment fonctionnent-ils ?
- Ce chiffrement est-il "sécurisé" ? Pourquoi ?
- Comment automatiser la détection de la langue pour identifier le bon décalage ?

"""
#################################################################################################
# IMPORT
from string import ascii_uppercase
from typing import List
from pyfiglet import Figlet
import sys
from tabulate import tabulate

#################################################################################################
# GLOBAL VARIABLES

MENU: List[str] = ["Encode message", "Decode message", "Force Brute",
                   "Offset match table", "Exit programm"]
FONT = "mono9"

#################################################################################################
# INPUT


def string_input(text: str) -> str:
    return input(text).strip()


def menu_input(text: str, length: int) -> int:
    while True:
        try:
            value = int(input(text))
            if 1 <= value <= length:
                return value
            print(f"Error > Value must be between 1-{length}...")
        except ValueError:
            print("ValueError > Enter integer value only...\n")


def offset_input(text: str) -> int:
    while True:
        try:
            value = int(input(text))
            if 0 <= value <= 25:
                return value
            print(f"Error > Value must be between 1-25...")
        except ValueError:
            print("ValueError > Enter integer value only...\n")


def confirmation(text: str) -> bool:
    while True:
        try:
            value = int(input(text))
            if value in (0, 1):
                return bool(value)
            print(f"Error > [{value}] not in (0, 1)...\n")
        except ValueError:
            print("ValueError > Enter integer value only...\n")

#################################################################################################
# ALGORYTHMES


def cesar_handle(msg: str, shift: int) -> str:
    result = []
    for char in msg:
        if char.isalpha():
            s = ord("A") if char.isupper() else ord("a")
            alpha_range = ord(char) - s
            modulo = (alpha_range + shift) % 26
            newchar = chr(s + modulo)
            result.append(newchar)
            print(alpha_range, modulo, char, newchar)
        else:
            result.append(char)
    return "".join(result)


def brute_force(msg: str) -> None:
    for shift in range(26):
        decrypt = cesar_handle(msg, -shift)
        print(f"Shift -{shift:02d} : {decrypt}")
    print("-"*25,)

#################################################################################################
# DISPLAY


def welcome() -> None:
    f = Figlet(font=FONT)
    print(f.renderText("CESAR"),)


def display_menu(menu: List[str]) -> None:
    print("-"*25,)
    for i, v in enumerate(menu, start=1):
        print(f"{i} : {v}")
    print("-"*25,)


def display_table(shift) -> None:
    alphabet = list(ascii_uppercase)
    cesaret = [cesar_handle(l, shift) for l in alphabet]
    table = {"Alphabet": alphabet, "Cesar code": cesaret}
    print(tabulate(table, headers="keys", tablefmt="pretty"))


#################################################################################################
# MAIN PROGRAMM


def main() -> None:
    welcome()
    print(cesar_handle("papa de pap 12", 3))
    #
    shift = offset_input("Enter cesar offset > ")
    print(f"\nCesar shift >>> [{shift}]\n",)
    #
    while True:
        #
        display_menu(MENU)
        choice = menu_input(f"Entrer choice (1-{len(MENU)}) > ", len(MENU))
        title = MENU[choice - 1]
        print(f"\nChoice > [{title}]",)
        #
        if choice == 1:
            text = string_input("Enter text to ENCODE > ")
            print(f"\nResult >>> {cesar_handle(text, shift)}\n")
        elif choice == 2:
            text = string_input("Enter text to DECODE > ")
            print(f"\nResult >>> {cesar_handle(text, -shift)}\n")
        elif choice == 3:
            text = string_input("Enter your message > ")
            brute_force(text)
        elif choice == 4:
            display_table(shift)
        else:
            conf = confirmation("Confirm programm exist (0=No / 1=Yes) ? ")
            if conf:
                print("\nGoobye, see you later...",)
                sys.exit(0)


#################################################################################################
# EXECUTION PROGRAMM
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\nUSER EXITS PROGRAMM BY [CTRL-C]...\n")
