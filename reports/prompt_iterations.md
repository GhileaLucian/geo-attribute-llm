# Prompt iteration status

Three candidate prompt versions are defined in src/prompts.py.

| Version | Intended change | Measured Claude development result |
| --- | --- | --- |
| v1 | Preserve unknown values; require explicit evidence; preserve OSM classes | Not run |
| v2 | Add Romanian barrier terms; avoid inferring a numeric speed from traffic calming | Not run |
| v3 | Handle contradictory tags/text and instructions embedded in input | Not run |

These are candidate changes, not demonstrated improvements. There is no selected
best Claude prompt and no Claude hold-out result. ANTHROPIC_API_KEY was unavailable
when the application and offline baseline reports were prepared.

After configuring a key, run all candidates on the same saved dev set:

```powershell
python run_pipeline.py --mode claude --split dev --prompt-version v1
python run_pipeline.py --mode claude --split dev --prompt-version v2
python run_pipeline.py --mode claude --split dev --prompt-version v3
```

Inspect saved metrics, class support, failure rates and actual error examples.
Record which measured error pattern changed. Choose one version before evaluating
osm_test.json. Run baseline and the chosen Claude version on the same hold-out
for the final comparison; report both development and test scores even if worse.

Hand-written hard cases are development checks, not part of the OSM hold-out.
Do not repeatedly tune against test outputs.
