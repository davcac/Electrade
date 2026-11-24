# Why did the Italian day-ahead price go to zero in the South on 13 November 2026?

**Perché il prezzo del giorno prima italiano è andato a zero nel Sud il 13 novembre 2026?**

---

## Short answer / Risposta breve

**English:** Because Southern Italy was long by thousands of MW at midday, and the power
could not leave: the Sud → Centro-Sud corridor was running near its Terna transit limit,
the 500 MW link to Greece was at 100 %, and the third way out, Malta, is a 225 MW link.
Exactly when solar and wind were producing at peak in a zone that could only export a
fraction of its surplus, the marginal unit in the South was free energy, and the zonal
price fell to the market floor: **0.00 EUR/MWh for 23 consecutive quarter-hours
(09:15 – 15:00, Italian time)**, while the rest of Italy was priced at ~194 EUR/MWh
at the same moment.

**Italiano:** Perché il Sud Italia era lungo di migliaia di MW a metà giornata e
l'energia non poteva uscire: il corridoio Sud → Centro-Sud era vicino al limite di
transito Terna, il collegamento da 500 MW verso la Grecia era al 100 % e la terza
via d'uscita, Malta, è un collegamento da 225 MW. Proprio quando solare ed eolico
producevano al picco in una zona che poteva esportare solo una frazione del surplus,
l'unità marginale nel Sud era energia gratuita e il prezzo zonale è caduto al
minimo di mercato: **0.00 EUR/MWh per 23 quarti d'ora consecutivi (09:15 – 15:00,
ora italiana)**, mentre il resto d'Italia era prezzato a ~194 EUR/MWh nello stesso
momento.

---

## Key figures / Cifre chiave

| | |
|---|---|
| **Event / Evento** | Thursday 13 November 2026, Italian day-ahead market (MGP), 15-minute MTU |
| **Affected zones / Zone coinvolte** | IT Sud, IT Calabria, IT Sicilia |
| **Duration / Durata** | 23 quarter-hours (09:15 – 15:00 CET), all at exactly 0.00 EUR/MWh |
| **Rest of Italy, same midday / Resto d'Italia, stesso mezzogiorno** | IT Nord / Centro-Nord / Centro-Sud ~ 194.46 EUR/MWh (average of 192 MTU) |
| **Solar energy at zero price / Energia solare a prezzo zero** | 57.02 % of total solar production in the 48-hour window (9 020.25 MWh of 15 820.75 MWh) |
| **Solar capture price / Prezzo catturato dal solare** | 85.54 EUR/MWh vs 194.46 EUR/MWh simple average (-56.01 %) |
| **Demand/supply settlement / Prezzo di settlement** | 0.00 EUR/MWh (period 38, 09:15–09:30) |
| **Demand at settlement price / Domanda al prezzo di settlement** | 5 005.2 MW (BID at price ≥ 0) |
| **Supply plateau at 0 €/MWh / Gradino OFF a 0 €/MWh** | 5 465.5 – 7 855.1 MW |
| **Simple offers included / Offerte semplici incluse** | 146 MTU15 + 14 MTU60 (BID + OFF) |
| **Block offers / Offerte a blocchi** | 13 MTU15 + 5 MTU60 (BID + OFF) |
| **Accepted blocks / Blocchi accettati** | BID 2.0 MW (MTU60); OFF 2.0 MW (MTU15) |
| **Macro-zone / Macrozona** | CALA; SICI; SUD; GREC; MALT; XGRE |
| **Transit resolution / Risoluzione transiti** | A09 PT15 (scheduled); A11 PT15 (except Greece PT60); A61 NTC PT60 |

---

## 1. The event, quarter-hour by quarter-hour / L'evento, quarto d'ora per quarto d'ora

The price did not fall gradually: it collapsed to zero in a single quarter-hour and
stayed there for 23 consecutive MTU (09:15 – 15:00 CET). The zero-price window is
the same for all three southern zones: IT Sud, IT Calabria and IT Sicilia.

Il prezzo non è caduto gradualmente: è crollato a zero in un singolo quarto d'ora
e vi è rimasto per 23 MTU consecutivi (09:15 – 15:00 CET). La finestra a prezzo
zero è identica per tutte e tre le zone meridionali: IT Sud, IT Calabria e
IT Sicilia.

| MTU (CET) | IT Sud price (EUR/MWh) | Note |
|---|---:|---|
| 08:45 | > 0 | Prezzo positivo |
| **09:00** | > 0 | Ultimo MTU con prezzo positivo |
| **09:15** | **0.00** | Inizio della finestra a prezzo zero |
| 09:30 – 14:45 | **0.00** | 23 MTU consecutivi a zero |
| **15:00** | > 0 | Fine della finestra; prezzo positivo |

Sardegna ha 5 MTU a zero in momenti diversi (09:45, 13:00–13:15, 13:45–14:00 CET),
mentre Nord, Centro-Nord e Centro-Sud non hanno mai toccato zero nel periodo analizzato.

---

## 2. The mechanism: surplus, flows and capacity / Il meccanismo: surplus, flussi e capacità

### 2.1 Production vs load / Produzione vs carico

In the zero-price quarter-hours, the three southern zones produce more than they
consume. The generation net of storage absorption (A75 minus B10/B25/B32) exceeds
the load (A65) in several intervals.

Nei quarti a prezzo zero, le tre zone meridionali producono più di quanto
consumano. La generazione netta degli assorbimenti (A75 meno B10/B25/B32) supera
il carico (A65) in diversi intervalli.

- **Gross generation A75** is stacked by source: solar, wind, hydro, gas, other.
- **Net generation (purple dashed line)** = A75 immissions − A75 storage absorption
  (types B10, B25, B32). This is the series compared with the load.
- **Surplus** = net generation − load A65.

### 2.2 External flows / Flussi esterni

The three zones exchange with the rest of Italy and abroad. The analysis uses:

- **A09** (scheduled commercial exchanges, day-ahead, A01) — published at PT15.
- **A11** (physical flows) — PT15 on most borders, **PT60 on the Greece border**.
- **A61** (NTC, day-ahead capacity) — **PT60** on all available borders.

Nei grafici a 15 minuti, A11 Grecia e A61 sono mostrati a gradino (il valore orario
si ripete sui quattro quarti d'ora coperti). Non è una misura nativa PT15.

### 2.3 Macro-zone balance / Saldo della macrozona

Considering Sud, Calabria and Sicilia as a single macro-zone (CALA; SICI; SUD;
GREC; MALT; XGRE), the analysis shows:

- The macro-zone is a **net exporter** in many zero-price MTU.
- The adjusted surplus (net generation + net import A11 − load) shows how much
  energy remains after accounting for physical flows.
- The Sud → Centro-Sud corridor was running near the available NTC limit during
  the zero-price window.

---

## 3. Demand and supply curve / Curva di domanda e offerta

For period 38 (09:15–09:30 CET, 08:15–08:30 UTC), the GME demand/supply file
shows:

- **Supply curve (red)**: cumulative simple offers (OFF), ascending by price.
- **Demand curve (blue)**: cumulative simple bids (BID), descending by price.
- **Settlement price**: 0.00 EUR/MWh (read from the GME `Prezzo accettato` field).
- The aggregate curves do not intersect exactly at the settlement: BID quantity at
  price ≥ 0 is 5 005.2 MW, while the OFF plateau at 0 EUR/MWh spans 5 465.5–7 855.1 MW.
  This is expected for a coupled, multi-zone market: the macro-zone is not a closed
  balance.

Offerte semplici incluse: 146 MTU15 + 14 MTU60. Offerte a blocchi: 13 MTU15 + 5 MTU60
(riepilogate a parte, non convertite in gradini indipendenti).

---

## 4. Solar value capture / Valorizzazione del solare

A virtual solar plant in Southern Italy, with a profile proportional to the
observed A75 aggregate production, selling all energy at the MGP zonal price:

| Metric / Metrica | Value / Valore |
|---|---:|
| **Simple price average / Media aritmetica** | 194.46 EUR/MWh (192 MTU) |
| **Production-weighted average / Media ponderata** | 85.54 EUR/MWh |
| **Gap / Scarto** | -108.92 EUR/MWh (-56.01 %) |
| **Solar energy at zero price / Energia a prezzo zero** | 57.02 % (9 020.25 MWh of 15 820.75 MWh) |
| **MTU at exactly zero / MTU esattamente a zero** | 23 (09:15–15:00 CET) |

The weighted price is a descriptive capture price of the observed solar profile.
It is not a contractual revenue or an actual MGP settlement.

Il prezzo ponderato è un capture price descrittivo del profilo solare osservato.
Non è un ricavo contrattuale né un settlement MGP effettivo.

---

## 5. Caveats and methodological notes / Note metodologiche

* **Day-ahead, not real time.** All analysis refers to the MGP (day-ahead) auction.
  No intraday market data is used.
* **ENTSO-E sparse curves.** With curveType A03, a quarter-hour is written only
  when its value changes; the missing positions repeat the previous one. The
  processing scripts re-expand these series. Ignoring this shifts every timestamp.
* **Flow direction.** ENTSO-E publishes one document per direction; the net flow
  is `f(forward) − f(backward)`. The Greece border is published at hourly
  resolution, the Italian internal borders and Sicily–Malta at 15 minutes.
* **NTC is an hourly value** and is applied to every quarter-hour of that hour.
  The comparison with physical flow is between the hourly limit and the hourly
  average of the flow.
* **Storage absorption.** The net A75 generation subtracts storage absorption of
  PSR types B10, B25 and B32 (accumulators). The gross generation remains visible
  in the stacked area; the purple dashed line is the net series used for surplus.
* **Demand/supply aggregation.** The macro-zone is not a closed balance: the
  auction is coupled across zones, and export orders are not an isolated
  market balance.
* **15-minute vs hourly.** Annual daily/hourly price screening remains hourly
  because the 15-minute GME source covers only 12–13 November 2026. Where both
  resolutions are available, the 15-minute data is used.

---

## 6. How to reproduce / Come riprodurre

```powershell
# Prezzi zonali a 15 minuti (GME)
python "presentazione lunedì 23\slide_2_scelta_evento_p_zero\15 minuti\genera_prezzi_15min.py"

# Grafici carico/produzione a 15 minuti
python "presentazione lunedì 23\slide_4_carico_production\15 minuti\genera_grafici_15min.py"

# Transiti a 15 minuti dagli XML ENTSO-E
python "presentazione lunedì 23\slide_5_mappa_transiti\15 minuti\prepara_transiti_15min.py"
python "presentazione lunedì 23\slide_5_mappa_transiti\15 minuti\genera_grafici_transiti_15min.py"

# Curva domanda/offerta macrozona (periodo 38)
python "presentazione lunedì 23\slide_3_dem_supp_macrozone\15 minuti\plot_domanda_offerta_15min.py"

# Valorizzazione solare a 15 minuti
python "presentazione lunedì 23\slide_7_valore_produzione\15 minuti\analizza_valore_15min.py"
```

### The code / Il codice

| File | What it does / Cosa fa |
|---|---|
| `slide_2/15 minuti/genera_prezzi_15min.py` | Normalizza il file GME 15 min (192 MTU, 7 zone) e plotta i prezzi. |
| `slide_4/15 minuti/genera_grafici_15min.py` | Carico A65 + generazione A75 con linea A75 netta degli accumuli; surplus e surplus adj. |
| `slide_5/15 minuti/prepara_transiti_15min.py` | Espande gli XML ENTSO-E A09/A11/A61 su griglia 15 min, con risoluzione nativa nel CSV. |
| `slide_5/15 minuti/genera_grafici_transiti_15min.py` | Barre giornaliere, linee A09/A11, macrozona, produzione+net import, surplus adj. |
| `slide_3/15 minuti/plot_domanda_offerta_15min.py` | Curve di merito GME: supply rossa, demand blu, settlement 0 EUR/MWh. |
| `slide_7/15 minuti/analizza_valore_15min.py` | Prezzo medio aritmetico vs ponderato sulla produzione solare, 192 MTU. |

---

## 7. Sources / Fonti

| Data / Dato | Source / Fonte | Licence / Licenza |
|---|---|---|
| Day-ahead prices (MGP, PT15) | [GME](https://www.mercatoelettrico.org/) — MGP download | Public data |
| Load (A65), generation (A75) | [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/) | ENTSO-E terms of use (free, non-commercial) |
| Cross-border flows (A09, A11) | ENTSO-E Transparency Platform | ENTSO-E terms of use |
| Transit limits (A61/NTC) | [Terna download centre](https://dati.terna.it/download-center) | Public open data |
| Demand/supply curves | GME — ME_DemandAndSupply (MGP) | Public data |

Data retrieved for delivery days 12–13 November 2026 (15-minute MTU).
ENTSO-E is the primary source for flows and generation; Terna publishes the limits
GME uses in the day-ahead auction.

---

## 8. Author / Autore

**Davide Cacciari** - economics and energy markets.
[LinkedIn](https://www.linkedin.com/in/davide-cacciari) · [GitHub](https://github.com/davcac)

MIT licence - see [LICENSE](LICENSE).