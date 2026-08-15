# Turbo AI — Documentazione Orchestrazione e Scenari (V 1.0)

## 1. Architettura Agnostica: Il Sistema di Selezione "Skill"

Turbo AI è progettato per essere indipendente dal modello sottostante. Il core del sistema risiede nella gestione delle **Skills**, memorizzate nel folder `/templates/skills`.

* **Meccanismo:** Il tool `turbo-select-skill` permette di variare il comportamento del sistema in tempo reale.
* **Struttura del folder:**
* `/generic`: Prompt basati sulla logica pura, funzionano su tutti i modelli.
* `/fine-tuned/[model-name]`: Prompt ottimizzati per le specificità (es. middleware di Copilot, capacità di esecuzione Python di Gemini, CLI di Grok).


* **Selezione:** L'utente sceglie la configurazione (es. `gemini-full-stack.skill` vs `grok-channel-b.skill`) all'inizio della sessione. Il sistema applica automaticamente il set di istruzioni, le direttive di routing e le limitazioni del modello scelto.

---

## 2. Scenari Operativi Consolidati

### Scenario 1: Enterprise Stack (Copilot & GPT)

* **Canale B (Torre di Controllo):** Copilot 365 (GPT 5.6 Think).
* *Skill Focus:* Gestione dei limiti di middleware, payload Base64 per evitare il trimming semantico aggressivo.


* **Canale A (Full Agentic):** Visual Studio + GitHub Copilot (Sonnet 5).
* *Modalità:* Integrazione nativa nell'IDE, delega diretta dei task di refactoring su file già aperti.


* **Considerazioni:** Ideale per workflow aziendali dove la sicurezza e l'integrazione con l'IDE sono prioritarie.

### Scenario 2: Google Ecosystem Stack (Gemini)

* **Canale B (Torre di Controllo):** Gemini Advanced (Web UI + Sandbox Python).
* *Skill Focus:* Sfruttamento della Sandbox Python per generare bundle scaricabili. Istruzioni per "validazione pre-link" (controllo integrità zip).


* **Canale A (Full Agentic):** Gemini API (via Anti-Gravity CLI).
* *Modalità:* CLI con `GEMINI_API_KEY` (AI Studio). Esecuzione batch di task su file system locale.


* **Considerazioni:** Configurazione ottimale per bilanciare la potenza del web per la pianificazione e l'efficienza della CLI per il lavoro sporco.

### Scenario 3: Grok Stack (High Velocity)

* **Canale B (Torre di Controllo):** Super Grok (Web Chat).
* *Skill Focus:* Gestione dei prompt in linguaggio naturale, routing ottimizzato per la velocità di risposta di Grok.


* **Canale A (Full Agentic):** Grok CLI / Build Agent.
* *Modalità:* CLI dedicata, ottimizzata per cicli di build rapidi e feedback immediato.


* **Considerazioni:** Workflow indicato per prototipazione rapida e task dove la velocità di esecuzione è il fattore critico.

---

## 3. Matrice di Configurazione Skill

Per ogni nuovo LLM introdotto nel framework, definire le seguenti variabili nel file di skill:

| Variabile | Descrizione |
| --- | --- |
| `ROUTING_THRESHOLD` | Livello di complessità oltre il quale il modello deve delegare al Canale A. |
| `OUTPUT_FORMAT` | Strategia di output (es. `BASE64` per middleware ostili, `MARKDOWN` per chat standard, `NATIVE_ZIP` per modelli con Sandbox). |
| `TEST_COMMAND` | Comando di esecuzione test locale (es. `python run_tests.py` o `pytest`). |
| `SYSTEM_PROMPT` | Direttive comportamentali specifiche (es. "Sei un orchestratore di torre di controllo"). |

---

## 4. Linee Guida per il Setup "Agnostico"

1. **Uniformità di Interfaccia:** Nonostante il modello cambi, il sistema di `unbundling` locale deve restare identico. Che il file arrivi via `Base64` o `ZIP scaricabile`, il tuo tool locale deve processarlo allo stesso modo.
2. **Versioning delle Skill:** Quando un modello viene aggiornato (es. passa da una versione "Think" alla successiva), aggiorna il file `.skill` dedicato. Non sovrascrivere mai le skill "Generic" che servono da backup.
3. **Strategia di Migrazione:** Se aggiungi un nuovo LLM, inizia clonando la skill generica, testa il routing di base, quindi ottimizza i `SYSTEM_PROMPT` in base a come il modello risponde ai tuoi task di delegazione.

---

*Questo documento funge da promemoria per le configurazioni correnti e future. Utilizzalo come base per espandere il supporto a nuovi modelli mantenendo la coerenza del workflow Turbo AI.*