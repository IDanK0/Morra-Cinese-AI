# DA AGGIUNGERE (Backlog)

Obiettivo: tenere traccia delle migliorie da fare (con priorità e “definizione di fatto” chiara).

## P0 — Migliorie UX/compatibilità (prima)

- [ ] **Rimuovere tutte le emoji e migliorare la grafica**
    - Motivo: Python non visualizza le emoji.
    - DoD (Done): nessuna schermata usa emoji; sostituite con elementi sempre visibili (testo/icone ASCII/forme), layout più pulito e coerente.

- [ ] **Fullscreen dalle impostazioni + responsività**
    - DoD (Done): toggle fullscreen nelle impostazioni; UI leggibile su risoluzioni diverse (almeno 720p e 1080p) senza sovrapposizioni o tagli.

## P1 — Classifica (miglioramenti funzionali)

- [ ] **Paging nella classifica + data e orario**
    - Cambiamento: rimuovere lo scroll “infinito” e introdurre pagine (es. 10 record per pagina).
    - DoD (Done): navigazione pagina avanti/indietro; ogni entry mostra data e ora del punteggio.

- [ ] **Evidenziare graficamente la Top 3**
    - DoD (Done): le prime 3 posizioni si distinguono chiaramente (stile diverso o sezione dedicata), senza usare emoji come unico elemento distintivo.

## P2 — Interazione e performance

- [ ] **Navigazione con gesti**
    - DoD (Done): almeno le azioni base sono eseguibili senza mouse/tastiera (es. conferma/indietro e cambio schermata), con feedback chiaro per evitare attivazioni involontarie.

- [ ] **Ottimizzazione performance (peso e caricamento modello)**
    - DoD (Done): caricamento più rapido del modello (idealmente lazy-load o caching), riduzione dei tempi di attesa percepiti e minori rallentamenti durante l’esecuzione.

## Extra

- [ ] **Effetti sonori**
    - DoD (Done): suoni opzionali (attivabili/disattivabili), volume non invasivo, nessun crash se audio non disponibile.