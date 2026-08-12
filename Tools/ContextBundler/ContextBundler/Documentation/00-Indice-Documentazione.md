---
title: Indice Documentazione ContextBundler
copyright: © 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
author: IK0VCK
type: index
product: Turbo-AI Tools
solution: ContextBundler
project: ContextBundler
version: 1.2
updated: 2026-08-12
---
# Indice Documentazione

## [01-Guida-CLI.md](./01-Guida-CLI.md)

Contiene la guida completa all'uso di ContextBundler da linea di comando, con:

- Sintassi del comando
- opzioni CLI (`--stdout`, `--base64`)
- modalità **smart-ass**
- formato del bundle prodotto.

## Formato del file da processare

Il file deve essere denominato `context-request-<descrizione>.md`.

Elenco puntuale di path relativi alla solution, uno per riga, che ContextBundler deve includere nel bundle.
Nessun wildcard, nessuna istruzione in linguaggio naturale: solo path esatti (verificati con list-files se non certi).
Si possono definire dei commenti iniziando la riga con `#`.
Righe vuote e righe con solo spazi/tab vengono ignorate.
non usare `-` o `*` come bullet, solo percorsi relativi alla solution.

### esempio di file di richiesta

```md
# Files to bundle
ContextBundler/Program.cs
ContextBundler/Constants/BundleFormatConstants.cs
.ai-context/Piano-Multi-Task.md
```

### estrazione di porzioni di file

Per estrarre solo alcune righe di un file invece del file intero, aggiungere
uno o più range dopo il path. Esempio con doppio range sullo stesso file:

```md
# Files to bundle
MyProject/Services/Exporter.cs:120-180,340-410
```
