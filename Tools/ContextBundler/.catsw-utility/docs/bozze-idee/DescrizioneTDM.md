# Turbo AI — Architettura del Sistema e Metodologia a Tre Canali

## Introduzione

**Turbo AI** è una metodologia e un framework di sviluppo assistito da modelli linguistici (LLM) basato sul principio **Human-in-the-Loop (HITL)**. L'obiettivo principale è massimizzare l'efficienza dello sviluppo software, ridurre l'attrito del copia-incolla manuale, azzerare le derive degli agenti autonomi e ottimizzare l'uso dei token sia su ambienti gratuiti (*Free Tier*) che aziendali (*Flat Rate*).

---

## Architettura a Tre Canali (A, B, C)

```
                        ┌────────────────────────────────────────┐
                        │      TORRE DI CONTROLLO (Canale B)     │
                        │  Governa il Piano, i Task, la Governance│
                        └───────────────────┬────────────────────┘
                                            │
                     ┌──────────────────────┼──────────────────────┐
                     │ (Delegazione/Task)   │ (Lavoro diretto)     │ (Brainstorming/Subtask)
                     ▼                      ▼                      ▼
          ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
          │     CANALE A       │ │     CANALE B       │ │     CANALE C       │
          │   Full Agentic     │ │  Semi-Automatico   │ │  Conversazionale   │
          │  (Visual Studio +  │ │ (Bundle + HITL +   │ │  (Chat Web / Text  │
          │  Copilot / Sonnet) │ │  Anti-Gravity CLI) │ │   Copy-Paste)      │
          └────────────────────┘ └────────────────────┘ └────────────────────┘

```

### Canale A: Full Agentic (Esecutore per Task Delimitati)

* **Ruolo:** Esecuzione di task ad alta intensità di scrittura o refactoring dove il contesto è ben circoscritto e non richiede una supervisione costante.
* **Funzionamento:** La Torre di Controllo (Canale B) analizza il task, ne valuta la semplicità/isolamento e genera un **prompt ottimizzato** destinato ad agenti integrati nell'IDE (es. GitHub Copilot su Visual Studio).
* **Vantaggio:** Sfrutta la scrittura diretta nel codice senza passare dalla gestione intermedia dei file di bundle.

---

### Canale B: Semi-Automatico con Human-in-the-Loop (Torre di Controllo)

* **Ruolo:** Cuore pulsante di Turbo AI. Gestisce la governance del progetto, l'orchestrazione del piano di lavoro, l'esecuzione dei task critici/architetturali e il routing dei task verso gli altri canali.
* **Funzionamento:**
1. Un tool locale compila un **Context Bundle** (stato Git, changelog, task atomico, file di governance e sorgenti richiesti).
2. L'LLM riceve il bundle e genera una soluzione (patch ZIP/markdown + script Python di test).
3. Il tool locale applica le modifiche ed esegue i test, salvando l'esito nel file `tuLLM.txt`.
4. **Gate di Controllo (HITL):** Il sistema va in pausa prima di reinviare l'esito all'LLM, permettendo allo sviluppatore di esaminare l'output a schermo e iniettare eventuali correzioni strategiche (*steering prompts*).


* **Vantaggio:** Zero cicli ciechi, massimo risparmio di token, qualità del codice garantita dalla validazione umana.

---

### Canale C: Conversazionale & Subtask Unbundling (Supporto Parallelo)

* **Ruolo:** Brainstorming architetturale, risoluzione di dubbi e sviluppo di subtask/micro-tool paralleli a costo zero.
* **Funzionamento:** Utilizzato tramite interfacce web conversazionali durante le fasi di attesa o pianificazione.
* **Evoluzione Futura:** Supporto al formato di **Unbundling via Copy-Paste / Base64**. Copiando il testo o le stringhe Base64 generate dall'LLM nella chat, il tool locale decodifica e posiziona automaticamente i file nel file system, estendendo le capacità agentiche anche agli LLM privi di funzionalità di download diretto.

---

## Soluzioni di Bypassing e Resilienza Protocollo

* **Bypass dei Middleware Aziendali (Base64 Payload):** Per evitare che i sistemi intermedi di compressione dell'input (es. Copilot 365) facciano il *summarization* del codice alterando i sorgenti, i bundle possono essere codificati in **Base64**. L'LLM decodifica la stringa in memoria mantenendo il $100\%$ dell'integrità dei byte (SHA match).
* **Isolamento dei Task e Reset del Contesto:** Ogniqualvolta un task atomico viene completato, la sessione della chat viene chiusa e ripartita "fresca". Lo stato del progetto non risiede nella memoria volatile dell'LLM ma nel file system e nel repository Git locale.