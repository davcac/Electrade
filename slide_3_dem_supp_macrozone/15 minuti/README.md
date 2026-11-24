# Curve aggregate domanda/offerta — periodo 38

Grafico GME-style per la macrozona indicata nel file `../DomandaOffertaME_20261113_38_MGP.xlsx`, il 13/11/2026, periodo 38. Gli orari GME sono in ora italiana: 09:15–09:30 CET (08:15–08:30 UTC).

## Esecuzione

```powershell
cd "C:\Users\Utente\Desktop\opencode CLI"
python "presentazione lunedì 23\slide_3_dem_supp_macrozone\15 minuti\plot_domanda_offerta_15min.py"
```

Output:

- `grafici/domanda_offerta_macrozona_20261113_periodo38.png` — supply rossa, demand blu, entrambe a gradini; prezzo di settlement evidenziato.
- `dati/curve_macrozona_20261113_periodo38.csv` — livelli di prezzo aggregati, quantità offerte/accettate e quantità cumulata.

Le curve di merito includono le offerte **semplici** MTU15 e MTU60 presenti nel file. Il prodotto semplice orario può incrociarsi con i prodotti da 15 minuti nel coupling: per questo i MW MTU60 restano MW e non vengono divisi per quattro. Riferimento: [descrizione pubblica EUPHEMIA](https://nemo-committee.eu/assets/files/euphemia-public-description.pdf), sezione sul cross-matching tra prodotti di diversa risoluzione.

Le **offerte a blocchi** non sono convertite in gradini indipendenti, perché la loro accettazione è vincolata su più intervalli; i volumi accettati sono riportati nella nota del grafico. Il settlement letto dal campo GME `Prezzo accettato` è 0,00 €/MWh. Nel file aggregato, la quantità BID cumulata al prezzo di settlement e l'inizio del gradino OFF a 0 €/MWh non coincidono (circa 5.005 MW contro 5.466 MW); il grafico mostra il settlement ma non inventa un punto di intersezione esatto.
