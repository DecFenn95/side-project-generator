"""Loading, compatibility rules, and sampling for Domain x User x Mechanic."""

import json
import random
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

MAX_ATTEMPTS = 50


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return slug.strip("-")


def load(name: str):
    return json.loads(DATA_DIR.joinpath(f"{name}.json").read_text(encoding="utf-8"))


DOMAINS = load("domains")
USERS = load("users")
MECHANICS = load("mechanics")
TAGS = load("tags")


def is_distinct(domain: dict, user: dict) -> bool:
    """The domain must not restate the user. Always enforced, chaos included."""
    domain_slug = slugify(domain["domain"])
    if domain_slug == slugify(user["user"]):
        return False
    return domain_slug not in user["avoid_domains"]


def shares_theme(domain: dict, user: dict) -> bool:
    """The topic must be something this audience actually cares about."""
    return bool(set(domain["themes"]) & set(user["themes"]))


def is_supported(domain: dict, user: dict, mechanic: dict) -> bool:
    """The pairing must afford everything the mechanic needs to work."""
    return set(mechanic["requires"]) <= set(domain["affords"]) | set(user["affords"])


def compatible_users(domain: dict, chaos: bool = False) -> list[dict]:
    return [
        user
        for user in USERS
        if is_distinct(domain, user) and (chaos or shares_theme(domain, user))
    ]


def compatible_mechanics(domain: dict, user: dict, chaos: bool = False) -> list[dict]:
    if chaos:
        return list(MECHANICS)
    return [m for m in MECHANICS if is_supported(domain, user, m)]


def pick_triple(rng: random.Random, chaos: bool = False) -> tuple[dict, dict, dict]:
    """Draw a domain, user, and mechanic that work together.

    Rejection sampling rather than a precomputed matrix: the lists are small
    enough that this is instant, and adding an entry needs no rebuild step.
    Chaos mode drops the theme and capability rules but never the distinctness
    rule, so a domain can never be paired with the audience it names.
    """
    for _ in range(MAX_ATTEMPTS):
        domain = rng.choice(DOMAINS)
        users = compatible_users(domain, chaos)
        if not users:
            continue
        user = rng.choice(users)
        mechanics = compatible_mechanics(domain, user, chaos)
        if not mechanics:
            continue
        return domain, user, rng.choice(mechanics)

    # Nothing satisfied the rules in time. Fall back to a distinct pair so the
    # button always produces something.
    domain = rng.choice(DOMAINS)
    users = [user for user in USERS if is_distinct(domain, user)] or USERS
    return domain, rng.choice(users), rng.choice(MECHANICS)
