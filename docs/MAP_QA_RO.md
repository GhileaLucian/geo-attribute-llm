# Ghid Map QA — proiect de portofoliu

## Pornire fără chei API

Din folderul proiectului, în PowerShell:

```powershell
python -m pip install -r requirements.txt
python run_mapqa.py all --mode rules --cached-only
python -m streamlit run app.py
```

Deschide http://localhost:8501 și fila **Map QA & ML**. Snapshot-ul și rapoartele
sunt incluse; nu trebuie să descarci din nou OSM sau să plătești un API.
Notebook-ul `notebooks/map_quality_analysis.ipynb` se execută din rapoarte salvate.
Harta afișează implicit un eșantion de 3.000 de geometrii, dar analiza folosește toate.

## Model local real prin LangChain

Ollama trebuie să fie pornit și să aibă modelul instalat:

```powershell
ollama pull qwen2.5:3b
python run_mapqa.py benchmark --mode langchain --prompt v6 --split dev
python run_mapqa.py benchmark --mode hybrid --prompt v6 --split hard
```

Aceste comenzi folosesc cache-ul atunci când cererea și modelul sunt neschimbate.
Replay fără Ollama / fără inferență:

```powershell
python run_mapqa.py benchmark --mode langchain --prompt v6 --split dev --cached-only
python run_mapqa.py benchmark --mode langchain --prompt v6 --split test_final --allow-holdout --cached-only
```

Nu regla promptul pe `test_final`. Versiunea v6 a fost înghețată înaintea evaluării.
Primul lot `test` a fost deja folosit de v5 și nu mai este un hold-out neatins.
Hold-out-ul vechi al sarcinii masked-tag rămâne separat și neatins.

## Ce acoperă din anunț

| Cerință | Implementare și dovadă |
|---|---|
| Prompt design / few-shot | v4/v5/v6, prompturi bilingve, mesaje salvate indirect prin fingerprint și cod versionat |
| Structured outputs | ChatOllama + LangChain + JSON Schema + Pydantic; v6 cere fiecare câmp |
| Map quality control | lungimi metrice, geometrii incomplete/intersecții, viteze suspecte, sens unic, bariere |
| Geospatial analysis | GeoPandas, Shapely, PyProj, UTM; asociere topologică și nearest-candidate separate |
| Benchmark | reguli vs LLM vs hybrid; precision/recall/F1, suport, matrice de confuzie, erori și rezultate brute |
| Ground truth curation | referințe derivabile din snapshot, verificare automată a integrității, coadă de review uman |
| LLM test-data generation | două propuneri generate local; carantină până la review, excluse din benchmark |
| Python / ML | pandas, NumPy, scikit-learn; clasificare RF, regresie RF, DBSCAN, IsolationForest |
| Prefect | flow cu task-uri, mod offline, deployment periodic, test limitat de programare |
| Jupyter / vizualizare | notebook executat, hartă PyDeck, matrici de confuzie și tabele comparative |
| Reproducibilitate | snapshot și split-uri SHA-256, seed-uri, versiuni pachete, cache, teste offline |

Acestea demonstrează un proiect practic, nu experiență profesională. Colaborarea
cu specialiști GIS, engleza, experiența cloud și benchmarkul cu Claude/OpenAI
nu pot fi create prin adăugarea de cod. Nu sunt declarate ca realizate.

## Date, referințe și limite

Snapshot separat: 14.591 de way-uri și 849 de noduri barrier din Cluj-Napoca,
descărcate prin Overpass. Datele includ geometria și ID-urile de noduri.
© OpenStreetMap contributors, [ODbL](https://www.openstreetmap.org/copyright).
Licența MIT a codului nu relicențiază baza OSM; fișierele de date/derivate OSM
rămân sub condițiile ODbL. Nu sunt incluse imagini satelitare sau date personale.

O barieră care împarte un nod cu drumul are conexiune topologică în snapshot;
asta nu dovedește singură că blochează toate vehiculele. O barieră apropiată
la maximum 10 m este numai candidat pentru review, nu etichetă confirmată.
Distanțele sunt în metri, nu grade. Geometriile incomplete sunt excluse, nu inventate.

Benchmarkul extrage informații explicite din texte controlate EN/RO, generate
din tag-uri și noduri reale. Nu este observație independentă de teren, test
reprezentativ pentru toate drumurile sau recuperare a informațiilor lipsă.
Eșantioanele prioritizează bariere: toate cele 40 de exemple finale au bariere;
nu măsoară false-positive pe absența barierei. Cazurile negative există doar
în setul fictiv de dezvoltare. Lotul final nu are limite numerice de viteză
și are doar trei referințe cunoscute pentru sens unic: procentul final nu
este o măsurare a extragerii vitezelor numerice. Textele repetitive produc cache hits între exemple:
numărul de segmente evaluate nu este numărul de cereri LLM unice.

Separarea pe nume de drum / way ID reduce suprapunerea directă, dar nu exclude
corelații între drumuri apropiate sau drumuri fără nume din aceeași zonă.
Scorurile ML prezic etichete OSM: nu sunt limite legale auditate. Clasificarea
exclude highway din features; regresia exclude maxspeed. Cluster-ele și cele
438 de sugestii IsolationForest nu sunt erori confirmate.

`reference_review_queue.json` are status pending. Referințele au trecut doar
verificarea automată împotriva sursei salvate. Propunerile LLM sunt și ele pending:
prima propunere folosește un tag `speed` și o explicație discutabilă — exemplu
concret de ce validarea JSON nu înlocuiește verificarea semantică umană.

## Programare

Test limitat, cu server local izolat și cleanup după terminare:

```powershell
python run_mapqa.py schedule-smoke
```

Deployment-ul periodic normal rulează numai cât comanda rămâne activă:

```powershell
python -m prefect server start
```

Într-un al doilea terminal PowerShell, din folderul proiectului:

```powershell
$env:PREFECT_API_URL = 'http://127.0.0.1:4200/api'
python run_mapqa.py serve --interval 3600
```

Folosește implicit reguli și snapshot local, fără API plătit. Ctrl+C oprește
runner-ul și pune deployment-ul pe pauză. Pe un server permanent, verifică și
dezactivează schedule-ul în Prefect dacă nu mai vrei să fie generate run-uri;
run-urile deja programate trebuie gestionate separat. Nu este instalat un
serviciu Windows persistent și nu a rămas activă o programare din smoke test.

Prefect 3.8.8 a eșuat la bulk insert cu SQLAlchemy 2.1.4 în acest mediu.
`requirements.txt` fixează SQLAlchemy la seria 2.0; versiunea verificată este
2.0.54. Schimbările de bulk DML din 2.1 sunt descrise în
[documentația SQLAlchemy](https://docs.sqlalchemy.org/en/21/orm/extensions/hybrid.html).

## Publicare și interviu

Publică sursele, testele, notebook-ul și rapoartele măsurate. Nu publica `.env`,
chei API, cache-uri Python, baze de date Prefect sau greutățile modelului.
Cheia API trimisă anterior în chat trebuie revocată; nu este folosită în această versiune.

La interviu explică diferența dintre structură validă și informație corectă,
de ce am făcut un hold-out nou și de ce scorul hibrid nu este numai efect de prompt.
Un răspuns bun include o limitare verificabilă, nu doar un procent.
