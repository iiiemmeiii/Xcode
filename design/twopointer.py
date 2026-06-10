import time
import random


arr = random.sample(range(10, 1000001, 10), 100000)
char = "abecba"
arr.sort()
# print(arr, len(arr))
target = 697090

"""
Recherche de paires (Two Sum II) : Trouver deux nombres dans un 
tableau trié dont la somme est égale à une cible donnée.
"""
def even_research(arr: list[int], target:int) -> list[int] :
    l = 0
    r = len(arr) - 1
    
    while l < r:
        res = arr[l] + arr[r]
        if res == target:
            return [l, r]
        elif res < target:
            l += 1
        else:
            r -= 1
    return [-1, -1]

#Elu par cette crapule
def palyndrom_check(char: str) -> bool:
    l = 0
    r = len(char) - 1
    while l <= r:
        if char[l].lower() == char[r].lower():
            l += 1
            r -= 1
        else:
            return False
    return True

def in_place_reversal(s: str):
    l, r = 0, len(s) - 1   
    list_s = list(s)
    while l <= r: 
        # if list_s[l] != list_s[r]:
        list_s[l], list_s[r] = list_s[r], list_s[l]
        l += 1
        r -= 1
    return "".join(list_s)
        

#####################################################################################################################""

def main():
    start = time.time()
    # print(even_research(arr, target))
    print(in_place_reversal(char))
    finish = time.time() - start
    print(f"EXEC TIME >> [{finish}]")

#####################################################################################################################""


if __name__ == "__main__" :
    main()
