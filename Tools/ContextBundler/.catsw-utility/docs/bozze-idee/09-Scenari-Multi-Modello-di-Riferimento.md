---
title: Scenari Multi-Modello di Riferimento
copyright: "© 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved."
author: IK0VCK
version: 1.0
updated: 2026-08-15
workflow: TDM 1.0
section: 9
---
# 9. Scenari Multi-Modello di Riferimento

TurboAI è agnostico rispetto al modello sottostante (§1, §2): quello che segue sono combinazioni concrete di Canale A/B/C — nella definizione canonica di §2, non ridefinita scenario per scenario — verificate o in corso di verifica. Ogni scenario ha uno *Skill Focus*: cosa cambia nel set di skill/istruzioni per adattarsi alle specificità del canale scelto.

## 9.1 Scenario "Google Ecosystem"

- **Canale B (Torre di Controllo):** Gemini Advanced su piano a pagamento (~4,99 €/mese) — il piano gratuito non basta: quello a pagamento abilita upload/download nativo di zip e markdown, condizione necessaria per operare come Canale B allo stesso titolo di Claude, Grok o GPT-5.6.
- **Canale A (Full Agentic):** Anti-Gravity CLI, autenticata via API key gratuita di Google AI Studio (non OAuth) — vedi configurazione `GEMINI_API_KEY`.
- **Skill Focus:** nessuna istruzione in linguaggio naturale nella ContextRequest (solo path espliciti verificati), validazione dell'integrità dello zip prima del link di download.
- **Considerazioni:** l'account usato per Gemini Advanced va isolato dall'account Google personale (profilo Chrome dedicato) per non mescolare storage/sessioni tra vita privata e workspace AI — dettaglio operativo, non parte del contratto TurboAI.

## 9.2 Scenario "Grok Stack (High Velocity)"

- **Canale B (Torre di Controllo):** SuperGrok (chat web).
- **Canale A (Full Agentic):** Grok CLI / Build Agent, loop chiuso con limite massimo di iterazioni di auto-correzione.
- **Skill Focus:** routing ottimizzato per la velocità di risposta, prompt in linguaggio naturale accettabili sul Canale B (nessuna limitazione di parsing strutturato come su Canale A).
- **Considerazioni:** indicato per prototipazione rapida dove la velocità di iterazione conta più della supervisione fine per singolo step.

## 9.3 Scenario "Enterprise a Bassa Restrizione"

- **Canale B (Torre di Controllo):** Copilot 365 con GPT-5.6 Think, su piano aziendale flat — nessun limite di token stringente, quindi nessuna necessità di comprimere le skill per risparmiare contesto (a differenza dei free tier di Canale B/C).
- **Canale A (Full Agentic):** GitHub Copilot in Visual Studio/VS Code con modello Sonnet 5, su piano individuale a ~30 €/mese — tier meno restrittivo del free tier, ma comunque un canale a pagamento separato dal piano aziendale del Canale B.
- **Skill Focus:** il canale Copilot 365 (indipendentemente dal modello sottostante) altera gli allegati in ingresso/uscita — rimuove o corrompe delimitatori con parentesi angolari, tronca porzioni di codice incorporate nel testo. La skill per questo canale richiede quindi payload in **base64** come formato obbligatorio (verificato byte-per-byte con hash), non i delimitatori standard usati su Claude/Grok.
- **Considerazioni:** questo scenario è quello con minori vincoli di quota rispetto ai contesti free-tier descritti altrove in questo documento, ma non è per questo esente da supervisione: anche un'esecuzione full-agentic su un tier a pagamento può produrre risultati mediocri che richiedono verifica e correzione manuale sul Canale B prima del commit — la disciplina dei Gate (§5) non è una misura compensativa dei tier gratuiti, resta necessaria indipendentemente dal budget disponibile.

## 9.4 Scenario Sperimentale: Grok CLI su Canale B con Gating Manuale

Variante non ancora consolidata, da testare in TurboAI Lab prima di proporla come scenario di riferimento al pari dei precedenti.

- **Idea:** riutilizzare Grok CLI — nativamente uno strumento da Canale A (full-agentic, loop di auto-correzione senza intervento) — nel ruolo di Canale B, disattivando l'auto-apply e il loop chiuso.
- **Funzionamento:** dopo ogni step la CLI si ferma; l'utente fa da man-in-the-middle, esamina `ToLlm.txt` prima di dare un comando di continue o di inserire uno steering prompt correttivo — lo stesso pattern HITL già usato per il Canale B conversazionale, ma applicato a uno strumento CLI invece che a una chat web.
- **Perché è interessante:** rompe l'assunzione implicita che "CLI = Canale A" e "chat web = Canale B" — il ruolo (governo/supervisione vs esecuzione autonoma) dipende dalla modalità operativa scelta, non dallo strumento in sé. Se verificato, apre la possibilità di usare qualunque CLI agentica anche in modalità supervisionata, senza dover necessariamente passare da un'interfaccia conversazionale per ottenere il gating umano.
- **Da verificare prima di consolidare:** se il costo/tempo di gating manuale su una CLI pensata per operare senza pause introduce frizioni (es. l'interfaccia CLI non è pensata per mostrare bene `ToLlm.txt` in modo leggibile a ogni pausa) che ne vanificano il vantaggio rispetto a un vero Canale B conversazionale.
