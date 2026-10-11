"""Saved-artifact viewer only: UI reruns never invoke a model or modify labels."""
import json
from pathlib import Path
import pandas as pd
import pydeck as pdk
import streamlit as st
from src.config import PROJECT_ROOT


@st.cache_data(show_spinner=False)
def read_artifact(path,modified_ns):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def saved(path):
    return read_artifact(str(path),path.stat().st_mtime_ns)


def render_mapqa():
    root=PROJECT_ROOT/'reports'/'mapqa'
    if not (root/'geometry_summary.json').exists():
        st.info('Run python run_mapqa.py prepare first. No network/model request is made by this tab.')
        return
    summary=saved(root/'geometry_summary.json')
    st.subheader('Map QA — actual OSM geometry')
    st.caption('OSM snapshot, not field-verified truth. Distances use '+summary['metric_crs']+'. QA flags need human review.')
    a,b,c=st.columns(3)
    a.metric('Road ways',summary['roads']); b.metric('Barrier nodes',summary['barrier_nodes']); c.metric('GIS review flags',summary['qa_issue_count'])
    choice=st.selectbox('Map layer',['Roads and barriers','GIS review suggestions','DBSCAN clusters','ML review suggestions'],key='mapqa_layer')
    limit=st.slider('Maximum displayed road geometries',200,15000,3000,200,key='mapqa_limit')
    geometries=saved(root/'roads.geojson')['features']
    ml=saved(root/'ml_roads.geojson')['features'] if (root/'ml_roads.geojson').exists() else []
    byid={f['properties']['way_id']:f['properties'] for f in ml}
    colors=[[47,128,237],[18,184,134],[255,169,77],[132,94,247],[240,101,149],[34,184,207],[250,82,82],[148,216,45]]
    rows=[]
    for f in geometries:
        prop=f['properties']; extra=byid.get(prop['way_id'],{})
        review=bool(prop.get('qa_categories'))
        if choice=='GIS review suggestions' and not review: continue
        if choice=='ML review suggestions' and not extra.get('ml_review_suggestion'): continue
        cluster=extra.get('cluster',-1)
        color=colors[cluster%len(colors)] if choice=='DBSCAN clusters' and cluster>=0 else ([220,60,60] if review else [70,120,180])
        rows.append({'path':f['geometry']['coordinates'],'way_id':prop['way_id'],'color':color,
                     'details':', '.join(prop.get('qa_categories',[])) or 'No GIS flag','cluster':cluster})
    count=len(rows)
    # Deterministic even sampling, not misleading first-N geography.
    if count>limit:
        rows=[rows[int(i*count/limit)] for i in range(limit)]
    barriers=[{'position':f['geometry']['coordinates'],'node_id':f['properties']['node_id']}
              for f in saved(root/'barriers.geojson')['features']]
    deck=pdk.Deck(layers=[
        pdk.Layer('PathLayer',rows,get_path='path',get_color='color',get_width=3,width_min_pixels=1,pickable=True),
        pdk.Layer('ScatterplotLayer',barriers,get_position='position',get_fill_color=[200,30,80],get_radius=4,
                  radius_min_pixels=2,pickable=True)],
        initial_view_state=pdk.ViewState(latitude=46.77,longitude=23.60,zoom=12),map_style=None,
        tooltip={'text':'Way {way_id}\n{details}\nCluster {cluster}'})
    st.pydeck_chart(deck,use_container_width=True)
    st.caption(f'Displayed {len(rows)} of {count} matching road ways; all {summary["roads"]} were analyzed. © OpenStreetMap contributors, ODbL. No paid basemap/API key required.')
    way=st.text_input('Inspect OSM way ID',value=rows[0]['way_id'] if rows else '',key='mapqa_way')
    feature=next((f for f in geometries if f['properties']['way_id']==way),None)
    if feature:
        with st.expander('Source tags and barrier association',expanded=False):
            st.json(feature['properties'])
            pairs=[a for a in saved(root/'barrier_associations.json') if a['way_id']==way]
            st.dataframe(pd.DataFrame(pairs),hide_index=True)
            st.link_button('Inspect this way on OSM','https://www.openstreetmap.org/way/'+way)
            st.caption('Shared node = topology. Nearest candidate ≠ confirmed connection.')
    st.subheader('Local evidence benchmark')
    files=sorted((root/'benchmarks').glob('*/benchmark_summary.json'))
    runs=[saved(p) for p in files]
    if runs:
        st.dataframe(pd.DataFrame([{k:r[k] for k in ('mode','prompt','split','n','exact_match_rate','failure_rate')} for r in runs]),hide_index=True)
        st.caption('v4/v5 allowed defaulted fields. v6 requires every field. Initial test was consumed; test_final is a fresh grouped sample. Hybrid includes Python policy guards. OSM-derived text is not independent ground truth.')
        selected=st.selectbox('Evidence report',files,format_func=lambda p:p.parent.name,key='mapqa_report')
        report=saved(selected)
        st.write('Error taxonomy:',report.get('error_detail_taxonomy',report['error_taxonomy']))
        attribute=st.selectbox('Evidence attribute',list(report['attributes']),key='mapqa_attribute')
        st.dataframe(pd.DataFrame(report['attributes'][attribute]['per_class']).T)
        with st.expander('Recorded failures and mismatches'):
            st.json(saved(selected.parent/'error_examples.json')[:5])
    if (root/'ml_summary.json').exists():
        ml_summary=saved(root/'ml_summary.json')
        st.subheader('Exploratory ML')
        st.dataframe(pd.DataFrame({k:v['report']['weighted avg'] for k,v in ml_summary['classification'].items()}).T)
        if ml_summary['regression']['status']=='evaluated':
            st.dataframe(pd.DataFrame(ml_summary['regression']['models']).T)
        st.caption('Group-separated OSM-label experiments, not verified legal speed prediction. Clusters/anomalies are descriptive review suggestions.')
    with st.expander('Reference provenance and reproducibility'):
        st.json(saved(PROJECT_ROOT/'data'/'mapqa'/'manifest.json'))
        st.json(saved(root/'reference_audit.json'))
        if (root/'schedule_smoke.json').exists(): st.json(saved(root/'schedule_smoke.json'))
        st.write('Human reference review is pending. Generated LLM scenarios are quarantined and excluded from benchmarking.')
    st.code('python run_mapqa.py all --mode rules\npython run_mapqa.py benchmark --mode langchain --prompt v6 --split dev\npython run_mapqa.py serve --interval 3600',language='powershell')
