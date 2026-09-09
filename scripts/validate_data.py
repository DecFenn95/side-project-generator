"""Check the data files for schema errors, unknown tags, collisions, and orphans.

Run with `python scripts/validate_data.py`. Exits non-zero on any error.
"""

import sys
from collections import Counter
from difflib import SequenceMatcher
from itertools import combinations
from os.path import commonprefix
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import combos

THEMES = set(combos.TAGS["themes"])
CAPABILITIES = set(combos.TAGS["capabilities"])

# How alike two names may be before they are probably the same idea twice. Set
# high because a shared root is the reliable signal and spelling alone is not:
# Pet Sitters and Career Switchers are unrelated but score well on letters.
SIMILARITY = 0.85
# Shortest shared word prefix that counts as the same root, which catches
# Freelance in Freelancers and Garden in Gardeners and Gardening, while leaving
# Home in Homeowners and Homebrewers alone.
STEM_LENGTH = 6

errors: list[str] = []
warnings: list[str] = []


def words(name: str) -> list[str]:
    return combos.slugify(name).split("-")


def distinguishing(name: str, common: set[str]) -> list[str]:
    """The words that set this name apart from the rest of the lists.

    Category words like Workers, Residents, and Households recur across whole
    families of deliberately parallel entries, so comparing on them reports
    every family member against every other. Dropping them leaves the words
    that actually carry the meaning, and returns nothing at all for a name
    built entirely from shared words, such as Family History.
    """
    return [word for word in words(name) if word not in common]


def shares_root(words_a: list[str], words_b: list[str]) -> bool:
    return any(
        len(commonprefix([word_a, word_b])) >= STEM_LENGTH
        for word_a in words_a
        for word_b in words_b
    )


def looks_alike(name_a: str, name_b: str, common: set[str]) -> bool:
    words_a = distinguishing(name_a, common)
    words_b = distinguishing(name_b, common)
    if words_a and words_b:
        if shares_root(words_a, words_b):
            return True
    else:
        # One of them is made only of words other entries also use, so a shared
        # root proves nothing. Family History and Local History share History
        # and mean different things. Fall back to comparing the whole names.
        words_a, words_b = words(name_a), words(name_b)
    ratio = SequenceMatcher(None, "-".join(words_a), "-".join(words_b)).ratio()
    return ratio >= SIMILARITY


def check_entries(entries: list[dict], key: str, tag_fields: dict[str, set]) -> None:
    seen = set()
    for entry in entries:
        name = entry.get(key)
        if not name:
            errors.append(f"{key}: entry missing its '{key}' field: {entry}")
            continue
        if not entry.get("description"):
            errors.append(f"{key} '{name}': missing description")
        if name in seen:
            errors.append(f"{key} '{name}': listed twice")
        seen.add(name)
        for field, vocabulary in tag_fields.items():
            values = entry.get(field)
            if values is None:
                errors.append(f"{key} '{name}': missing '{field}'")
                continue
            unknown = set(values) - vocabulary
            if unknown:
                errors.append(f"{key} '{name}': unknown {field} {sorted(unknown)}")


def check_collisions() -> None:
    named = (
        [("domain", e["domain"]) for e in combos.DOMAINS]
        + [("user", e["user"]) for e in combos.USERS]
        + [("mechanic", e["mechanic"]) for e in combos.MECHANICS]
    )

    by_slug: dict[str, list[tuple[str, str]]] = {}
    for kind, name in named:
        by_slug.setdefault(combos.slugify(name), []).append((kind, name))
    for slug, group in by_slug.items():
        if len(group) > 1:
            where = ", ".join(f"{kind} '{name}'" for kind, name in group)
            errors.append(f"slug '{slug}' used by {where}")

    counts = Counter(word for _, name in named for word in set(words(name)))
    common = {word for word, count in counts.items() if count > 1}

    for (kind_a, name_a), (kind_b, name_b) in combinations(named, 2):
        if name_a != name_b and looks_alike(name_a, name_b, common):
            warnings.append(f"{kind_a} '{name_a}' looks like {kind_b} '{name_b}'")


def check_avoid_domains() -> None:
    slugs = {combos.slugify(entry["domain"]) for entry in combos.DOMAINS}
    for user in combos.USERS:
        for slug in user["avoid_domains"]:
            if slug not in slugs:
                errors.append(
                    f"user '{user['user']}': avoid_domains '{slug}' is not a domain"
                )


def check_orphans() -> None:
    """Every entry must appear in at least one valid triple."""
    live_domains: set[str] = set()
    live_users: set[str] = set()
    live_mechanics: set[str] = set()
    valid_pairs = 0

    for domain in combos.DOMAINS:
        for user in combos.compatible_users(domain):
            mechanics = combos.compatible_mechanics(domain, user)
            if not mechanics:
                continue
            valid_pairs += 1
            live_domains.add(domain["domain"])
            live_users.add(user["user"])
            live_mechanics.update(m["mechanic"] for m in mechanics)

    for entries, key, live in (
        (combos.DOMAINS, "domain", live_domains),
        (combos.USERS, "user", live_users),
        (combos.MECHANICS, "mechanic", live_mechanics),
    ):
        for entry in entries:
            if entry[key] not in live:
                errors.append(f"{key} '{entry[key]}': appears in no valid triple")

    total = len(combos.DOMAINS) * len(combos.USERS)
    share = valid_pairs / total if total else 0
    print(f"{valid_pairs} of {total} domain-user pairs are valid ({share:.0%})")


check_entries(combos.DOMAINS, "domain", {"themes": THEMES, "affords": CAPABILITIES})
check_entries(combos.USERS, "user", {"themes": THEMES, "affords": CAPABILITIES})
check_entries(combos.MECHANICS, "mechanic", {"requires": CAPABILITIES})
check_collisions()
check_avoid_domains()
check_orphans()

for warning in warnings:
    print(f"warning: {warning}")
for error in errors:
    print(f"error: {error}")

if errors:
    print(f"\n{len(errors)} error(s)")
    sys.exit(1)
print(f"\nok, {len(warnings)} warning(s)")
