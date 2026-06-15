"""
### Projet 9 — Quiz Culturel

**Thème :** Éducation / Jeux

**Description :**
Un quiz en ligne de commande avec des questions à choix multiples. Les questions sont
chargées depuis un fichier JSON. L'utilisateur choisit un thème et une difficulté.

**Contraintes :**
- Fichier de questions en JSON avec format standardisé
- Mélanger les questions à chaque partie (ordre aléatoire)
- Mélanger aussi l'ordre des réponses proposées
- Afficher un récapitulatif détaillé à la fin (bonnes/mauvaises réponses)
- Score final avec lettre (A, B, C)

**Pistes de réflexion :**
- Conçois toi-même le format JSON de tes questions
- Comment mélanger une liste avec `random.shuffle()` ?
- Explore `random.sample()` vs `random.shuffle()`

Json format
    Theme {
        facile [
            {
                question: str
                reponse: []
                correct: str
                temps: 15
            }
        ]
        moyen [
            {
                question: str
                reponse: []
                correct: str
                temps: 15
            }
        ]
        difficile [
            {
                question: str
                reponse: []
                correct: str
                temps: 15
            }
        ]
    }

"""

##########################################################################################################
# IMPORT
import pathlib as pl
import json
from typing import Any, Dict, List, Tuple, TypeAlias
from pyfiglet import figlet_format
from random import sample, shuffle
from tabulate import tabulate
from copy import deepcopy

# réutilisables et découplées, précondition, générique
##########################################################################################################
# TYPE
Package: TypeAlias = Dict[str, Any]
Level: TypeAlias = List[Package]
Topics: TypeAlias = Dict[str, Level]
Quiz: TypeAlias = Dict[str, Topics]
##########################################################################################################
# GLOBALS VARIABLE
QUIZ_FILE = "base.json"
quiz = "QUIZ GAME"
font = "mono9"

##########################################################################################################
# FILES MANAGMENT


def load_data(filename: str, mode: str = "r", encoding: str = "utf-8") -> Quiz:
    try:
        file_path = pl.Path(filename)
        if not file_path.exists():
            print("\nFile not found...")
            return {}
        with open(filename, mode, encoding=encoding) as file:
            data: Quiz = json.load(file)
        return data
    except json.JSONDecodeError:
        print("\nLoad file Error...")
        return {}

##########################################################################################################
# INPUT


def confirmation_input(text: str) -> bool:
    while True:
        try:
            value: int = int(input(text))
            if value in (0, 1):
                return bool(value)
            print("\nValue must between (0/1)")
        except ValueError:
            print("\nInvalid entry -> Excepted (0/1)")


def number_input(text: str, length: int) -> int:
    while True:
        try:
            value = int(input(text))
            if 1 <= value <= length:
                return value
            print("\nInvalid entry -> Excepted [Value must be > 0])")
        except ValueError:
            print("\nInvalid entry -> Excepted integer value)")

##########################################################################################################
# FEATURES FONCTIONS


def play_game(data: Quiz, topic: str, difficulty: str) -> Tuple[int, List[Dict[str, str]]]:
    score = 0
    packs = deepcopy(data[topic][difficulty])
    packs = sample(packs, len(packs))
    recapitulations = []
    for pack in packs:
        correct = pack["correct"]
        reponses = deepcopy(pack["reponses"])
        question = pack["question"]
        print(f"\n{question}")
        reponse = handle_response(reponses)
        is_correct: bool = (reponse == correct)
        if is_correct:
            score += 1
        recap = handle_recap(question, reponse, correct, is_correct)
        recapitulations.append(recap)
    return score, recapitulations


##########################################################################################################
# UTILS FUNCTIONS
def handle_response(reponses: List[str]) -> str:
    shuffle(reponses)  # Cause reponses is list
    display_responses(reponses)
    choice = number_input(f"Your answser (1-{len(reponses)}) > ", len(reponses))
    return get_choice(reponses, choice)


def handle_recap(question: str, answer: str, correct: str, is_correct: bool) -> Dict[str, str]:
    return {
        "Questions": question,
        "Answers": answer,
        "Corrections": "--" if is_correct else correct
    }


def get_choice(items: List[str], choice: int) -> str:
    return items[choice - 1]


def recapitulation(recap: List[Dict[str, str]]) -> None:
    print("\nRECAPITULATION\n",)
    table = tabulate(recap, headers="keys", tablefmt="pipe")
    print(table)


def score_mention(score: int, total: int) -> None:
    perc = (score / total) * 100
    if perc >= 85:
        res = "A"
    elif perc >= 70:
        res = "B"
    elif perc >= 50:
        res = "C"
    elif perc >= 30:
        res = "D"
    else:
        res = "E"
    print(f"\nYou final score >>> [{res}]")
#########################################################################################################
# DISPLAY CLI FUNCTIONS


def welcome(quiz: str) -> None:
    render = figlet_format(quiz, font=font)
    print(render)


def display_topic(data: Quiz) -> None:
    print("Available Topics:\n",)
    for i, v in enumerate(data, start=1):
        print(f"({i}) - {v}")


def display_difficulty(data: Quiz, topic: str) -> None:
    print("\nDifficulty stage:\n",)
    for i, v in enumerate(list(data[topic].keys()), start=1):
        print(f"({i}) - {v}")


def display_responses(res: List[str]) -> None:
    for i, v in enumerate(res, start=1):
        print(f"({i}) - {v}")
##########################################################################################################
# PROGRAM RUNTIME FUNCTION


def main() -> None:
    data: Quiz = load_data(QUIZ_FILE)
    topics = list(data.keys())
    #
    welcome(quiz)
    while True:
        display_topic(data)
        #
        choice_topic = number_input(
            f"\nChoice topic's number (1-{len(topics)}) > ", len(topics))
        topic = get_choice(topics, choice_topic)
        print(f"\n >>> Topic [{topic}]")
        #
        difficulties = list(data[topic].keys())
        display_difficulty(data, topic)
        choice_difficulty = number_input(
            f"\nChoice difficulty's number (1-{len(difficulties)}) > ", len(difficulties))
        difficulty = get_choice(difficulties, choice_difficulty)
        print(f"\n >>> Level [{difficulty}]")
        #
        score, recap = play_game(data, topic, difficulty)
        #
        total = len(data[topic][difficulty])
        score_mention(score, total)
        recapitulation(recap)
        conf = confirmation_input("Replay game ? (0=No / 1=Yes) > ")
        if not conf:
            print("\nSee you next...\n")
            break


##########################################################################################################
# EXECUTION
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nUser canceled the program by ctrl-c...\n")
