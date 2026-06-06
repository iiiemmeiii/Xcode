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
import pysnooper
import winsound
from rich import print as rprint
import threading

time_set: dict[str, int | bool] = {
    "tierce": 0,
    "sec": 0,
    "min": 0,
    "hour": 0,
    "leap": 60,
    "limit": 1/60,
    "is_running": True
}


etat: dict[str, bool] = {"run": True}

menu: dict[str, str] = {
    "Mode 1": {
        "name": "Current time",
        "sub_menu": None
    },
    "Mode 2": {
        "name": "Stopwatch",
        "sub_menu": ["Start", "Stop", "Reset"]
    },
    "Mode 3": {
        "name": "Countdown",
        "sub_menu": ["Start", "Stop", "Reset"],
        "times_items": ["Hours", "Minutes", "Seconds"]
    },

    "Mode 4": {
        "name": "Exit utility",
        "sub_menu": None
    },
}


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

# @pysnooper.snoop()


def handle_stopwatch(menu: dict, value: int) -> None:
    modes = list(menu.keys())
    sub_menu = target_submenu(modes, value)
    start, stop, reset = sub_menu[0], sub_menu[1], sub_menu[-1]
    conf: int = binary_input(f"\n{start} (0/1)> ")
    if conf:

        sub_menu.remove(start)
        is_running = time_set["is_running"]
        start_stopwatch(time_set["tierce"], time_set["sec"],
                        time_set["min"], time_set["hour"],
                        time_set["limit"], time_set["leap"], is_running)
        print("")

        switch_stopwatch_oper(sub_menu, stop, start, reset)

    else:
        print("no start")
    print()


def handle_countdown() -> None:
    pass

############################################################################################
# UTILS


def target_submenu(modes: list[str], value: int) -> tuple[list[str], list[str]]:
    target_mode = modes[value - 1]
    sub_menu: list[str] = menu[target_mode]["sub_menu"]
    if target_mode:
        return sub_menu
    return None


def switch_stopwatch_oper(sub_menu, stop, start, reset, data):
    while data["is_running"]:

        data["is_running"] = False
        sub_menu[0] = stop if is_running else start
        action = stop if is_running else start
        diplay_submenu(sub_menu)
        choice = number_input(f"{action} (1) / {reset} (2) > ")
        if choice == 1:

            is_running = not is_running
            continue
        elif choice == 2:
            print(sub_menu[choice - 1])
            break


############################################################################################
# STOPWATH MODE


def start_stopwatch(tierce, sec, minut, hour, limit, leap, is_running: bool):
    while is_running:
        tierce += 1
        print(
            f"Start >>> {hour:02d}:{minut:02d}:{sec:02d}:{tierce}", end="\r", flush=True)
        if tierce == limit:
            sec += 1
            tierce = 0
        if sec == limit:
            minut += 1
            sec = 0
        if minut == limit:
            hour += 1
            minut = 0
        t.sleep(leap)


def stop_stopwatch(tierce, sec, minut, hour, running: bool):
    while not running:
        print(f"Stop >>> {hour:02d}:{minut:02d}:{sec:02d}:{tierce}", end="\r")
        return tierce, sec, minut, hour


def reset_stopwatch():
    pass

############################################################################################
# DISPLAY


def diplay_submenu(submenu: list[str]) -> None:
    for index, subm in enumerate(submenu, start=1):
        print(f"{index} - {subm}", flush=True)


def display_menu() -> None:
    for index, value in enumerate(menu.keys(), start=1):
        mode, definition = value, menu[value]["name"]
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

        if value == 1:
            current_time = get_current_time()
            rprint(current_time)
            continue
        elif value == 2:
            rprint("MODE 2")
            thread_chrono = threading.Thread(
                target=handle_stopwatch, args=(time_set,))
            thread_input = threading.Thread(
                target=switch_stopwatch_oper, args=(time_set,))

            thread_chrono.start()
            thread_input.start()

            thread_chrono.join()
            thread_input.join()
            # handle_stopwatch(menu, value)
        elif value == 3:
            rprint("MODE 3")
            # handle_countdown()
        elif value == 4:
            confirmation = binary_input(
                "\nAre you sure to exit utility ? >>> ")
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
