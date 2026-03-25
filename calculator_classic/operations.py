import re
from typing import List


OPERATORS: List[str] = ["//", "**", "%", "/", "*", "+", "-"]


def parse_operators(operation: str) -> tuple[int, str, int]:
    # Extraire et parser
    pattern = r"^(-?\d+)\s*(//|\*\*|[%/*+\-])\s*(-?\d+)$"
    m = re.match(pattern, operation.strip())
    if not m:
        raise ValueError
    (x, op, y) = (m.group(1)), m.group(2), int(m.group(3))

    return int(x), op, int(y)
