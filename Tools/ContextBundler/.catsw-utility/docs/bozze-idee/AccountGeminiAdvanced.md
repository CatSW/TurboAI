# Strategia di Isolamento: Sandbox AI & Storage Workspace

## 1. Obiettivo della Strategia

Implementare una separazione netta tra l'account **Personale (Primary)** e l'account **AI Workspace (Sandbox)** per:

1. **Mitigazione del rischio:** Evitare blocchi automatici o sovrapposizioni di storage qualora si decidesse di terminare l'abbonamento o di sforare le soglie di archiviazione.
2. **Gestione dei dati:** Mantenere i dati del progetto Turbo AI e i documenti di lavoro pesanti separati dalla vita privata (foto, mail personali).
3. **Pulizia delle Sessioni:** Evitare conflitti tra cookie/cache tra l'account di navigazione quotidiana e quello dedicato all'AI.

---

## 2. Configurazione Tecnica (Account Sandbox)

### Creazione e Setup

1. **Creazione:** Crea un nuovo account Google (es. `nome.turbo.ai@gmail.com`).
2. **Abbonamento:** Attiva il piano Google One (es. 4.99€/mese) **esclusivamente** su questo account.
3. **Isolamento Browser (Cruciale):** Non passare tra gli account all'interno della stessa istanza del browser. Usa i **Profili di Google Chrome** (o Edge):
* Crea un profilo Chrome chiamato "Turbo AI".
* Accedi solo con l'account Sandbox.
* **Vantaggio:** Le sessioni, la cronologia e i cookie di questo profilo sono fisicamente separati dal profilo "Personale". Non dovrai mai effettuare il logout dal principale per usare l'AI.



---

## 3. Strategia di Gestione Risorse (Exit Strategy)

Il timore di un blocco "a cascata" sul profilo principale è infondato se mantieni i due account distinti. Tuttavia, la gestione dei dati richiede disciplina per evitare perdite:

* **Regola dello Storage:** Se decidi di non rinnovare il piano:
1. Hai 30 giorni (o il termine del ciclo di fatturazione) per migrare i file che superano i 15GB del piano gratuito.
2. Poiché l'account è isolato, se non rinnovi, **solo l'account Sandbox smetterà di ricevere mail o sincronizzare drive** quando superi la soglia. L'account Principale continuerà a funzionare normalmente.


* **Backup preventivo:** Usa il tool [Google Takeout](https://takeout.google.com/) una volta al mese per esportare i file generati nel Workspace Sandbox e salvarli localmente o su un NAS/Disco esterno, così da non dover dipendere dallo storage in cloud per i tuoi progetti finiti.

---

## 4. Integrazione in Turbo AI (Canale C)

L'account Sandbox diventa il motore esecutivo del **Canale C** e il supporto per le operazioni pesanti.

### Workflow Operativo

1. **Canale B (Torre di Controllo):** Continua a girare sul tuo setup CLI locale con API Key.
2. **Canale C (Sandbox AI):** Quando hai bisogno di brainstorming complesso o di usare la Python Sandbox di Gemini:
* Apri il **Profilo Chrome "Turbo AI"**.
* Carica i file pesanti o il contesto di lavoro.
* Sfrutta la Sandbox Python per generare i bundle/zip.
* Scarica gli output direttamente sul PC (nella cartella dedicata al progetto Turbo AI).



### Sincronizzazione con il Progetto locale

Non tentare di usare Google Drive come "hard disk" del progetto.

* **Principio:** L'account Sandbox serve per **processare**, non per **archiviare**.
* **Workflow:**
1. Carica input da locale -> Elabora su Web AI -> Scarica output su locale.
2. Il repository Git locale è la tua *Single Source of Truth*. L'account Sandbox è solo un'estensione temporanea della potenza di calcolo.



---

## 5. Sintesi Operativa — Differenze tra CLI e Sandbox Web

| Feature | Anti-Gravity CLI (API Key) | Sandbox Web (Account Sandbox) |
| --- | --- | --- |
| **Utilizzo principale** | Canale A & B (Automazione) | Canale C (Brainstorming/Manuale) |
| **Storage Dati** | File System Locale (Git) | Cloud Sandbox (Temporaneo) |
| **Isolamento** | Chiave API dedicata | Profilo Browser dedicato |
| **Rischio Blocco** | Nullo (Billing separato) | Nullo (Account separato) |
| **Workflow** | Esecuzione Script | Interazione Manuale |

### Prossimi passi per la sperimentazione:

1. **Crea il profilo Chrome** e testa se l'accesso ai file (upload/download) è fluido con l'account Sandbox.
2. **Testa la Sandbox Python:** Chiedi a Gemini (sul profilo Sandbox) di creare un file zip da un esempio di codice banale e verifica se il link di download appare correttamente.
3. **Consolidamento:** Una volta verificato che il workflow Sandbox funziona, integra il download dei file nella tua procedura di validazione manuale del Canale C.

---

*Documento salvato nel tuo registro di sistema per Turbo AI. Utilizzalo come guida per configurare l'account dedicato e minimizzare i rischi operativi.*