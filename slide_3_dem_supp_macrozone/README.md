# Slide 3 — Curve di domanda e offerta nel tempo

> **Scopo finale:** mostrare le curve di domanda e offerta per un'ora dell'evento (periodo 40, 09:45-10:00 del 13/11) per illustrare l'intersezione sul tratto piatto a prezzo zero, per i mercati accoppiati Nord/Centro, Sud e Sardegna.

**Domanda:** nelle ore successive l'intersezione si sposta davvero?

**Output previsto (stato attuale):**
- `grafici/01_domanda_offerta_nord.png` — curva domanda/offerta per il mercato Nord/Centro (periodo 40)
- `grafici/01_domanda_offerta_sud.png` — curva domanda/offerta per il mercato Sud (periodo 40)
- `grafici/01_domanda_offerta_sardegna.png` — curva domanda/offerta per il mercato Sardegna (periodo 40)

**Dati necessari (presenti)**
- curve domanda/offerta di ogni ora della finestra → `ME_DemandAndSupply (MGP)`, selezione oraria (campo `Hour`)
- file presenti: `DemandAndSupplyME_20261113_40_MGP_{nord,centronord,centrosud,sud,calabria,sicilia,sardegna}.xlsx` (7 mercati accoppiati), periodo 40 = 09:45-10:00 del 13/11/2026
- per ora: quantità offerta per livello di prezzo e quantità accettata → `Price`, `Quantity`, `AcceptedQuantity` (colonne `Offered price(€/MWh)`, `Offered quantity(MW)`, `Accepted quantity(MW)`)
- volume offerto a prezzo zero: variabile che spiega la persistenza → stesso dataset
- prezzo zonale delle altre zone nella stessa ora → `ME_ZonalPrices (MGP, PT60)`

**Script**
- `plot_domanda_offerta.py` — legge 3 file (nord, sud, sardegna), concatena Simple offers + Block offers, costruisce le curve di offerta (crescente) e domanda (decrescente), traccia il prezzo di equilibrio e evidenzia il tratto piatto a prezzo zero. Output: 3 PNG in `grafici/`.

**Stato:** parziale (18/11/2026). Dati scaricati per un'unica ora (periodo 40, 09:45-10:00 del 13/11/2026) per 7 mercati accoppiati; grafico prodotto per 3 gruppi (Nord/Centro, Sud, Sardegna). L'obiettivo originale (small multiples per tutte le 48 ore + heatmap ora × livello di prezzo) non e' stato realizzato: servirebbero i file `DemandAndSupplyME` per ogni ora della finestra.
