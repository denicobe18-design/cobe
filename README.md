# DOXA Quant Core

Papirnati kokpit za naredbu **200 € → 1.000 € u 60 minuta**. Ako sat istekne
bez cilja, ili kapital padne ispod minimalnog uloga, ured se zatvara. Svijeće i
knjiga naloga dolaze s Binance Vision toka (`data-api.binance.vision`), funding
s OKX perpetuala. `api.binance.com` i Binance futures često vrate 451 izvan
nekih mreža, pa motor koristi ove javne izvore. Svaki ulaz i izlaz plaća 0,10%
naknade i klizanje iz spreada. **Nijedan nalog ne ide na burzu** i ključ burze
nije potreban.

Živa cijena odlučuje. Pet puta u jednom satu nije zajamčeno i rezultat se ne
namješta. Stari dnevnik od 10 sati se na prvom pokretanju zamjenjuje novim
satom od 200 €.

Svaki agent vodi svoju igru i pamti njezin rub:

- **Whale** vodi knjigu kad je bid zid jak, i dip kad se 1m RSI diže iz dna.
- **MTF** vodi momentum čim je okret tu, bez čekanja da svih šest kaže da.
- **Radar** vodi nalet kad je cijena i knjiga u hypu.
- Potrebna je jedna potvrda drugog mozga. Skeptik i BTC Guard i dalje mogu zaustaviti ulaz.
- Igra koja četiri puta završi u minusu postaje hladna i taj agent je više ne nudi.
- Trejd koji za četiri minute nije ni taknuo plus grebe se, da kapital ide u sljedeću igru.

Živa cijena i dalje odlučuje o dobiti.

## Što radi

Sedam agenata glasa, osmi uči:

1. **Whale** — neravnoteža L2 knjige (lokalni order book iz diff-deptha, 50 razina).
2. **BTC Guard** — pad BTC-a u 3 minute uz volumen; diže stop na ulaz i zabranjuje nove kupnje.
3. **Skeptik** — veto ako se poklope dvije crvene zastavice (volumen, funding, RSI).
4. **Trail** — na +0,45% breakeven, na +0,7% zatvara 65%, ostatak 1,2×ATR. Početni stop je 0,45%, cilj 1,2% i tada se ostatak odmah zatvara.
5. **Radar** — brzi lokalni skor cijene, knjige i fundinga. Diže ulog samo unutar Kelly kapice.
6. **MTF** — brzi ulaz: 15m iznad EMA21 i 1m okret. Bez 1m svijeća ostaje stari 4h/1h/15m stack.
7. **Kelly** — donji ulog je 12% da stane više pozicija odjednom, papirnata poluga 10×. Gotovina izlazi samo kao margin plus naknada, ne cijeli nominal.
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
