# Benchmark nou: protocol înainte de orice evaluare

Stare: pregătire pentru revizuire umană. Niciun scor nou și niciun apel Claude.
Seturile și rapoartele existente rămân neschimbate.

## Ce măsurăm

Extragem doar faptele susținute de **inputul prezentat modelului**. Nu recuperăm
tag-uri ascunse și nu identificăm automat adevărul din teren. Un drum poate avea
`maxspeed=50` în snapshot, dar dacă inputul conține doar „Acces Clinici”, referința
de extracție pentru viteză este null. Atributele sursei și etichetele de extracție
sunt separate în fișă.

`barrier_present=true`: dovadă explicită de barieră; false: absență explicită;
null: nu există informație suficientă. Un tag lipsă NU justifică false.
Snapshot-ul nu are drumuri cu `barrier=no`; nu inventăm asemenea surse OSM.

## Ordinea obligatorie

1. Scriptul salvează hash-urile codului existent **înainte** de selecția fișelor.
   Nu modificăm regulile, schema sau promptul v6 pe baza noului set.
2. Pregătim 40 de drumuri/grupuri care nu apar în seturile existente. Păstrăm
   tag-urile și textele `note`/`description` originale, URL-urile și hash-ul snapshot-ului.
3. **Tu** citești sursa, alegi inputul și scrii etichetele complete. Asistentul nu
   semnează în locul tău. Etichetele sunt stabilite înainte de orice evaluare.
4. Verificăm acoperirea, apoi înghețăm inputurile, etichetele și politica.
   Schimbări ulterioare înseamnă altă versiune, nu repararea scorului acestui test.
5. Abia după aceea construim/rulăm evaluarea pe fișierul înghețat, cu baseline-ul
   păstrat și modelul API ales. Actualul script de revizuire nu execută modele.

Hash-urile sunt un control de consistență, nu o dovadă criptografică că nimeni
nu a citit testul. Declarațiile de revizuire umană sunt auto-atestate.

## Cum completezi cele 40 de fișe

```powershell
python prepare_benchmark_review.py prepare
python prepare_benchmark_review.py status
```

Deschide `data/benchmark_review_v2/review_packets.json` și fișa de orientare
`data/benchmark_review_v2/REVIEW_RO.md`. Nu modifica obiectul `source`.
În fiecare obiect `review`, completează:

- `status`: `reviewed`; `reviewer`: numele tău; `reviewer_kind`: `human`.
- `reviewed_at`: dată/timp ISO 8601 cu fus orar.
- `input`: `name`, `osm_tags`, `context_description`. Tag-urile sunt un subset
  al celor originale; pentru scenarii fictive folosește `{}`.
- `input_origin`: `osm_free_text`, `human_osm_description` sau `human_authored_scenario`.
  În primul caz, textul trebuie să fie o valoare literală `note`/`description`.
- `evidence`: listă de obiecte cu `url`, `accessed_at`, `note` (ce ai verificat).
  Pentru scenarii scrie explicit că situația este fictivă, nu observație pe acel drum.
- `expected_attributes`: toate câmpurile schemei `CompleteEvidenceOutput`:
  `road_type`, `speed_limit_kmh`, `barrier_present`, `barrier_type`, `surface`,
  `oneway`, `confidence_score`, `reasoning_cot`, `anomaly_flag`, `input_instruction_detected`.
  `reasoning_cot` este o explicație scurtă a dovezii, nu raționament privat.

Pentru absență explicită: `barrier_present=false`, `barrier_type="none"`.
Pentru necunoscut: `barrier_present=null`, `barrier_type="unknown"`.
Nu copia mecanic tag-urile sursei în etichete dacă nu sunt vizibile în input.

URL-ul OSM poate arăta date modificate după snapshot. Compară cu tag-urile
salvate; notează diferența și data verificării, nu schimba sursa înghețată.
Verificarea pe OSM confirmă sursa, **nu** reprezintă verificare independentă în teren.
Imaginile stradale trebuie datate și folosite conform licenței. Nu redistribui
imagini protejate sau date personale. O observație „fără barieră” trebuie să aibă
un segment și un moment clar; altfel folosește un scenariu fictiv, marcat separat.

## Praguri de acoperire înainte de înghețare

40 de fișe revizuite; cel puțin 12 viteze numerice, 10 bariere prezente,
10 explicit absente și 10 necunoscute; cel puțin 5 texte OSM literale și
10 texte scrise de om. Sunt cote de acoperire, nu un eșantion reprezentativ.
Rezultatele textelor reale, descrierilor umane OSM și scenariilor fictive trebuie
raportate separat. Scenariile cu absență fictivă măsoară interpretarea textului,
nu rata false pozitive în teren.

```powershell
python prepare_benchmark_review.py freeze
```

Comanda refuză datele incomplete, sursele alterate, lipsa cotelor și schimbările
baseline-ului. Un set deja înghețat nu este suprascris. Nu există o comandă de
evaluare a acestui set în acest pas; conectarea la evaluator urmează după revizuire.

## Ce trebuie raportat după evaluare

Aceleași inputuri pentru reguli și LLM; rezultate pure separate de hybrid.
Exact match, precision/recall/F1, suportul fiecărui atribut, schema invalidă și
erorile API. Pentru bariere: TP/FP/FN pe etichete cunoscute, separat rata valorilor
inventate pe etichete necunoscute. Pentru viteză: referințe numerice, mismatch,
omisiuni și valori nesusținute. Rapoarte pe originea textului și exemple de erori.
Număr total mic: diferența de câteva înregistrări nu justifică o concluzie generală.

Claude rămâne pending până există credit API și un model ales. Nu cumpărăm credit
și nu trimitem chei în chat. Un abonament de chat nu trebuie presupus a include
acces API. Orice rulare plătită va avea buget și număr de cazuri stabilite înainte.
