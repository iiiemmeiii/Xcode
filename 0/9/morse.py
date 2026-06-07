"""
**Thème :** Algo / morse / Son

**Description :**
développer un algorithme bidirectionnel capable de traduire du texte en signal sonore Morse (génération de bips)
**Contraintes :**
- Les codes morce seront donnés en format json 
- Saisie libre : L'utilisateur peut entrer n'importe quel texte (une lettre, un mot, une phrase ou un paragraphe).
- Lecture audio : Le programme joue les bips Morse correspondants au texte.
- Option de répétition : L'utilisateur peut choisir de rejouer le son et définir lui-même le nombre de répétitions souhaité.
- Historique automatique : Chaque traduction est sauvegardée dans un fichier texte selon ce format précis
    ex
    transcription 1
    Contenu : [Le texte d'origine]
    transcription morse : [Le résultat en points et traits].
    .
        # 1. All 26 English letters (A-Z)
        morse_letters = {
            'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',   'E': '.',
            'F': '..-.',  'G': '--.',   'H': '....',  'I': '..',    'J': '.---',
            'K': '-.-',   'L': '.-..',  'M': '--',    'N': '-.',    'O': '---',
            'P': '.--.',  'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
            'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',  'Y': '-.--',
            'Z': '--..'
        }

        # 2. Numbers 0-9
        morse_numbers = {
            '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
            '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.'
        }

        # 3. Common punctuation marks
        morse_punctuation = {
            '.': '.-.-.-',  # Point / Period
            ',': '--..--',  # Virgule / Comma
            '?': '..--..',  # Point d'interrogation / Question mark
            '!': '-.-.--',  # Point d'exclamation / Exclamation mark
            ':': '---...',  # Deux-points / Colon
            ';': '-.-.-.',  # Point-virgule / Semicolon
            '-': '-....-'   # Trait d'union ou Moins / Hyphen or Minus
        }

        # 4. Special characters
        morse_special = {
            "'": '.----.',  # Apostrophe
            '"': '.-..-.',  # Guillemet / Quotation mark
            '/': '-..-.',   # Barre oblique / Slash
            '(': '-.--.',   # Parenthèse ouvrante / Open parenthesis
            ')': '-.--.-',  # Parenthèse fermante / Close parenthesis
            '&': '.-...',   # Esperluette / Ampersand
            '=': '-...-',   # Égal / Equals sign
            '+': '.-.-.',   # Plus / Plus sign
            '_': '..--.-',  # Tiret bas / Underscore
            '@': '.--.-.',  # Arobase / At sign
            '$': '...-..-'  # Dollar sign
        }

"""
import pathlib
import json
import winsound
import time

# ""
# GLOBAL VARIABLE
filename = "morse_code.json"
file_text = "historique.txt"
# ""
# INPUT


def number_input(message: str, minimum: int = 1) -> int:

    while True:
        try:
            valeur = int(input(message))
            if valeur >= minimum:
                return valeur
            print(f"Veuillez entrer un nombre supérieur ou égal à {minimum}.")
        except ValueError:
            print("Entrée invalide. Veuillez saisir un nombre entier.")


def conformation(text: str) -> bool:
    while True:
        try:
            value: int = int(input(text))
            if not 0 <= value <= 1:
                continue
            if value == 1:
                return True
            return False
        except ValueError:
            pass


def text_input(text): return input(text).strip().upper()

# ""
# FILE HANDLE


def read_file(filename):
    with open(filename, "r") as file:
        return file.readlines()


def write_file(filename, arr, mode="w"):
    with open(filename, mode) as file:
        file.writelines(arr)


def historique(filename, value, transcript):
    # numero_transcrip = 0
    arr = []

    path = pathlib.Path(filename)

    if not path.exists():
        numero_transcrip = 1
    else:
        loader = read_file(filename)
        content_join = "".join(loader)
        numero_transcrip = content_join.count("Transcription") + 1

    his = f"Transcription {numero_transcrip}\n"
    his += f"Contenu > {value}\n"
    his += f"Traduction morse > {transcript}\n\n"

    write_file(filename, [his], mode="a")


def load_file(filename: str) -> dict:
    try:
        path = pathlib.Path(filename)
        if not path.exists():
            return None

        with open(filename, "r", encoding="utf8") as file:
            morce_code = json.load(file)
            return morce_code

    except json.JSONDecodeError:
        print("Erreur lors du chargement des données")


# ""
# HANDLE TRANSCRIPTION  fr: str, morse: str
def transcript_to_morce(text: str, alphabet: dict) -> str:
    split_text: list[str] = text.split(" ")
    final_sentence: list[str] = []
    for mot in split_text:
        morse: list[str] = []
        for char in mot:
            if char in alphabet:
                morse.append(alphabet[char])
        final_sentence.append("".join(morse))
    return " / ".join(final_sentence)


def convert_to_beeps(text: str, repetitions: str) -> None:
    freq = 800
    unit_time = 70

    dot_duration = unit_time
    dash_duration = unit_time * 3
    symbol_pause = unit_time / 1000
    word_pause = (unit_time * 7) / 1000
    for rep in range(repetitions):
    
        print(f"\n>>> [Lecture {rep + 1}/{repetitions}]")
        

        for char in text:
            if char == ".":
                winsound.Beep(freq, dot_duration)
                time.sleep(symbol_pause)
            elif char == "-":
                winsound.Beep(freq, dash_duration)
                time.sleep(symbol_pause)
            elif char == "/":
                time.sleep(word_pause)
        if rep < repetitions - 1:
            time.sleep(1.5)


# ""
# UTILS
def inialize_all_char(data: dict):
    categories = list(data.keys())
    french_to_morse = {}
    for category in categories:
        french_to_morse.update(data[category])
    morse_to_french = {v: k for k, v in french_to_morse.items()}
    return french_to_morse, morse_to_french


def main() -> None:
    morse_code = load_file(filename)
    fr, morse = inialize_all_char(morse_code)

    value = text_input("\nEntrer votre text >>> ")

    traduction_morse = transcript_to_morce(value, fr)
    print(f"\nRésultat en Morse :\n{traduction_morse}\n")
    historique(file_text, value, traduction_morse)

    repetitions = number_input("Combien de fois voulez-vous ? (Min 1) >>> ")

    convert_to_beeps(traduction_morse, repetitions)


if __name__ == "__main__":
    try :
        main()
    except KeyboardInterrupt :
        print("\nCanceled ....")
    
