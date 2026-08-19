# Turbo AI - Learned Lesson: Maometto e la naming convention

**Learned Lesson**: Adattare i tool, non forzare l'LLM
Contesto: Con il problema della naming convention del file decorato/duplicato, si è tentato di correggere il comportamento dell'LLM affinando le istruzioni nelle skill. Nonostante l'LLM capisse l'errore dopo averglielo segnalato, nelle sessioni a freddo continuava ad avere fluttuazioni imprevedibili.

**Lesson Learned**: Quando un LLM mostra comportamenti incostanti su dettagli deterministici (come la formattazione dei nomi file) e l'ottimizzazione del prompt non risolve al primo colpo, è inefficace e dispersivo insistere a guidare l'LLM via istruzioni.

**Azione**: Applicare il principio "Se la montagna non va a Maometto...": spostare il controllo dal lato generativo al codice deterministico. È preferibile adattare i tool a valle tramite regex e sanitizzazione per gestire l'input non strutturato in modo tollerante e robusto.