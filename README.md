# DOXA Quant Core

Papirnati kokpit za izazov **200 € → 1.000 € u 10 sati**. Svijeće i knjiga naloga
dolaze s Binance Vision toka (`data-api.binance.vision`), funding s OKX perpetuala.
`api.binance.com` i Binance futures često vrate 451 izvan nekih mreža, pa motor
koristi ove javne izvore. Svaki ulaz i izlaz plaća 0,10% naknade i klizanje iz
spreada. **Nijedan nalog ne ide na burzu** i ključ burze nije potreban.

Prošli rub ne jamči sljedeći. Kelly samo reže ulog; ne čini gubitak nemogućim.

## Što radi

Sedam agenata glasa, osmi uči:

1. **Whale** — neravnoteža L2 knjige (lokalni order book iz diff-deptha, 50 razina).
2. **BTC Guard** — pad BTC-a u 3 minute uz volumen; diže stop na ulaz i zabranjuje nove kupnje.
3. **Skeptik** — veto ako se poklope dvije crvene zastavice (volumen, funding, RSI 4h).
4. **Trail** — na +3% breakeven, na +5% pola pozicije, ostatak 2×ATR iza vrha.
5. **Radar** — brzi lokalni skor cijene, knjige i fundinga. Diže ulog samo unutar Kelly kapice.
6. **MTF** — 4h iznad EMA50, 1h RSI pada prema 45, 15m okret. Ulaza nema bez 3/3.
7. **Kelly** — polu-Kelly iz uzorka nakon 10 trejdova; do tada konzervativni prior.
8. **Učitelj** — nakon svakog zatvaranja miče pragove unutar tvrdih granica, u istom procesu.

## Pokretanje

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Adresa je obično `http://localhost:8501`. Dnevnik je `data/crypto_wallet.json`.

Na poslužitelju, bez sučelja:

```bash
python -m doxa.daemon
```

Drugi proces smije samo gledati. Dva motora se ne pokreću odjednom.

## Što trebaš napraviti sam

- Ništa, za papir. Javni Binance mora biti dohvatljiv s računala na kojem motor radi.
- Telegram: u `.env` stavi `TELEGRAM_BOT_TOKEN` i `TELEGRAM_CHAT_ID`.
- Vanjski učitelj: `TEACHER_URL` (i po želji `TEACHER_TOKEN`). Odgovor smije vratiti
  samo parametre unutar granica. Ako ga nema, lokalni učitelj radi sam.
- Poslužitelj blizu burze (Frankfurt ili Tokyo) i pravi novac nisu dio ovog koda.
  Pravi nalozi se namjerno ne šalju.
