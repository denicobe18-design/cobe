# Luma Living — demo trgovina

Responzivni Streamlit demo katalog s pretragom i oglednom košaricom. Projekt se
može objaviti na Streamlit Community Cloudu, ali trenutačno **nije spreman za
primanje stvarnih narudžbi ili plaćanja**.

## Lokalno pokretanje

Potrebni su Python 3.10 ili noviji i pip:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Zatim otvori adresu koju Streamlit ispiše u terminalu (obično
`http://localhost:8501`).

## Objavljivanje na Streamlit Community Cloudu

1. Napravi GitHub repozitorij i prenesi projektne datoteke u njega. `app.py`
   mora biti u korijenu repozitorija.
2. Otvori [Streamlit Community Cloud](https://share.streamlit.io/) i prijavi se
   GitHub računom.
3. Odaberi **Create app**, zatim repozitorij, granu i putanju `app.py`.
4. U naprednim postavkama odaberi Python 3.12 ili noviji i klikni **Deploy**.
5. Nakon objave otvori dodijeljenu javnu adresu i provjeri katalog i košaricu.

Community Cloud instalira ovisnosti iz `requirements.txt`, a izgled aplikacije
čita iz `.streamlit/config.toml`.

## Važno prije stvarne prodaje

- Javno objavljena trenutna verzija je **samo demo**. Proizvodi, cijene,
  ocjene i tekstovi su ogledni. Košarica ne šalje narudžbe; plaćanje i dostava
  nisu povezani. Stranica zato izričito upozorava posjetitelje da ne upisuju
  osobne ni platne podatke.
- Prije pokretanja prodaje zamijeni ogledni katalog stvarnim artiklima i
  cijenama, zatim poveži sigurno spremanje narudžbi i pružatelja plaćanja.
- Dodaj stvarne podatke trgovca i podrške te pravne stranice (uvjeti prodaje,
  privatnost, kolačići, dostava i povrat) usklađene s poslovanjem i propisima.
- Tajne, API ključeve i vjerodajnice nikad ne spremaj u GitHub repozitorij.
  Ako ih aplikacija bude trebala, unesi ih kroz **Settings → Secrets** na
  Streamlit Community Cloudu i čitaj ih iz `st.secrets`.

Objavljivanje koda na javnom GitHub repozitoriju i deploy na Community Cloudu
objavit će demo na internetu; sama priprema projekta ne stvara GitHub račun,
repozitorij ni objavljenu adresu.
