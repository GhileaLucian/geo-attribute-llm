import geopandas as gpd
import pytest
from shapely.geometry import LineString
from src.mapqa_ml import groups_for
from src.spatial_ml_audit import east_holdout, compare_models


@pytest.fixture
def roads():
    rows = [{'way_id': str(i), 'tags': {'highway': 'residential' if i % 2 else 'footway', 'name': 'Road ' + str(i // 3), 'lanes': '2'},
             'length_m': 5, 'node_count': 2, 'centroid_x_m': i * 100 + 2.5, 'centroid_y_m': 100,
             'geometry': LineString([(i * 100, 100), (i * 100 + 5, 100)])} for i in range(120)]
    return gpd.GeoDataFrame(rows, crs='EPSG:32634')


def test_spatial_full_geometries_and_groups_separated(roads):
    train, test, metadata = east_holdout(roads)
    assert metadata['guaranteed_minimum_x_separation_m'] >= 200
    assert not set(groups_for(roads).iloc[train]) & set(groups_for(roads).iloc[test])
    assert set(train).isdisjoint(test)
    assert roads.iloc[train].geometry.bounds.maxx.max() <= metadata['cutoff_x_m'] - 200
    assert roads.iloc[test].geometry.bounds.minx.min() >= metadata['cutoff_x_m']


def test_ablation_same_rows_no_target_features(roads):
    train, test, _ = east_holdout(roads)
    result = compare_models(roads, train, test)
    models = result['models']
    assert len(models) == 3 and result['test_n'] == len(test)
    assert all('highway' not in m['features'] for m in models.values())
    assert 'centroid_x_m' in models['forest_with_coordinates']['features']
    assert 'centroid_x_m' not in models['forest_without_coordinates']['features']
    assert all(m['classification_report']['weighted avg']['support'] == len(test) for m in models.values())


def test_spatial_rejects_degrees_and_nonpositive_buffer(roads):
    with pytest.raises(ValueError, match='metric CRS'): east_holdout(roads.to_crs(4326))
    with pytest.raises(ValueError, match='Positive'): east_holdout(roads, 0)


def test_spatial_does_not_retune_for_small_sample(roads):
    with pytest.raises(ValueError, match='Insufficient'): east_holdout(roads.iloc[:20])
