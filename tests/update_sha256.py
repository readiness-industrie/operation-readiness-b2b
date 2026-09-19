import hashlib
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "simulation-data.js",
    "robots.txt",
    "sitemap.xml",
    "assets/favicon.svg",
    "assets/og-readiness.png",
    "assets/og-readiness.svg",
]
lines = []
for rel in FILES:
    data = (ROOT / rel).read_bytes()
    lines.append(f"{hashlib.sha256(data).hexdigest()}  {rel}")
(ROOT / "tests/public-site.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("updated tests/public-site.sha256")
