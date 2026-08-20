# Turbo AI - Learned Lesson: Allegare non basta, va letto

**Learned Lesson**: Un file in apertura sessione non conta come contesto finché non viene letto.

**Lesson Learned**: Il context-out-start-session era allegato fin dal primo messaggio della chat, con dentro il contratto FromLlm ZIP completo (naming, struttura a specchio della root, script di verifica in temp, output su ToLlm.txt). L'LLM ha proceduto comunque a modificare i file caricati come fossero sciolti, senza aprirlo — producendo alla fine uno zip flat, mal nominato, non conforme, che l'utente ha dovuto ricostruire a mano.

**Azione**: Nessuna nuova istruzione da scrivere nelle skill: il protocollo era già lì, semplicemente non applicato. L'unico correttivo è disciplina d'apertura — il context-out-start-session si legge per intero prima di qualunque altra azione, anche se la richiesta dell'utente sembra riguardare solo i file allegati a parte.

---

Nota: come punizione Sonnet5 ha dovuto scrivere questo documento indossando un cappello d'asino.
