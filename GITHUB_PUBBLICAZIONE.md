# Registro — preparazione repository GitHub `Electrade`

Data: 22/11/2026. Eseguito da: agente OpenCode, su richiesta di Davide.

## Stato prima

- Cartella `C:\Users\Utente\Desktop\opencode CLI\presentazione lunedì 23`
- Non era un repository Git (nessuna cartella `.git`)
- 119 file, circa 12,8 MB, di cui un file `__pycache__/create_master_pptx.cpython-314.pyc`
- Nessun segreto reale nei file: `ROADMAP.md` contiene solo i segnaposto `<LOGIN>` / `<PASSWORD>`;
  gli script `scarica_entsoe.py` e `scarica_transiti_entsoe.py` leggono `ENTSOE_TOKEN`
  da variabile d'ambiente o dal volume `A:\secrets.env`, mai da file nel progetto.
- GitHub CLI (`gh`) e GitHub Desktop non installati. `git` 2.56 presente, con
  `credential.helper=manager` (Git Credential Manager di Windows).

## Cosa ho fatto io (locale, nessun invio in rete)

1. `git init -b main`
   → creata cartella nascosta `.git`; ramo iniziale `main`.
2. Creato `.gitignore` con:
   ```
   __pycache__/
   *.pyc
   ```
3. `git add .` → 119 file in area di staging (cache Python esclusa).
   Git ha avvisato che su Windows convertirà LF → CRLF al prossimo checkout: comportamento
   normale di `core.autocrlf`, senza effetti sui contenuti.
4. `git status --short` → verificato che `__pycache__` non fosse presente.
5. `git commit -m "Analisi prezzi zero Electrade: deck, script, dati e grafici delle 6 slide"`
   → commit `024ee37`, 119 file, 142042 righe inserite.
6. Creato questo file e committato come secondo commit.

## Cosa deve fare Davide (pubblicazione — non fatto dall'agente)

1. Aprire https://github.com/new, fare il login.
   - Repository name: `Electrade`
   - Visibilità: **Private**
   - **Non** spuntare "Add a README file", ".gitignore" o license: il repo deve essere vuoto,
     altrimenti il primo push trova file già esistenti e viene rifiutato.
   - Creare il repository.
2. In PowerShell, copiare e incollare **una riga alla volta**:

```powershell
cd "C:\Users\Utente\Desktop\opencode CLI\presentazione lunedì 23"
git remote add origin https://github.com/davcac/Electrade.git
git push -u origin main
```

Spiegazione: `git remote add origin ...` registra l'indirizzo remoto nel file `.git/config`;
non scarica né carica nulla. `git push` invia il commit; `-u` collega `main` locale a
`origin/main`, così in futuro basta `git push`. Al primo push Git Credential Manager
chiederà il login a GitHub (finestra di autenticazione): le credenziali finiscono
nell'archivio credenziali di Windows, non nel repository.

3. Verifica dopo il push:

```powershell
git status
git log --oneline -3
```

`git status` deve dire `working tree clean` / `nothing to commit`.

## Nota

Il nome `davcac/Electrade` non risulta pubblico (verifica del 22/11/2026).
Se GitHub dicesse che il nome è già occupato, controllare se esiste un repo privato
con lo stesso nome: in quel caso usare quel repo (vuoto) invece di crearne uno nuovo.
