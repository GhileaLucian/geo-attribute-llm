"""
Interactive Streamlit Web Dashboard for GeoAttribute-LLM.
Allows live interactive testing of road attribute extraction and QA benchmarking.
"""

import json
from pathlib import Path
import streamlit as st
import pandas as pd
from PIL import Image

from src.models import RoadSegmentInput, RoadAttributes, RoadType, BarrierType, SurfaceType
from src.extractor import OpenStreetMapAttributeExtractor
from src.dataset_generator import build_cluj_osm_dataset

st.set_page_config(
    page_title="GeoAttribute-LLM | Map QA Dashboard",
    page_icon="🗺️",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main-title { font-size: 28px; font-weight: 800; color: #0f172a; margin-bottom: 2px; }
    .subtitle { font-size: 15px; color: #475569; margin-bottom: 20px; }
    .metric-card { background-color: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 12px; text-align: center; }
    .metric-val { font-size: 22px; font-weight: 800; color: #0284c7; }
    .metric-lbl { font-size: 12px; color: #475569; text-transform: uppercase; font-weight: 600; }
    .cot-box { background-color: #f8fafc; border-left: 4px solid #0284c7; padding: 12px; border-radius: 4px; font-family: monospace; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🗺️ GeoAttribute-LLM: Geospatial Quality Control</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Automated Map Quality Assurance, LLM Attribute Extraction &amp; Ground-Truth Benchmarking</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["🔍 Interactive Road Segment Inspector", "📊 Benchmark & Evaluation Metrics", "⚙️ Pipeline Architecture (Prefect)"])

dataset = build_cluj_osm_dataset()
segment_map = {f"{s.segment_id} - {s.name}": s for s in dataset}

with tab1:
    st.subheader("Test Road Attribute Extraction in Real Time")
    
    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        selected_key = st.selectbox("Select an OpenStreetMap segment from Cluj-Napoca:", list(segment_map.keys()))
    with col_btn:
        st.write("")
        st.write("")
        run_btn = st.button("🚀 Extract Attributes (LLM)", type="primary", use_container_width=True)

    segment: RoadSegmentInput = segment_map[selected_key]

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("##### 📍 Input OpenStreetMap Data")
        st.write(f"**Segment ID:** `{segment.segment_id}`")
        st.write(f"**Context:** {segment.context_description}")
        st.markdown("**Raw OSM Tags:**")
        st.json(segment.osm_tags)

    with c2:
        st.markdown("##### 🤖 Extraction Output")
        
        extractor = OpenStreetMapAttributeExtractor(use_live_api=False)
        extracted = extractor.extract_attributes(segment)

        # Display badges
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{extracted.road_type.value}</div><div class="metric-lbl">Road Type</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{extracted.speed_limit_kmh} km/h</div><div class="metric-lbl">Speed Limit</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{"YES" if extracted.barrier_present else "NO"}</div><div class="metric-lbl">Barrier ({extracted.barrier_type.value})</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{extracted.surface.value}</div><div class="metric-lbl">Surface</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**🧠 Chain-of-Thought (CoT) Reasoning:**")
        st.markdown(f'<div class="cot-box">{extracted.reasoning_cot}</div>', unsafe_allow_html=True)

        if segment.expected_attributes:
            exp = segment.expected_attributes
            is_match = (
                exp.road_type == extracted.road_type and
                exp.barrier_present == extracted.barrier_present and
                exp.surface == extracted.surface
            )
            st.markdown("<br>", unsafe_allow_html=True)
            if is_match:
                st.success(f"✅ Ground-Truth Match Verified! (Confidence: {extracted.confidence_score*100:.0f}%)")
            else:
                st.warning("⚠️ Discrepancy detected against ground truth (Cataloged in error taxonomy).")

with tab2:
    st.subheader("Benchmark Metrics & Spatial Error Taxonomy")
    
    metrics_file = Path("reports/metrics_summary.json")
    chart_file = Path("reports/evaluation_metrics_chart.png")

    if metrics_file.exists():
        with open(metrics_file, "r", encoding="utf-8") as f:
            metrics = json.load(f)

        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        kpi1.metric("Evaluated Segments", metrics["total_segments_evaluated"])
        kpi2.metric("Exact Match Rate", f"{metrics['exact_segment_match_rate']*100:.1f}%")
        kpi3.metric("Road Type F1", f"{metrics['attributes']['road_type']['f1_score']*100:.1f}%")
        kpi4.metric("Barrier F1", f"{metrics['attributes']['barrier_present']['f1_score']*100:.1f}%")
        kpi5.metric("Surface F1", f"{metrics['attributes']['surface_type']['f1_score']*100:.1f}%")

        c_chart, c_err = st.columns([1.2, 1])
        with c_chart:
            st.markdown("##### 📈 Precision & Recall Benchmark")
            if chart_file.exists():
                st.image(str(chart_file), use_container_width=True)
        with c_err:
            st.markdown("##### 🚨 Spatial Error Taxonomy Breakdown")
            errs = metrics.get("error_taxonomy_breakdown", {})
            if errs:
                err_df = pd.DataFrame(list(errs.items()), columns=["Error Taxonomy", "Count"])
                st.dataframe(err_df, use_container_width=True)
                st.info("💡 The taxonomy categorizes speed hallucinations and boundary ambiguities to refine system prompts iteratively.")
    else:
        st.warning("Run `python run_pipeline.py` first to generate the benchmark artifacts.")

with tab3:
    st.subheader("Prefect Workflow Orchestration")
    st.markdown("""
    The pipeline is orchestrated with **Prefect 3.8**, decoupling operations into monitored, retriable tasks:
    1. `load-osm-ground-truth` (Cache & Load 50 Cluj road segments)
    2. `extract-attributes-batch` (Runs LangChain structured output extraction with retry policy)
    3. `benchmark-and-evaluate` (Scikit-learn precision/recall calculation)
    4. `generate-visualizations` (Matplotlib chart generation)
    5. `export-artifacts` (Automated markdown & JSON reporting)
    """)
    st.code("""
# Run the pipeline from terminal:
python run_pipeline.py
    """, language="bash")
