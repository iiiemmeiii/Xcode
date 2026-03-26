**Solution: Calculatrice Classique**

## Fichier principal

- calculator.py

"""
from operations import parse_operators
from calculify import add, neg, mult, div, modulo, intdiv, square
import traceback


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

            
            

def main():
    print(
        """
          ## CALCULATOR ##
          [1] -> LUNCH CALCULATOR
          [2] -> EXIT CALCULATOR   
          
          EX: 1*5 , 9%2
          """
    )
    
    

    while True:
        operation = input("Enter operation: ").strip()

        # Enter l'opéeration
        if operation.lower() == "exit":
            print("aurevoir")
            exit(1)
        
        try:
            x, op, y = parse_operators(operation)
            if op in ("//", "%","/") and y == 0 :
                raise ZeroDivisionError("")
            result = calculate(op, x, y)
            
        except ValueError:
            print(f"ERROR in Line  :  (number[operand]number) ")
            print(traceback.format_exc())
        except ZeroDivisionError as e:
            print(f"ERROR in Line  :  {e} ")
            print(traceback.format_exc())
        else:
            print(f"resultat: {result}")


15


if __name__ == "__main__":
    main()
"""

## MODULE 1: operation.py

"""
import re
from typing import List


OPERATORS: List[str] = ["//", "**", "%", "/", "*", "+", "-"]


def parse_operators(operation: str) -> tuple[int, str, int]:
    # Extraire et parser
    for operator in OPERATORS:
        print(f"operator: {operator}\nopertion input: {operation}")
        pattern = r"^(-?\d+)\s*(//|\*\*|[%/*+\-])\s*(-?\d+)$"
        m = re.match(pattern, operation.strip())
        if not m:
            raise ValueError("UNKONW OPERATOR")

        return (int(m.group(1)), m.group(2), int(m.group(3)))
    
       
        

"""

## MODULE 2: calculify.py

"""
add = lambda x, y: x + y
neg = lambda x, y: x - y
div = lambda x, y: x / y
mult = lambda x, y: x * y
square = lambda x, y: x ** y
modulo = lambda x, y: x % y
intdiv = lambda x, y: x // y

"""

2 - Lors de la division meme si les 2 nombres sont entier
la resultat est toujours float

3 - il arrondi au nombre negatif inférieur

4 - Parser avec int et mettre un try except pour attraper les erreurs