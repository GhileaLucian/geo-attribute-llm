# Archived README — published experiment history

This preserves the README from commit f58c842 before the front page was shortened.
Measured reports and datasets are unchanged. Relative links below are historical;
use the current root README for working navigation.

# GeoAttribute-LLM

## Map QA + local LangChain + ML (new)

An offline-first portfolio pipeline with actual Cluj-Napoca road geometry:
14,591 OSM ways, 849 barrier nodes, metric GIS checks, bilingual evidence
extraction, a real LangChain/ChatOllama adapter, classification, regression,
clustering, an executed notebook and a Streamlit map. No paid API call is needed.

```powershell
python -m pip install -r requirements.txt
python run_mapqa.py all --mode rules --cached-only
python -m streamlit run app.py
```

Open the **Map QA & ML** tab. Saved artifacts work without Ollama.
To run the local model, start Ollama, install `qwen2.5:3b`, then:

```powershell
python run_mapqa.py benchmark --mode langchain --prompt v6 --split dev
python run_mapqa.py benchmark --mode hybrid --prompt v6 --split hard
python run_mapqa.py schedule-smoke
```

Measured v6 results (exact match across all eight evaluated fields):

| Dataset | n | Rules | Local LangChain | Hybrid guards |
|---|---:|---:|---:|---:|
| Controlled OSM-derived development text | 80 | 82.5% | 81.25% | 81.25% |
| Fictional hard development cases | 15 | 100% | 80% | 86.7% |
| Fresh grouped final controlled-text test | 40 | 87.5% | 90% | 90% |

The final difference is **one record**, not evidence of general superiority.
All final examples have barriers, so barrier false-positive performance is not
measured there. Texts are generated from OSM tags, not independent field truth.
The final sample has **zero numeric speed references** and only three known
one-way references; speed extraction is not measured by that final score.
Per-class support, failures, raw responses and actual error examples are saved
in `reports/mapqa/benchmarks`; repetitive inputs share cached responses.

v4/v5 allowed omitted optional fields; the model often described facts only in
its explanation. v6 requires every output field explicitly. The first evidence
test was consumed by v5; a fresh disjoint grouped test was reserved before
freezing v6. Earlier experiments are retained, not overwritten with better scores.

Exploratory grouped-test ML: road-family weighted F1 **0.703** versus majority
baseline **0.290** (3,549 test ways); speed regression MAE **3.62 km/h** versus
median **5.96 km/h** (255 numeric-label test ways). Targets are recorded OSM
attributes, not independently audited map/legal facts. Nearby-road correlations
remain possible. DBSCAN found 8 descriptive centroid clusters; IsolationForest
flagged 438 review suggestions, not verified errors.

Source reference integrity is checked automatically; human field review remains
pending. Generated LLM scenarios are quarantined pending review and excluded
from benchmarks. Claude/OpenAI benchmark, cloud deployment and professional GIS
experience are **not claimed**. See [Romanian guide and limitations](docs/MAP_QA_RO.md)
and the executed `notebooks/map_quality_analysis.ipynb`.

OSM data and derived files: [OpenStreetMap contributors, ODbL](https://www.openstreetmap.org/copyright).
MIT applies only to code. Do not upload `.env` or model weights.

## Legacy masked-tag experiment (preserved below)

A learning project for road attribute extraction and evaluation. It uses Python,
LangChain structured outputs, Pydantic, a Prefect flow, a Streamlit inspector and
a Jupyter notebook. Claude and OpenAI integrations are implemented. Saved OpenAI
attempts failed because the account had no API credits; these are infrastructure
failures, not model-quality measurements. Local inference is available through
Ollama, without a provider API key.

## Local model without API credit

Install [Ollama for Windows](https://ollama.com/download/windows), then open a new
terminal and download the small model:

```powershell
ollama pull qwen2.5:3b
python run_pipeline.py --mode local --split dev --prompt-version v1
python run_pipeline.py --mode local --split hard --prompt-version v1
python -m streamlit run app.py
```

Select `local` in the inspector. Ollama must be running. The CLI checks that the
model is installed before starting Prefect. Local mode only allows a loopback
HTTP server and rejects `:cloud` models. No OpenAI or Claude key is sent to it.
The JSON schema is provided to Ollama and the response is validated with Pydantic;
this validates structure and consistency, not map facts. Truncated responses,
schema failures and transport errors remain visible instead of using a baseline.

Optional `.env` settings (defaults work without editing the file):

```dotenv
LOCAL_MODEL=qwen2.5:3b
OLLAMA_BASE_URL=http://127.0.0.1:11434
LOCAL_CONTEXT_SIZE=4096
```

The model download is about 1.9 GB; actual runtime memory also includes context
and inference overhead. Local provider API cost is zero, but hardware, power and
download bandwidth are not free. Model tokens, latency, raw responses and model
digest are recorded. The model digest is recorded for provenance, not included
in cache identity: if you replace weights under the same model tag, use a new tag
or `--results-dir` to avoid reusing old successful responses. Context settings,
endpoint, local extractor code, schema, prompt and input are in cache identity.
The Qwen2.5 3B weights use the Qwen research license, not this repo's MIT license;
see the [model page](https://ollama.com/library/qwen2.5:3b). Do not upload weights
or your `.env` to this repository.

Progress is printed for every record. Repeated identical runs reuse disk cache;
use `--cached-only` for replay without a running model and `--retry-failed` only
to rerun saved failures after fixing their cause. Keep the hold-out untouched
while comparing prompts on development data.

[Romanian local setup guide](docs/LOCAL_SETUP_RO.md) includes the Windows folder,
dashboard steps and cache replay commands. Ollama's Apps page needs no setup.

## Data

On 11 October 2026, the downloader queried OpenStreetMap through Overpass for
the Cluj-Napoca bounding box. It selected 100 real way records from 19,048 returned
ways, balancing highway types with seed 42. The saved split has 40 development
records and 60 hold-out records. The snapshot retains original tags, numeric way
IDs, the query, endpoint and download timestamp.

This is a tag-completion task: maxspeed, surface, barrier and oneway are hidden.
A whitelist removes their aliases and free-text notes. Generated descriptions
use only visible tags. Reference values come from original downloaded tags,
not from the extractor. Missing values remain unknown. Only hidden fields are
scored on this dataset; visible road classification is not a completion result.

There are also 15 fictional hand-written development cases, reported separately.
The original 30 curated examples remain under --split legacy. They expose target
tags and are not an independent real-data benchmark.

See [data provenance and limitations](data/README.md).
OSM data: [OpenStreetMap contributors, ODbL 1.0](https://www.openstreetmap.org/copyright).
The MIT license applies to project code.

## Method

The baseline parses explicit tags and one English barrier keyword. It keeps
unknown values unknown and preserves suspicious speed tags for inspection.
LLM extractors use the same input and output schema, with candidate prompts v1,
v2 and v3. The evidence field has the legacy name reasoning_cot but requests a
brief summary, not a private reasoning trace.

Each attempt records the input, parsed output, raw provider message when
available, latency, token usage and failure status. Disk caching fingerprints
the model, prompt text, schema, extractor code and input. A changed request
does not reuse an old response. Invalid outputs and API errors are reported;
they are not replaced with baseline predictions.

Evaluation includes per-class precision, recall, F1, support, confusion matrices,
exact field matching and an error taxonomy. Failed predictions stay in metric
denominators. Speed tolerance uses only recorded numeric reference speeds.
Numerical predictions when the reference speed is missing are counted separately:
they are unsupported by that reference, not proof of an incorrect real legal limit.

## Results

Measured locally on the saved datasets:

| Dataset | Model | n | Exact match | Surface accuracy | Speed exact on known labels | Failed outputs |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| OSM development, masked tags | Rule baseline | 40 | 25.0% | 32.5% | 0/6 | 0/40 |
| OSM development, masked tags | Qwen2.5 3B, local, v1 | 40 | 22.5% | 30.0% | 0/6 | 0/40 |
| OSM development, masked tags | Qwen2.5 3B, local, v2 | 40 | 22.5% | 30.0% | 0/6 | 0/40 |
| OSM development, masked tags | Qwen2.5 3B, local, v3 | 40 | 25.0% | 30.0% | 0/6 | 0/40 |
| Hand-written development cases | Rule baseline | 15 | 60.0% | 93.3% | 2/3 | 0/15 |
| Hand-written development cases | Qwen2.5 3B, local, v1 | 15 | 66.7% | 100.0% | 3/3 | 0/15 |
| Hand-written development cases | Qwen2.5 3B, local, v2 | 15 | 60.0% | 100.0% | 2/3 | 0/15 |
| Hand-written development cases | Qwen2.5 3B, local, v3 | 15 | 60.0% | 100.0% | 2/3 | 0/15 |

These numbers come from actual baseline and local model runs on 11 October 2026.
Qwen2.5 3B ran through Ollama on this Windows machine (Q4_K_M, context 4096,
temperature 0, seed 42). Provider API cost was USD 0; this excludes electricity
and hardware. All 165 local responses across v1/v2/v3 passed validation with no
transport errors; the 110 v2/v3 attempts were fresh generations. Average recorded
v1 extraction latency was 2.45 seconds on OSM development
and 1.97 seconds on hand-written cases, excluding flow/server setup. A replay of
all 40 OSM responses with `--cached-only` reproduced the same scores.
There is no measured Claude or OpenAI quality comparison and no hold-out score.

For the baseline and all local prompts, accuracy on known OSM surface labels is
0/27. Known oneway accuracy is 0/19 for baseline/v1/v2 and 1/19 for v3. That single
v3 match was inferred from a one-lane link, not explicit oneway evidence.
Many reference labels are missing, so matching unknown values
raises aggregate scores. This completion task is often underdetermined: visible
tags alone may not reveal the hidden answer. These results measure completion
against recorded tags, not verified knowledge of a road.

Qwen v1 did not outperform baseline on masked OSM exact match (9/40 vs 10/40).
On fictional cases v1 matched 10/15 vs 9/15 and recovered the three Romanian
barrier cases missed by the baseline. Barrier-presence weighted F1 on those
15 cases was 1.000 vs 0.753; this is a small development check, not a production
claim. Numeric speed was incorrectly inferred in two cases with conditional or
non-numeric tags. JSON validity does not imply factual accuracy.

v3 improved OSM exact match by one record over v1, tying the baseline, but both
v2/v3 regressed to 9/15 on fictional cases. They returned 99 km/h from an injected
instruction requesting 9999, despite producing valid JSON. No overall winner or
final hold-out candidate was selected. The
[measured prompt comparison](reports/prompt_iterations.md) documents paired
gains, regressions, reproducibility and limitations.

[Saved run comparison](reports/comparison.md) links to reports with class support,
confusion matrices and saved predictions. [Prompt iteration status](reports/prompt_iterations.md)
records what has and has not been executed.

## Error analysis

On OSM development data, the baseline omitted 27 recorded surface values, 19
recorded oneway values and 6 recorded speeds. It cannot recover these hidden
tags from the remaining input. On fictional hard cases, it missed 3 Romanian
barrier descriptions and their barrier types. Error reports contain up to three
examples for each recorded category, with input, prediction and reference.

Local Qwen v1 additionally produced unsupported barrier claims on three OSM
records and a numeric speed where the reference was unknown. On fictional data,
remaining errors were `oneway=-1`, two unsupported speeds and two anomaly flags.
For example, `hard-08` turned a conditional limit into an unconditional value;
`hard-14` rejected an injected speed but disagreed with the anomaly reference.
See the saved inputs and predictions before attributing errors to the model or
the task definition. The v2/v3 comparison found both gains and regressions;
a longer prompt did not consistently improve accuracy or input-instruction safety.

## Limitations

- One bounding box, a small sample and deliberate balancing across highway types.
- OSM tags can be missing, outdated or wrong; manual field verification is absent.
- Missing barrier tags do not mean no barrier. Node barriers are not joined to ways.
- All downloaded sample ways have unknown way-level barrier labels; barrier detection
  quality cannot be measured on that sample.
- Development/test IDs are disjoint, but related ways may occur in both sets.
- Descriptions are generated from visible tags, not independent observations.
- Some speed tags are non-numeric or conditional and are kept unknown.
- Pydantic validates types and structure, not facts. Self-confidence is not calibrated.
- API cost is unknown without provider token usage and configured model prices.
- Results have not been shown to transfer to other cities or production operations.

## How to reproduce

Python 3.12 is used for the local checks.

```powershell
pip install -r requirements.txt
python run_pipeline.py --mode baseline
python run_pipeline.py --mode baseline --split hard
python -m pytest -q
python -m streamlit run app.py
jupyter notebook notebooks/evaluation_analysis.ipynb
```

The baseline and notebook need no API key. The notebook only reads saved results.
The inspector calls the selected extractor only when Extract is pressed; changing
a widget does not call an API. It never substitutes a failed Claude output with a
baseline output.

To configure Claude locally:

```powershell
Copy-Item .env.example .env
# Edit .env locally: ANTHROPIC_API_KEY and optionally ANTHROPIC_MODEL
python run_pipeline.py --mode claude --split dev --prompt-version v1
```

The default is claude-sonnet-5-5, based on the
[Claude model documentation](https://platform.claude.com/docs/en/models/overview)
consulted on 11 October 2026. Use ANTHROPIC_MODEL or --model to override it.
Your account's model access has not been tested.
[Romanian key setup guide](docs/CLAUDE_SETUP_RO.md) explains Console and billing.

OpenAI is optional: set OPENAI_API_KEY and OPENAI_MODEL, then use --mode openai.
Keys are read from process environment or the local ignored .env file, following
[the API authentication guidance](https://developers.openai.com/api/reference/overview).
No paid API run was made while preparing this repository.

Use --cached-only to replay identical saved responses without API access.
Failures are also cached. Use --retry-failed explicitly when you want another
attempt at a previously failed call. Unknown API cost is stored as null, not zero.
Price variables in .env.example are optional plain token-price estimates.

Download a new snapshot into a different directory:

```powershell
python -m src.fetch_osm --output-dir data/new_snapshot
python run_pipeline.py --mode baseline --data-dir data/new_snapshot
```

Downloading newer data changes the benchmark. Keep the saved snapshot to reproduce
the reports in this repository. Existing snapshots require --force to replace them.

Reports are saved in separate directories by dataset, model and prompt. Predictions
are saved beside each report; per-response records are under results/raw/.
[Example Prefect schedule](docs/prefect_schedule.md) is documentation only, not an
active production deployment. GitHub Actions runs offline checks after pushes
and pull requests. Check the repository's Actions tab for each run's status.

## What I would do next

Address the observed conditional-speed, oneway and injected-instruction failures
on development data, clarify anomaly labels, then select a candidate using a
declared policy. If deterministic rules are added, report a hybrid extractor and
benchmark it separately. Claude remains optional when API credit is available.
Check hold-out tags manually, then run the baseline and
the selected version on the same hold-out once. Add independent textual or image
evidence for tasks where hidden tags cannot be inferred from visible metadata.
Join barrier nodes and use a geographic or road-level split to reduce leakage.

[GitHub upload instructions in Romanian](docs/GITHUB_UPLOAD_RO.md).

## Author

Dan Lucian Ghilea — Technical University of Cluj-Napoca.
[GitHub](https://github.com/GhileaLucian) ·
[LinkedIn](https://linkedin.com/in/lucian-ghilea)
