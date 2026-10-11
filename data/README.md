# Data provenance

Downloaded snapshot: 11 October 2026 (UTC). Exact timestamp, query, endpoint,
server timestamp and original tags are saved in osm_raw.json.

The Overpass query returned 19,048 highway ways in the Cluj-Napoca bounding box
46.70,23.48,46.82,23.70. The script selected 100 ways, balanced across highway
types, with seed 42. Some types are paths, steps, planned or construction ways.
This is not a representative sample of driving roads in the city.

osm_dev.json contains 40 records. osm_test.json contains 60 records.
IDs are disjoint, but nearby ways or ways with the same name may occur in both.
The hold-out has not been evaluated in the saved runs.

maxspeed, surface, barrier and oneway are hidden from model input. A whitelist
removes aliases and free-text notes that could expose their values. Generated
descriptions contain only visible tags. Reference labels are normalized from
the original tags. Only the hidden target fields are scored on this dataset;
visible road_type and anomaly_flag are not scored. A missing tag remains unknown.
Numeric speeds with mph are converted to km/h; non-numeric and conditional speeds
are not converted into an assumed legal limit.

This completion task is often underdetermined: the remaining tags may not reveal
the hidden answer. An abstaining extractor will miss recorded tags. A guessed
value may be plausible but is not independently validated.

Only way-level barrier tags are collected. All 100 selected ways have no
way-level barrier tag. This dataset cannot measure barrier detection quality.
Bollards and gates are often separate nodes, which this downloader does not join.
Use the separate fictional cases to exercise barrier behavior during development.

hard_cases.json has 15 fictional hand-written development scenarios. The source
field is hand-written, IDs start with hard-, and no OSM way IDs are assigned.
Their labels describe the intended interpretation of each scenario. They are
not independently collected map observations.

osm_ground_truth_cluj.json is the original 30-example curated fixture. Its IDs
are symbolic names, not numeric OSM IDs, and its collection method is unrecorded.
It exposes target tags and some examples matched the old few-shot prompts.
Do not use it to claim independent accuracy on real OSM data.

Attribution: [OpenStreetMap contributors](https://www.openstreetmap.org/copyright).
Downloaded and derived OSM data are available under ODbL 1.0. The repository's
MIT license covers application code, not a relicensing of OSM data.

Manual review of the hold-out on openstreetmap.org has not been completed.
The downloader is not a substitute for checking the tags or field observations.

## Separate Map QA geometry/evidence snapshot

`mapqa/snapshot.json` contains actual road geometry and barrier nodes, separate
from the old 100-way masked-tag dataset. Its query, endpoint, date, licence and
SHA-256 are in `mapqa/manifest.json`. Node membership supports topological joins;
metric nearest candidates are review suggestions, not labels.

`evidence_dev.json` (80), `evidence_test.json` (40) and `evidence_hard.json` (15)
describe the first evidence experiment. v5 consumed the initial test.
`evidence_test_final.json` reserves 40 additional disjoint road groups for v6;
its manifest records that history explicitly. Do not tune against this final set.
All real-data evidence texts are controlled bilingual transcriptions of OSM tags
and topologically connected barriers, not independently collected observations.
Positive-barrier sampling is nonrepresentative. Repetitive texts share model cache.

`reports/mapqa/reference_review_queue.json` records source tags/node IDs and
pending human review. Automatic source integrity is not field verification.
Generated scenario proposals are fictional, pending review and excluded from
benchmark loading. Full methods and limits: [Map QA guide](../docs/MAP_QA_RO.md).
