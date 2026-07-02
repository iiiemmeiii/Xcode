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
from typing import List, Tuple
from pyfiglet import Figlet
import sys
from tabulate import tabulate

#################################################################################################
# GLOBAL VARIABLES

ALPHABET: List[str] = [v for v in ascii_uppercase]
MENU: List[str] = ["Decode message", "Force Brute",
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
            return int(input(text))
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


def encode(dec: int, msg: str) -> str:
    offset = offset_letters(dec, ALPHABET)
    for ch in msg:
        if ch.upper() in ALPHABET:
            nch = offset[ALPHABET.index(ch.upper())]
            nch = nch.lower() if ch.islower() else nch.upper()
            msg = msg.replace(ch, nch)
    return msg


def decode(dec: int, msg: str) -> str:
    # je VeUx Tr3 ->  PuL mh YhXa Wu3
    offset = offset_letters(dec, ALPHABET)
    for ch in msg:
        if ch.upper() in offset:
            nch = ALPHABET[offset.index(ch.upper())]
            nch = nch.lower() if ch.islower() else nch.upper()
            msg = msg.replace(ch, nch)
    return msg


def brute_force() -> None:
    pass
#################################################################################################
# UTILS


def offset_letters(dec: int, alphabet: list[str]) -> list[str]:
    offset_alphabet = []
    for i, v in enumerate(alphabet):
        mod = (i + dec) % len(alphabet)
        v = v.replace(v, alphabet[mod])
        offset_alphabet.append(v)
    return offset_alphabet


#################################################################################################
# DISPLAY
def welcome() -> None:
    f = Figlet(font=FONT)
    print(f.renderText("CESAR"),)


def display_menu(menu: List[str]) -> None:
    for i, v in enumerate(menu, start=1):
        print(f"{i} : {v}")
    print("-"*20,)


def dislay_table(dec) -> None:
    offset = offset_letters(dec, ALPHABET)
    table = {"Alphabet": ALPHABET, "Cesar code": offset}
    print(tabulate(table, headers="keys", tablefmt="pretty"))
#################################################################################################
# MAIN PROGRAMM


def main() -> None:

    welcome()
    dec = offset_input("Enter cesar offset > ")
    print(f"\nOffset: [{dec}]\n",)
    msg = string_input("Enter your message > ")
    msg_encoded = encode(dec, msg)
    print(f"\nEncoded message > {msg_encoded}\n",)
    while True:
        display_menu(MENU)
        choice = menu_input(f"Entrer choice (1-{len(MENU)}) > ", len(MENU))
        if choice == 1:
            msg_decoded = decode(dec, msg_encoded)
            print(f"\n[{MENU[choice - 1]}] > {msg_decoded}\n",)
        elif choice == 2:
            print(f"\n[{MENU[choice - 1]}]",)
        elif choice == 3:
            print(f"\n[{MENU[choice - 1]}]",)
            dislay_table(dec)
        else:
            print(f"\n[{MENU[choice - 1]}]",)
            conf = confirmation("Confirm programm exist (0-1) ? ")
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
