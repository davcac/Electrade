# Slide 2 — Scelta dell'evento: il criterio, non la preferenza

> **Scopo finale:** scegliere, con criterio (ore consecutive a prezzo zero), la finestra di 48 ore da analizzare, e mostrare le serie dei prezzi zonali per novembre e per le 48 ore dell'evento.

**Domanda:** quale evento analizzo, e con quale criterio?

**Output previsto (prodotto):**
- tabella degli eventi candidati (data, zona, ore consecutive a prezzo zero, prezzo minimo) — vedi `ROADMAP.md` (sezione "Stato della slide 1")
- `grafici/01_serie_per_zona_novembre.png` — 7 pannelli, prezzo orario MGP per zona, 1/11 → 15/11/2026
- `grafici/02_serie_per_zona_12_13_novembre.png` — 7 pannelli, prezzo orario MGP per zona, 12-13/11/2026 (48 ore)

**Dati necessari**
- sequenze di ore consecutive a prezzo zero per zona → `ME_ZonalPrices (MGP, PT60)`, elaborazione di `slide_1_prezzi/dati/` (file `20260101_20261115_MGP_PrezziZonali.xlsx`)
- prezzi di tutte le zone nelle 48 ore dell'evento → stesso dataset
- curva domanda/offerta di un'ora: prezzo, quantità offerta e accettata → `ME_DemandAndSupply (MGP)` con il campo `Hour` (dati in `slide_3_curve_tempo/`, periodo 40 = 09:45-10:00 del 13/11/2026)
- limiti tecnici di offerta e regole di formazione del prezzo → DTF 20 MPE e Disciplina del mercato elettrico, artt. 41-42

**Evento scelto (18/11/2026): 12 e 13 novembre 2026.** Finestra di 48 ore.

Motivazione: il 12/11/2026 il prezzo orario va a zero per 5 ore consecutive in
Sud, Calabria e Sicilia (09:00-13:00 circa); il 13/11/2026 lo stesso per 5 ore.
Il resto delle zone (Nord, Centro Nord, Centro Sud, Sardegna) non tocca zero.
Questo e' l'evento a prezzi zero piu' recente (il piu' recente con prezzi negativi
resta il 14/10/2026, in ottobre, con −0,01 €/MWh in Sud/Calabria/Sicilia).

**File della cartella**
- `plot_novembre_per_zona.py` — produce `grafici/01_serie_per_zona_novembre.png` (7 pannelli, 1/11 → 15/11)
- `plot_12_13_novembre_per_zona.py` — produce `grafici/02_serie_per_zona_12_13_novembre.png` (7 pannelli, 12-13/11)
- `grafici/` — output dei due script

**Stato:** completato (18/11/2026).
