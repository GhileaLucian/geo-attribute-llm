# Pregătire pentru interviu — răspunsuri susținute de proiect

Folosește răspunsurile ca puncte de pornire, nu ca text memorat. Spune ce ai
implementat și testat, nu că ai experiență de producție. Adaptările Claude/OpenAI
nu sunt un benchmark reușit: apelurile OpenAI anterioare au eșuat.

## 1. Tell me about yourself

“I am developing my Python and AI workflow skills through practical projects.
For this role, I built GeoAttribute-LLM: a road-attribute extraction and map QA
pipeline. I used AI-assisted coding, then checked outputs with tests and saved
evaluation reports. It is a portfolio project, not a production system.”

Nu declara experiență de lucru, educație sau nivel de engleză care nu este în CV.

## 2. What does your project do?

“It extracts explicit road facts into structured JSON and compares predictions
with reference labels. A separate GIS workflow analyzes road geometries and
barrier nodes from an OSM snapshot of Cluj-Napoca. The Streamlit app displays
saved results; changing a map filter does not call a model.”

Arată `app.py`, `src/mapqa_flow.py`, `src/mapqa_benchmark.py`.
Nu spune că repară automat harta sau că toate etichetele sunt adevăr de teren.

## 3. How did you improve the prompt?

“I tested versions on development data. With v5, the model often omitted fields
that had schema defaults. In v6 I required every field and explicitly instructed
the model to put observed facts in those fields. Development exact match changed
from 2.5% to 81.25%. Both schema and prompt changed, so I cannot attribute the
improvement to the prompt alone.”

Arată `CompleteEvidenceOutput` și `evidence_messages` în `src/mapqa_evidence.py`.
JSON valid nu înseamnă fapte corecte. Nu cere raționamentul privat al modelului;
proiectul cere un scurt rezumat al dovezilor, deși câmpul vechi se numește `reasoning_cot`.

## 4. Did the LLM beat the baseline?

“Not convincingly. On 80 development texts, Qwen 3B scored 81.25% exact match
and the rules scored 82.5%. On the final 40-record sample, it was 90% versus
87.5%, a difference of one record. That sample has no numeric speed references
and only positive barrier cases, so it does not establish general superiority.”

Pe cele 15 cazuri dificile de dezvoltare: reguli 100%, LLM 80%.
Nu le prezenta ca test independent și nu promite că un model mai mare va câștiga.

## 5. What do precision, recall and F1 mean?

“For barrier detection, precision is the proportion of predicted barriers that
are correct. Recall is the proportion of reference barriers that are found.
F1 balances precision and recall. I also report sample support and extraction
failures; an unknown reference is not a negative barrier example.”

Exemplu: TP=8, FP=2, FN=4 → precision=8/10=0.8; recall=8/12≈0.667;
F1=2TP/(2TP+FP+FN)=16/22≈0.727. Un set doar cu bariere prezente nu măsoară
false pozitive pe drumuri explicit fără barieră. Cod: `src/mapqa_benchmark.py`.

## 6. Where does your ground truth come from?

“The current references are normalized OSM tags and topologically attached
barrier nodes. The texts are mostly controlled transcriptions of those same
sources. Automated checks verify source consistency, not independent field
truth. A new benchmark is pending human review before any evaluation.”

Un tag verificat pe openstreetmap.org confirmă sursa OSM, nu situația actuală
din teren. Imagini datate sau observații independente sunt un alt nivel de dovadă.

## 7. How do you handle missing data and malicious instructions?

“Missing evidence stays null or unknown. I do not invent legal speed limits
from a road category. Instructions embedded in road descriptions are untrusted
data. The output can flag an attempted instruction separately from conflicting
road observations.”

`oneway=-1` este tot sens unic. `maxspeed:conditional` singur nu este o limită
generală. Un pod nu implică o barieră. Cazurile sunt în `data/mapqa/evidence_hard.json`.

## 8. Why did you use a projected coordinate system?

“Longitude and latitude are angular coordinates. I project this local dataset
to UTM zone 34N, EPSG:32634, so lengths and distance thresholds use metres.
I distinguish a barrier sharing a road node from a nearby candidate.”

Cluj este în zona UTM 34N. Nu presupune aceeași proiecție pentru orice țară.
O barieră conectată geometric nu dovedește că toate vehiculele sunt blocate.
Cod: `src/mapqa_geo.py`.

## 9. What ML methods did you use?

“I used random forests for exploratory classification and regression, compared
with majority and median baselines. DBSCAN groups nearby road centroids using
distance in metres. Isolation Forest proposes records for review; it does not
prove they are mapping errors.”

`eps=200` este raza vecinătății DBSCAN în metri, `min_samples=8` pragul de
densitate; nu am cerut opt clustere. `contamination=0.03` stabilește aproximativ
3% sugestii, nu descoperă automat rata reală de erori. Cod: `src/mapqa_ml.py`.
Nu prezenta regresia maxspeed drept identificare a limitei legale.

## 10. How do you prevent leakage?

“The original ML split groups roads by name, with IDs for unnamed roads, and
keeps groups apart. However, nearby roads can still cross the split. I therefore
compare a geographic hold-out and versions with and without coordinates.
Preprocessing is fitted only on the training partition.”

Pentru grupuri, 25% se referă la grupuri, nu obligatoriu la 25% din înregistrări.
Pentru LLM: dezvoltare separată de test; referințe stabilite înainte de evaluare;
reguli și prompturi înghețate. Nu ajustezi regulile după vizualizarea noului test.
Dacă auditul spațial nu a rulat încă, spune „I plan to compare”, nu „I compared”.
Auditul este acum salvat: pe zona estică F1 ponderat este 0,629 cu coordonate
și 0,632 fără. Vezi `docs/SPATIAL_ML_AUDIT_RO.md`; nu interpreta diferența
ca dovadă cauzală sau absență completă de leakage.

## 11. What did you actually run with LangChain and Prefect?

“LangChain called the local Ollama model through ChatOllama with a JSON schema.
I saved actual responses and errors. Prefect runs the offline QA tasks, and I
completed a scheduled smoke test on a local server. The current Map QA tasks
have retries set to zero; scheduling and API retries are different mechanisms.”

Cod: `src/mapqa_evidence.py`, `src/mapqa_flow.py`, `src/mapqa_schedule.py`.
Nu spune Claude/OpenAI testat cu succes, cloud deployment sau rulare exclusiv pe CPU.

## 12. What would you do next, and how would you collaborate?

“I would agree with a map expert on what counts as a barrier and what evidence
is sufficient. Then I would have a mixed reference set reviewed before running
the frozen baseline and a funded API model. I would share error examples, support
counts and limitations, and use feedback to design a separate development set.”

Aceasta este abordarea propusă, nu o colaborare profesională deja realizată.
Pentru salariu discută așteptările tale; proiectul nu dovedește bugetul acestui job.

## Demonstrație de 5 minute, fără cost API

1. Pornește `python -m streamlit run app.py`; arată harta din Map QA & ML.
2. Deschide README: scop, 81.25% vs 82.5%, limitele testului final.
3. Arată schema obligatorie și o eroare salvată, nu doar exemple reușite.
4. Explică diferența dintre null și false pentru o barieră.
5. Arată notebook-ul executat și fișele noi încă nerevizuite.

Repetă fără aplicație aceste patru idei: metri vs grade; JSON valid vs fapt corect;
unknown vs absent; dezvoltare vs test înghețat. Dacă nu poți explica un modul,
spune ce ai verificat și ce mai trebuie să înveți; nu improviza rezultate.
