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
- Score final avec lettre (A, B, C, D, F)

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
from random import sample, shuffle, choice
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
def play_game(data: Dict[str, Any],topic: str, difficulty: str):
    pass
        
    

##########################################################################################################
# UTILS FUNCTIONS
def topic_choice(data: Dict[str, Any], choice: int) -> Any:
    topics: List[str] = list(data.keys())
    if 0 <= choice <= len(topics):
        return topics[choice - 1]
    return None


def difficulty_choice(data: Dict[str, Any], topic: str, choice: int) -> Any:
    difficulties: List[str] = list(data[topic].keys())
    if 0 <= choice <= len(difficulties):
        return difficulties[choice - 1]
    return None

def random_question(questions: List[str]) -> Any:
    return choice(questions)

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
        break


##########################################################################################################
# EXECUTION
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nUser canceled the program by ctrl-c...\n")
