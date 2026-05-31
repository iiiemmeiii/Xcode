"""
### Projet 8 — Horloge et Chronomètre

**Thème :** Temps / Interface CLI

**Description :**
Un programme avec 3 modes : affichage de l'heure actuelle, 
chronomètre (start/stop/reset), et compte à rebours avec alerte sonore ou visuelle.

**Contraintes :**
- Mode chronomètre en temps réel (mise à jour dans le terminal)
- Le compte à rebours prend une durée en entrée (format `mm:ss`)
- Affichage "en direct" dans le terminal sans créer de nouvelles lignes (utiliser `\r`)
- Sauvegarder les temps du chronomètre dans un historique

**Pistes de réflexion :**
- Explore les modules `time` et `datetime`
- Comment effacer une ligne dans le terminal sans effacer tout l'écran ?
- Quelle est la différence entre `time.time()` et `time.perf_counter()` ?
"""
import time as t
import datetime as dt
import pysnooper, winsound
from rich import print as rprint

modes: list[str] = [f"mode {i}" for i in range(1, 5, 1)]
definitions: list[str] = ["Current time", "Stopwatch", "Countdown", "Exit utility"]


def binary_input(text: str) -> bool:
    while True:
        try:
            value: int = int(input(text))
            if not 0 <= value <= 1:
                rprint("\n[red]You have to enter value between (0 or 1)...")
                continue
            if value == 0:
                return bool(value)
            return bool(value)
        except ValueError:
            rprint(
                f"\n[red]ValueError: Enter positif integer number ! not string...")


def number_input(text: str,  nim: int = 1) -> int:
    while True:
        try:
            value: int = int(input(text))
            if not value >= nim:
                rprint(
                    f"\n[red]Your value [{value}] has to be greather or equal to {nim}")
                continue
            return value
        except:
            rprint(
                f"\n[red]ValueError: Enter positif integer number ! not string...")
############################################################################################
# UTILITY MODE LOGIC
def get_current_time() -> str:
    time_scd = t.time()
    conv_time = t.ctime(time_scd).split()[3]
    return f"\nCurrent time > [yellow]{conv_time}"
def handle_stopwatch() -> None:
    pass

def handle_countdown() -> None:
    pass

############################################################################################
# DISPLAY

def display_menu() -> None:
    assembly: list[tuple[str, str]] = zip(modes, definitions)
    for index, value in enumerate(assembly, start=1):
        mode, definition = value[0], value[1]
        rprint(f"[white]{index} - [green]{mode} > {definition}")

def welcome() -> None:
    rprint(f"\n[white]{"".join("#" for _ in range(35))}")
    rprint(f"[white]{"HORLOGE UTILITY":>25}")
    rprint(f"[white]{"".join("#" for _ in range(35))}\n")

def main() -> None:
    welcome()
    display_menu()
    while True: 
        value: int = number_input("\nEnter your mode (1-4) >>> ") 

        if value == 1 :
            current_time = get_current_time()
            rprint(current_time)
            continue
        elif value == 2 :
            rprint("MODE 2")
            # handle_stopwatch()
        elif value == 3 :
            rprint("MODE 3")
            # handle_countdown() 
        elif value == 4 :
            confirmation = binary_input("\nAre you sure to exit utility ? >>> ")
            if confirmation:
                rprint(f"\n[bold yellow]EXIT UTILITY ! GOODEBYE...")
                exit(0)
            else:
                continue
        else:
            rprint("\n[yellow]Enter valid mode id (1-3)...")
            continue
        break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        rprint("\n[red]ERROR: Operation cancelled by user [crtl-c]...\n")
