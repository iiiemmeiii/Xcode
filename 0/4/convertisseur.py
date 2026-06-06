from typing import Dict, List, Callable

####################################################
# Formula base types
####################################################

func = Callable[[float], float]
subCatergories = Dict[str, func]
categories = Dict[str, subCatergories]
formulaTypes = Dict[str, categories]

####################################################
# Formula
####################################################

FORMULA_BASE: formulaTypes = {
    "Température": {
        "celsius": {
            "celsius - kelvin": lambda v: v + 273.15,
            "celsius - fahrenheit": lambda v: (v * 9 / 5) + 32,
        },
        "kelvin": {
            "kelvin - celsius": lambda v: v - 273.15,
            "kelvin - fahrenheit": lambda v: (v - 273.15) * 9 / 5 + 32,
        },
        "fahrenheit": {
            "fahrenheit - celsius": lambda v: (v - 32) * 5 / 9,
            "fahrenheit - kelvin": lambda v: (v - 32) * 5 / 9 + 273.15,
        },
    },
    "Masse": {
        "kg": {
            "kg - livre": lambda v: v * 2.20462,
            "kg - gramme": lambda v: v * 1000,
        },
        "livre": {
            "livre - kg": lambda v: v / 2.20462,
            "livre - gramme": lambda v: v / 2.20462 * 1000,
        },
        "gramme": {
            "gramme - kg": lambda v: v / 1000,
            "gramme - livre": lambda v: v / 1000 * 2.20462,
        },
    },
    "Distance": {
        "km": {
            "km - miles": lambda v: v * 0.621371,
            "km - milles marins": lambda v: v / 1.852,
        },
        "miles": {
            "miles - km": lambda v: v / 0.621371,
            "miles - milles marins": lambda v: v / 1.15078,
        },
        "milles marins": {
            "milles marins - km": lambda v: v * 1.852,
            "milles marins - miles": lambda v: v * 1.15078,
        },
    },
}

####################################################
# Display Helper Methods ->>>>>>>>
####################################################
"""
Display categories (index. categorie)
"""


def title() -> None:
    print("=" * 40)
    print("CONVERTOR APPLICATION")
    print("=" * 40)


def displayCategories(categories: List[str]) -> None:
    for index, category in enumerate(categories, 1):
        print(f"\t{index}. {category}")


def categorieChoice(content: str, maxIndex: int) -> int:
    while True:
        try:
            entrie = int(input(f"{content} - (1-{maxIndex})  >>> "))
            if 1 <= entrie <= maxIndex:
                return entrie
            print(f"Entrer number between (1-{maxIndex})")

        except ValueError:
            print("Invalid Number - Retry")


def numberToConvert(content: str) -> float:
    while True:
        entrie = input(f"{content} >>> ")
        try:
            return float(entrie)
        except ValueError:
            print("Invalid Entrie - ex: 5.12 or 5 or 5.0 ")


####################################################
# Navigation Methods ->>>>>>>>
####################################################


def setCatergory() -> str:
    _categories = list(FORMULA_BASE.keys())
    print("\n --- Catergories ---")
    displayCategories(_categories)
    choice = categorieChoice("Your Category", len(_categories))
    return _categories[choice - 1]


def setSubCatergory(category: str) -> str:
    _subCategories = list(FORMULA_BASE[category].keys())
    print(f"\n --- Sub Catergories ({category}) ---")
    displayCategories(_subCategories)
    choice = categorieChoice("Your Sub Category", len(_subCategories))
    return _subCategories[choice - 1]


def setConversionUnit(category: str, subCategory: str) -> str:
    _conversion = list(FORMULA_BASE[category][subCategory].keys())
    print(f"\n--- Conversion Unit ({subCategory}) ---")
    displayCategories(_conversion)
    choice = categorieChoice("Your Conversion", len(_conversion))
    return _conversion[choice - 1]


def targetConversionFormula(
    category: str, subCategory: str, conversionUnit: str
) -> None:
    targetFormula = FORMULA_BASE[category][subCategory][conversionUnit]
    unit = conversionUnit.split("-")
    convertFrom, convertTo = unit[0].strip(), unit[-1].strip()
    print(f"\nConvert from [{convertFrom}] to [{convertTo}]")
    num = numberToConvert("Enter Number")
    result = round(targetFormula(num), 4)
    print(f"\nAnswer >>> {num} {convertFrom} = {result} {convertTo}")


def main() -> None:
    title()
    while True:
        try:
            category = setCatergory()
            subCategory = setSubCatergory(category)
            converionUnit = setConversionUnit(category, subCategory)
            targetConversionFormula(category, subCategory, converionUnit)

            print()
            replay = input("Replay (y/n) ? >>> ").strip().lower()

            if not replay == "y":
                print("\n\t GOODBYE !!! \n")
                break
        except KeyboardInterrupt:
            print("\n\n INTERRUPATION - GOODBYE !!! \n")
            break


if __name__ == "__main__":
    main()



