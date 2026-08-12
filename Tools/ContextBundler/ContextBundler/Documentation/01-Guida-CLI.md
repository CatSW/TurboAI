---
title: Guida CLI ContextBundler
copyright: © 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
author: IK0VCK
type: guide
product: Turbo-AI Tools
solution: ContextBundler
project: ContextBundler
version: 1.2
updated: 2026-08-12
---
# Guida CLI ContextBundler

## Sintassi

    dotnet run -- <rootPath> <inputFile.md> [outputFile.md] [--stdout] [--base64]

- `rootPath`: radice della solution/repo a cui sono relativi i path del bundle.
- `inputFile.md`: file di richiesta (context-request), elenco dei path/range da includere.
- `outputFile.md`: opzionale — file su cui scrivere il bundle generato.

## Modalità smart-ass (nessun argomento posizionale)

Se lanciato senza argomenti posizionali, il tool seleziona automaticamente il
file `context-request*.md` più recente nella directory corrente e genera
`context-out-<descrizione>.md`, dove `<descrizione>` è la parte del nome
successiva a `context-request-`.

## Formato di inputFile.md

Elenco di entry, una per riga:

    src/MyLibrary/Class1.cs                     -> intero file
    src/MyLibrary/Class1.cs:120-180             -> solo le righe 120-180
    src/MyLibrary/Class1.cs:63-82,133-152       -> più estratti non contigui dallo stesso file

Righe vuote, righe che iniziano con `#` e bullet (`-`, `*`) vengono ignorati/normalizzati.
Formato dettagliato dei path in [00-Indice-Documentazione.md](./00-Indice-Documentazione.md).

## Opzioni

### `--stdout`

Scrive il bundle su stdout invece che su file — utile per pipe (es. `| Set-Clipboard`).
I messaggi di stato vanno su stderr per non sporcare l'output.

### `--base64`

Scrive l'output finale (file o stdout) come stringa base64 del bundle, invece
del testo UTF-8. Compatibile con `--stdout`.

## Formato del bundle prodotto

Ogni file incluso è delimitato da:

    <<<FILE path="..." bytes="..." sha256="...">>>
    ...contenuto...
    <<<END FILE>>>

Il contenuto non subisce escaping di `<`/`>` (il meccanismo `[LT]`/`[GT]`
introdotto in v1.1 è stato rimosso in v1.2).

## Vedi anche

`00-Indice-Documentazione.md` per il formato di `context-request-<descrizione>.md`.
