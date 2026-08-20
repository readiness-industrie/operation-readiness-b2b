import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent


class PublicPageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.local_links = []
        self.canonical = None
        self.title_seen = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "a" and values.get("href", "").startswith("#"):
            self.local_links.append(values["href"][1:])
        if tag == "link" and values.get("rel") == "canonical":
            self.canonical = values.get("href")
        if tag == "title":
            self.title_seen = True


parser = PublicPageParser()
parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))
missing_targets = sorted(target for target in parser.local_links if target and target not in parser.ids)
if missing_targets:
    raise SystemExit(f"Ancres publiques cassées : {missing_targets}")
if not parser.canonical or urlparse(parser.canonical).scheme != "https":
    raise SystemExit("Canonical HTTPS absent.")
if not parser.title_seen:
    raise SystemExit("Title public absent.")
robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
if "Sitemap:" not in robots or "Disallow: /" in robots:
    raise SystemExit("robots.txt empêcherait l'indexation ou n'expose pas le sitemap.")
ET.parse(ROOT / "sitemap.xml")
print("Site public inchangé : empreintes, JavaScript, ancres, canonical, robots et sitemap valides.")
