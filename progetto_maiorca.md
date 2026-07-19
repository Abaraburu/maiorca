# Progetto Maiorca: Mappa e Guida Interattiva

## 🎯 Obiettivo del Progetto
Creare una guida turistica digitale e personalizzata per il viaggio a Maiorca. Il sistema combinerà la comodità visiva di **Google My Maps** con la flessibilità e ricchezza di contenuti di un sito web ospitato su **GitHub Pages**.

## 🏗️ Architettura

Il progetto si divide in due componenti principali che lavorano in sinergia:

### 1. Google My Maps (La Mappa Visiva)
*   **Funzione:** Fornire una visione geografica d'insieme di tutte le tappe.
*   **Caratteristiche:**
    *   Pin divisi in **Categorie** (es. 🏖️ Spiagge, 🏛️ Attrazioni, 🍽️ Ristoranti).
    *   Pin **Colorati** in base alla categoria per un'immediata comprensione visiva.
    *   **Descrizione del Pin:** Conterrà il link diretto alla pagina web dedicata a quel luogo.
*   **Gestione:** Aggiornata tramite importazione periodica di un file `.csv` o `.kml`.

### 2. GitHub Pages (La Guida Dettagliata)
*   **Funzione:** Ospitare le informazioni dettagliate, i media e gli appunti personali per ogni luogo.
*   **Caratteristiche per ogni Pagina Luogo (HTML):**
    *   Titolo e descrizione completa.
    *   **Integrazione TikTok:** Video incorporati per vedere subito perché il posto è stato salvato.
    *   Galleria fotografica.
    *   Note utili (parcheggi, orari, consigli).
    *   Stile grafico curato (CSS personalizzato).

---

## 🔄 Il Flusso di Lavoro (Workflow)

Quando viene trovato un nuovo luogo interessante (ad es. su TikTok), il processo sarà questo:
*(Nota: una stessa location può avere più link TikTok. Se viene segnalato un nuovo link per un luogo già esistente, aggiungi semplicemente il nuovo link alla sua pagina).*

1.  **Raccolta Dati:** Segnalazione del nome del luogo, coordinate e link del video TikTok/sito web.
2.  **Creazione/Aggiornamento Dati Mappa:** Inserimento della nuova riga nel file dati per My Maps, assegnando la categoria corretta e il link alla futura pagina web.
3.  **Generazione Pagina Web:** Creazione del file `.html` dedicato all'interno del progetto GitHub, incorporando il video TikTok e le informazioni.
4.  **Pubblicazione:** 
    *   Push del codice su GitHub per aggiornare le pagine web.
    *   Click su "Importa" in Google My Maps per aggiornare i pin.

## 🚀 Prossimi Passi
- [x] Inizializzare la struttura base del sito HTML/CSS.
- [x] Creare il file base `mappe_maiorca.csv` per My Maps.
- [ ] Inserire il primo luogo di prova (Spiaggia o Attrazione) per testare l'integrazione mappa-sito.
