# Slide 2 — prezzi MGP a 15 minuti (cartella di analisi)

Questa sottocartella conserva la variante quartoraria, senza sostituire i grafici orari al livello superiore.

## Fonte e convenzione temporale

- Input GME: `../20261112_20261113_MGP_PrezziZonali_15min.xlsx`.
- 192 righe: 48 ore × 4 periodi da 15 minuti, 7 zone.
- `Ora=1` è la prima ora del giorno, 00:00–01:00; `Periodo=1..4` identifica i quattro quarti d'ora. Il timestamp di ogni riga è l'inizio dell'intervallo di consegna, in ora italiana.
- Il CSV normalizzato conserva timestamp locale e UTC; il grafico usa asse UTC.

## Output e riproduzione

```powershell
cd "C:\Users\Utente\Desktop\opencode CLI"
python "presentazione lunedì 23\slide_2_scelta_evento_p_zero\15 minuti\genera_prezzi_15min.py"
```

- `dati/prezzi_zonali_15min_48h.csv` — prezzi zonali normalizzati, 192 timestamp.
- `grafici/prezzi_zonali_15min_48h.png` — serie a 15 minuti con tacche rosse solo dove il prezzo è esattamente 0 €/MWh.

Nel file sono 23 quarti d'ora a zero per Sud, Calabria e Sicilia; Sardegna ha 5 quarti d'ora a zero. Questo conteggio non equivale a 23/5 ore e non va confuso con la classificazione oraria.
