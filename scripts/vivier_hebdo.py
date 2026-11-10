#!/usr/bin/env python3
"""Ajoute au vivier des libellés lus sur des pages publiques.

Ne qualifie pas, n'invente pas d'adresse, n'envoie rien.
Les noms listés dans prospection/exclus-connus.md sont ignorés.
"""

from __future__ import annotations

import html
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
EXCLUS = ROOT / "prospection" / "exclus-connus.md"
VIVIER = ROOT / "prospection" / "vivier.md"
UA = "ReadinessIndustry-vivier/1.0 (veille publique hebdomadaire)"
OISE_INDEX = "https://www.oise.gouv.fr/Actions-de-l-Etat/Environnement/Les-installations-classees/Par-arretes"
SOMME_2026 = "https://www.somme.gouv.fr/Actions-de-l-Etat/Environnement/ICPE/Base-des-arretes-prefectoraux/2026"
PREFIXES = {
    "ST", "CI", "MDA", "ACD", "OL", "APENREG", "APC", "APMD", "APABROG",
    "APS", "APMU", "APAUTO", "APLIQUIDATION", "APRECTIF", "APENR", "AIPEOL",
    "PE", "DONNER", "ACTE", "APMD", "APA",
}


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=45) as response:
        raw = response.read()
    return raw.decode("utf-8", errors="replace")


def strip_accents(value: str) -> str:
    table = str.maketrans("àâäéèêëïîôöùûüç", "aaaeeeeiioouuuc")
    return value.lower().translate(table)


def normalize(value: str) -> str:
    value = strip_accents(html.unescape(value))
    value = value.replace("\xa0", " ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def ignored_names() -> list[str]:
    if not EXCLUS.exists():
        return []
    text = EXCLUS.read_text(encoding="utf-8")
    match = re.search(r"```exclus\n(.*?)```", text, re.S)
    if not match:
        return []
    return [line.strip() for line in match.group(1).splitlines() if line.strip() and not line.strip().startswith("#")]


def is_ignored(label: str, names: list[str]) -> bool:
    norm = normalize(label)
    for name in names:
        token = normalize(name)
        if not token:
            continue
        if len(token) < 5:
            if re.search(rf"(^| ){re.escape(token)}( |$)", norm):
                return True
        elif token in norm:
            return True
    return False


def visible_text(page: str) -> str:
    page = re.sub(r"(?is)<script.*?>.*?</script>", " ", page)
    page = re.sub(r"(?is)<style.*?>.*?</style>", " ", page)
    page = re.sub(r"(?is)<[^>]+>", " ", page)
    page = html.unescape(page).replace("\xa0", " ")
    return re.sub(r"\s+", " ", page)


def somme_rows(page: str, source: str, names: list[str]) -> list[dict[str, str]]:
    rows = []
    seen = set()
    text = visible_text(page)
    pattern = re.compile(
        r"Soci[eé]t[eé]\s+(.+?)\s+-\s*[Cc]ommune\s+d(?:e\s+|['’])\s*([A-Za-zÀ-ÿ'’ \-]{3,50})"
    )
    for match in pattern.finditer(text):
        company = re.sub(r"\s+", " ", match.group(1)).strip(" -")
        city = re.sub(r"\s+", " ", match.group(2)).strip()
        city = re.split(r"\s+Arr", city)[0]
        city = re.sub(r"[\s\-–—]+$", "", city).strip(" -")
        if "AMIENS" not in strip_accents(city).upper() and "amiens" not in strip_accents(city):
            continue
        if is_ignored(company, names):
            continue
        key = normalize(company + " " + city)
        if key in seen:
            continue
        seen.add(key)
        rows.append({
            "source": source,
            "label": company,
            "city": city.title() if city.isupper() else city,
            "note": "Libellé lu sur la page des arrêtés. Pas une cible qualifiée.",
        })
    return rows


def oise_month_links(page: str) -> list[str]:
    links = re.findall(r'href="([^"]*Par-arretes/26-[^"]+)"', page)
    clean = []
    for link in links:
        if link.startswith("/"):
            link = "https://www.oise.gouv.fr" + link
        if link not in clean:
            clean.append(link)
    return clean[:2]


def oise_rows(page: str, source: str, names: list[str]) -> list[dict[str, str]]:
    rows = []
    seen = set()
    for href in re.findall(r'href="([^"]+\.pdf)"', page, re.I):
        filename = href.split("/")[-1]
        stem = re.sub(r"\.pdf$", "", filename, flags=re.I)
        parts = stem.split("_")
        if parts and parts[0].isdigit():
            parts = parts[1:]
        while parts and parts[0].upper() in PREFIXES:
            parts = parts[1:]
        label = " ".join(parts).strip()
        if len(label) < 4 or is_ignored(label, names):
            continue
        key = normalize(label)
        if key in seen:
            continue
        seen.add(key)
        if href.startswith("/"):
            href = "https://www.oise.gouv.fr" + href
        rows.append({
            "source": source,
            "label": label,
            "city": "",
            "note": "Nom issu du fichier d'arrêté, à confirmer dans le PDF. " + href,
        })
    return rows


def load_existing() -> dict[str, dict[str, str]]:
    if not VIVIER.exists():
        return {}
    text = VIVIER.read_text(encoding="utf-8")
    found = {}
    for line in text.splitlines():
        if not line.startswith("| 20"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        key = normalize(cells[1] + " " + cells[2] + " " + cells[3])
        found[key] = {
            "date": cells[0],
            "source": cells[1],
            "label": cells[2],
            "city": cells[3],
            "note": cells[4],
        }
    return found


def render(rows: list[dict[str, str]], failures: list[str], today: str) -> str:
    lines = [
        "# Vivier de libellés publics",
        "",
        "Fichier alimenté par `scripts/vivier_hebdo.py` et l'action du lundi.",
        "Une ligne est un libellé lu sur une page publique. Ce n'est pas une cible, pas une adresse, pas un mail.",
        "La Somme n'est retenue ici que pour les communes dont le nom contient Amiens.",
        "",
        f"Dernière lecture : {today}.",
        "",
        "| Première lecture | Source | Libellé | Commune | Note |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {date} | {source} | {label} | {city} | {note} |".format(**row)
        )
    if failures:
        lines.extend(["", "## Sources non lues ce jour", ""])
        for failure in failures:
            lines.append(f"- {failure}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    today = datetime.now(ZoneInfo("Europe/Paris")).date().isoformat()
    names = ignored_names()
    existing = load_existing()
    failures = []
    fresh: list[dict[str, str]] = []

    try:
        somme = fetch(SOMME_2026)
        fresh.extend(somme_rows(somme, SOMME_2026, names))
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        failures.append(f"Somme indisponible : {error}")

    try:
        index = fetch(OISE_INDEX)
        for month_url in oise_month_links(index):
            try:
                month = fetch(month_url)
                fresh.extend(oise_rows(month, month_url, names))
            except (urllib.error.URLError, TimeoutError, OSError) as error:
                failures.append(f"Oise indisponible ({month_url}) : {error}")
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        failures.append(f"Index Oise indisponible : {error}")

    merged = dict(existing)
    added = 0
    for row in fresh:
        key = normalize(row["source"] + " " + row["label"] + " " + row["city"])
        if key in merged:
            continue
        merged[key] = {
            "date": today,
            "source": row["source"],
            "label": row["label"].replace("|", "/"),
            "city": row["city"].replace("|", "/"),
            "note": row["note"].replace("|", "/"),
        }
        added += 1

    ordered = sorted(merged.values(), key=lambda item: (item["date"], item["label"]))
    VIVIER.parent.mkdir(parents=True, exist_ok=True)
    VIVIER.write_text(render(ordered, failures, today), encoding="utf-8")
    print(f"libellés au fichier : {len(ordered)} ; nouveaux : {added} ; échecs de lecture : {len(failures)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
