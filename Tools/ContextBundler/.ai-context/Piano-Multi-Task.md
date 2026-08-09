---
title: Piano Multi-Task turbo-ai
solution: TurboAI
release_target: TurboAI v1.0 - to be continued
as_of: 2026-08-09
status: COMPLETED
workflow: TDM 1.0
---

# TurboAI - Piano multi-task rilascio

## 1. Obiettivo

Questo è solo un esempio di piano. estrapolato da `C:\Repo\CatSW\TurboAI\Lab\Tools\ContextBundler\.ai-context\`

## 2. Decisioni vincolanti

### 2.1 Delimitazione dei file nel bundle

Ogni file incluso nel bundle è delimitato da marker espliciti di apertura e
chiusura (non un singolo header `## File:`), riportanti path, lunghezza in
byte e SHA-256 del contenuto sorgente. Il marker di chiusura è obbligatorio
anche per l'ultimo file del bundle. Formato indicativo:

```
<<<FILE path="..." bytes="..." sha256="...">>>
...contenuto...
<<<END FILE>>>
```

### 2.2 Escaping e Markdown

### 2.3 Encoding

### 2.4 Preservazione dei caratteri di controllo

### 2.5 Versionamento del formato

### 2.6 Compatibilità e retrocompatibilità

## 3. Scope

### Incluso

### Escluso

## 4. Strategia TDM semplificata

## 5. Milestone e task

### M1 - Delimitazione, escaping ed encoding del bundle

**Obiettivo:** il bundle prodotto da ContextBundler delimita ogni file in
modo non ambiguo, non altera il Markdown/JSON sorgente e dichiara
l'encoding usato.

#### T1.1 - Delimitatori di file con hash e lunghezza

- **Durata:** 2-3 ore
- **Rischio:** R2 (tocca il core della serializzazione, ma è additivo)
- **Canale:** B
- **Attività:**
  - sostituire il marker `## File:` con i delimitatori `<<<FILE ...>>>` /
    `<<<END FILE>>>` (sezione 2.1);
  - calcolare SHA-256 e byte-length del contenuto sorgente per ogni file
    incluso;
  - garantire una newline canonica prima e dopo ogni delimitatore, incluso
    l'ultimo file del bundle.
- **Criterio atteso:** un bundle su un set di file misti (md, json, cs, ps1)
  non presenta più casi come l'Anomalia 5 (marker attaccato al contenuto
  precedente).
- **Verifiche:** confronto byte-a-byte tra hash dichiarato nel bundle e hash
  ricalcolato sul sorgente originale, su almeno 5 file di test.

#### T1.2 - Escaping Markdown dichiarativo (default: nessuno)

#### T1.3 - Encoding UTF-8 esplicito e rilevamento mojibake


### M2 - Fedeltà del contenuto (controllo caratteri, JSON, fence)

### M3 - Versionamento del formato e test end-to-end

### M4 - Timestamp post-estrazione ZIP (process-zip-and-scripts-from-llm)

**Obiettivo:** una build eseguita dopo l'estrazione di una patch ZIP riflette
sempre il sorgente appena estratto, non un assembly incrementale obsoleto
(Anomalia 9). Milestone indipendente da M1-M3, scorporabile dal piano se si
vuole trattarla separatamente.

<next_task>
#### T42 - Piano Completato

- Guru Meditation
- chiedere all'utente di creare un nuovo piano di esecuzione
</next_task>

---

## 6. Copertura minima obbligatoria

Derivata dalle decisioni vincolanti della sezione 2:

- percorso positivo: bundle su file misti (md, json, cs, py, ps1, txt con
  accentate) prodotto senza anomalie rilevabili;
- errori ad alto valore: file con fence sbilanciato, file JSON con
  caratteri che potrebbero essere escaped, file con sequenze `\r`/`\n`
  letterali;
- compatibilità protetta: FromLlm-Unbundler.ps1 su un bundle in formato
  precedente (prerelease v1.2) continua a funzionare finché non viene aggiornato in
  un'iterazione successiva (verifica di non-regressione, non di supporto
  al nuovo formato);
- sicurezza e assenza di dati sensibili: non applicabile in modo specifico
  a questo piano, nessuna nuova superficie di dati sensibili introdotta;
- verifiche dell'artefatto reale: bundle generato realmente ispezionato
  (non solo output di test unitari), su almeno un caso con tutti i tipi di
  file coinvolti.

## 7. Contratto esecutivo comune

Ogni task esecutivo deve:

1. verificare baseline e working tree;
2. limitare la discovery ai file necessari;
3. fermarsi su drift materiale;
4. modificare solo lo scope autorizzato;
5. aggiornare i test insieme al comportamento;
6. eseguire verifiche proporzionate e non simulare output;
7. riepilogare file, decisioni, comandi, esiti e residui;
8. se eseguito sul Canale A, produrre run state e frammento Markdown
   richiesti dal TDM senza commit né cleanup finale;
9. lasciare a B1 review di milestone, append al log, cleanup e
   autorizzazione al commit.

## 8. Definition of Done

L'iniziativa è chiudibile quando:

- tutti i gate (M1-M4) sono superati;
- ogni decisione vincolante della sezione 2 è coperta da un criterio
  verificato;
- la suite golden-file (T3.2) passa;
- un bundle reale su ContextBundler (o solution equivalente) non
  riproduce più le anomalie 1-8 osservate nel documento originale;
- il caso reale di timestamp/build incrementale (Anomalia 9, M4) è
  risolto o esplicitamente rimandato con motivazione;
- i rischi residui sono espliciti (in particolare: anomalie introdotte nei
  passaggi 3-5 della catena, fuori dal controllo di ContextBundler);
- B1 assegna lo stato `VERIFIED`.
