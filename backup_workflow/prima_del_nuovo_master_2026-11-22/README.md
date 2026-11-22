# Presentazione Electrade

Modifica testi, note e impaginazione in `Presentazione_Electrade_MASTER.pptx`.
Per spostare o ridimensionare un grafico, sposta o ridimensiona il suo
segnaposto nel master, conservando il testo `{{GRAFICO_…}}`.

Quando cambiano i dati, rigenera i PNG con gli script nelle rispettive cartelle.
Per aggiornare il PowerPoint, esegui dalla cartella del progetto:

```powershell
python aggiorna_presentazione.py
```

Lo script incorpora i 14 PNG e sostituisce `Presentazione_Electrade_AGGIORNATA.pptx`
dopo aver verificato il file generato. Su Windows, chiudi la copia aggiornata
in PowerPoint prima di rigenerarla se il programma tiene bloccato il file.

L'associazione tra segnaposto e PNG è nel dizionario `CHARTS` dello script.
Per cambiare il grafico associato a una slide, aggiorna il percorso corrispondente.
