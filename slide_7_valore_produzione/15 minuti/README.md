# Slide 7 — valorizzazione solare a 15 minuti

Questa variante confronta la media temporale dei prezzi MGP quartorari con il prezzo medio ponderato sulla produzione solare effettiva A75 della zona Sud.

## Formula

- Energia solare per quarto: `potenza A75 (MW) × 0,25 h`.
- Prezzo medio semplice: media aritmetica dei 192 prezzi MGP quartorari.
- Prezzo ponderato sulla produzione: `Σ(prezzo_qh × energia_solare_qh) / Σ(energia_solare_qh)`.

Il prezzo ponderato è un capture price descrittivo del profilo solare osservato; non è un ricavo contrattuale né un settlement effettivo.

## Esecuzione e output

```powershell
cd "C:\Users\Utente\Desktop\opencode CLI"
python "presentazione lunedì 23\slide_7_valore_produzione\15 minuti\analizza_valore_15min.py"
```

Fonti: prezzi in `slide_2_scelta_evento_p_zero/15 minuti/dati/prezzi_zonali_15min_48h.csv`; produzione solare in `slide_4_carico_production/dati/carico_produzione_48h.csv`.

Output: `dati/valorizzazione_quartoraria_sud.csv`, `dati/risultati_15min.json`, `grafici/valorizzazione_solare_sud_15min.png`.

Risultato corrente: prezzo medio semplice ≈194,46 €/MWh; prezzo ponderato sulla produzione solare ≈85,54 €/MWh. Il file riporta controlli su copertura, allineamento e timestamp.

Nella presentazione, il grafico a barre contiene 192 valori di energia (uno per MTU); una barra è rossa soltanto se il prezzo GME Sud dello stesso quarto d'ora è esattamente 0 €/MWh. La produzione A75 è potenza media quartoraria, convertita in MWh con `MW × 0,25 h`.
