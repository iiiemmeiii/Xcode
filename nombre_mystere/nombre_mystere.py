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
            l: int = int(input("Choose level >>> "))
            if l not in (1, 2, 3):
                print("ENTER LEVEL BETWEEN (1 - 2 - 3) ")

                continue
            return l
        except ValueError:
            print("INVALID LEVEL: ONLY INTERGER NUMBER")


##########################################
def handle_guess_number_input() -> int:
    while True:
        try:
            g: int = int(input("Enter guess >>> "))
            return g
        except ValueError:
            print("ENTER INTEGER VALUE")


# Lien entre valid_level_input() et random_guess()
def random_guess(l: int) -> int:
    if l == 1:
        return random.randint(1, 50)
    elif l == 2:
        return random.randint(1, 100)
    elif l == 3:
        return random.randint(1, 1000)


def saveScoreFile(score: int):
    (filename, action) = ("score.txt", "w")

    try:
        with open(filename, action) as file:
            file.write(f"SCORE >>> {score} ATTEMPTS / 5")
    except Exception as e:

        (log, action) = ("log.txt", "w")
        with open(log, action) as logF:
            logF.write(f"Exception : \n{e}")


def menu():
    print(
        """
####### WELCOME TO GUESS GAME ########
CHOOSE LEVEL : 
    >>> 1 - EASY
    >>> 2 - MEDIUM
    >>> 3 - DIFFICULT

ENTER THE GUESS NUMBER >>>
YOU GET 5 LIVES
          """
    )


def main():
    menu()
    l: int = valid_level_input()  # Choose level
    label(l)
    rn: int = random_guess(l)  # random guess number by level
    print(rn)
    (life, attempts) = (5, 0)
    chance = life
    while True:
        g: int = handle_guess_number_input()
        ##########################################

        if life == 1 or g == rn:
            attempts += 1
            print("GAME END !!")

            print("Score = {0} / {1}".format(attempts, chance))
            saveScoreFile(attempts)
            break

        if g > rn:
            attempts += 1
            life -= 1
            print(f"{g} IS TOO LARGE")
            print(f"{attempts} ATTEMPTS")
            print(f"LEFT {life} LIFE\n")

            continue
        elif g < rn:
            attempts += 1
            life -= 1
            print(f"{g} IS TOO SMALL")
            print(f"{attempts} ATTEMPTS")
            print(f"LEFT {life} LIFE\n")
            continue


# >>>>>>>>> <<<<
if __name__ == "__main__":
    main()
