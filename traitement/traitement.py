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
# ////////////////////////////////////////////////////////
if sys.arg[2] donc show input
else if not sys.argv[2] show input
<>
"""
from typing import List
import sys, os
import re
from collections import Counter


def readFromFile(file) -> str:
    if not os.path.exists(file):
        print("not exist")
        return
    with open(file, "r") as f:
        content = f.readline()
        return str(content)

def splitFormat(text: str, sep: str) -> List[str]:
    return re.split(sep, text)
    
def CountSentence(text: str) -> int :
    return len([sentence for sentence in splitFormat(text, r"\.") if sentence])

def CountWord(text: str) -> int : 
    return len([word for word in splitFormat(text, r"\s") if word])

def CountChar(text: str) -> int :
    return len([char for char in splitFormat(text, r"(.)") if char])
    

def main() -> None:
    filename = sys.argv[-1]
    text = readFromFile(filename)
    s = CountSentence(text)
    w = CountWord(text)
    c = CountChar(text)
    
    print(s,w,c)


if __name__ == "__main__":
    main()
