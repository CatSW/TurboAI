#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License.
"""Test writer per dogfooding di tw.py (TailWatch v2.0).

Scrive su 'test-tailwatch-target.txt' nella cartella corrente, in tre
scenari pensati per stressare esattamente i punti discussi nella review:

  1. Append incrementale con un carattere UTF-8 multi-byte ('e' accentata,
     2 byte: 0xC3 0xA8) spezzato deliberatamente tra due write() separati
     da una pausa piu' lunga del poll_interval di tw.py (0.35s). Se tw.py
     decodifica ogni chunk isolatamente, qui dovrebbe comparire un
     carattere di rimpiazzo (replacement char) al posto della lettera
     accentata: questo e' il test del rischio di mojibake segnalato
     nella review.
  2. Rewrite completo (truncate) con contenuto piu' lungo e diverso dal
     precedente: verifica il rilevamento standard del reset.
  3. Rewrite completo con un file molto corto (3 byte, sotto la soglia
     dei 64 byte usata per l'header): verifica che il confronto funzioni
     anche sotto quella soglia.

Uso:
  Terminale 1:  python tw.py test-tailwatch-target.txt 5
  Terminale 2 (stessa cartella):  python test-tw-writer.py

Osserva l'output di tw.py durante lo scenario 1: se compaiono caratteri
di rimpiazzo al posto di lettere accentate, il fix ha ancora il problema
di decodifica-per-poll segnalato nella review.
"""
import time
from pathlib import Path

TARGET = Path("test-tailwatch-target.txt")


def main():
    print("=== Scenario 1: append con carattere UTF-8 spezzato a meta' ===")
    TARGET.write_bytes(b"Avvio scrittura incrementale\n")
    time.sleep(1.0)

    with open(TARGET, "ab") as f:
        f.write(b"Prova caratteri accentati: caff")
        f.flush()
    time.sleep(0.6)  # pausa a META' del carattere multi-byte (0xC3 0xA8)

    with open(TARGET, "ab") as f:
        f.write(b"\xc3")
        f.flush()
    time.sleep(0.6)  # secondo byte scritto separatamente, ancora a meta' carattere

    with open(TARGET, "ab") as f:
        f.write(b"\xa8 buonissimo, cosi' come perche', gia', puo'.\n")
        f.flush()
    time.sleep(2.0)

    print("=== Scenario 2: rewrite completo con contenuto piu' lungo ===")
    nuovo_contenuto = (
        "Nuova run completa.\n"
        "Riga 1: dati diagnostici\n"
        "Riga 2: altri dati con accenti: e' a' o' u' i'\n"
        "Riga 2bis: e a o u i accentate: \u00e8 \u00e0 \u00f2 \u00f9 \u00ec\n"
        "Riga 3: fine run.\n"
    )
    TARGET.write_text(nuovo_contenuto, encoding="utf-8")
    time.sleep(2.0)

    print("=== Scenario 3: rewrite completo con file molto corto (<64 byte) ===")
    TARGET.write_text("OK\n", encoding="utf-8")
    time.sleep(2.0)

    print("Test completato.")
    print("Verifica nell'output di tw.py:")
    print("  - Scenario 1: nessun carattere di rimpiazzo sulla lettera accentata")
    print("  - Scenario 2 e 3: banner '[ NEW LOG DETECTED ]' a ogni rewrite")


if __name__ == "__main__":
    main()
