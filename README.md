# DOXA Quant Core

Papirnati kokpit za naredbu **100 € → 200 € u jednom satu**. Sat na ekranu je cilj.
Kad sat istekne, motor i dalje ulazi. Ured staje kad je 200 € na računu nakon
naknade, ili kad kapital padne ispod minimalnog uloga od 2 €. Svijeće i
knjiga naloga dolaze s Binance Vision toka (`data-api.binance.vision`), funding
s OKX perpetuala. `api.binance.com` i Binance futures često vrate 451 izvan
nekih mreža, pa motor koristi ove javne izvore. Svaki ulaz i izlaz plaća 0,10%
naknade i klizanje iz spreada. **Nijedan nalog ne ide na burzu** i ključ burze
nije potreban.

Živa cijena odlučuje. Udvostručiti 100 € u satu traži niz trejdova koji nakon
naknade ostanu u plusu. To se ne događa samo zato što je naredba upisana, i
rezultat se ne namješta. Stari dan (misija `day-1000`) na prvom pokretanju
postaje novi sat od 100 €.

Svaki agent vodi svoju igru i pamti njezin rub:

- **Whale** vodi knjigu kad je bid zid jak, i dip kad se 1m RSI diže iz dna.
- **MTF** vodi momentum čim je okret tu, bez čekanja da svih šest kaže da.
- **Radar** vodi nalet kad je cijena i knjiga u hypu.
- Skeptik (dvije zastavice) i BTC Guard i dalje mogu zaustaviti jedan ulaz. Učitelj više ne gasi cijeli ured.
- Igra koja četiri puta završi u minusu postaje hladna i taj agent je više ne nudi.
- **Tempo** i dalje vodi protok čim knjiga nije ask zid i spread je podnošljiv, pa hladna igra ne zaustavlja trejdanje.
- Trejd koji 25 sekundi nije ni taknuo plus grebe se. Učenje gleda zadnjih 40 trejdova i radi veći korak.
- Poluga je 5×, ulog oko 4%. Na 10× bi naknada pojela račun prije cilja.
- Ured u sučelju je Three.js scena: povlačenje rotira, kotačić bliži, desni klik pomiče. Kamera ostaje dok se brojevi osvježavaju.

Živa cijena i dalje odlučuje o dobiti.

## Što radi

Sedam agenata glasa, osmi uči:

1. **Whale** — neravnoteža L2 knjige (lokalni order book iz diff-deptha, 50 razina).
2. **BTC Guard** — pad BTC-a u 3 minute uz volumen; diže stop na ulaz i zabranjuje nove kupnje.
3. **Skeptik** — veto ako se poklope dvije crvene zastavice (volumen, funding, RSI).
4. **Trail** — na +0,3% breakeven, na +0,6% zatvara 70%, ostatak 1,2×ATR. Početni stop je 0,4%, cilj 1,0%.
5. **Radar** — brzi lokalni skor cijene, knjige i fundinga. Diže ulog samo unutar Kelly kapice.
6. **MTF** — brzi ulaz: 15m iznad EMA21 i 1m okret. Bez 1m svijeća ostaje stari 4h/1h/15m stack.
7. **Kelly** — donji ulog je 4% kapitala, papirnata poluga 5×. Gotovina izlazi samo kao margin plus naknada, ne cijeli nominal. Zadnjih 40 trejdova uči brže od cijelog dnevnika.
8. **Učitelj** — nakon svakog zatvaranja miče pragove unutar tvrdih granica. Slab uzorak reže Kelly, ali ne gasi ulaze.

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
