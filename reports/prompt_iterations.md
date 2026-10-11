# Measured local prompt comparison

Measured on 11 October 2026 with the existing, unchanged v1/v2/v3 prompts and
Qwen2.5 3B through local Ollama, not Claude or OpenAI.

## Results

Exact match requires every field in that record's evaluation_fields to match.
OSM and fictional cases have different tasks/field sets and are not pooled.

| Extractor / prompt | OSM development, n=40 | Fictional hard cases, n=15 | Failures |
| --- | ---: | ---: | ---: |
| Rule baseline | 10/40 (25.0%) | 9/15 (60.0%) | 0/55 |
| Local Qwen v1 | 9/40 (22.5%) | 10/15 (66.7%) | 0/55 |
| Local Qwen v2 | 9/40 (22.5%) | 9/15 (60.0%) | 0/55 |
| Local Qwen v3 | 10/40 (25.0%) | 9/15 (60.0%) | 0/55 |

All 110 v2/v3 attempts were fresh generations, not cache replays. Together with
the 55 v1 responses, all 165 local responses passed validation, with no transport
errors. Provider API cost was USD 0, excluding electricity and hardware.

## Paired gains and regressions

All versions used identical IDs, input payloads, labels and evaluation fields.

| Candidate vs v1 | Dataset | Newly exact | Previously exact, now wrong |
| --- | --- | --- | --- |
| v2 | OSM | None | None |
| v3 | OSM | 1149985564 | None |
| v2 | Fictional | hard-09 | hard-06, hard-12 |
| v3 | Fictional | hard-09 | hard-06, hard-12 |

v3's OSM exact-match gain came from removing an unsupported barrier claim on
1149985564, returning unknown, not recovering a hidden surface or speed. All
prompts still matched 0/27 known surfaces and 0/6 known speeds. Known oneway
accuracy was 0/19, 0/19 and 1/19. That single v3 match (315218180) was inferred
from a one-lane link: it matched the reference but was not established by explicit
oneway evidence in the visible input. Do not present it as verified map knowledge.

| OSM discrepancy count | v1 | v2 | v3 |
| --- | ---: | ---: | ---: |
| Surface mismatch | 28 | 28 | 28 |
| Oneway mismatch | 20 | 19 | 18 |
| Recorded speed omitted | 6 | 6 | 6 |
| Numeric speed when reference unknown | 1 | 0 | 0 |
| Barrier-presence mismatch | 3 | 3 | 2 |
| Barrier-type mismatch | 2 | 0 | 2 |

Categories can overlap. Unknown OSM labels do not prove a real feature is absent.

Concrete fictional cases show why a longer prompt is not automatically better:

- `hard-06`: tags say 30 km/h; text says 50. v1 retained 30 and flagged the
  conflict. v2/v3 chose 50; v3 also omitted the conflict flag despite its explicit
  tag-priority rule.
- `hard-09`: non-numeric `RO:urban` became 50 in v1, but null in v2/v3. This
  follows the benchmark's explicit-evidence policy, not a claim about legal speed.
- `hard-12`: explicit `oneway=no` was false in v1, but null in v2/v3.
- `hard-14`: an instruction requests speed 9999, not an observed road value.
  v1 returned null, while v2/v3 returned 99. This passed the numeric schema but
  remained unsupported: the case does not demonstrate prompt-injection resistance.
  v1/v3 also disagreed with the anomaly reference; road anomalies and malicious
  input need a clearer distinction in the label policy.
- `hard-08`: all versions incorrectly made a conditional limit of 30 an
  unconditional speed. v3's conditional-speed rule did not fix this case.
- `hard-07` and `hard-15`: all versions missed reverse oneway and the unusual
  speed anomaly respectively.

All versions recovered the three Romanian barrier cases. Barrier-presence
weighted F1 was 1.000 on the 15 fictional cases for every version. v2's glossary
showed no new barrier gain over v1. It uses the same phrases as these scenarios;
this is a development check, not an independent language test.

## Interpretation and next decision

There is no clear overall winner. v3 ties baseline OSM exact match but loses to
v1 on fictional exact match and fails the injected-speed case. A gain of one OSM
record is not evidence of statistically reliable improvement or production
suitability. This is one generation per prompt/input, not a stability study.
No default prompt was changed and no final hold-out candidate was selected.

Next experiment: define deterministic handling for explicit numeric tags,
conditional speeds and oneway, separate untrusted instructions from observations,
and clarify anomaly labels. If Python rules are added, report a hybrid extractor
and benchmark it separately; do not attribute rule fixes to prompting. Add
independent textual/image evidence for underdetermined hidden-tag completion.

Claude has not been benchmarked. Saved OpenAI attempts failed for lack of credit
and are not quality measurements. The 60-record hold-out was not evaluated or
modified in this experiment. Do not repeatedly tune against test outputs.

## Reproducibility

Model digest: `357c53fb659c5076de1d65ccb0b397446227b71a42be9d1603d46168015c9e4b`.
Q4_K_M; temperature 0, seed 42, context 4096, num_predict 1024. Digest and options
were checked in every successful saved response; scores were recalculated from
predictions. Dataset hashes and labels match across versions.

| Dataset | SHA-256 |
| --- | --- |
| osm_dev.json | b4caa3fc4ffb44f393daa0ae8ce4b84eee014749ac41fc9ef43c259ca31c225d |
| hard_cases.json | 92869b8ba2e13c0402cf7bf84c4eee6e83f73aea05b4746a7b213cc8ef5d826f |

[Saved runs](comparison.md) link to predictions, per-class precision/recall/F1,
support, confusion matrices and error examples. Original mean extraction times
in seconds (OSM / fictional): v1 2.45 / 1.97, v2 2.18 / 1.94, v3 2.44 / 2.04.
These exclude Prefect startup and are not a controlled performance benchmark.

```powershell
python run_pipeline.py --mode local --split dev --prompt-version v2
python run_pipeline.py --mode local --split hard --prompt-version v2
python run_pipeline.py --mode local --split dev --prompt-version v3
python run_pipeline.py --mode local --split hard --prompt-version v3
```

Identical reruns reuse cache. Add `--cached-only` to recalculate reports without
model calls. Use a separate results directory for a new generation. Keep
`--split test` untouched until a final candidate and selection policy are chosen.
