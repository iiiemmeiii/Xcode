import random
import os

RANGES = {1: 50, 2: 100, 3: 1000}


def getScoreFileByLevel(level: int) -> int:
    return f"score_level_{level}"


def getBestFromScoreFile(level: int) -> int | None:
    filename = getScoreFileByLevel(level)
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, "r") as file:
            # current_best_score > 1
            content = file.read().strip()
            # return score cast in integer if there is content in score file
            return int(content.split(">")[-1]) if content else None
    except (Exception, IOError):
        return None


"""Ecrire le fichier de score"""


def setBestScoreFile(newscore: int, level: int) -> bool:
    filename = getScoreFileByLevel(level)
    # write file if new best score or score file content None
    # car plus le score est petit plus il est meilleurs
    best_score: int = getBestFromScoreFile(level)
    if best_score is None or newscore < best_score:
        try:
            with open(filename, "w") as file:
                file.write(f"current_best_score > {newscore}")
            return True
        except Exception:
            return False
    return False


def menu():
    print(
        """
####### WELCOME TO GUESS GAME ########
CHOOSE LEVEL :
    >>> 1 - EASY -> (1 - 50) 
    >>> 2 - MEDIUM -> (1 - 100) 
    >>> 3 - DIFFICULT -> (1 - 1000) 
        """
    )


def getLevelEntry() -> int:
    while True:
        try:

            level = int(input("Votre choix >>> "))
            if level in RANGES:
                print(
                    f"\nNiveau {level} : trouver un nombre entre 1 et {RANGES[level]}"
                )
                return level
            print("Veuillez choisir 1, 2 ou 3.")
        except:
            print("Veuillez entrer un nombre valide")


def getGuess(max: int) -> int:
    while True:
        try:
            guess = int(input("Entrer votre nombre >>> "))
            if 1 <= guess <= max:
                return guess
            print(f"votre nombre doit entre comprise entre 1 et {max}")
        except ValueError:
            print("Enter un nombre entier valid")


# def give_strategic_tip(attempts: int, level: int) -> None:
#     """Affiche un conseil sur la stratégie dichotomique à la première tentative."""
#     if attempts == 1:
#         mid = RANGES[level] // 2
#         print(f"\n💡 ASTUCE : La stratégie optimale est la dichotomie.")
#         print(f"   Commencez par {mid} pour éliminer 50 % des possibilités !")


def play(level, max, secret_number):
    attempts: int = 0
    while True:
        # Entrer le nombre deviné
        guess = getGuess(max)

        # A chaque iteration de la boucle incrementé, la tentative de 1 et l'afficher
        attempts += 1
        print(f"\nTentative : {attempts}")

        if guess < secret_number:
            print(f"[{guess}] est TROP PETIT!")
            continue
        elif guess > secret_number:
            print(f"[{guess}] est TROP GRAND!")
            continue
        else:
            print(f"\n🎉 BRAVO ! Vous avez trouvé le nombre {secret_number} !")
            print(f"📊 Nombre de tentatives : {attempts}")

            isSaveScore = setBestScoreFile(attempts, level)

            if isSaveScore:
                print(f"✨ NOUVEAU MEILLEUR SCORE ! {attempts} tentatives ✨")
            break


def setReplay() -> bool:
    while True:
        try:
            print(
                """
        REPRENDRE LE JEU ? 
        1 >>> OUI   
        0 >>> NON   """
            )
            answer = int(input("Votre reponse ? "))
            if answer not in (0, 1):
                print(" choisir 1 > OUI | 0 > OUI")
                continue
            if answer == 1:
                return True
            return False
        except:
            print("Choix erroné : lire indication")


def main():
    # Choix du niveau d'abord pour afficher le bon meilleur score
    while True:
        menu()
        level = getLevelEntry()

        bestscore = getBestFromScoreFile(level)

        if bestscore is not None:
            print(f"🏆 MEILLEUR SCORE (niveau {level}) : {bestscore} tentative(s)\n")
        else:
            print(f"🏆 Aucun nouveau meilleurs score1\n")

        # il n'y a que max car elle est dynamique dans le range, le min est constant
        x, maxi = 1, RANGES[level]
        secret_number = random.randint(x, maxi)
        print(f"secret : {secret_number}")
        play(level, maxi, secret_number)
        if not setReplay():
            break
        continue


# >>>>>>>>> <<<<
if __name__ == "__main__":
    main()
