# Guida all'Integrazione di Anti-Gravity CLI (Gemini API Key) in Turbo AI

La presente guida descrive la procedura di configurazione e utilizzo della **CLI di Google Anti-Gravity** tramite le credenziali di **Google AI Studio**, anziché tramite il flusso OAuth standard. Viene inoltre illustrato come integrare la CLI nel framework **Turbo AI** per operare nei canali **Canale B (Torre di Controllo / HITL)** e **Canale A (Full Agentic)**.

---

## 1. Creazione delle API Key su Google AI Studio

Per utilizzare i modelli Gemini con un pacchetto di richieste separato e ottimizzato per lo sviluppo, occorre generare una chiave API dedicata.

1. Accedere al portale **[Google AI Studio](https://aistudio.google.com/)** utilizzando il proprio account Google.
2. Nel menu di navigazione a sinistra, selezionare la voce **Get API key**.
3. Fare clic su **Create API key**.
4. Scegliere se associare la chiave a un progetto Google Cloud esistente oppure crearne uno nuovo (es. `TurboAI-Dev`).
5. Copiare la chiave alfanumerica generata e conservarla in un luogo sicuro.

> **Avvertenza di Sicurezza:** Non inserire mai la chiave API all'interno dei file del repository Git. Assicurarsi che i file di configurazione locale (es. `.env`) siano inclusi nel file `.gitignore`.

---

## 2. Configurazione e Uso della chiave nella CLI di Anti-Gravity

Per fare in modo che la CLI utilizzi la chiave API anziché la sessione browser OAuth, è necessario impostare la variabile d'ambiente standard utilizzata dall'SDK di Google.

### Configurazione delle Variabili d'Ambiente

#### Su Linux / macOS (`~/.bashrc` o `~/.zshrc`):

```bash
export GEMINI_API_KEY="LA_TUA_CHIAVE_API_QUI"

```

*Ricaricare la configurazione del terminale con `source ~/.bashrc`.*

#### Su Windows (PowerShell):

```powershell
$env:GEMINI_API_KEY="LA_TUA_CHIAVE_API_QUI"

```

#### Su Windows (Prompt dei comandi - CMD):

```cmd
set GEMINI_API_KEY=LA_TUA_CHIAVE_API_QUI

```

### Verifica del Funzionamento

Eseguire un comando di test tramite la CLI senza passare per la procedura di login via browser:

```bash
antigravity --version

```

Se la variabile `GEMINI_API_KEY` è presente nel sistema, la CLI reindirizzerà automaticamente le chiamate verso l'infrastruttura di Google AI Studio sfruttando il pacchetto gratuito (*Free Tier*).

---

## 3. Modalità Canale B: Anti-Gravity CLI in "Human-in-the-Loop" (Torre di Controllo)

In questo scenario, **Turbo AI** utilizza la CLI come motore esecutivo headless, ma mantiene il controllo umano sui cicli di test prima di procedere.

### Workflow del Canale B

1. **Generazione del Bundle:** Turbo AI crea il file bundle contenente il task isolato, lo stato Git e le direttive di Governance.
2. **Invocazione della CLI:** Il tool locale lancia Anti-Gravity CLI passandogli il bundle come input.
3. **Scrittura Diretta su Disco:** La CLI genera ed estrae i file sorgente modificati e lo script di test Python direttamente nella cartella locale del progetto (senza passare dall'interfaccia web).
4. **Esecuzione Test:** Turbo AI esegue lo script Python e cattura i log nel file `tuLLM.txt`.
5. **Gate di Controllo (HITL):** Il sistema arresta l'esecuzione automatica e mostra a schermo l'esito.

```
+-------------------+      +--------------------+      +--------------------+
|  Generazione      | ---> | Anti-Gravity CLI   | ---> | Scrittura Patch    |
|  Context Bundle   |      | (GEMINI_API_KEY)   |      | e Test Python      |
+-------------------+      +--------------------+      +--------------------+
                                                                 |
                                                                 v
+-------------------+      +--------------------+      +--------------------+
| Pause/Intervento  | <--- | Gate di Controllo  | <--- | Esecuzione Test    |
| Sviluppatore      |      | (Mostra tuLLM.txt) |      | e Generazione Log  |
+-------------------+      +--------------------+      +--------------------+

```

### Esempio di Integrazione nello Script Locale (Pseudo-Codice)

```python
# 1. Esecuzione chiamata CLI con il Bundle iniziale
import subprocess

def run_channel_b_step(bundle_path):
    cmd = f'antigravity run --input "{bundle_path}" --model gemini-2.5-flash'
    subprocess.run(cmd, shell=True)
    
    # 2. Esecuzione automatica dello script di test generato
    test_result = subprocess.run('python run_tests.py', capture_output=True, text=True)
    
    with open("tuLLM.txt", "w") as f:
        f.writelines(test_result.stdout)

    # 3. GATE HUMAN-IN-THE-LOOP
    print("\n--- OUTPUT TEST (tuLLM.txt) ---")
    print(test_result.stdout)
    print("--------------------------------")
    
    user_choice = input("[C]ontinua, [I]ntervieni con prompt, [A]nnulla: ")
    if user_choice.lower() == 'i':
        feedback = input("Inserisci le istruzioni di correzione per il modello: ")
        # Invia il feedback alla CLI nella chiamata successiva
    elif user_choice.lower() == 'c':
        # Procede al task successivo nel piano
        pass

```

---

## 4. Modalità Canale A: Anti-Gravity CLI in "Full Agentic"

Quando la Torre di Controllo (Canale B) individua un task atomico, a basso rischio o puramente esecutivo, può delegarne l'esecuzione al **Canale A** in modalità completamente autonoma.

### Workflow del Canale A

1. **Routing:** Il Canale B valuta il task e genera un prompt di delega.
2. **Esecuzione in Loop Chiuso:** La CLI di Anti-Gravity viene invocata con un limite massimo di tentativi (es. max 3 o 5 cicli di auto-correzione).
3. **Auto-Repair:** Se i test falliscono, il log di errore viene re-inviato immediatamente alla CLI senza richiedere l'approvazione dell'utente.
4. **Riconsegna:** Se i test passano, la modifica viene consolidata; se il limite di tentativi viene raggiunto senza successo, il task viene restituito al Canale B per l'analisi manuale.

### Esempio di Comando per il Canale A

```bash
antigravity agent --prompt-file "task_delega_canale_a.txt" \
                  --auto-apply \
                  --max-iterations 3 \
                  --test-command "python run_tests.py"

```

---

## 5. Sintesi dell'Integrazione in Turbo AI

| Caratteristica | Interfaccia Web Gemini | Anti-Gravity CLI + API Key |
| --- | --- | --- |
| **Download ZIP / File** | Non disponibile direttamente | **Nativo sul File System** |
| **Gestione Cache (KV Cache)** | Limitata alla sessione web | **Ottimizzata via API** |
| **Pausa Human-in-the-Loop** | Manuale via Chat Web | **Automatizzabile tramite Script** |
| **Delega Full Agentic (Canale A)** | Impossibile | **Eseguibile via Script / Loop** |
| **Gestione Token** | Soggetta a rate limit web | **Quota sviluppatore AI Studio** |