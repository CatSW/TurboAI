---
title: Piano Multi-Task turbo-ai
solution: TurboAI
release_target: TurboAI v1.0 - to be continued
as_of: 2026-08-12
status: IN_PROGRESS
workflow: TDM 1.0
---

# TurboAI - Piano multi-task supporto copilot

## 1. Obiettivo

Supporto a Copilot 365.

## 2. Decisioni vincolanti

### 2.1 Delimitazione dei file nel bundle

Ripristinare la versione 1.0

```
<<<FILE path="..." bytes="..." sha256="...">>>
...contenuto...
<<<END FILE>>>
```

### 2.2 Escaping

Ripristinare uso invariato dei caratteri < e > al posto delle sequenze [LT] e [GT] introdotte nel tentativo della 1.1

### 2.3 Preservare test su Golden Files XML

Il test per il caso XML aggiunto nella 1.1 deve essere mantenuto ma aggiornarlo al formato della 1.0

## 5. Milestone e task

### M1 - Ripristino funzionalità 1.0

**Obiettivo:** ripristinare il formato definito nella versione 1.0.

#### T1.1 - ripristino fence

#### T1.2 - ripristino < e >

Ripristinare uso invariato dei caratteri < e > al posto delle sequenze [LT] e [GT] introdotte nel tentativo della 1.1
<next_task>
### M2 - supporto output base64 opzionale

#### T2.1 - aggiungere gestione passaggio opzione generazione output finale in formato base64

#### T2.2 - implementare generazione base64 da richiamare se opzione attiva
</next_task>
Riferimento implementativo: tool standalone già testati e usati sul canale Copilot 365 (`.catsw-utility/artifacts/file-to-base64.py`, `base64-to-file.py`). Una volta integrata l'opzione nel tool, i due script standalone non sono più necessari operativamente ma restano in `artifacts/` come riferimento.

#### T2.3 - implementare nuovi test di verifica nuova funzionalità opzione output base64

### M3 - rilascio nuova versione

#### T3.1 - aggiornare versione 1.3.0.0 con compilazione AOT e copia del nuovo exe nella .catsw-utility del progetto TurboAI

#### T3.2 - aggiornare il Changelog

#### T3.3 - aggiornare documentazione

#### T3.4 - aggiornare skill (skill-uso-tools.md e dipendenze) per riflettere i path in .ai-context

#### T42 - Piano Completato

- Guru Meditation
- chiedere all'utente di creare un nuovo piano di esecuzione
