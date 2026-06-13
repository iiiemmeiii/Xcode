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
from typing import Any, Dict, List
from pyfiglet import figlet_format
from random import sample, shuffle
from tabulate import tabulate
from copy import deepcopy
##########################################################################################################
# GLOBALS VARIABLE
QUIZ_FILE = "base.json"
quiz = "QUIZ GAME"
font = "mono9"

##########################################################################################################
# FILES MANAGMENT


def load_data(filename: str, mode: str = "r", encoding: str = "utf-8") -> Dict[str, Any]:
    try:
        file_path = pl.Path(filename)
        if not file_path.exists():
            print("\nFile not found...")
            return {}
        with open(filename, mode, encoding=encoding) as file:
            data = json.load(file)
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
            if 0 <= value <= 1:
                print("\nValue must between (0/1)")
                continue
            if value == 0:
                return False
            return True
        except ValueError:
            print("\nInvalid entry -> Excepted (0/1)")


def number_input(text: str, minimum: int = 1) -> int:
    while True:
        try:
            value = int(input(text))
            if not value >= 1:
                print("\nInvalid entry -> Excepted [Value must be > 0])")
                continue
            return value
        except ValueError:
            print("\nInvalid entry -> Excepted integer value)")


def answer_input(text: str) -> str:
    return input(text).strip().lower()

##########################################################################################################
# FEATURES FONCTIONS


def play_game(data: Dict[str, Any], topic: str, difficulty: str) -> Any:
    score = 0
    copy_concern = deepcopy(data[topic][difficulty])
    packs = sample(copy_concern, len(copy_concern))
    recap_list = []
    for pack in packs:
        question = pack["question"]
        reponses = pack["reponses"]
        correct = pack["correct"]
        shuffle(reponses)
        # Print question
        print(question)
        # Display response
        display_responses(reponses)
        # Flat is better than nested
        while True:
            choice = number_input("Your answser... > ")
            answer = reponse_choice(reponses, choice)
            if answer is not None:
                break
            print(f"{choice} is invalid.....")
                

        is_correct = (answer == correct)
        if is_correct:
            score += 1
        recap = {
            "Questions": question,
            "Answers": answer,
            "Corrections": "--" if is_correct else correct
        }
        recap_list.append(recap)
    return score, recap_list


##########################################################################################################
# UTILS FUNCTIONS
def topic_choice(data: Dict[str, Any], choice: int) -> Any:
    topics: List[str] = list(data.keys())
    if 1 <= choice <= len(topics):
        return topics[choice - 1]
    return None


def difficulty_choice(data: Dict[str, Any], topic: str, choice: int) -> Any:
    difficulties: List[str] = list(data[topic].keys())
    if 1 <= choice <= len(difficulties):
        return difficulties[choice - 1]
    return None


def reponse_choice(res: List[str], choice: int) -> Any:
    if 1 <= choice <= len(res):
        return res[choice - 1]
    return None


def recapitulation(recap: Dict[str, Any]) -> None:
    print("\nRECAPITULATION\n",)
    table = tabulate(recap, headers="keys", tablefmt="pipe")
    print(table)


def score_mention(score: int, res: str = "") -> None:
    match score:
        case 5:
            res = "A"
        case 4:
            res = "B"
        case 3:
            res = "C"
        case 2:
            res = "D"
        case 1:
            res = "E"
        case _:
            res = "--"
    print(f"\n Score >>> {res}")
##########################################################################################################
# DISPLAY CLI FUNCTIONS


def welcome(quiz: str) -> None:
    render = figlet_format(quiz, font=font)
    print(render)


def display_topic(data: Dict[str, Any]) -> None:
    print("Available Topics:\n",)
    for i, v in enumerate(data, start=1):
        print(f"({i}) - {v}")


def display_difficulty(data: Dict[str, Any], topic: str) -> None:
    print("\nDifficulty stage:\n",)
    for i, v in enumerate(list(data[topic].keys()), start=1):
        print(f"({i}) - {v}")


def display_responses(res: List[str]) -> None:
    for i, v in enumerate(res, start=1):
        print(f"({i}) - {v}")
##########################################################################################################
# PROGRAM RUNTIME FUNCTION


def main() -> None:
    quiz_data: Dict[str, Any] = load_data(QUIZ_FILE)
    welcome(quiz)
    display_topic(quiz_data)

    while True:
        choice_topic = number_input("\nChoice topic's number (1-3) > ")
        topic = topic_choice(quiz_data, choice_topic)
        if topic == None:
            continue
        print(topic)
        display_difficulty(quiz_data, topic)
        choice_difficulty = number_input(
            "\nChoice difficulty's number (1-3) > ")
        difficulty = difficulty_choice(quiz_data, topic, choice_difficulty)
        if difficulty == None:
            continue
        print(difficulty)
        score, recap = play_game(quiz_data, topic, difficulty)

        score_mention(score)
        recapitulation(recap)
        break


##########################################################################################################
# EXECUTION
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nUser canceled the program by ctrl-c...\n")


# def play_game(data: Dict[str, Any], topic: str, difficulty: str) -> Any:
#     pointer, score = 0, 0
#     copy_concern= deepcopy(data[topic][difficulty])
#     pack = sample(copy_concern, len(copy_concern))
#     recap_list = []
#     while pointer < len(pack):
#         question = pack[pointer]["question"]
#         reponses = pack[pointer]["reponses"]
#         shuffle(reponses)
#         correct = pack[pointer]["correct"]
#         print(question)
#         display_responses(reponses)
#         choice = number_input("Your answser... > ")
#         res = reponse_choice(reponses, choice)
#         if res is None:
#             continue

#         is_correct = (res == correct)
#         if is_correct:
#              score += 1
#         recap = {
#                 "Questions": question,
#                 "Answers": res,
#                 "Corrections": "--" if is_correct else correct
#             }
#         recap_list.append(recap)
#         pointer += 1
#         if pointer == len(pack):
#             return score, recap_list
