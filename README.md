# DOXA Quant Core

Papirnati kokpit za naredbu **100 € → 1.000 € u 24 sata, uz najmanje 1.000 trejdova**.
Ured staje tek kad su na računu i novac i kvota. Ako dan istekne bez oba uvjeta,
ili kapital padne ispod minimalnog uloga, ured se zatvara. Svijeće i
knjiga naloga dolaze s Binance Vision toka (`data-api.binance.vision`), funding
s OKX perpetuala. `api.binance.com` i Binance futures često vrate 451 izvan
nekih mreža, pa motor koristi ove javne izvore. Svaki ulaz i izlaz plaća 0,10%
naknade i klizanje iz spreada. **Nijedan nalog ne ide na burzu** i ključ burze
nije potreban.

Živa cijena odlučuje. Deset puta veći račun kroz tisuću trejdova traži da
prosječni trejd zaradi oko 0,90 € nakon naknade. To se ne događa samo zato
što je naredba upisana, i rezultat se ne namješta. Stari sat od 200 € na
prvom pokretanju postaje novi dan od 100 €.

Svaki agent vodi svoju igru i pamti njezin rub:

- **Whale** vodi knjigu kad je bid zid jak, i dip kad se 1m RSI diže iz dna.
- **MTF** vodi momentum čim je okret tu, bez čekanja da svih šest kaže da.
- **Radar** vodi nalet kad je cijena i knjiga u hypu.
- Potrebna je jedna potvrda drugog mozga. Skeptik i BTC Guard i dalje mogu zaustaviti ulaz.
- Igra koja četiri puta završi u minusu postaje hladna i taj agent je više ne nudi.
- **Tempo** vodi protok čim je knjiga iznad ask zida, posebno dok kvota od 1.000 trejdova kasni.
- Trejd koji 50 sekundi nije ni taknuo plus grebe se. Učenje gleda zadnjih 40 trejdova i radi veći korak.
- Poluga je 5×, ulog oko 4%, da tisuću ulaza uopće stane u 100 €. Na 10× bi naknada pojela račun prije kvote.

Živa cijena i dalje odlučuje o dobiti.

## Što radi

Sedam agenata glasa, osmi uči:

1. **Whale** — neravnoteža L2 knjige (lokalni order book iz diff-deptha, 50 razina).
2. **BTC Guard** — pad BTC-a u 3 minute uz volumen; diže stop na ulaz i zabranjuje nove kupnje.
3. **Skeptik** — veto ako se poklope dvije crvene zastavice (volumen, funding, RSI).
4. **Trail** — na +0,45% breakeven, na +0,7% zatvara 65%, ostatak 1,2×ATR. Početni stop je 0,45%, cilj 1,2% i tada se ostatak odmah zatvara.
5. **Radar** — brzi lokalni skor cijene, knjige i fundinga. Diže ulog samo unutar Kelly kapice.
6. **MTF** — brzi ulaz: 15m iznad EMA21 i 1m okret. Bez 1m svijeća ostaje stari 4h/1h/15m stack.
7. **Kelly** — donji ulog je 4% kapitala, papirnata poluga 5×. Gotovina izlazi samo kao margin plus naknada, ne cijeli nominal. Zadnjih 40 trejdova uči brže od cijelog dnevnika.
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
