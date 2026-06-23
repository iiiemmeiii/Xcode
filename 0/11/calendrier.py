
"""
### Projet 10 — Calendrier ASCII

**Thème :** Date / Affichage formaté

**Description :**
    Affiche un calendrier mensuel en ASCII dans le terminal pour n'importe 
    quel mois/année. 
    Permet de naviguer entre les mois.

**Contraintes :**
- Afficher les jours correctement alignés (lundi en premier)
- Mettre en évidence le jour actuel avec des crochets `[15]`
- Permettre d'ajouter des événements liés à une date (sauvegardés en JSON)
- Afficher les jours avec événements avec un marqueur `*`

**Pistes de réflexion :**
- Explore le module `calendar` (il existe déjà !)
- Pourquoi ne pas en recoder un de zéro pour comprendre comment il fonctionne ?
- Comment déterminer le premier jour d'un mois donné ?


0 <= microseconds < 1000000
0 <= seconds < 3600*24 (the number of seconds in one day)
-999999999 <= days <= 999999999
MINYEAR <= year <= MAXYEAR
1 <= month <= 12
1 <= day <= number of days in the given month and year

"""

from datetime import date
from typing import List, Dict, Tuple, TypeAlias
from pathlib import Path
from json import dump, load, JSONDecodeError
import sys
import re
import pysnooper as ps


######################################################################################################
# GLOBAL TYPE
Content: TypeAlias = Dict[str, str]
Data: TypeAlias = Dict[str, Content]

######################################################################################################
# GLOBAL VARIABLE
list_of_months: List[str] = ['January', 'February', 'March', 'April',
                             'May', 'June', 'July', 'August',
                             'September', 'October', 'November', 'December']
day_name: List[str] = ["Mo", "Tu", "We", "th", "Fr", "Sa", "Su"]
list_of_dom = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
main_menu = ["Next month", "Prev month", "Add Event", "Exit"]

min_year = date.min.year
max_year = date.max.year

min_month = date.min.month
max_month = date.max.month

args = sys.argv

filename = "event.json"
######################################################################################################
# SYS HANDLE AND HELPER


def ismonth(m: int) -> bool:
    return min_month <= m <= max_month


def isyear(y: int) -> bool:
    return min_year <= y <= max_year
# @ps.snoop()


def sys_handler(arg: List[str]) -> Tuple[int, int]:
    try:
        if len(arg) > 3:
            run_helper()
            exit(1)

        if len(arg) == 2:
            run_helper()
            exit(1)

        if len(arg) < 2:
            return date.today().year, date.today().month
        if len(arg) == 3:
            m, y = int(arg[1]), int(arg[-1])
            if not ismonth(m):
                range_helper(m, min_month, max_month)
                exit(1)
            if not isyear(y):
                range_helper(y, min_year, max_year)
                exit(1)
            # m, y = int(arg[1]), int(arg[-1])
            return y, m
        return (0, 0)
    except ValueError:
        print(f"\nOnly digit values are required for year and ...")
        return (0, 0)


def run_helper() -> None:
    print("\nRUN APP HELPER > python file.py month[int] years[int]")
    print("\tE.G [python file.py 2 1970\n")


def range_helper(part: int, min_i: int, max_i: int) -> None:
    print(f"\nEXPECTED > [{part}] must between {min_i}-{max_i}\n")

######################################################################################################
# FILE


def init_dump(filename: str, mode: str = "w", encoding: str = "utf8", event: Data = {}):
    with open(filename, mode, encoding=encoding) as file:
        dump(event, file, indent=4)


def load_file(filename: str) -> Data:
    try:
        path = Path(filename)
        if not path.exists():
            init_dump(filename)
        with open(filename, "r") as file:
            content: Data = load(file)
            return content
    except JSONDecodeError:
        print(f"JSONDecodeError: {JSONDecodeError.msg}")
        return {}

######################################################################################################
# INPUT


def menu_input(text: str, length: int) -> int:
    while True:
        try:
            value: int = int(input(text))
            if 1 <= value <= length:
                return value
            print(f"\nValue must be between (1-{length})...")
        except ValueError:
            print(f"\nOnly integer value is required (1-{length})...")


def confirmation(text: str) -> bool:
    while True:
        try:
            value: int = int(input(text))
            if value in (0, 1):
                return bool(value)
            print(f"\nValue must be between (0-1)...")
        except ValueError:
            print("\nOnly integer value is required (0-1)...")


def string_input(text: str):
    name_pattern = r"^[a-zA-Z]{2,}$"
    date_pattern = r"^\d{1,2}([/-])\d{1,2}\1\d{4}$"
    while True:
        data = input(text).strip()
        mn = re.match(name_pattern, data)
        md = re.match(date_pattern, data)
        if mn or md:
            return data
        print("Invalid Entry: \n\tName (2 char min and only string char) \n\tDate (xx/xx/xxxx or xx-xx-xxx)")


######################################################################################################
# LOGIC ALGO
def next_month(m: int, y: int):
    m += 1
    if m > 12:
        m = 1
        y += 1
    return m, y


def prev_month(m: int, y: int):
    m -= 1
    if m < 1:
        m = 12
        y -= 1
    return m, y


def isleap(y): return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)


######################################################################################################
# UTILS FUNCTION
def add_event(name: str, date: str, data: Data) -> Data:
    num = 1 if len(data) == 0 else len(data) + 1
    content: Data = {
        f"event_{num}": {
            "name": name,
            "date": date
        }
    }
    data.update(content)
    # init_dump(filename, event=data)
    return data


def day_per_month(month: int, year: int, list_month: List[str], list_dom: List[int]) -> Tuple[str, List[str]]:
    try:
        for _ in list_month:
            if not list_month[month - 1]:
                return "", []
            if isleap(year):
                list_dom[1] = 29
            n = list_dom[month - 1]
    except ValueError:
        print("ValueError: Integer value is required...")
        return "", []
    else:
        mois = list_month[month - 1]
        dom = [str(i) for i in range(1, n + 1, 1)]
        return mois, dom


def fdow(y: int, m: int, d: int = 1) -> int:
    return date(y, m, d).weekday()


def today(y: int, m: int, d: int = 1) -> int:
    return date(y, m, d).today().day


def get_choice(choice: int, menu: List[str]):
    return menu[choice - 1]
######################################################################################################
# CLI DISPLAY


def display_calendar(m: int, y: int) -> None:
    fd = fdow(y, m)
    gap = 5
    space = "-"
    arr = []
    dow = ""
    month, dom = day_per_month(m, y, list_of_months[:], list_of_dom[:])
    for i, n in enumerate(day_name):
        if fd == i:
            arr.append(space)
            arr *= i
        dow += f"{n:>{gap}}"
    arr += dom
    title = f"{month} {y}"
    print(f"{title:^35}")
    print(dow)
    for i, d in enumerate(arr):
        end = "\n" if (i+1) % 7 == 0 else ""
        d = f"[{d}]" if i + 1 == today(y, m) else d
        print(f"{d:>{gap}}", end=end)


def display_menu(menu: List[str]) -> None:
    print("\n")
    for i, item in enumerate(menu, start=1):
        print(f"{i} > {item}")


def welcome() -> None:
    print("="*30)
    print(f"{"CALENDAR APP":^30}")
    print("="*30)
######################################################################################################
# MAIN PROGRAM


def core() -> None:
    welcome()
    y, m = sys_handler(args)
    display_calendar(m, y)
    display_menu(main_menu)
    while True:
        choice = menu_input("\nEnter your choice > ", len(main_menu))
        title = get_choice(choice, main_menu)
        if choice == 1:
            print(f">>> [{title}]")
            # Persistance changing vaiable pointer in memory
            m, y = next_month(m, y)
            display_calendar(m, y)
        elif choice == 2:
            print(f">>> [{title}]")
            m, y = prev_month(m, y)
            display_calendar(m, y)
        elif choice == 3:
            name_event = string_input("\tNom de l'event > ")
            date_event = string_input("\tDate de l'event > ")
            current_data = load_file(filename)
            event = add_event(name_event, date_event, current_data)
            init_dump(filename, event=event)
        else:
            conf: bool = confirmation("Are you sure to exist ? (0-1) > ")
            if conf:
                print("\n\n Good bye ...")
                exit(0)


if __name__ == "__main__":
    try:
        core()
    except KeyboardInterrupt:
        print("\nUser is canceled program by [ctrl-c]...\n")


"""
# Tomohiko Sakamoto's Algorithm- Finding the day of the week
def day_of_the_week(y, m, d=1):
    t = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4]
    if (m < 3):
        y = y - 1
    return (y + y // 4 - y // 100 + y // 400 + t[m - 1] + d) % 7) + 1
    
def switch(h) :
    return {
        0 : "Saturday",
        1 : "Sunday",
        2 : "Monday",
        3 : "Tuesday",
        4 : "Wednesday",
        5 : "Thursday",
        6 : "Friday",
    }[h]

def Zellercongruence(day, month, year) :
    if (month == 1) :
        month = 13
        year = year - 1

    if (month == 2) :
        month = 14
        year = year - 1
    q = day
    m = month
    k = year % 100;
    j = year // 100;
    h = q + 13 * (m + 1) // 5 + k + k // 4 + j // 4 + 5 * j
    h = h % 7
    print(switch (h))
"""
