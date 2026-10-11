# GeoAttribute-LLM

A learning project for road attribute extraction and evaluation. It uses Python,
LangChain structured outputs, Pydantic, a Prefect flow, a Streamlit inspector and
a Jupyter notebook. Claude and OpenAI integrations are implemented; neither API
has been evaluated in the saved runs.

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
| Hand-written development cases | Rule baseline | 15 | 60.0% | 93.3% | 2/3 | 0/15 |

These numbers come from actual baseline runs. API cost for these runs is USD 0
because no model API was used. Invalid outputs: 0/55. There is no measured Claude
or OpenAI comparison and no hold-out score yet.

Surface accuracy on known OSM surface labels is 0/27; oneway accuracy on known
OSM labels is 0/19. Many reference labels are missing, so matching unknown values
raises aggregate scores. This completion task is often underdetermined: visible
tags alone may not reveal the hidden answer. These results measure completion
against recorded tags, not verified knowledge of a road.

[Saved run comparison](reports/comparison.md) links to reports with class support,
confusion matrices and saved predictions. [Prompt iteration status](reports/prompt_iterations.md)
records what has and has not been executed.

## Error analysis

On OSM development data, the baseline omitted 27 recorded surface values, 19
recorded oneway values and 6 recorded speeds. It cannot recover these hidden
tags from the remaining input. On fictional hard cases, it missed 3 Romanian
barrier descriptions and their barrier types. Error reports contain up to three
examples for each recorded category, with input, prediction and reference.

These patterns identify missing capabilities. They do not establish that an LLM
will recover the tags or that any prompt change has improved a score.

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

Run Claude candidates on development data, inspect actual errors and select a
version using evidence. Check hold-out tags manually, then run the baseline and
the selected version on the same hold-out once. Add independent textual or image
evidence for tasks where hidden tags cannot be inferred from visible metadata.
Join barrier nodes and use a geographic or road-level split to reduce leakage.

[GitHub upload instructions in Romanian](docs/GITHUB_UPLOAD_RO.md).

## Author

Dan Lucian Ghilea — Technical University of Cluj-Napoca.
[GitHub](https://github.com/GhileaLucian) ·
[LinkedIn](https://linkedin.com/in/lucian-ghilea)
