# Slide 5 — transiti a 15 minuti

Questa variante legge gli XML ENTSO-E già scaricati in `../dati/` e produce un CSV quartorario in questa sottocartella. Non modifica il CSV né i grafici orari esistenti.

## Risoluzioni native

- A09 (scambi programmati, day-ahead A01): pubblicato PT15 sui confini disponibili; le serie compresse A03 sono espanse secondo le posizioni/persistenze nel documento.
- A11 (flussi fisici): la maggior parte dei confini è PT15; il confine con la Grecia è PT60. Per allinearlo al grafico quartorario, il valore orario è mostrato a gradino sui quattro quarti d'ora e la risoluzione nativa resta indicata nel CSV. Non è una nuova misura PT15.
- A61 (NTC): PT60 nei file disponibili. Nel grafico Sud→Centro-Sud il limite NTC resta orario e viene mostrato a gradino, mentre A09 è PT15.

## Esecuzione

```powershell
cd "C:\Users\Utente\Desktop\opencode CLI"
python "presentazione lunedì 23\slide_5_mappa_transiti\15 minuti\prepara_transiti_15min.py"
python "presentazione lunedì 23\slide_5_mappa_transiti\15 minuti\genera_grafici_transiti_15min.py"
python "presentazione lunedì 23\slide_5_mappa_transiti\15 minuti\plot_export_sud_centrosud_15min.py"
```

`dati/transiti_48h_15min.csv` contiene direzione, timestamp UTC/locale, A09/A11/A61 e la risoluzione nativa di ogni serie.

Grafici in `grafici/`: barre giornaliere import/export A09 per 12 e 13 novembre; linee A09/A11 per zona; macrozona; produzione+net import; surplus adj per le tre zone e per la macrozona; `export_sud_centrosud_15min.png` con A09 quartorario, NTC orario a gradino e tacche rosse per ciascun MTU con prezzo Sud esattamente zero. Le barre giornaliere convertono i MW quartorari in MWh moltiplicando ogni intervallo per 0,25 h.

Nei grafici di surplus adj la produzione A75 è **al netto degli assorbimenti degli accumuli** (`B10`, `B25`, `B32`), poi viene aggiunto l'import netto fisico A11 e il risultato è confrontato con il carico A65.

Nel grafico `surplus_adj_3zone_15min.png` i tre pannelli condividono la scala Y 0-6000 MW, così i valori assoluti delle zone sono confrontabili.
