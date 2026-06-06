def single_table(n: int, limit: int):
    for i in range(1, limit + 1, 1):
        print(f"{n:>2} * {i:>2}  = {n*i:>4}")


def complete_table(limit: int):
    for i in range(1, 11, 1):
        for g in range(1, limit + 1, 1):
            l = f"{i:>2} * {g:>2}  = {i*g:>4}"
            r = f"{i+1:>2} * {g:>2}  = {(i+1)*g:>4}"
            print(f"{l:<15} {r:<15}")
        print()


def adjust_table(n: int, limit: int):
    for i in range(1, limit + 1, 1):
        for g in range(1, 13, 1):
            l = f"{i} * {g:>2}  = {(i)*(g):>3}"

            if i + 1 <= n:
                r = f"{i+1:>10} * {g:>2}  = {(i+1)*(g):>3}"
                print(f"{l:<15} {r:<15}")
        print()


def isPositive(n):
    return n > 0


def getPositiveMod(n: int):
    while True:
        try:
            val = int(input(n))
            if not isPositive(val):
                print("Mode value must be positive")
                continue
            return val
        except ValueError:
            print("Enter valid digit positive number")


def menu():
    print(
        """
    MULTIPLICATION TABLE
    1 ->>> Mode Sigle
    2 ->>> Mode Complete
    3 ->>> Mode Ajust
    --------------------
    Ex: Mode 1 - (Entrer a number) >>>  
        Mode 2 - (Genrate complete TB between 1 - 10)
                Generating... 1 - 10
        Mode 3 - (Genrate TB between 1 - N) >>> 5 
                Generating... 1 - 5
        Mode 4 - exit 
          """
    )


def main():
    menu()
    while True:

        mode = input("Choose your mode (1 - 2 - 3 - 4) >>> ")

        if mode == "1":
            n = getPositiveMod("Enter single number >>> ")
            limit = getPositiveMod("Enter Limit  >>> ")
            single_table(n, limit)
        elif mode == "2":
            limit = getPositiveMod("Enter Limit  >>> ")
            complete_table(limit)
        elif mode == "3":
            n = getPositiveMod("Enter single number >>> ")
            limit = getPositiveMod("Enter Limit  >>> ")
            adjust_table(n, limit)
        elif mode == "4":
            print("exit...".upper())
            break
        else:
            print("Mode number incorrect >>>>>> read menu".upper())


if __name__ == "__main__":
    main()
