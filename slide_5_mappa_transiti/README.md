# Slide 5 — Mappa e transiti: perché il surplus non esce

> **Scopo finale:** calcolare i flussi fisici (A11) e commerciali (A09) tra le zone a prezzo zero e i loro vicini, per ottenere il net import per zona (da sommare alla produzione totale). Usare il surplus di slide 4, aggiungere il net import e ottenere il surplus adj (surplus + net import). Inoltre, verificare se e quanto e' satura la connessione Sud-CentroSud, dedotta come possibile responsabile dei prezzi a zero.

**Domanda:** è un problema di rete? quale vincolo limita l'uscita dalla zona?

**Output previsto:** mappa schematica delle zone di mercato e degli interconnettori (spessore = capacità, colore = congestione) + barre del limite di trasferimento per ora nella finestra dell'evento, contro il valore normale.

**Dati necessari**
- limiti di transito fra zone, per ora → `ME_TransmissionLimits (MGP)`
- flussi e saturazione per coppia di zone → `ME_Transits (MGP)`
- limiti di trasferimento fra aree e piano di manutenzione → Terna
- flussi programmati e capacità sui confini → ENTSO-E Transparency
- prezzi ai due lati del vincolo: se divergono, il vincolo è saturo → `ME_ZonalPrices (MGP, PT60)`

**Stato:** in corso (19/11/2026). Dati scaricati: transiti ENTSO-E (A11/A09/A61) per 6 confini delle zone a zero + limiti GME (ME_TransmissionLimits). Script: scarica_transiti_entsoe.py, elabora_limiti_gme.py, plot_import_export.py, plot_import_export_linee.py, plot_macrozone.py, plot_export_capacity.py, plot_saturazione_sud_centrosud.py, plot_surplus_adj.py. Grafici in grafici/ e nuovo/grafici/. Il "surplus adj" (surplus + net import) e' calcolato in nuovo/plot_surplus_adj.py.
