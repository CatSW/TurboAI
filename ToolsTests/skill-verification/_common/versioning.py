#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0
"""
Ricava le versioni da registrare nei report a partire dal front-matter di
file esistenti, senza mai chiederle interattivamente:

- versione TurboAI: campo `versione-turbo-ai` nel front-matter di
  <TurboAiWorkingRoot>/.catsw-utility/README.md
- versione skill Canale B: campo `version` nel front-matter del file skill
  (tipicamente la copia fresca di skill-uso-tools.md messa in golden/ da
  `run_test.py setup`)

ASSUNZIONE DA CONFERMARE: il path esatto di .catsw-utility/README.md.
Se la versione TurboAI vive altrove, aggiorna solo TURBO_README_REL sotto.
"""

from __future__ import annotations

import re
from pathlib import Path

TURBO_README_REL = Path(".catsw-utility") / "README.md"
TURBO_VERSION_KEY = "versione-turbo-ai"
SKILL_VERSION_KEY = "version"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _read_frontmatter(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm


def get_turbo_version(turbo_ai_working_root: Path) -> str:
    """Legge 'versione-turbo-ai' dal front-matter di .catsw-utility/README.md.
    Ritorna stringa vuota se il file o il campo non ci sono (mai un'eccezione)."""
    readme = turbo_ai_working_root / TURBO_README_REL
    return _read_frontmatter(readme).get(TURBO_VERSION_KEY, "")


def get_skill_version(skill_file: Path) -> str:
    """Legge 'version' dal front-matter del file skill indicato.
    Ritorna stringa vuota se il file o il campo non ci sono (mai un'eccezione)."""
    return _read_frontmatter(skill_file).get(SKILL_VERSION_KEY, "")
