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

123456              # Trop court, que des chiffres
motdepasse          # Mot du dictionnaire
password123         # Mot commun + chiffres
azerty              # Motif clavier
01/01/1990          # Date de naissance
monchienRex         # Info personnelle + nom animal
Password123!        # Mot commun + chiffres + spécial (trop prévisible)
Minimum absolu	12 caractères
Recommandé	16 caractères
Très sécurisé	20+ caractères
Ultra sécurisé (clés)	32+ caractères

<h1>
"""
from string import ascii_lowercase, ascii_uppercase, digits, punctuation, Formatter
import secrets, random
from typing import Callable, Any, List

fmt : Callable[[str, Any], List[Any]] = lambda text, *args : Formatter().format(text, args)

# fmt = Formatter().format

def question(text) -> str :
    while True :
        r = input(text).strip().lower()
        if not r in ("o", "n") :
            print(fmt("{} Answer Expected : \"o\" or  \"n\" - retry", r))
            continue
        return r
        

def setNumber(text) -> int :
    while True:
        try :
            n = int(input(text))
            if n > 0 :
                return n
            print(fmt("Must be greather 0"))
        except ValueError:
            print(fmt("Not a number - retry"))
       
        
def def_longureur(choix: str, text: str ) -> int :
    if choix == "o":
        n = setNumber(text)
        return n
    return random.randint(4, 20)

def def_minuscule(l:int, choix: str) -> str:
    if choix == "o" : 
        return "".join(secrets.choice(ascii_lowercase) for _ in range(l))
    return ""
        
    
def def_majiscule(l:int, choix: str, minus: str) -> str: 
    if choix == "o" :
        return "".join(secrets.choice(f"{ascii_uppercase}{minus}") for _ in range(l))
    return ""
        
    
def def_digit(l:int, choix: str, minus: str, majus: str) -> str: 
    if choix == "o" :
        return "".join(secrets.choice(f"{minus}{digits}{majus}") for _ in range(l))
    return ""
    
        
    
def def_symbol(l:int, choix: str, minus: str, majus: str, digit: str) -> str: 
    if choix == "o" :
        return "".join(secrets.choice(f"{punctuation}{digit}{minus}{majus}") for _ in range(l))
    return ""
    
        
    


def main() -> None :
    a = ""
    while True:
        ql = question("Definir Longueur (o or n) : ")
        
        l = def_longureur(ql, "Votre longueur : ")
        
        qm = question("Definir Minnuscule (o or n): ")  
        minus = def_minuscule(l, qm)
        
        qmaj = question("Definir Majuscule (o or n): ")  
        maj = def_majiscule(l,qmaj, minus)
        
        qdigit = question("Definir digits (o or n): ")  
        digit = def_digit(l, qdigit, minus, maj)
        
        qponc = question("Definir Ponctuation (o or n): ")  
        ponc = def_symbol(l, qponc, minus, maj, digit)
        
        a += ponc
        
        break
    print(a)
        

if __name__ == "__main__" :
    main()

