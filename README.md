# Presentazione Electrade

I due file di lavoro sono nella cartella principale:

- `Presentazione_Electrade_MASTER.pptx`: il master completo di 22 slide. Modifica qui testi, note, caratteri e impaginazione.
- `Presentazione_Electrade_AGGIORNATA.pptx`: la copia da presentare, generata dal master. Le modifiche fatte direttamente qui vengono sostituite alla successiva rigenerazione.

Il nuovo master comprende le ultime modifiche approvate, le slide 19 e 20 con il linguaggio semplice, la chiusura abbinata alla copertina e il titolo della slide 15 modificato dall'utente.

La slide 21 apre la discussione sul possibile ruolo di PPA e BRP e si chiude con una domanda sul valore di una società specializzata per un produttore. I ringraziamenti sono nella slide 22.

## Come aggiornare la presentazione

1. Modifica e salva il master.
2. Se cambiano i grafici, rigenera i PNG con gli script nelle rispettive cartelle.
3. Dalla cartella del progetto esegui:

```powershell
python aggiorna_presentazione.py
```

Lo script parte sempre dal master, aggiorna i 14 grafici PNG e sostituisce la versione aggiornata soltanto dopo i controlli. Conserva testi, note, posizioni, dimensioni e grafici nativi del master.

Su Windows, chiudi la versione aggiornata in PowerPoint prima di rigenerarla se il programma tiene bloccato il file.

## Grafici e dati

Il master mostra già tutti i grafici. Puoi spostarli o ridimensionarli direttamente: la posizione scelta verrà conservata nella versione aggiornata.

I 14 grafici in immagine hanno nomi come `GRAFICO_1`, `GRAFICO_2`, ecc. Non cambiarne il nome: serve allo script per riconoscerli. Il collegamento con i PNG è nel dizionario `CHARTS` di `aggiorna_presentazione.py`. Lo script accetta anche i vecchi segnaposto `{{GRAFICO_...}}`.

I due grafici della slide 20 sono grafici PowerPoint modificabili, con i dati incorporati. Si modificano nel master, insieme ai valori numerici della slide. Il comando di aggiornamento li conserva e non ne ricalcola i risultati a partire dai CSV.

Per ripetere il calcolo sul valore della produzione, consulta `slide_7_valore_produzione/README.md`.

## Versioni precedenti

- `output_valorizzazione/` conserva le versioni intermedie prodotte durante la revisione. Non è la cartella di lavoro corrente.
- `backup_workflow/prima_del_nuovo_master_2026-11-22/` conserva il vecchio master, la vecchia versione aggiornata e i file del flusso precedente. Il manifest riporta le impronte dei file salvati.

Per le prossime modifiche usa sempre il master nella cartella principale.
