"""
### Projet 5 — Analyse de Texte

**Thème :** Traitement de texte / Statistiques

**Description :**
L'utilisateur entre un texte (ou un nom de fichier `.txt`).
Le programme affiche :
    - nombre de mots,
    - de phrases,
    - de caractères,
    - les 5 mots les plus fréquents,
    - et le mot le plus long.

**Contraintes :**
- Ignorer la casse (traiter "Python" et "python" comme le même mot)
- Ignorer la ponctuation lors du comptage des mots
- Afficher les résultats dans un tableau formaté en ASCII
- Accepter le texte via saisie directe ou via un fichier en argument (`sys.argv`)

**Pistes de réflexion :**
- Comment nettoyer une chaîne de ses caractères spéciaux ?
- Explore le module `collections.Counter`
- Qu'est-ce que `sys.argv` et comment l'utiliser ?
<>
"""

from typing import List
import sys, os
import re
from collections import Counter


def readFromFile(file) -> str:   
    try :      
        with open(file, "r") as f:
            # strip supprime le \n final au bout de la ligne
            return f.readline().rstrip("\n")   
    except FileNotFoundError:
        print(f"{file} not found - verifiy filename")
        return
    


def splitText(text: str, sep: str) -> List[str]:
    return [item for item in re.split(sep, text) if item]


def CountSentence(text: str) -> int:
    return len(splitText(text, r"\."))


def CountWord(text: str) -> int:
    return len(splitText(text, r"\s"))


def CountChar(text: str) -> int:
    return len(splitText(text, r"(.)"))

def ReccurentWord(text: str) -> List[tuple]:
    listWord = dict(Counter(splitText(text, r"\s")).most_common(5))
    reccurent = []
    for k, v in listWord.items() :
        reccurent.append((k,v))
    return reccurent
        

def MostWordLength(text: str) -> str:
    listWord = splitText(text, r"\s")
    maxLength =  max(len(w) for w in listWord)
    word = "".join([word for word in listWord if len(word) == maxLength])
    return word




def main() -> None:
    filename = sys.argv[-1]
    text = readFromFile(filename)
    s = CountSentence(text)
    w = CountWord(text)
    c = CountChar(text)
    rw = ReccurentWord(text)
    mw = MostWordLength(text)
    print(s, w, c, rw, mw)
   


if __name__ == "__main__":
    main()
