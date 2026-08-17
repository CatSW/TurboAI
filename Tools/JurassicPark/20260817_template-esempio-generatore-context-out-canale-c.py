from pathlib import Path
# Contenuto del bundle context-out da generare dall'LLM - questo è un esempio !
# il nome del file da gnerare davvero deve essere `context-out-<descriozione>.md` con descrizione opportuna !
CONTEXT_OUT_CONTENT = r"""# CONTEXT BUNDLE
# BundleFormatVersion: 3
# ContextBundler V1.3.0.0
# Generated: 2026-08-17 18:00:00
<<<FILE path="mela/prova_mela.txt" bytes="19" sha256="d0408544a4d6f857bf308c0efee69cae197d197f22312d8a0d481bb2d63f0d2c">>>
Ciao, sono una mela.
<<<END FILE>>>
<<<FILE path="pera/pera.txt" bytes="18" sha256="4d7dbcb3eeefbe7dd2c9f8749f7e411b7d8bf3faef1b2c4e25a25b15a4b771e7">>>
Ciao, sono una pera.
<<<END FILE>>>
"""
def main():
    # Percorso di output nella directory corrente
    output_path = Path("context-out-test.md")
    # Scrittura atomica in UTF-8 con newlines LF
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(CONTEXT_OUT_CONTENT.strip() + "\n")
    print(f"File '{output_path}' generato con successo in formato UTF-8 (LF)!")
if __name__ == "__main__":
    main()