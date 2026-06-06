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
from typing import List, Tuple
import pyperclip as pc



def binary_input(text: str) -> bool:
    """_summary_
    function for asking input
    value : int(input)  -> 0 or 1
    Returns:
        bool(0) = False or bool(1) = True
    """
    while True:
        try:
            # convert input in int
            value = int(input(text))

            # if value is 0 or 1
            if value in (0, 1):
                 # return bool(0) = false or bool(1) = true
                return bool(value)
            
            print("Value must be 0 or 1")           
        
        # if is not and int number raiise exeception
        except ValueError:
            print("Not a number - retry")

def number_input(text: str, minimum_value: int = 1) -> int:
    """_summary_
    function for asking input
    value : int(input)
    value > minimum_value
    Returns:
        int(value)
    """
    while True:
        try:
            value = int(input(text))

            # if condition is true
            if value >= minimum_value:
                return value
            print(f"Input Value must be greather or equal to {minimum_value}")
        
        except ValueError:
            print("Not a number - retry")


def build_password_chars() -> Tuple[str, List[str]]:
    """_summary_
    function builts char contains in password
    based on binary input response
    Char must be :
        ascii_lowercase (and/or) ascii_uppercase (and/or) digits (and/or) punctuation

        if User choose an option (True)
            - add this option to chars
            - ensure that chars contains at least one char of this option
    Returns:
        tuple(chars: str, required_chars_per_choice:List[str])
    """

    chars: str = ""
    required_chars_per_choice = []

    choose_minus = binary_input("Choose lowercase char ? (0/1) >>> ")
    if choose_minus:
        chars += ascii_lowercase
        required_chars_per_choice.append(secrets.choice(ascii_lowercase))

    choose_majus = binary_input("Choose uppercase char ? (0/1) >>> ")
    if choose_majus:
        chars += ascii_uppercase
        required_chars_per_choice.append(secrets.choice(ascii_uppercase))

    choose_digits = binary_input("Choose digits char ? (0/1) >>> ")
    if choose_digits:
        chars += digits
        required_chars_per_choice.append(secrets.choice(digits))

    choose_punctuation = binary_input("Choose punctuation char ? (0/1) >>> ")
    if choose_punctuation:
        # add all punctuation to chars string
        chars += punctuation

        # select one of punctuation and add to array
        required_chars_per_choice.append(secrets.choice(punctuation))

    return chars, required_chars_per_choice


def generate_unique_password(length: int, chars: str, required_chars: List[str]) -> str:
    """_summary_
    Function generate unique secure password based on
    OS Entropie and Secrets module

    arg : length: int, chars: str, required_chars: List[str]

    if chars is empty  -> Error
    if lenght > len(required_chars_per_choice) -> Error


    Returns:
        str(password)

    """

    if len(chars) == 0:
        raise ValueError("Your Charset is Emply - Retry to chars")

    # [a, T, 1, :] = 3 and length = 2
    if len(required_chars) > length:
        raise ValueError("Insufficient length")

    # Copy array to keep safe the orginal array
    passwords_list = required_chars.copy()  # 4

    remaining_length = length - len(passwords_list)  # l = 10 -- 10 - 3 = 7

    passwords_list.extend(secrets.choice(chars) for _ in range(remaining_length))

    secrets.SystemRandom().shuffle(passwords_list)

    return "".join(passwords_list)


def evaluate_password_force(password: str):
    length = len(password)

    has_lower = any(char.islower() for char in password)
    has_upper = any(char.isupper() for char in password)
    count_digits = sum(char.isdigit() for char in password)
    count_punctuation = sum(char in punctuation for char in password)

    score: int = 0

    if length >= 8: # score = 1
        score += 1

    if length >= 12: # score = 1
        score += 1

    if length >= 16: # score = 1
        score += 1

    if has_lower: # score = 1
        score += 1

    if has_upper: # score = 1
        score += 1

    if count_digits >= 4: # score = 1
        score += 1

    if count_punctuation >= 5: # score = 1
        score += 1

    if score <= 2:
        return "Faible"
    if score <= 4:
        return "Moyen"

    if score <= 5:
        return "Fort"

    if score <= 7:
        return "Tres fort"


def generate_multiple_passwords(count: int, length: int, chars: str, required_chars: List[str]) -> List[str]:

    return [
        generate_unique_password(length, chars, required_chars) for _ in range(count)
    ]

def display_passwords(passwords: List[str]) -> None:
    
    for index, pwd in enumerate(passwords, start=1) :
        print(f"\t{index} - {pwd} >>> {evaluate_password_force(pwd)}")


def choose_password(passwords:List[str])  -> str:
    while True :
        choice = number_input(f"Choose betwen 1 and {len(passwords)}  >>> ")
        if choice <= len(passwords) :
            return passwords[choice - 1]
        print("Invalid Choice")
    


        
def copy_to_clipboard(password: str) -> None :
    choice = binary_input("Copy to clipboard ? (0/1) >>> ")
    
    if choice :
        print("Password copied")
        pc.copy(password)
    else :
       print("Password did not copy") 
    
    

# <>
def main() -> None:
    length = number_input("Set length >>> ")

    chars, required_chars = build_password_chars()
    if not chars  :
        print("chars vide")
        return

    count = number_input("How many password generate ? >>> ")
    x = generate_multiple_passwords(
        count=count, length=length, chars=chars, required_chars=required_chars
    )
    
    display_passwords(x)
    
    g = choose_password(x)
    
    copy_to_clipboard(g)

    # print()


if __name__ == "__main__":
    main()


