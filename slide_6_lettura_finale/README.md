# Slide 6 — Lettura finale e discussione aperta

> **Scopo finale:** chiudere l'analisi con una tabella spiegazione→evidenza→stato (confermata/da verificare/aperta), le domande aperte da girare all'esperto, e la chiusura "da desk": chi compra a prezzo zero, chi perde, perché la risposta è di sistema.

## Tabella: spiegazione → evidenza → stato

| Spiegazione | Evidenza nei dati | Stato |
|---|---|---|
| **Merit order: rinnovabili a costo nullo** | Surplus (produzione − carico) nelle ore a prezzo zero (slide 4, `02_surplus_7zone.png`); curva di offerta con tratto piatto a 0 €/MWh (slide 3, periodo 40) | Confermata |
| **Capacità di uscita ridotta** | Saturazione Sud→CentroSud: flusso fisico ≈ limite GME nelle ore a zero (slide 5, `export_sud_centrosud.png`); net import negativo (export) per Sud | Da verificare |
| **Lo zero non coincide col floor** | Prezzi negativi (−0,01 €/MWh) in Sud/Calabria/Sicilia; floor tecnico = −600 €/MWh (slide 1) | Confermata |
| **PUN maschera la divergenza** | PUN Index GME = 14 ore a zero vs 177–180 al Sud/Calabria/Sicilia (slide 1) | Confermata |
| **Lato domanda: pompaggi/domanda elastica** | Curve di domanda in slide 3 (solo 1 ora, periodo 40); da estendere | Aperta |
| **Surplus adj (surplus + net import)** | Surplus originale + net import fisico per Sud/Calabria/Sicilia (slide 4 + slide 5, `04_surplus_adj_3zone.png`) | Da verificare |

## Dati numerici di contesto (slide 1)

| Zona | Ore a zero (≤ 0) | Ore negative | Minimo (€/MWh) | Media (€/MWh) |
|---|---|---|---|---|
| Nord | 14 | 0 | 0,00 | 160,40 |
| Centro Nord | 14 | 0 | 0,00 | 160,97 |
| Centro Sud | 69 | 0 | 0,00 | 158,08 |
| Sud | 177 | 4 | −0,01 | 153,74 |
| Calabria | 178 | 4 | −0,01 | 153,27 |
| Sicilia | 180 | 4 | −0,01 | 160,15 |
| Sardegna | 91 | 6 | −2,03 | 151,26 |
| PUN Index GME | 14 | 0 | 0,00 | 159,38 |

## Evento scelto (slide 2)

**12 e 13 novembre 2026** (finestra di 48 ore). 5 ore consecutive a prezzo zero in Sud, Calabria e Sicilia (10:00–14:00 UTC) in entrambi i giorni. Il resto delle zone non tocca zero.

## Curve di domanda/offerta (slide 3)

Dati per un'unica ora (periodo 40 = 09:45-10:00 del 13/11/2026) per 7 mercati accoppiati. Grafico prodotto per 3 gruppi (Nord/Centro, Sud, Sardegna). L'intersezione si trova sul tratto piatto a prezzo zero della curva di offerta.

## Produzione e carico (slide 4)

- Surplus (produzione − carico) nelle ore a prezzo zero per Sud, Calabria, Sicilia.
- Fonti: solare, eolico, resto (idro + gas + altro).
- Carico e produzione da ENTSO-E (A65 + A75), granularita' 15 minuti, in parte estrapolato.
- Surplus adj = surplus + net import (slide 5).

## Flussi e transiti (slide 5)

- Net import per zona: Sud esporta ~2.568 MW verso Centro-Sud, importa da Calabria (~511 MW) e Grecia (~94 MW).
- Calabria: importa da Sud e Sicilia, esporta verso Sud e Sicilia.
- Sicilia: importa da Calabria, esporta verso Calabria e Malta.
- Saturazione Sud→CentroSud: flusso fisico ≈ limite GME/NTC nelle ore a zero.
- Surplus adj calcolato in `slide_5_mappa_transiti/nuovo/plot_surplus_adj.py`.

## Domande aperte per l'esperto

1. Il criterio (ore consecutive a zero in ≥ 2 zone) regge per scegliere l'evento?
2. L'indice nazionale (PUN) è il riferimento giusto o serve la mediana?
3. Su quale punto saresti più severo? "Prezzo zero = surplus non esportabile" regge?
4. Quale fonte è l'autorità sui limiti di transito (GME, Terna, ENTSO-E)?
5. Il net import da slide 5 coincide con il bilancio zonale (carico − produzione)?

## Chiusura "da desk"

- **Chi compra a prezzo zero:** chi ha domanda elastica o pompaggi (arbitraggio).
- **Chi perde:** i produttori che offrono a costo nullo (surplus non vendibile) — il loro surplus non esce dalla zona.
- **Perché la risposta è di sistema:** il prezzo zero non è un'anomalia, ma il risultato dell'interazione tra merit order (rinnovabili a costo nullo), capacità di uscita ridotta e floor tecnico. La soluzione non è abbassare il prezzo, ma aumentare la capacità di uscita o la domanda elastica.

---

**Stato:** bozza (19/11/2026). Da completare con la lista delle spiegazioni possibili (troncata nel piano originale) e i numeri definitivi.
