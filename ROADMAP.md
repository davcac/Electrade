# Roadmap — Presentazione Electrade (colloquio finale, lunedì 23/11/2026 ore 16:30)

> File di lavoro, modificabile da Davide in qualsiasi momento.
> Trascrizione **verbatim** del piano, 18/11/2026.
> Nota: il piano è stato fornito **troncato** nell'ultimo punto
> ("Considerazioni e discussione aperta ... le spiegazioni possibili sono:").
> Manca la lista delle spiegazioni possibili → da completare quando Davide la fornisce.

---

## REGOLA DI METODO (18/11/2026)

**Ogni passo deve essere chiaro, spiegato e replicabile a mano: se il progetto
fosse da rifare da solo, deve essere possibile rifarlo. Per ogni dato va saputo
*su quale sito* e *dove* è stato trovato.**

Ogni cartella di questo progetto corrisponde a **una slide** del piano e contiene
un `README.md` con: domanda della slide, output previsto, dati necessari, da dove
si prendono e — dove serve — i comandi equivalenti fatti a mano.

### Mappa delle cartelle = mappa delle slide

| cartella | slide | contenuto |
|---|---|---|
| `slide_1_prezzi/` | 1 · Prezzi | completata (18/11/2026): dati GME 1/1→15/11/2026, 4 script, 7 grafici |
| `slide_2_evento/` | 2 · Scelta dell'evento | completata (18/11/2026): evento scelto 12-13/11/2026, 2 grafici |
| `slide_3_curve_tempo/` | 3 · Curve nel tempo | parziale (18/11/2026): dati periodo 40 per 7 mercati, grafico per 3 gruppi |
| `slide_4_per_fonte/` | 4 · Per fonte e zona | completata (18/11/2026): dati ENTSO-E, CSV 14.564 righe, grafico prodotto |
| `slide_5_mappa_transiti/` | 5 · Mappa e transiti | (da fare) |
| `slide_6_lettura_finale/` | 6 · Lettura finale | bozza: tabella spiegazione→evidenza→stato, domande aperte, chiusura da desk. |
| — | deck | `Presentazione_Electrade_6_punti.pptx` + `make_briefing_pptx.py` |

### Scelte di metodo prese finora (18/11/2026)

- **Base di lavoro: prezzi orari** (`GranularityType=PT60`). Motivo: confrontabilità
  con i conteggi pubblicati (GME, Italia Solare, Renewo) e gestione del cambio
  dell'ora legale. Attenzione: `GranularityType` vale solo per MGP e solo dal
  1/10/2025; chiedendo PT15/PT30 prima di quella data non tornerebbe nulla.
- **Metodo di accesso ai dati di mercato: API GME**, di default.
- **Finestra di analisi: 48 ore**, scelta sul grafico annuale delle slide 1 e poi
 Zoom sul singolo scenario.

---

## REGISTRO DELLE FONTI (dove è stato trovato ogni cosa)

| cosa | fonte | dove |
|---|---|---|
| Protocollo API GME (endpoint, auth, richiesta dati, quote) | *Guida al servizio delle API* (15/10/2025) | https://www.mercatoelettrico.org/Portals/0/Documents/it-IT/20251015Manuale_tecnico_API.pdf — cap. 1 Endpoint, 2 Autenticazione, 3 Richiesta dati, 4 Quote utente |
| Campi di `ME_ZonalPrices` (FlowDate, Hour 1-25, Market, Zone, Price, Period, Notes) e `Attributes: GranularityType` | stessa guida | cap. 5.52 |
| `Zone = "PUN"` = PUN Index GME; zone di mercato NORD, CNOR, CSUD, SUD, CALA, SICI, SARD | stessa guida | cap. 5.52 e la specifica degli indicatori di spread |
| Elenco completo dei 57 dataset API (e conferma che **non** esiste un dataset con la produzione fisica) | stessa guida | indice del documento |
| Come ottenere le credenziali (form, PEC, cambio password, validità 6 mesi, contatti) | *Interfaccia API* + *Guida utente al servizio API* | https://www.mercatoelettrico.org/it-it/Home/InterfacciaAPI · https://www.mercatoelettrico.org/Portals/0/Documents/it-IT/20251015Manuale_tecnico_Utente_API.pdf |
| Prezzi MGP letti a mano (controllo incrociato) | sito GME, Esiti MGP | https://www.mercatoelettrico.org/it-it/Home/Esiti/Elettricita/MGP/Esiti/PrezziZonali |
| Passaggio a 15 minuti dal 1/10/2025 (SDAC) | GME Relazione Annuale 2025, BOX 1 | https://gme.mercatoelettrico.org/Portals/0/Documents/it-IT/Gme_RelazioneAnnualeWeb_2025.pdf |
| GME conta le ore a zero fino al 30/09/2025 e i quarti d'ora dopo: la metrica cambia con il mercato | GME Relazione Annuale 2025, Tab. 2.1.4 | idem |
| Limite tecnico minimo di offerta (-500 €/MWh, poi -600 €/MWh dal 29/05/2026) | Avviso GME 07/05/2026 su DTF 20 MPE rev. 04 | https://www.mercatoelettrico.org/it-it/Home/AvvisieComunicati/AvvisieComunicatiME?id=7484 |
| Prezzo zero = intersezione col tratto piatto a 0, non il floor | GME "Vademecum Borsa Elettrica" + RSE "Il mercato del giorno prima (MGP)" | https://gme.mercatoelettrico.org/Portals/0/Documents/it-IT/20260131VademecumBorsaElettrica.pdf · https://www.rse-web.it/wp-content/uploads/2024/02/02_MGP.pdf |
| Dati di produzione per zona e tecnologia (fisici, non di mercato) | ENTSO-E Transparency, art. 16.1.b "Actual Generation per Production Type" | https://transparency.entsoe.eu/ |
| Per l'Italia il dato orario ENTSO‑E è in parte estrapolato e viene rivisto a D+1 e D+40 | ENTSO‑E, nota sul Paese Italia in "Detailed Data Descriptions" | https://eepublicdownloads.entsoe.eu/clean-documents/Transparency/MoP_Ref2_DDD_v3r4.pdf |
| Esempio di grafico già fatto (aree impilate per fonte + carico) | `energy-data/log/15_grafici_2026-10-19_17-12-07.png` | cartella `energy-data/` |
| Esempi esterni di ore a prezzo zero nel 2026 (solo come benchmark, non usati nei dati) | Italia Solare, GME Newsletter, Renewo | https://www.italiasolare.eu/ · https://gme.mercatoelettrico.org/Portals/0/Documents/Newsletter/20261116Newsletter.pdf |

### Protocollo API GME in forma eseguibile a mano

```powershell
# 1) token (cap. 2)
curl.exe -X POST "https://api.mercatoelettrico.org/request/api/v1/Auth" `
  -H "Content-Type: application/json" `
  -d "{\"Login\":\"<LOGIN>\",\"Password\":\"<PASSWORD>\"}"

# 2) dati (cap. 3) - PT60 = prezzi orari
curl.exe -X POST "https://api.mercatoelettrico.org/request/api/v1/RequestData" `
  -H "Content-Type: application/json" -H "Authorization: Bearer <TOKEN>" `
  -d "{\"Platform\":\"PublicMarketResults\",\"Segment\":\"MGP\",\"DataName\":\"ME_ZonalPrices\",\"IntervalStart\":20260101,\"IntervalEnd\":20260107,\"Attributes\":{\"GranularityType\":\"PT60\"}}"

# 3) quote (cap. 4)
curl.exe -H "Authorization: Bearer <TOKEN>" "https://api.mercatoelettrico.org/request/api/v1/GetMyQuotas"
```

La risposta del punto 2 ha `ContentResponse` = **base64 di uno zip** con dentro il
`.json` dei dati.

---

## Stato della slide 1 — completata il 18/11/2026

**Dati:** scaricati a mano dal sito GME (Esiti MGP → Prezzi zonali) per il periodo
1/1/2026 → 15/11/2026, 7.656 ore (24 h/giorno; 23 il 29/03, 25 il 25/10).
File: `20260101_20261115_MGP_PrezziZonali.xlsx` (7 zone + Italia) e
`20260101_20261115_PUN.xlsx` (PUN Index GME). Verifica: la colonna "Italia" del
file zonale coincide esattamente col PUN file (differenza massima 0,0000).

**Grafici prodotti** (in `slide_1_prezzi/grafici/`):
- `01_serie_prezzi_mgp.png` — serie orarie delle 8 grandezze, con le ore a prezzo
  zero evidenziate (banda rossa attorno allo zero)
- `02_heatmap_ore_zero.png` — heatmap zona × mese, conteggio ore a prezzo zero
- `03_statistiche_zero.txt` — statistiche complete

**Risultati (ore a prezzo zero, ≤ 0 €/MWh)**

| zona | ore a zero | ore negative | minimo (€/MWh) | media (€/MWh) |
|---|---|---|---|---|
| Nord | 14 | 0 | 0,00 | 160,40 |
| Centro Nord | 14 | 0 | 0,00 | 160,97 |
| Centro Sud | 69 | 0 | 0,00 | 158,08 |
| Sud | 177 | 4 | −0,01 | 153,74 |
| Calabria | 178 | 4 | −0,01 | 153,27 |
| Sicilia | 180 | 4 | −0,01 | 160,15 |
| Sardegna | 91 | 6 | −2,03 | 151,26 |
| PUN Index GME | 14 | 0 | 0,00 | 159,38 |

**Sequenze consecutive più lunghe di ore a prezzo zero**

| zona | n. sequenze (≥ 3 ore) | più lunga |
|---|---|---|
| Sud, Calabria, Sicilia | 26 | 9 ore (12/05/2026 09:00 → 17:00) |
| Centro Sud | 11 | 8 ore (12/05/2026 09:00 → 16:00) |
| Sardegna | 12 | 8 ore (12/05/2026 09:00 → 16:00) |
| Nord, Centro Nord | 2 | 5 ore (01/05/2026 10:00 → 14:00) |

**Candidati per la finestra di 48 ore dello scenario (slide 2):**
- **12/05/2026** (9 ore consecutive a zero in Sud, Calabria, Sicilia) — evento lungo e pulito
- **14/10/2026** (8 ore consecutive, con prezzi negativi fino a −0,01 €/MWh) — evento spettacolare

**Cosa è emerso (per la chiave di lettura finale):**
- il prezzo zero è concentrato al Sud, in Calabria e in Sicilia (177-180 ore), mentre al Nord e al Centro Nord è marginale (14 ore); la Sardegna è stabile (91 ore)
- sono comparsi i **primi prezzi negativi del MGP italiano** (−0,01 €/MWh in Sud, Calabria, Sicilia; −2,03 €/MWh in Sardegna): il floor tecnico (−600 €/MWh dal 29/05/2026) non è il limite che conta, il prezzo zero è il prezzo dell'offerta marginale accettata
- il PUN Index GME è una media ponderata per gli acquisti e maschera la divergenza fra zone (media 159,38 €/MWh, mentre il Sud è a 153,74 e la Sardegna a 151,26)

---

---

## Stato della slide 2 \u2014 completata il 18/11/2026

**Evento scelto:** 12 e 13 novembre 2026 (finestra di 48 ore). 5 ore consecutive a
prezzo zero in Sud, Calabria e Sicilia in entrambi i giorni; il resto delle zone
non tocca zero.

**Grafici prodotti** (in `slide_2_evento/grafici/`):
- `01_serie_per_zona_novembre.png` \u2014 7 pannelli, prezzo orario MGP per zona, 1/11 \u2192 15/11/2026
- `02_serie_per_zona_12_13_novembre.png` \u2014 7 pannelli, prezzo orario MGP per zona, 12-13/11/2026 (48 ore)

**Script:** `plot_novembre_per_zona.py`, `plot_12_13_novembre_per_zona.py` (input: `slide_1_prezzi/20260101_20261115_MGP_PrezziZonali.xlsx`).

---

## Stato della slide 3 \u2014 parziale (18/11/2026)

**Dati:** `DemandAndSupplyME_20261113_40_MGP_{nord,centronord,centrosud,sud,calabria,sicilia,sardegna}.xlsx`
(7 mercati accoppiati), periodo 40 = 09:45-10:00 del 13/11/2026. Ogni file ha fogli
`Simple offers` e `Block offers`.

**Grafici prodotti** (in `slide_3_curve_tempo/grafici/`):
- `01_domanda_offerta_nord.png` \u2014 mercato Nord/Centro
- `01_domanda_offerta_sud.png` \u2014 mercato Sud
- `01_domanda_offerta_sardegna.png` \u2014 mercato Sardegna

**Script:** `plot_domanda_offerta.py` (solo 3 dei 7 mercati). L'obiettivo originale
(small multiples per tutte le 48 ore + heatmap ora \u00d7 livello di prezzo) non e' stato
realizzato: servirebbero i file `DemandAndSupplyME` per ogni ora della finestra.

---

## Stato della slide 4 \u2014 completata il 18/11/2026

**Dati:** ENTSO-E Transparency (A65 load + A75 generation) per le 7 zone italiane,
finestra 12-13/11/2026. 14 XML grezzi in `slide_4_per_fonte/dati/` +
`carico_produzione_48h.csv` (14.564 righe, granularita' 15 minuti).

**Grafico prodotto:** `slide_4_per_fonte/grafici/01_produzione_carico_7zone.png`
(7 pannelli, generazione impilata per fonte + carico).

**Script (due step):**
- `scarica_entsoe.py` \u2014 download + CSV (richiede volume A: montato)
- `plot_produzione.py` \u2014 grafico da CSV (non richiede il volume)
- `scarica_produzione_entsoe.py` \u2014 script monolitico originale (riferimento)

---

## Stato finale (20/11/2026)

Tutti e 6 i punti hanno un README aggiornato con scopo finale.

| Slide | Stato | Cartella |
|---|---|---|
| 1 · Prezzi | completata | `slide_1_prezzi_pun_zone/` |
| 2 · Scelta evento | completata | `slide_2_scelta_evento_p_zero/` |
| 3 · Curve nel tempo | parziale (1 ora, 3 mercati) | `slide_3_dem_supp_macrozone/` |
| 4 · Per fonte e zona | completata (surplus semplice) | `slide_4_carico_production/` |
| 5 · Mappa e transiti | in corso (net import, saturazione, surplus adj) | `slide_5_mappa_transiti/` |
| 6 · Lettura finale | bozza | `slide_6_lettura_finale/` |

**Prossimi passi:** completare slide 3 (più ore), slide 5 (saturazione definitiva), slide 6 (lista spiegazioni possibili + numeri definitivi).

## Domanda guida

> Perché in alcune ore del 2026 il prezzo zonale di alcune zone italiane è andato a zero?

## 1. Prezzi

Scarico dal GME i prezzi orari del PUN nazionale e delle sette zone per il 2026 e li plotto sullo stesso grafico. Gestisco le ore duplicate o mancanti del cambio ora legale. Il PUN serve da riferimento visivo.

## 2. Scelta dell'evento

Dal grafico osservo che in alcune ore il prezzo di alcune zone va a zero. Scelgo un singolo evento particolarmente lungo, motivo la scelta e restringo l'analisi a quel periodo. Mostro le curve di domanda e offerta del GME per un'ora dell'evento, per illustrare cosa succede quando il prezzo è a zero, in particolare dove la domanda interseca il tratto piatto dell'offerta. Verifico anche il floor di prezzo previsto dalle regole di mercato.

## 3. Curve di domanda e offerta nel tempo

Estendo il passaggio precedente a più ore dell'evento, per vedere come cambia l'intersezione.

## 4. Domanda e offerta per fonte, per zona

Per ciascuna delle sette zone, nelle ore dell'evento, plotto dal GME i volumi di domanda (acquisti) e i volumi di offerta venduti per fonte o tecnologia, tenendo distinti i pompaggi se il dato lo permette. Confronto la zona con prezzo zero con le altre nelle stesse ore. Usando una sola fonte, già organizzata per zona di mercato, evito la mappatura regione-zona.

## 5. Mappa e transiti

Costruisco una mappa delle zone di mercato analizzate e degli interconnettori con gli altri paesi, usando l'ENTSO-E Transparency Platform e i dati Terna. Per le ore dell'evento, confronto flusso programmato e capacità disponibile su ciascun collegamento, e verifico se i prezzi ai due lati divergono. Per i limiti di transito tra le zone interne uso il GME, e Terna per il piano di indisponibilità di rete. Prima di fissare il piano controllo che tutti questi dati siano effettivamente pubblicati e in quale formato.

## 6. Considerazioni e discussione aperta

Non essendo un esperto del settore, chiudo riportando ciò che emerge dai grafici e lascio il dibattito aperto con chi valuta l'analisi. Come chiave di lettura finale, le spiegazioni possibili sono:

<!-- DA COMPLETARE: lista delle spiegazioni possibili (troncata nel piano originale) -->

---

## Scelta dell'evento (18/11/2026)

**Evento scelto: 12 e 13 novembre 2026.** Finestra di 48 ore, una per slide.

Motivazione: il 12/11/2026 il prezzo orario va a zero per 5 ore consecutive in
Sud, Calabria e Sicilia (09:00-13:00 circa); il 13/11/2026 lo stesso per 5 ore.
Il resto delle zone (Nord, Centro Nord, Centro Sud, Sardegna) non tocca zero.
Questo è l'evento a prezzi zero più recente (il più recente con prezzi negativi
resta il 14/10/2026, in ottobre, con −0,01 €/MWh in Sud/Calabria/Sicilia).

Grafici prodotti:
- `slide_2_evento/grafici/01_serie_per_zona_novembre.png` (1/11 → 15/11, 7 pannelli)
- `slide_2_evento/grafici/02_serie_per_zona_12_13_novembre.png` (12-13/11, 48 ore, 7 pannelli)

Da qui in poi l'analisi (curve di domanda/offerta, per fonte, mappa e transiti)
è riferita a queste 48 ore.
