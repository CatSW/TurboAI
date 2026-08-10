#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0

import sys
import os
from pathlib import Path

# __file__ è in .catsw-utility/artifacts/switch-skill.py
# .resolve().parent.parent punta a .catsw-utility/
BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
SKILLSETS_DIR = DOCS_DIR / "tool-skillsets"
TARGET_FILE = DOCS_DIR / "skill-uso-tools.md"


def load_options():
    """Carica dinamicamente tutte le skill .md da tool-skillsets."""
    options = [("Nessuna selezione (Seleziona una skill sotto)", None)]

    if not SKILLSETS_DIR.is_dir():
        return options

    md_files = sorted(SKILLSETS_DIR.glob("*.md"), key=lambda p: p.name.lower())
    for md in md_files:
        label = md.stem  # nome senza estensione
        options.append((label, md))

    return options


OPTIONS = load_options()


# Astrazione per la lettura cross-platform di un tasto in modalità raw
class KeyReader:
    def __init__(self):
        self.is_windows = os.name == 'nt'
        if not self.is_windows:
            import tty
            import termios
            self.tty = tty
            self.termios = termios

    def get_key(self):
        if self.is_windows:
            import msvcrt
            key = msvcrt.getch()
            if key in (b'\x00', b'\xe0'):
                key = msvcrt.getch()
                if key == b'H':
                    return 'UP'
                elif key == b'P':
                    return 'DOWN'
                return 'OTHER'
            elif key in (b'\r', b'\n'):
                return 'ENTER'
            return 'OTHER'
        else:
            fd = sys.stdin.fileno()
            old_settings = self.termios.tcgetattr(fd)
            try:
                self.tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == '\x1b':  # Sequenza di escape (es. Frecce)
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[':
                        ch3 = sys.stdin.read(1)
                        if ch3 == 'A':
                            return 'UP'
                        elif ch3 == 'B':
                            return 'DOWN'
                elif ch in ('\r', '\n'):
                    return 'ENTER'
                return 'OTHER'
            finally:
                self.termios.tcsetattr(fd, self.termios.TCSADRAIN, old_settings)


key_reader = KeyReader()


def render_menu(selected_idx):
    # Pulisce la console in modo cross-platform (Sequenza ANSI universale)
    print("\033[H\033[J", end="")
    print("=== SELEZIONE SKILL TOOL ===\n")
    print(f"Sorgente: {SKILLSETS_DIR}\n")
    print("Usa le frecce SU/GIÙ e premi INVIO per confermare:\n")

    for idx, (label, _) in enumerate(OPTIONS):
        prefix = " [*] " if idx == selected_idx else " [ ] "
        print(f"{prefix}{label}")
    print()


def get_menu_choice():
    if len(OPTIONS) <= 1:
        raise FileNotFoundError(
            f"Nessun file .md trovato in:\n  {SKILLSETS_DIR}\n"
            "Aggiungi almeno un file .md nella cartella tool-skillsets."
        )

    selected_idx = 0
    while True:
        render_menu(selected_idx)
        action = key_reader.get_key()

        if action == 'UP':
            selected_idx = max(0, selected_idx - 1)
        elif action == 'DOWN':
            selected_idx = min(len(OPTIONS) - 1, selected_idx + 1)
        elif action == 'ENTER':
            if selected_idx == 0:
                print("\n⚠️  Devi selezionare una skill valida! Spostati in basso con le frecce.")
                print("Premi INVIO per riprovare...")
                while key_reader.get_key() != 'ENTER':
                    pass
            else:
                return OPTIONS[selected_idx][1]  # Path del file selezionato


def process_switch(selected_path: Path):
    if not selected_path.exists():
        raise FileNotFoundError(f"File non trovato: {selected_path}")

    content = selected_path.read_text(encoding="utf-8")
    TARGET_FILE.write_text(content, encoding="utf-8")
    print(f"\n✅ Generato 'docs/skill-uso-tools.md' da [{selected_path.stem}].")


def main():
    try:
        selected = get_menu_choice()
        process_switch(selected)
    except Exception as e:
        print(f"\n❌ SI È VERIFICATO UN ERRORE:\n{e}\n")
        print("Premi INVIO per chiudere...")
        while key_reader.get_key() != 'ENTER':
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
