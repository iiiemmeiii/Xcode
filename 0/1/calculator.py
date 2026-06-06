"""### Projet 1 — Calculatrice Classique

**Thème :** Mathématiques / Interface CLI

**Description :**
Crée une calculatrice interactive en ligne de commande. 
L'utilisateur entre deux nombres, choisit une opération (+, -, *, /, //, %, **), 
et le résultat s'affiche.

**Contraintes :**
- Gérer la division par zéro avec un message explicite
- Proposer à l'utilisateur de recommencer après chaque calcul
- Afficher un menu clair avec les opérations disponibles
- Utiliser au minimum 5 fonctions distinctes (une par opération + menu + boucle principale)

**Pistes de réflexion :**
- Comment Python gère-t-il les types `int` vs `float` lors d'une division ?
- Que se passe-t-il avec `//` sur des nombres négatifs ?
- Comment valider que l'entrée utilisateur est bien un nombre ?

---"""

from operations import parse_operators
from calculify import add, neg, mult, div, modulo, intdiv, square


def calculate(op: str, x: int, y: int) -> int | float:
    match op:
        case "**":
            return square(x, y)
        case "%":
            return modulo(x, y)
        case "/":
            return div(x, y)
        case "*":
            return mult(x, y)
        case "+":
            return add(x, y)
        case "-":
            return neg(x, y)
        case "//":
            return intdiv(x, y)
        case _:
            raise ValueError("UNKONW OPERATOR")


# analyser l'input et retourner un tuple de x, y et operand


def menu():
    print(
        """
    ## CALCULATOR ##
    [1] -> LUNCH CALCULATOR
    [2] -> EXIT CALCULATOR   
    
    EX: 1*5 , 9%2
    """
    )


def main():

    menu()
    
    while True:
        operation = input("Enter operation: ").strip()

        # Enter l'opéeration
        if operation.lower() == "exit":
            print("aurevoir")
            break

        try:
            x, op, y = parse_operators(operation)
            if op in ("//", "%", "/") and y == 0:
                raise ZeroDivisionError
            result = calculate(op, x, y)

        except ValueError:
            print(f"ERROR in Line  :  (number[operand]number) ")
        except ZeroDivisionError as e:
            print(f"ERROR in Line  :  {e} ")
        else:
            print(f"resultat: {result}")


if __name__ == "__main__":
    main()
