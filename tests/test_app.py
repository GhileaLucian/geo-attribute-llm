"""The dashboard must never call an extractor just because a widget reruns."""

from unittest.mock import Mock
from streamlit.testing.v1 import AppTest
from src.config import PROJECT_ROOT


def test_api_selection_does_not_call_an_extractor(monkeypatch):
    import src.recording
    mocked = Mock(side_effect=AssertionError("No extraction expected before button click"))
    monkeypatch.setattr(src.recording, "extract_batch", mocked)
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py")).run(timeout=20)
    assert not app.exception
    # Dataset, segment, engine, version, saved run, attribute.
    app.selectbox[2].select("claude").run(timeout=20)
    assert not app.exception
    assert mocked.call_count == 0


def test_extract_click_runs_once_and_rerun_reuses_session(monkeypatch):
    from src.extractor import RuleBasedBaselineExtractor
    from src.models import ExtractionResult
    import src.recording

    def fake_batch(dataset, *args, **kwargs):
        selected = dataset[0]
        return [ExtractionResult(
            segment_id=selected.segment_id, expected=selected.expected_attributes,
            extracted=RuleBasedBaselineExtractor().extract_attributes(selected),
            execution_time_ms=1
        )]
    mocked = Mock(side_effect=fake_batch)
    monkeypatch.setattr(src.recording, "extract_batch", mocked)
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py")).run(timeout=20)
    app.button[0].click().run(timeout=20)
    assert not app.exception
    assert mocked.call_count == 1
    app.run(timeout=20)
    assert not app.exception
    assert mocked.call_count == 1
