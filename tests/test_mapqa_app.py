"""The new map/ML tab must be inspectable without a model or a paid API."""
from unittest.mock import Mock
from streamlit.testing.v1 import AppTest
from src.config import PROJECT_ROOT


def test_map_layers_and_report_filters_are_read_only(monkeypatch):
    import src.mapqa_evidence
    import src.mapqa_benchmark
    mock=Mock(side_effect=AssertionError('Dashboard must not invoke local inference'))
    monkeypatch.setattr(src.mapqa_evidence.LangChainEvidenceExtractor,'extract',mock)
    monkeypatch.setattr(src.mapqa_benchmark,'benchmark',mock)
    app=AppTest.from_file(str(PROJECT_ROOT/'app.py')).run(timeout=30)
    assert not app.exception
    assert any(tab.label=='Map QA & ML' for tab in app.tabs)
    for option in ('GIS review suggestions','DBSCAN clusters','ML review suggestions'):
        app.selectbox(key='mapqa_layer').select(option).run(timeout=30)
        assert not app.exception
    app.selectbox(key='mapqa_attribute').select('speed_limit_kmh').run(timeout=30)
    assert not app.exception and not mock.called
