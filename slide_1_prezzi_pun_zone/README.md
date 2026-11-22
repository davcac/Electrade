# Slide 1 — Prezzi: la mappa delle ore a prezzo zero

> **Scopo finale:** mostrare se e quando i prezzi nell'anno hanno toccato zero, per il PUN Index GME e per ciascuna delle 7 zone di mercato.

**Domanda:** dove e quando il prezzo zonale va a zero?

**Output previsto (prodotto):**
- `grafici/01_serie_prezzi_mgp.png` — serie orarie del PUN Index GME e delle 7 zone dal 1/1/2026 al 15/11/2026, con le ore a prezzo zero evidenziate
- `grafici/02_heatmap_ore_zero.png` — heatmap zona × mese con il conteggio delle ore a prezzo zero
- `grafici/03_statistiche_zero.txt` — conteggi, sequenze consecutive, min/max, per zona

Cosa contiene questa cartella:

| file | cosa è |
|---|---|
| `20260101_20261115_MGP_PrezziZonali.xlsx` | dati GME scaricati a mano: prezzi orari delle 7 zone + Italia (PUN) + mercati esteri |
| `20260101_20261115_PUN.xlsx` | PUN Index GME orario (stesso periodo) |
| `plot_prezzi.py` | script che produce i 3 grafici/statistiche sopra (orari) |
| `plot_prezzi_daily.py` | variante giornaliera (stessi 3 file, suffisso `_DAILY`) |
| `plot_prezzi_per_zona.py` | 7 grafici, uno per zona, solo prezzi zonali (`04_serie_per_zona.png`) |
| `grafici/` | output degli script |
| `README.md` | questo file |

---

## 1. Da dove vengono i dati (scaricati a mano)

Fonte: sito GME, pagina Esiti MGP → Prezzi zonali
https://www.mercatoelettrico.org/it-it/Home/Esiti/Elettricita/MGP/Esiti/PrezziZonali

1. aprire la pagina, accettare le condizioni generali del sito (banner "CONTINUA SU MERCATOELETTRICO.ORG")
2. selezionare il periodo 01/01/2026 → 15/11/2026 e il formato Excel
3. scaricare il file "Prezzi zonali" → `20260101_20261115_MGP_PrezziZonali.xlsx`
4. scaricare il file "PUN" (PUN Index GME) per lo stesso periodo → `20260101_20261115_PUN.xlsx`

Il file zonale ha 26 colonne: `Date`, `Hour`, `Italia`, `Italy (unconstrained)`, `Austria`, `Calabria`, `Central-northern Italy`, `Corsica AC`, `Corsica`, `Centeral-southern Italy`, `France`, `Greece`, `North`, `Sardegna`, `Sicilia`, `Slovenia`, `Southern-Italy`, `Switzerland`, `Slovenia Coupling`, `France Coupling`, `Austria Coupling`, `Malta`, `Montenegro`, `Greece Coupling`, `IT-Coupling`, `Notes`. Le 7 colonne delle zone italiane sono: `North`, `Central-northern Italy`, `Centeral-southern Italy`, `Southern-Italy`, `Calabria`, `Sicilia`, `Sardegna`.

Il file PUN ha `Date`, `Hour`, `€/MWh` (= PUN Index GME).

Verifica fatta: la colonna `Italia` del file zonale coincide esattamente con il PUN file (differenza massima 0,0000).

## 2. Produrre i grafici

```powershell
cd "C:\Users\Utente\Desktop\opencode CLI"
python "presentazione lunedì 23\slide_1_prezzi\plot_prezzi.py"
```

Output in `slide_1_prezzi/grafici/`.

## 3. Cosa dice il dato (verifica sui numeri)

Periodo: 1/1/2026 → 15/11/2026, 7.656 ore (24 h/giorno; 23 il 29/03, 25 il 25/10).

**Ore a prezzo zero (≤ 0 €/MWh) per zona**

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
| Sud, Calabria, Sicilia | 26 | 9 ore (12/05/2026, 09:00 → 17:00) |
| Centro Sud | 11 | 8 ore (12/05/2026, 09:00 → 16:00) |
| Sardegna | 12 | 8 ore (12/05/2026, 09:00 → 16:00) |
| Nord, Centro Nord | 2 | 5 ore (01/05/2026, 10:00 → 14:00) |

Candidati per la finestra di 48 ore dello scenario (slide 2): il **12/05/2026** (9 ore consecutive a zero in Sud, Calabria, Sicilia) oppure il **14/10/2026** (8 ore consecutive, con prezzi negativi fino a −0,01 €/MWh). Scelta finale (18/11/2026): **12 e 13 novembre 2026** (5 ore consecutive a zero in Sud, Calabria, Sicilia in entrambi i giorni) — vedi `slide_2_evento/README.md`.

## 4. Cosa significa per la lettura

- Il PUN Index GME è una media ponderata per gli acquisti: riassume la divergenza fra zone e **non** la mostra.
- Il prezzo zero è concentrato al Sud, in Calabria e in Sicilia (177-180 ore nel periodo), mentre al Nord e al Centro Nord è marginale (14 ore). La Sardegna è stabile (91 ore) — non ha avuto l'aumento marcato delle altre zone.
- Sono comparsi i primi prezzi negativi del MGP italiano (−0,01 €/MWh in Sud, Calabria, Sicilia; −2,03 €/MWh in Sardegna): il floor tecnico (−600 €/MWh dal 29/05/2026) non è il limite che conta; il prezzo zero è il prezzo dell'offerta marginale accettata.

## 5. Per un controllo incrociato senza API

Gli stessi prezzi si leggono a mano su https://www.mercatoelettrico.org/it-it/Home/Esiti/Elettricita/MGP/Esiti/PrezziZonali (download annuale). Serve a validare che i numeri dei grafici tornino.

## 6. Note tecniche sul dato

- Granularità: oraria (24 ore per giorno, 23 il 29/03/2026, 25 il 25/10/2026). Il cambio dell'ora legale è gestito con timezone `Europe/Rome`.
- Verifica fatta: la colonna `Italia` del file zonale coincide esattamente con il PUN file (differenza massima 0,0000 su 7.656 righe).
- Il grafico di riferimento già fatto: `energy-data/log/15_grafici_2026-10-19_17-12-07.png` (stesso stile: aree impilate per fonte + carico).

## 7. Grafico per zona (7 pannelli, solo prezzi zonali)

Per vedere, zona per zona, il profilo orario del prezzo (il PUN Index GME è escluso):

```powershell
cd "C:\Users\Utente\Desktop\opencode CLI"
python "presentazione lunedì 23\slide_1_prezzi\plot_prezzi_per_zona.py"
```

Output: `grafici/04_serie_per_zona.png` — 7 pannelli (4×2, l'ultimo con la legenda), ciascuno con la serie oraria della zona, la banda attorno allo zero e il rug delle ore a prezzo zero (con il conteggio nel titolo). Serve a scegliere, zona per zona, la finestra di 48 ore del caso di studio.

## 8. Variante giornaliera (prezzi medi del giorno)

Stessi due file di input, scaricati in formato daily invece che hourly:
`20260101_20261115_MGP_PrezziZonali_daily.xlsx` e `20260101_20261115_PUN_daily.xlsx`.

```powershell
cd "C:\Users\Utente\Desktop\opencode CLI"
python "presentazione lunedì 23\slide_1_prezzi\plot_prezzi_daily.py"
```

Output in `grafici/` (suffisso `_DAILY` per non sovrascrivere gli orari):
- `01_serie_prezzi_mgp_DAILY.png` — serie giornaliere (linee + marker), PUN Index + 7 zone
- `02_heatmap_prezzi_DAILY.png` — heatmap zona × mese, prezzo medio giornaliero (annotato in €/MWh)
- `03_statistiche_zero_DAILY.txt` — statistiche giornaliere per zona

**Differenza rispetto alla versione oraria (importante):** sul prezzo giornaliero (media del giorno) **non esistono giorni a prezzo zero** — il minimo giornaliero è 51,81 €/MWh in Sardegna. Le ore a prezzo zero sono un fenomeno intra-giornaliero e richiedono i dati orari (vedi `01_serie_prezzi_mgp.png`). La variante giornaliera serve a vedere il livello medio e la stagionalità; quella oraria serve a vedere il fenomeno.

## Stato

Completato (18/11/2026): dati scaricati a mano dal sito GME (1/1/2026 → 15/11/2026), 4 script di plot, 7 grafici in `grafici/`. Lo scenario scelto per le slide successive e' il 12-13/11/2026.
