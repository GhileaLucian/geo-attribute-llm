"""Fixed, offline classification audit; never alters earlier ML reports."""
from pathlib import Path
import hashlib
import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report
from sklearn.pipeline import make_pipeline

from src.config import PROJECT_ROOT
from src.mapqa_data import read_snapshot, save_json
from src.mapqa_geo import geometry_frames
from src.mapqa_ml import features, groups_for, road_family, split_indices


def east_holdout(roads, buffer_m=200):
    """Fixed eastern quarter by centroid x, excluding boundary-crossing roads.

    Test lines are entirely east of the boundary; training lines entirely west
    of boundary minus buffer. Thus full geometries, not just centroids, are apart.
    Same-name groups are removed from training if present in test.
    """
    if roads.crs is None or not roads.crs.is_projected or any(
            axis.unit_name.lower() not in ('metre', 'meter') for axis in roads.crs.axis_info):
        raise ValueError('Spatial audit needs a projected metric CRS')
    if buffer_m <= 0:
        raise ValueError('Positive geographic buffer required')
    cutoff = float(roads.centroid_x_m.quantile(.75))
    bounds = roads.geometry.bounds
    test = np.flatnonzero((bounds.minx >= cutoff).to_numpy())
    groups = groups_for(roads)
    test_groups = set(groups.iloc[test])
    train = np.flatnonzero(((bounds.maxx <= cutoff - buffer_m) & ~groups.isin(test_groups)).to_numpy())
    if len(train) < 20 or len(test) < 20:
        raise ValueError('Insufficient roads after spatial/group exclusions')
    if set(groups.iloc[train]) & test_groups:
        raise ValueError('Group leakage in spatial split')
    metadata = {'method': 'Eastern region: full geometry bounds; cutoff at 75th percentile centroid x',
                'cutoff_x_m': cutoff, 'buffer_m': buffer_m,
                'guaranteed_minimum_x_separation_m': float(bounds.iloc[test].minx.min() - bounds.iloc[train].maxx.max()),
                'excluded_n': len(roads) - len(train) - len(test),
                'train_n': len(train), 'test_n': len(test),
                'road_group_overlap': 0}
    return train, test, metadata


def compare_models(roads, train, test):
    X = features(roads)
    y = roads.tags.map(lambda t: road_family(t['highway']))
    if y.iloc[train].nunique() < 2:
        raise ValueError('Need multiple classes in training')
    models = {}
    specs = [('majority', DummyClassifier(strategy='most_frequent'), list(X.columns)),
             ('forest_with_coordinates', RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=2), list(X.columns)),
             ('forest_without_coordinates', RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=2),
              [c for c in X.columns if c not in ('centroid_x_m', 'centroid_y_m')])]
    for name, model, columns in specs:
        estimator = make_pipeline(SimpleImputer(strategy='median', add_indicator=True), model)
        estimator.fit(X.iloc[train][columns], y.iloc[train])
        prediction = estimator.predict(X.iloc[test][columns])
        models[name] = {'features': columns, 'classification_report': classification_report(
            y.iloc[test], prediction, output_dict=True, zero_division=0)}
    return {'train_n': len(train), 'test_n': len(test),
            'train_class_support': y.iloc[train].value_counts().to_dict(),
            'test_class_support': y.iloc[test].value_counts().to_dict(), 'models': models}


def run(output=PROJECT_ROOT / 'reports' / 'spatial_ml_audit'):
    output = Path(output)
    if output.exists():
        raise FileExistsError('Audit already exists; use a new output directory, never overwrite results')
    roads, _, _ = geometry_frames(read_snapshot())
    X = features(roads)
    groups = groups_for(roads)
    tr, te = split_indices(X, groups)
    st, se, policy = east_holdout(roads)
    result = {'classification_only': True, 'crs': str(roads.crs),
              'snapshot_sha256': hashlib.sha256(
                  (PROJECT_ROOT / 'data/mapqa/snapshot.json').read_bytes()).hexdigest(),
              'grouped_split': compare_models(roads, tr, te),
              'geographic_split': {**compare_models(roads, st, se), 'policy': policy},
              'fixed_before_fit': {'seed': 42, 'n_estimators': 100, 'max_depth': 10,
                                   'cutoff_quantile': .75, 'buffer_m': 200, 'hyperparameter_search': False},
              'limitations': ['One geographic hold-out, not spatial cross-validation or independent ground truth.',
                              'Eastern roads can have a different class mix; scores across splits are not directly comparable.',
                              'Coordinate ablation uses identical rows within each split; it does not prove causation or previous leakage.',
                              'A 200m gap reduces immediate-neighbour leakage but not all spatial correlation.',
                              'Geometry and tags still reflect OSM mapping practice; no production accuracy claim.']}
    save_json(output / 'summary.json', result)
    save_json(output / 'splits.json', {
        'grouped': {'train_ids': roads.iloc[tr].way_id.tolist(), 'test_ids': roads.iloc[te].way_id.tolist()},
        'geographic': {'train_ids': roads.iloc[st].way_id.tolist(), 'test_ids': roads.iloc[se].way_id.tolist()}})
    return result
