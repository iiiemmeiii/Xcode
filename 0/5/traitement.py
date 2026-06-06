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
            return f.read()  
    except FileNotFoundError:
        print(f"{file} not found - verifiy filename")
        return
    


def extract_words(words) -> List[str]:
    return re.findall(r"\b\w+\b", words)


def CountSentence(text) -> int:
    return len([s for s in re.split(r"[!.?]", text)  if s.strip()])


def CountWord(words) -> int:
    return len(words)


def CountChar(text) -> int:
    return len(text)

def ReccurentWord(words) -> dict:
    return Counter(words).most_common(5)
    
        

def MostWordLength(words) -> str:
    return max(words, key=len) 

def TableASCII(text: str) -> None :
    print(f"+{"-"*15}+{"-"*15}+{"-"*15}+{"-"*20}+{"-"*40}+")
    print(f"|{"Phrases":>10}{"Mots":>16}{"Chars":>15}{"5 Current":>21}{"Longer":>25}{"|":>23}")
    print(f"+{"-"*15}+{"-"*15}+{"-"*15}+{"-"*20}+{"-"*40}+")
    
    words = extract_words(text)
    
    s = CountSentence(text)
    w = CountWord(words)
    c = CountChar(text)
    rw = ReccurentWord(words)
    mw = MostWordLength(words)
    
    freq = ", ".join([f"{k}({v})" for k,v in rw])
    
    print(f"|{s:>5}{w:>20}{c:>15}{freq:>50}{mw:>40}")
    
        
    


def main() -> None:
    
    args = sys.argv
    if len(args) == 2:
        filename = sys.argv[-1]
        text = readFromFile(filename)
    else :
        text = input("Enter your text: ").strip().lower()
        
    TableASCII(text)    

if __name__ == "__main__":
    main()
