import random
from datetime import date
from typing import Tuple


def get_current_term() -> Tuple[int, int]:
    now = date.today()
    year = now.year
    month = now.month

    return (
        year - 1 if month < 8 else year,
        2 if 2 <= month < 8 else 1
    )


def get_term_before(term: dict) -> Tuple[int, int]:
    if term['term'] == 1:
        return term['year'] - 1, 2
    else:
        return term['year'], 1


def random_ipv6() -> str:
    return ':'.join(['fe80'] + [hex(random.randint(0, 0xffff))[2:] for _ in range(7)])
