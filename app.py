"""Streamlit inspector and viewer for saved benchmark runs."""

import hashlib
import json
import os
import pandas as pd
import streamlit as st

from src.config import PROJECT_ROOT, load_configuration, resolve_model
from src.dataset_generator import load_ground_truth_dataset
from src.evaluator import percentage
from src.recording import extract_batch, input_payload

load_configuration()
st.set_page_config(page_title="GeoAttribute QA", layout="wide", initial_sidebar_state="collapsed")
st.markdown((PROJECT_ROOT / "assets" / "dashboard.css").read_text(encoding="utf-8"), unsafe_allow_html=True)
st.title("GeoAttribute QA")
st.caption("Road attribute extraction and saved evaluation results. Local Ollama needs no API key; cloud APIs require your own key.")

tab_inspector, tab_benchmark, tab_workflow, tab_mapqa = st.tabs([
    "Segment Inspector", "Benchmark & Error Taxonomy", "How to run", "Map QA & ML"
])

with tab_inspector:
    split_name = st.selectbox("Dataset", ["OSM development", "Hand-written hard cases", "Legacy curated examples"])
    filenames = {
        "OSM development": "osm_dev.json", "Hand-written hard cases": "hard_cases.json",
        "Legacy curated examples": "osm_ground_truth_cluj.json"
    }
    try:
        dataset = load_ground_truth_dataset(PROJECT_ROOT / "data" / filenames[split_name])
    except (FileNotFoundError, ValueError) as exc:
        st.error(str(exc))
        st.stop()
    segment = st.selectbox("Segment", dataset, format_func=lambda value: f"{value.segment_id} — {value.name}")
    col_engine, col_prompt = st.columns(2)
    mode = col_engine.selectbox("Extractor", ["baseline", "local", "claude", "openai"])
    version = col_prompt.selectbox("Prompt version", ["v1", "v2", "v3"], disabled=mode == "baseline")
    if mode == "baseline":
        version = "v1"
    cached_only = st.checkbox("Use saved response only (no API calls)", value=False)
    model = resolve_model(mode)
    key_name = "ANTHROPIC_API_KEY" if mode == "claude" else "OPENAI_API_KEY"
    key_available = bool(os.getenv(key_name)) if mode in ("claude", "openai") else True
    if mode == "local":
        st.caption(f"Local model: {model}. Start Ollama first. No OpenAI/Claude request is made.")
    if not key_available and not cached_only:
        st.info(f"{key_name} is missing. Configure .env locally, or select saved responses.")
    if segment.source == "hand-written":
        st.caption("Fictional development scenario; not a downloaded OSM way.")
    elif segment.source == "hand-curated-unverified":
        st.warning("Legacy examples expose target tags and are not independently verified OSM records.")
    else:
        st.caption(f"Source: {segment.source}; collected: {segment.collected_at}.")
        st.link_button("Open OSM way", f"https://www.openstreetmap.org/way/{segment.osm_way_id}")
        st.caption("Hidden tags: " + ", ".join(segment.hidden_attributes))
    payload_key = hashlib.sha256(json.dumps(input_payload(segment), sort_keys=True).encode()).hexdigest()
    selection = (segment.segment_id, mode, model, version, payload_key)
    if st.button("Extract", type="primary", disabled=not (key_available or cached_only)):
        try:
            with st.spinner("Extracting attributes..."):
                result = extract_batch(
                    [segment], mode, model, version, PROJECT_ROOT / "results", cached_only=cached_only
                )[0]
            st.session_state["inspector_output"] = {"selection": selection, "result": result}
        except (ValueError, FileNotFoundError) as exc:
            st.error(str(exc))
            st.session_state.pop("inspector_output", None)
    left, right = st.columns(2)
    with left:
        st.subheader("Model input")
        st.json(input_payload(segment))
    with right:
        st.subheader("Extraction output")
        saved = st.session_state.get("inspector_output")
        if saved and saved["selection"] == selection:
            result = saved["result"]
            if result.status != "success" or result.extracted is None:
                st.error(f"{result.status}: {result.error_message}")
            else:
                st.caption(f"{mode} / {model} / {version}; cache hit: {result.cache_hit}")
                st.json(result.extracted.model_dump(mode="json"))
                exact = all(
                    getattr(segment.expected_attributes, field) == getattr(result.extracted, field)
                    for field in segment.evaluation_fields
                )
                st.write("Match on evaluated fields" if exact else "Difference on evaluated fields")
                st.caption("Confidence is an uncalibrated self-assessment, not a correctness probability.")
        else:
            st.info("Press Extract to run the selected engine. Changing a selection does not call the API.")
        with st.expander("Reference labels (not sent to the model)"):
            st.json(segment.expected_attributes.model_dump(mode="json"))
            st.write("Evaluated fields:", segment.evaluation_fields)

with tab_benchmark:
    files = sorted((PROJECT_ROOT / "reports").glob("*/metrics_summary.json"))
    if not files:
        st.info("No saved benchmark runs. Run python run_pipeline.py --mode baseline.")
    else:
        summaries = [json.loads(path.read_text(encoding="utf-8")) for path in files]
        table = [{
            "Dataset": m["dataset_file"], "Mode": m["extractor_mode"], "Model": m["model_name"],
            "Prompt": m["prompt_version"], "n": m["total_segments_evaluated"],
            "Exact": percentage(m["exact_segment_match_rate"]),
            "Failed": percentage(m["failure_rate"])
        } for m in summaries]
        st.dataframe(pd.DataFrame(table), hide_index=True, use_container_width=True)
        st.caption("Compare identical datasets only. High unknown-label support can inflate scores.")
        selected = st.selectbox("Saved run", files, format_func=lambda path: path.parent.name)
        metrics = json.loads(selected.read_text(encoding="utf-8"))
        st.caption(f"Recorded run: {metrics['run_at']}; dataset SHA-256: {metrics['dataset_sha256']}")
        if not any(m["extractor_mode"] == "claude" for m in summaries):
            st.info("No Claude benchmark has been run. The table contains no Claude measurements.")
        a, b, c, d = st.columns(4)
        a.metric("Labeled attempts", metrics["total_segments_evaluated"])
        b.metric("Exact match", percentage(metrics["exact_segment_match_rate"]))
        c.metric("Invalid outputs", percentage(metrics["invalid_output_rate"]))
        d.metric("API errors", metrics["api_errors"])
        chart = selected.parent / "evaluation_metrics_chart.png"
        if chart.exists():
            st.image(str(chart), use_container_width=True)
        st.subheader("Confusion matrix")
        choices = [key for key, value in metrics["attributes"].items() if value.get("count") and "confusion_matrix" in value]
        if choices:
            attribute = st.selectbox("Attribute", choices)
            values = metrics["attributes"][attribute]
            matrix = values["confusion_matrix"]
            st.caption("Rows: reference; columns: prediction.")
            st.dataframe(pd.DataFrame(matrix["values"], index=matrix["labels"], columns=matrix["labels"]))
            st.dataframe(pd.DataFrame(values["per_class"]).T)
        st.subheader("Error counts")
        st.json(metrics["error_taxonomy_breakdown"])
        with st.expander("Real examples from this saved run"):
            st.markdown((selected.parent / "error_examples.md").read_text(encoding="utf-8"))

with tab_workflow:
    st.write("The Prefect flow loads a saved dataset, extracts or reuses responses, evaluates predictions, and exports reports.")
    st.write("Responses are cached by model, prompt, schema, code and input. Failed outputs remain visible in evaluation.")
    st.code("python run_pipeline.py --mode baseline\npython run_pipeline.py --mode local --split dev --prompt-version v1\npython run_pipeline.py --mode local --split hard --prompt-version v1", language="powershell")
    st.write("For local inference, install Ollama and run ollama pull qwen2.5:3b. The model runs on this computer; no provider API fee. Hardware and electricity are not free.")
    st.write("Copy .env.example to .env and configure your key locally before using an API.")
    st.write("Use the development set to compare prompt versions. Keep the hold-out test for the final selected version.")
    st.caption("OSM data: OpenStreetMap contributors, ODbL. See data/README.md for sources and limitations.")

with tab_mapqa:
    from src.mapqa_dashboard import render_mapqa
    render_mapqa()
