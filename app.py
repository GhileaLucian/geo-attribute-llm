"""
Streamlit Web Application: GeoAttribute QA Platform
Minimalist, high-end SaaS interface inspired by Linear and Mapbox Studio.
Strictly light-themed, zero emojis, clean typography and subtle components.
"""

import os
import json
from pathlib import Path
import streamlit as st
import pandas as pd

from src.models import RoadSegmentInput, RoadAttributes
from src.extractor import get_extractor, RuleBasedBaselineExtractor
from src.dataset_generator import load_ground_truth_dataset

# Configuration
st.set_page_config(
    page_title="GeoAttribute QA",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern Minimalist CSS
st.markdown("""
<style>
    /* Global Resets & Typography */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #0f172a;
    }
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Header Container */
    .header-box {
        background: #ffffff;
        border-bottom: 1px solid #e2e8f0;
        padding: 24px 32px 20px;
        margin: -4rem -4rem 24px -4rem;
    }
    .header-title {
        font-size: 21px;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #0f172a;
        margin: 0;
    }
    .header-subtitle {
        font-size: 13.5px;
        color: #64748b;
        margin-top: 4px;
    }
    
    /* Cards */
    .card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .card-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Metric Pills & Badges */
    .attr-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        margin-top: 8px;
    }
    .attr-item {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 12px 14px;
    }
    .attr-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748b;
        margin-bottom: 4px;
    }
    .attr-val {
        font-size: 15px;
        font-weight: 600;
        color: #0f172a;
    }
    
    /* Reasoning Box */
    .reasoning-box {
        background: #f8fafc;
        border-left: 3px solid #0284c7;
        padding: 12px 14px;
        border-radius: 0 6px 6px 0;
        font-size: 12.5px;
        line-height: 1.5;
        color: #334155;
        margin-top: 8px;
    }
    
    /* Status Labels */
    .status-verified {
        color: #059669;
        font-size: 12px;
        font-weight: 600;
    }
    .status-anomaly {
        color: #d97706;
        font-size: 12px;
        font-weight: 600;
    }

    /* Tabs styling override */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 4px 12px;
        font-size: 13.5px;
        font-weight: 500;
        color: #64748b;
        background-color: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: #0f172a !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #0284c7 !important;
    }
    
    /* Remove streamlit padding gaps */
    div.block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Application Header
st.markdown("""
<div class="header-box">
    <div class="header-title">GeoAttribute Quality Assurance Platform</div>
    <div class="header-subtitle">Comparative benchmark: Rule-based Baseline vs Claude 3.5 Sonnet / GPT-4o on OpenStreetMap data</div>
</div>
""", unsafe_allow_html=True)

# Load ground-truth dataset strictly from JSON
data_file = Path("data/osm_ground_truth_cluj.json")
dataset = load_ground_truth_dataset(data_file)
segment_map = {f"{s.segment_id} — {s.name}": s for s in dataset}

# Top Navigation Tabs
tab_inspector, tab_benchmark, tab_workflow = st.tabs([
    "Segment Inspector",
    "Benchmark & Error Taxonomy",
    "Pipeline Architecture"
])

# ---------------------------------------------------------
# TAB 1: SEGMENT INSPECTOR
# ---------------------------------------------------------
with tab_inspector:
    opt_col, ctrl_col, btn_col = st.columns([1.5, 3, 1])
    with opt_col:
        engine_choice = st.selectbox(
            "Extractor Engine:",
            ["Rule-Based Baseline", "Claude 3.5 Sonnet (Live API)", "OpenAI GPT-4o (Live API)"],
            index=0
        )
    with ctrl_col:
        selected_key = st.selectbox(
            "Select road segment from benchmark dataset:",
            list(segment_map.keys())
        )
    with btn_col:
        st.write("")
        st.write("")
        run_extraction = st.button("Extract", type="primary", use_container_width=True)

    segment: RoadSegmentInput = segment_map[selected_key]
    
    # Initialize appropriate extractor
    extractor_error = None
    try:
        if "Claude" in engine_choice:
            extractor = get_extractor("claude")
        elif "OpenAI" in engine_choice:
            extractor = get_extractor("openai")
        else:
            extractor = get_extractor("baseline")
        extracted = extractor.extract_attributes(segment)
    except Exception as e:
        extractor_error = str(e)
        # Fallback to baseline
        extractor = RuleBasedBaselineExtractor()
        extracted = extractor.extract_attributes(segment)

    if extractor_error:
        st.warning(f"Live API unavailable ({extractor_error}). Displaying Rule-based Baseline output instead.")

    col_left, col_right = st.columns([1, 1], gap="medium")

    with col_left:
        st.markdown("""
        <div class="card">
            <div class="card-title">
                <span>Input Metadata</span>
                <span style="font-weight: 500; color: #94a3b8;">Source: OpenStreetMap (Cluj-Napoca)</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.write(f"**Segment Identifier:** `{segment.segment_id}`")
        st.write(f"**Road Name:** {segment.name}")
        st.write(f"**Context:** {segment.context_description}")
        
        st.markdown("<p style='font-size: 11px; font-weight: 600; text-transform: uppercase; color: #64748b; margin-top: 14px; margin-bottom: 6px;'>OSM Tags</p>", unsafe_allow_html=True)
        
        # Clean Table for Tags
        tags_df = pd.DataFrame(list(segment.osm_tags.items()), columns=["Key", "Value"])
        st.dataframe(tags_df, hide_index=True, use_container_width=True, height=180)
        
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        # Check against ground truth
        is_exact = False
        if segment.expected_attributes:
            exp = segment.expected_attributes
            is_exact = (
                exp.road_type == extracted.road_type and
                exp.barrier_present == extracted.barrier_present and
                exp.surface == extracted.surface and
                (exp.speed_limit_kmh == extracted.speed_limit_kmh if exp.speed_limit_kmh else True)
            )

        status_html = '<span class="status-verified">Verified Match</span>' if is_exact else '<span class="status-anomaly">Discrepancy Cataloged</span>'

        st.markdown(f"""
        <div class="card">
            <div class="card-title">
                <span>Extraction Output [{extractor.name}]</span>
                {status_html}
            </div>
            <div class="attr-grid">
                <div class="attr-item">
                    <div class="attr-label">Road Classification</div>
                    <div class="attr-val">{extracted.road_type.value}</div>
                </div>
                <div class="attr-item">
                    <div class="attr-label">Speed Limit</div>
                    <div class="attr-val">{f"{extracted.speed_limit_kmh} km/h" if extracted.speed_limit_kmh else "Not specified"}</div>
                </div>
                <div class="attr-item">
                    <div class="attr-label">Physical Barrier</div>
                    <div class="attr-val">{"Present (" + extracted.barrier_type.value + ")" if extracted.barrier_present else "None"}</div>
                </div>
                <div class="attr-item">
                    <div class="attr-label">Surface Material</div>
                    <div class="attr-val">{extracted.surface.value}</div>
                </div>
            </div>
            <div style="margin-top: 16px;">
                <div class="attr-label">Reasoning Trace</div>
                <div class="reasoning-box">{extracted.reasoning_cot}</div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 14px; font-size: 11.5px; color: #64748b;">
                <span>One-Way: <strong>{"Yes" if extracted.oneway else "No"}</strong></span>
                <span>Confidence: <strong>{extracted.confidence_score*100:.0f}%</strong></span>
                <span>Anomaly Flag: <strong>{"Yes" if extracted.anomaly_flag else "None"}</strong></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 2: BENCHMARK & ERROR TAXONOMY
# ---------------------------------------------------------
with tab_benchmark:
    metrics_path = Path("reports/metrics_summary.json")
    chart_path = Path("reports/evaluation_metrics_chart.png")

    if metrics_path.exists():
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)

        mode_ran = metrics.get("extractor_mode", "baseline").upper()
        st.caption(f"Currently viewing evaluation artifacts generated for: **{mode_ran}**")

        m_cols = st.columns(5)
        m_cols[0].metric("Evaluated Segments", f"{metrics['total_segments_evaluated']}")
        m_cols[1].metric("Exact Match Rate", f"{metrics['exact_segment_match_rate']*100:.1f}%")
        m_cols[2].metric("Road Classification F1", f"{metrics['attributes']['road_type']['f1_score']*100:.1f}%")
        m_cols[3].metric("Barrier Detection F1", f"{metrics['attributes']['barrier_present']['f1_score']*100:.1f}%")
        m_cols[4].metric("Surface Material F1", f"{metrics['attributes']['surface_type']['f1_score']*100:.1f}%")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        chart_col, err_col = st.columns([1.1, 1], gap="medium")
        with chart_col:
            st.markdown("""
            <div class="card">
                <div class="card-title">Precision &amp; Recall Performance</div>
            """, unsafe_allow_html=True)
            if chart_path.exists():
                st.image(str(chart_path), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with err_col:
            st.markdown("""
            <div class="card">
                <div class="card-title">Spatial Error Taxonomy</div>
            """, unsafe_allow_html=True)
            err_dict = metrics.get("error_taxonomy_breakdown", {})
            if err_dict:
                err_df = pd.DataFrame([
                    {"Error Category": k, "Count": v, "Percentage": f"{v/metrics['total_segments_evaluated']*100:.1f}%"}
                    for k, v in err_dict.items()
                ])
                st.dataframe(err_df, hide_index=True, use_container_width=True)
                st.caption("Discrepancies are categorized into domain-specific error types to prioritize prompt refinements.")
            else:
                st.write("Zero errors detected across the current evaluation suite.")
            st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 3: PIPELINE ARCHITECTURE
# ---------------------------------------------------------
with tab_workflow:
    st.markdown("""
    <div class="card">
        <div class="card-title">Prefect Workflow Orchestration</div>
        <p style="font-size: 13px; color: #475569; line-height: 1.6;">
            The QA pipeline runs as a resilient Prefect flow coordinating 5 distinct tasks:
        </p>
        <ol style="font-size: 13px; color: #334155; line-height: 1.8; margin-left: 18px;">
            <li><strong>Data Ingestion:</strong> Loads verified OpenStreetMap road segments from <code>data/osm_ground_truth_cluj.json</code>.</li>
            <li><strong>Batch Extraction:</strong> Runs the selected extractor (Rule-Based Baseline, Claude 3.5 Sonnet, or GPT-4o) using LangChain and strict Pydantic schemas.</li>
            <li><strong>Benchmarking:</strong> Computes precision, recall, and F1 scores using scikit-learn.</li>
            <li><strong>Error Taxonomy:</strong> Maps discrepancies into structured categories (speed hallucinations, road class mismatches).</li>
            <li><strong>Artifact Export:</strong> Generates evaluation reports and Matplotlib summary charts.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='font-size: 12px; font-weight: 600; text-transform: uppercase; color: #64748b;'>Command Line Execution</p>", unsafe_allow_html=True)
    st.code("""
# Run the rule-based baseline (no API key required):
python run_pipeline.py --mode baseline

# Run with Anthropic Claude 3.5 Sonnet (requires ANTHROPIC_API_KEY):
python run_pipeline.py --mode claude
    """, language="bash")
