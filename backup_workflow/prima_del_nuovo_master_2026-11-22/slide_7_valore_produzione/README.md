# Valorizzazione del profilo solare su base oraria

Caso descrittivo per le due slide finali della presentazione Electrade.

## Perimetro e fonti

- Zona Sud, separata da Calabria e Sicilia.
- Dal 12/11/2026 alle 00:00 al 14/11/2026 alle 00:00, estremo finale escluso, ora italiana CET (UTC+1). Nessun cambio d'ora nella finestra.
- Prezzi medi orari della zona Sud: `../slide_1_prezzi_pun_zone/20260101_20261115_MGP_PrezziZonali.xlsx`, colonna `Southern-Italy`, fonte GME.
- Produzione solare quartoraria in MW: `../slide_4_carico_production/dati/carico_produzione_48h.csv`, filtri `zone = IT Sud` e `source = solar`, fonte ENTSO-E A75.

L'impianto virtuale ha un profilo proporzionale alla produzione aggregata osservata. Ridimensionare tutti i valori per la stessa costante positiva non cambia prezzo ponderato e quota di energia a prezzo zero. I volumi assoluti nel dataset sono quelli della zona, non quelli di un singolo impianto reale.

## Aggregazione e calcoli

1. Allineare produzione e prezzi all'ora italiana di inizio intervallo. Nel file GME l'ora 1 indica 00:00-01:00.
2. Per ogni ora verificare la presenza dei quattro quarti d'ora 00, 15, 30 e 45.
3. Energia oraria in MWh = somma delle quattro potenze quartorarie in MW moltiplicate per 0,25 ore. Equivalentemente, potenza media dei quattro quarti moltiplicata per un'ora. Sommare soltanto i quattro valori in MW senza il fattore 0,25 sovrastimerebbe l'energia.
4. Valore teorico orario in euro = energia oraria per prezzo medio orario zonale.
5. Prezzo ponderato sulla produzione = somma dei valori teorici orari divisa per la somma dell'energia.
6. Prezzo medio della zona = media aritmetica dei 48 prezzi orari, incluse le ore notturne.
7. Scarto assoluto = prezzo ponderato meno prezzo medio. Scarto percentuale = prezzo ponderato diviso prezzo medio, meno uno.
8. Quota a prezzo zero = energia delle ore con prezzo medio esattamente zero divisa per l'energia totale. I prezzi negativi rimangono distinti.

## Risultati del caso

| Indicatore | Valore |
|---|---:|
| Prezzo medio zonale | 194,46 €/MWh |
| Prezzo ponderato sulla produzione solare | 87,24 €/MWh |
| Scarto assoluto | -107,22 €/MWh |
| Scarto percentuale rispetto alla media | -55,14% |
| Energia nelle ore a prezzo zero | 50,43% |
| Ore con prezzo medio zero | 5 |
| Ore con prezzo medio negativo | 0 |

Le cinque ore a prezzo esattamente zero del 13 novembre iniziano alle 10, 11, 12, 13 e 14 CET, equivalenti alle 9, 10, 11, 12 e 13 UTC. Coprono l'intervallo 10:00-15:00 CET, estremo finale escluso. Alle 09:00 CET il prezzo è invece positivo, pari a 0,0025 €/MWh: sul grafico con scala 0-300 appare prossimo alla linea dello zero. La slide evidenzia gli zeri esatti con marcatori e colonne arancioni.

Controlli eseguiti: 192 quarti d'ora, 48 ore complete, nessun timestamp duplicato, valori finiti e potenze non negative, concordanza dei timestamp UTC e locali, conservazione dell'energia nell'aggregazione. I file JSON riportano gli hash SHA-256 delle fonti.

## Interpretazione

Nel caso selezionato, circa metà della produzione solare coincide con le cinque ore a prezzo medio zero. Il prezzo medio ponderato sulla produzione è inferiore al prezzo medio della zona. Questo rende concreto il collegamento fra profilo temporale e valorizzazione spot della produzione.

Il calcolo è una stima descrittiva a prezzi medi orari. Moltiplicare l'energia oraria per il prezzo medio orario perde la covariazione fra produzione e prezzo all'interno dell'ora: non ricostruisce il valore quartorario esatto sul MGP. Il profilo è quello osservato a posteriori, non un programma di vendita day-ahead. Il calcolo esclude gli effetti di contratti, incentivi, costi, commissioni e sbilanciamenti.

Lo scarto dalla media non misura una perdita o un ricavo alternativo conseguibile. La finestra è selezionata per un evento di prezzo zero e non rappresenta la redditività annuale del solare.

## Riproduzione

Eseguire `analizza_valore_orario.py` con Python 3. Non richiede librerie esterne, token o accesso alla rete. Produce `dati/valorizzazione_oraria_sud.csv` e `dati/risultati.json`.

`aggiungi_slide.mjs` importa una copia della presentazione aggiornata da 18 slide, aggiorna i contatori, aggiunge due slide con grafici nativi modificabili e produce `../output_valorizzazione/Presentazione_Electrade_valorizzazione_oraria_orari_chiari.pptx`. La presentazione sorgente rimane invariata. Il builder richiede il runtime Node e la skill Presentations di Codex, i relativi percorsi come argomenti e la variabile `RUNTIME_NODE_MODULES`. Il finalizzatore non sovrascrive un risultato già esistente.
