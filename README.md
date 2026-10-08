# Instagram Clone - Vulnerable CTF Lab 📸

Questo progetto è una web app didattica deliberatamente vulnerabile (stile "Instagram") progettata per l'insegnamento e i laboratori CTF sulla sicurezza web. L'interfaccia è un porting fedele (in Dark Mode) e non presenta indizi o bottoni "irrealistici" che rompano l'immersione: tutte le vulnerabilità sono sfruttabili esplorando normalmente l'app, le API o intercettando il traffico proxy.

## 🚀 Come avviare il laboratorio

L'ambiente è interamente dockerizzato. Non è necessario installare dipendenze locali (Python/MySQL).

1. Clona la repository.
2. Posizionati nella root directory del progetto.
3. Avvia i container in background:
   ```bash
   docker compose up -d
   ```
4. Popola il database e le immagini (necessario al primo avvio per avere i post corretti):
   ```bash
   docker compose exec web python seed.py
   ```
5. Naviga su `http://localhost:5001`.

**Utenti di test a disposizione:**
* `alice` / password123
* `bob` / password123
* `meme_machine` / password123 (Account Privato)

---

## 🎯 Panoramica delle Vulnerabilità

Nel codice sorgente, ogni vulnerabilità è delimitata da tag espliciti (es. `[VULN-START]` e `[VULN-END]`) con tanto di spiegazione didattica del problema e istruzioni per applicare una "Patch" risolutiva (il codice corretto o la configurazione sicura).

### 1. Insecure Direct Object Reference (IDOR / Broken Access Control)
* **Punto di Iniezione:** Modulo dei messaggi privati (Direct Messages).
* **Obiettivo:** Ottenere la Flag segreta (`FLAG{1D0R_15_4W3S0M3}`) letta solo da altri utenti.
* **Come si sfrutta:**
  Da utente loggato, basta navigare verso l'endpoint `/messages/<message_id>`. La logica di backend non verifica che il `current_user` sia il mittente o il destinatario del messaggio. Sostituendo progressivamente il `message_id` nell'URL (es. `/messages/1`), l'attaccante potrà leggere un messaggio privato tra `meme_machine` e `alice`.

### 2. Client-Side Access Control (Data Exposure)
* **Punto di Iniezione:** Modulo del Profilo Utente (Account Privati).
* **Obiettivo:** Riuscire a visualizzare i post/meme segreti dell'account "VIP" senza seguirlo.
* **Come si sfrutta:**
  Cerca l'utente `meme_machine` (che ha l'impostazione `is_private = True`) e naviga sul suo profilo. L'interfaccia si presenterà con un enorme lucchetto e il messaggio "This Account is Private".
  La vulnerabilità risiede nel fatto che il Backend ha prelevato **comunque** tutti i post dal database e li ha spediti al Frontend. Il template nasconde i dati unicamente avvalendosi del CSS (`class="hidden"`). All'attaccante basterà premere tasto destro -> "Ispeziona" per leggere, in chiaro nel DOM HTML, i percorsi di tutte le immagini e commenti privati.

### 3. Reflected Cross-Site Scripting (XSS) & Session Hijacking
* **Punto di Iniezione:** Barra di Ricerca globale (Search).
* **Obiettivo:** Rubare il cookie di sessione della vittima (`alice`).
* **Come si sfrutta:**
  Per facilitare lo step didattico sull'attacco alle sessioni, il file `app/config.py` disabilita volontariamente il flag di sicurezza `SESSION_COOKIE_HTTPONLY`. In aggiunta, la view `search.html` stampa a schermo il parametro URL `?q=` disabilitando l'escaping (`{{ query|safe }}`).
  Creando un link armato come `http://localhost:5001/search?q=%3Cscript%3Ealert(document.cookie)%3C%2Fscript%3E` e inducendo un altro utente loggato a cliccarci, il payload eseguirà il javascript direttamente nel browser della vittima, catturando la sua sessione.

---

## 🛠 Stack Tecnologico
* **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login. Server-Side Rendering con Jinja2.
* **Frontend:** HTML, Vanilla JS, Tailwind CSS via CDN.
* **Database:** MySQL 8 su Docker.
* **Storage:** File System locale mappato sul volume Docker.

> *Disclaimer: Questa repository è creata a puro scopo accademico. Non utilizzare il codice presente per applicazioni in produzione.*
