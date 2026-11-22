# Slide 4 — Chi offre davvero: volumi per fonte e zona

> **Scopo finale:** mostrare il carico e la produzione fisica per fonte (solare, eolico, resto) per le 7 zone italiane sulla finestra di 48 ore (12-13/11/2026), per capire quale fonte offre il surplus che schiaccia il prezzo a zero.

> **Nota:** il surplus semplice (produzione - carico) e' il risultato di questa slide. Il "surplus adj" (surplus + net import) richiede i net import di slide 5 e viene calcolato in `slide_5_mappa_transiti/nuovo/plot_surplus_adj.py`.

**Domanda:** l'offerta che schiaccia il prezzo e' rinnovabile, idroelettrica o gas?

**Output previsto (prodotto):**
- `dati/` — XML grezzi ENTSO-E (A65 load + A75 generation per le 7 zone) + dataset tidy CSV
- `grafici/01_produzione_carico_7zone.png` — 7 pannelli (uno per zona): generazione impilata per fonte + carico, sulla finestra di 48 ore (12-13/11/2026)

**Approccio: ENTSO-E Transparency Platform** (non piu' GME). Nel punto 4 dell'analisi ci spostiamo dai prezzi (GME) alla produzione fisica e al carico (ENTSO-E). Il token arriva da `A:\secrets.env` (`ENTSOE_TOKEN`), montato dall'utente quando OpenCode e' spento.

## Come lanciare (due step separati)

Step 1 - download (richiede il volume A: montato, OpenCode spento):
```powershell
cd "C:\Users\Utente\Desktop\opencode CLI"
python "presentazione lunedì 23\slide_4_per_fonte\scarica_entsoe.py"
# smontare A: prima di riaprire OpenCode
```

Step 2 - grafico (non richiede il volume, funziona anche con OpenCode aperto):
```powershell
cd "C:\Users\Utente\Desktop\opencode CLI"
python "presentazione lunedì 23\slide_4_per_fonte\plot_produzione.py"
```

Opzioni step 1: `--start YYYY-MM-DD` · `--end YYYY-MM-DD` (default: 12-13/11/2026) · `--out` (cartella output).
Opzioni step 2: `--csv` (percorso CSV) · `--out` (percorso PNG).

Il vecchio script monolitico `scarica_produzione_entsoe.py` resta come riferimento.

## File della cartella
- `scarica_entsoe.py` — step 1: download A65+A75 per le 7 zone, parsing XML, scrittura CSV tidy (`dati/carico_produzione_48h.csv`). Richiede token ENTSO-E.
- `plot_produzione.py` — step 2: legge il CSV e produce `grafici/01_produzione_carico_7zone.png`. Non richiede token.
- `scarica_produzione_entsoe.py` — script monolitico originale (download + grafico in un solo passo), conservato come riferimento.
- `dati/` — 14 XML grezzi (A65+A75 per 7 zone) + `carico_produzione_48h.csv` (14.564 righe, granularita' 15 minuti)
- `grafici/01_produzione_carico_7zone.png` — grafico prodotto (18/11/2026)

## Dati scaricati
- **A65** (Actual Total Load) per bidding zone: carico per zona (risoluzione 15 minuti per l'Italia)
- **A75** (Actual Generation per Production Type): generazione per tipo (solare, eolico, idroelettrico, gas, altro)
- 7 zone italiane (EIC ENTSO-E = bidding zone = zona di mercato GME): IT Nord, IT Centro-Nord, IT Centro-Sud, IT Sud, IT Calabria, IT Sicilia, IT Sardegna
- Nota: il dato orario ENTSO-E per l'Italia e' in parte misurato e in parte estrapolato, revisionato a D+1 e D+40.

## Note sul grafico
- Le fonti A75 sono aggregate in 3 serie: solare, eolico, resto (idro + gas + altro).
- I punti rossi sull'asse x indicano le ore a prezzo zero (13/11/2026, 10:00-14:00) per Sud, Calabria, Sicilia.
- Il carico (nero) e la generazione (aree impilate) vengono entrambi da ENTSO-E.

## Fonti e dove le ho trovate
- Client ENTSO-E di riferimento (codice gia' pubblicato): `github/entsoe-repo/src/entsoe.py` (funzioni `read_token`, `download`, `parse_load_or_generation`, `expand_series`)
- Download pattern: `github/entsoe-repo/src/download.py` (A65 + A75 per le 7 zone)
- Documentazione ENTSO-E Transparency: https://transparency.entsoe.eu/
- Specifica del dataset A75: https://transparencyplatform.zendesk.com/hc/en-us/articles/16648290299284-Actual-Generation-per-Production-Type-16-1-B-C
- Nota per l'Italia: il dato orario e' in parte misurato e in parte estrapolato. Vedi "Detailed Data Descriptions" v3r4: https://eepublicdownloads.entsoe.eu/clean-documents/Transparency/MoP_Ref2_DDD_v3r4.pdf
- Grafico di riferimento (stesso stile): `energy-data/log/15_grafici_2026-10-19_17-12-07.png` (aree impilate per fonte + carico)

## Differenza rispetto ai dati GME
- **GME** da' l'offerta/vendita in asta (il lato mercato: prezzi, curve, rifiuti). Il grafico del punto 4 e' il lato **fisico**: produzione effettiva immessa in rete e carico misurato.
- Le due grandezze non coincidono: la differenza e' l'energia venduta OTC, l'autoconsumo e il surplus tagliato.
- Coerenza del confronto: entrambe le grandezze (produzione e carico) vengono da ENTSO-E, quindi sono misurate allo stesso modo.

**Stato:** completato (18/11/2026). Dati scaricati, CSV (14.564 righe) e grafico prodotti. Script separati in due step.
