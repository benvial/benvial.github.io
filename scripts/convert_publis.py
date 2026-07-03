"""Convert publis/publis.bib to src/data/publications.json

Uses pybtex for proper LaTeX → Unicode conversion (accents, math, etc.)
Matches the original convert.py formatting: abbreviated first names,
italic titles, links with Dimensions badges.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIB_PATH = ROOT / "publis" / "publis.bib"
OUT_PATH = ROOT / "src" / "data" / "publications.json"


def _ensure_empty(msg=""):
    if msg:
        print(msg)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("[]")
    sys.exit(0)


try:
    from pybtex.database import parse_file
    from pybtex.richtext import Text
except ImportError:
    _ensure_empty("pybtex not installed. Writing empty publications.json")

if not BIB_PATH.exists():
    _ensure_empty(f"No {BIB_PATH} found. Writing empty publications.json")

bib_data = parse_file(str(BIB_PATH))

# Pre-compile regex for \href{url}{text} → text
HREF_RE = re.compile(r"\\href\s*\{[^}]*\}\{([^}]*)\}")


def enrich(s: str) -> str:
    r"""Convert LaTeX text to Unicode via pybtex. Handles \href, accents, math."""
    if not s:
        return ""
    s = str(s)  # ensure plain string (pybtex may return Text)
    # Handle \href: extract display text, discard URL
    s = HREF_RE.sub(r"\1", s)
    try:
        return str(Text.from_latex(s))
    except Exception:
        return s.replace("{", "").replace("}", "")


def format_authors(entry):
    """Abbreviated first names, full last names (matching original convert.py)."""
    authors = []
    for person in entry.persons.get("author", []):
        first = str(person.rich_first_names[0].abbreviate()) if person.rich_first_names else ""
        last = " ".join(str(p) for p in person.rich_last_names) if person.rich_last_names else ""
        authors.append({"first": enrich(first), "last": enrich(last)})
    return authors


def _format_persons(entry, role):
    """Abbreviated first names, full last names for any person role (editor, etc.)."""
    persons = []
    for person in entry.persons.get(role, []):
        first = str(person.rich_first_names[0].abbreviate()) if person.rich_first_names else ""
        last = " ".join(str(p) for p in person.rich_last_names) if person.rich_last_names else ""
        persons.append(f"{enrich(first)} {enrich(last)}")
    return persons


def make_pub(entry):
    fields = entry.fields
    editors = _format_persons(entry, "editor")
    return {
        "key": entry.key,
        "type": entry.original_type,
        "authors": format_authors(entry),
        "title": enrich(fields.get("title", "")),
        "journal": enrich(fields.get("journal", "")),
        "booktitle": enrich(fields.get("booktitle", "")),
        "volume": fields.get("volume", ""),
        "number": fields.get("number", ""),
        "pages": fields.get("pages", ""),
        "year": fields.get("year", ""),
        "doi": fields.get("doi", ""),
        "url": fields.get("url", ""),
        "school": enrich(fields.get("school", "")),
        "address": enrich(fields.get("address", "")),
        "note": enrich(fields.get("note", "")),
        "isbn": fields.get("isbn", ""),
        "editor": ", ".join(editors) if editors else enrich(fields.get("editor", "")),
        "howpublished": enrich(fields.get("howpublished", "")),
        "pubtype": fields.get("type", ""),
    }


CATEGORIES = {
    "Articles in international peer-reviewed journals":   {"type_filter": ["article"]},
    "Contribution to a book chapter":                      {"type_filter": ["book"]},
    "Proceedings of international peer-reviewed conferences": {"type": "inproceedings", "pubtype": "lecture comittee"},
    "International peer-reviewed conferences":             {"type": "inproceedings", "pubtype": "conference"},
    "National conferences and seminars":                   {"type": "inproceedings", "pubtype": "france"},
    "PhD thesis":                                          {"type_filter": ["phdthesis"]},
    "Software and codes":                                  {"type": "misc", "pubtype": "code"},
    "In preparation":                                      {"type": "misc", "pubtype": "prep"},
}

publications = []

for cat_name, filters in CATEGORIES.items():
    pubs = []
    for key, entry in bib_data.entries.items():
        pub = make_pub(entry)

        if "type_filter" in filters:
            if pub["type"] in filters["type_filter"]:
                pubs.append(pub)
        elif "type" in filters:
            if pub["type"] == filters["type"] and pub["pubtype"] == filters.get("pubtype", ""):
                pubs.append(pub)

    if pubs:
        publications.append({"category": cat_name, "items": pubs})

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUT_PATH.write_text(json.dumps(publications, indent=2, ensure_ascii=False))

total = sum(len(c["items"]) for c in publications)
print(f"Generated publications.json: {total} publications in {len(publications)} categories")
