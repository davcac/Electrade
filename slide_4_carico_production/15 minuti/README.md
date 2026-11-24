# Slide 4 — rigenerazione a 15 minuti

Questa sottocartella contiene copie quartorarie dei grafici, lasciando intatti script e PNG orari nella cartella genitore. Carico e generazione A65/A75 sono già a 15 minuti; qui si riallineano i marker rossi ai prezzi GME quartorari esattamente uguali a zero.

La linea viola tratteggiata è la **generazione A75 netta degli assorbimenti degli accumuli**: immissioni A75 meno assorbimenti A75 dei tipi PSR `B10`, `B25` e `B32`. È questa serie netta, non la somma lorda delle aree impilate, che viene confrontata con il carico A65 per calcolare surplus e deficit.

Prezzi normalizzati da slide 2: `../../slide_2_scelta_evento_p_zero/15 minuti/dati/prezzi_zonali_15min_48h.csv`.
Dati A65/A75: `../dati/carico_produzione_48h.csv` e XML A75 originali.

## Esecuzione

```powershell
cd "C:\Users\Utente\Desktop\opencode CLI"
python "presentazione lunedì 23\slide_4_carico_production\15 minuti\genera_grafici_15min.py"
```

Grafici prodotti in `grafici/`: `01_produzione_carico_7zone_15min.png`, `02_surplus_7zone_15min.png`, `02_surplus_3zone_15min.png`, `03_surplus_linea_7zone_15min.png`, `05_surplus_macrozone_15min.png`.

I marker sono intervalli con prezzo esattamente zero, non ore intere: 23 intervalli in Sud/Calabria/Sicilia e 5 in Sardegna. La scala temporale dei nuovi grafici è UTC.
