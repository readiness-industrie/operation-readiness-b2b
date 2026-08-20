#!/bin/sh
set -eu
sha256sum --check tests/public-site.sha256
node --check app.js
node --check simulation-data.js
python3 scripts/validate_public_site.py
