########## LEVEL ############################################################""
import random


def label(l: int):
    if l == 1:
        print(f"LEVEL {l} (RANDOM BETWEEN 1 - 50)")

    elif l == 2:
        print(f"LEVEL {l} (RANDOM BETWEEN 1 - 100)")

    elif l == 3:
        print(f"LEVEL {l} (RANDOM BETWEEN 1 - 1000)")


def valid_level_input() -> int:
    while True:
        try:
            l: int = int(input("Choose level: "))
            if l not in (1, 2, 3):
                print("ERROR 123 ")
                continue
            return l
        except ValueError:
            print("ValueError")


def handel_level():
    l = valid_level_input()
    label(l)


##########################################
def handle_guess_number_input() -> int:
    while True:
        try:
            g: int = int(input("Enter guess: "))
            return g
        except ValueError:
            print("guess valueroor")


# Lien entre valid_level_input() et random_guess()
def random_guess(l: int) -> int:
    if l == 1:
        return random.randint(1, 50)
    elif l == 2:
        return random.randint(1, 100)
    elif l == 3:
        return random.randint(1, 1000)


def main():
    l: int = valid_level_input() # Choose level
    label(l)
    rn: int = random_guess(l) # random guess number by level
    print(rn)
    (life, attempts) = (5, 0)
    print(f"outside {life}")
    chance = life
    while True:
        g: int = handle_guess_number_input()
        ##########################################
        
        if life == 0 or g == rn:
            print("GAME END !!")
            
            print("Score = {0} / {1}".format(attempts, chance))
            break
        
        if g > rn :
            attempts += 1
            life -= 1
            print(f"{g} IS TOO LARGE")
            print(f"{attempts} ATTEMPTS")
            print(f"LLEFT {life} LIFE")
            
            continue
        elif g < rn :
            attempts += 1
            life -= 1
            print(f"{g} IS TOO SMALL")
            print(f"{attempts} ATTEMPTS")
            print(f"LLEFT {life} LIFE")
            continue
            

# >>>>>>>>> <<<<
if __name__ == "__main__":
    main()


