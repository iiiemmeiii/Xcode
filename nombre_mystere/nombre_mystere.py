# < pour >
import random


def label(l: str) -> str:

    if l == "1":
        return f"LEVEL {l} (GUESS BETWEEN 1 - 50)"
    elif l == "2":
        return f"LEVEL {l} (GUESS BETWEEN 1 - 100)"
    elif l == "3":
        return f"LEVEL {l} (GUESS BETWEEN 1 - 1000)"
    else:
        return f"{l} > INVALID LEVEL NUMBER | READ MENU"


def random_number(level: str) -> int:

    if level == "1":
        return random.randint(1, 50)
    elif level == "2":
        return random.randint(1, 100)
    elif level == "3":
        return random.randint(1, 1000)
    else:
        return 0


def validate_input(msg):
    while True:
        try:
            n = int(input(msg).strip())
            if n <= 0:
                raise ValueError
            return n
        except ValueError:
            print("Enter positive int numbr")


def main():

    score: int = 0
    life: int = 5
    trackScor = 0
    essai = 0
    while True:
        # Select Level      
        levelinput: str = input("choose level>>> ")
        
        # Display level
        r: str = label(levelinput)
        if not r == "1":
            continue
    
        print(r)
        
        # Generate random according to the level
        r = random_number(levelinput)
        print(f"RANDOM ==== {r}")
        # Enter guess
        while True :
            guess = validate_input("Enter guess >>> ")
            if life != 0:
                if guess > r :
                    life -= 1
                    trackScor += 0
                    essai += 1
                    print(f"{guess} IS TOO LARGE")
                    print(f"ATTEMPTS {essai}")
                    continue
                # Si guess sup à random number
                elif guess <  r :
                    life -= 1
                    score += 0
                    essai += 1
                    print(f"{guess} IS TOO SMALL")
                    print(f"ATTEMPTS {essai}")
                    continue
                else :
                    life -= 1
                    score += 1
                    essai += 1
                    print(f"{guess} CORRECT")
                    print(f"SCORE >  {score} / {essai}")
                    break
            if life == 0 and guess != r :
                print(f"GAME END")
                print(f"SCORE >>>>>>>>>  {score} / {essai} attempts")
                break
            
        break
            

if __name__ == "__main__":
    main()
