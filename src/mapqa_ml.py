"""Fixed exploratory ML experiments; predictions are not legal map attributes."""
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, confusion_matrix, mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder
from src.mapqa_data import save_json
from src.osm_values import parse_speed


def features(roads):
    frame=roads[['way_id','length_m','node_count','centroid_x_m','centroid_y_m']].drop(columns='way_id').copy()
    frame['lanes']=roads.tags.map(lambda t: float(t['lanes']) if str(t.get('lanes','')).isdigit() else np.nan)
    frame['bridge']=roads.tags.map(lambda t: int(t.get('bridge')=='yes'))
    frame['tunnel']=roads.tags.map(lambda t: int(t.get('tunnel')=='yes'))
    return frame


def groups_for(roads):
    return roads.apply(lambda r: r.tags.get('name') or 'way:'+r.way_id,axis=1)


def split_indices(frame, groups):
    if len(set(groups))<4: raise ValueError('Need at least four distinct road groups')
    train,test=next(GroupShuffleSplit(n_splits=1,test_size=.25,random_state=42).split(frame,groups=groups))
    assert not set(groups.iloc[train]) & set(groups.iloc[test])
    return train,test


def road_family(highway):
    if highway in ('footway','path','steps','pedestrian','cycleway','bridleway'): return 'non_motorized'
    if highway in ('motorway','trunk','primary','secondary','tertiary','motorway_link','trunk_link','primary_link','secondary_link','tertiary_link'): return 'major_road'
    if highway in ('residential','living_street','service','unclassified','track'): return 'local_road'
    return 'other'


def run_ml(roads, output):
    X=features(roads)
    groups=groups_for(roads)
    train,test=split_indices(X,groups)
    y=roads.tags.map(lambda t:road_family(t['highway']))
    classification={}
    for name,model in [('majority',DummyClassifier(strategy='most_frequent')),
                        ('random_forest',RandomForestClassifier(n_estimators=100,max_depth=10,random_state=42,n_jobs=2))]:
        estimator=make_pipeline(SimpleImputer(strategy='median',add_indicator=True),model)
        estimator.fit(X.iloc[train],y.iloc[train])
        prediction=estimator.predict(X.iloc[test])
        labels=sorted(set(y.iloc[test])|set(prediction))
        classification[name]={'report':classification_report(y.iloc[test],prediction,zero_division=0,output_dict=True),
                              'confusion_matrix':{'labels':labels,'values':confusion_matrix(y.iloc[test],prediction,labels=labels).tolist()}}
    speeds=roads.tags.map(lambda t:parse_speed(t.get('maxspeed')))
    known=speeds.notna() & (speeds>=0) & (speeds<=300)
    regression={'status':'not_evaluated','reason':'Need at least 40 known numeric speed labels and four road groups.'}
    if known.sum()>=40 and groups[known].nunique()>=4:
        XR=X.loc[known].copy()
        XR['highway']=roads.loc[known,'tags'].map(lambda t:t['highway'])
        yr=speeds[known].astype(float)
        gr=groups[known]
        tr,te=split_indices(XR,gr)
        numeric=list(X.columns)
        transformer=ColumnTransformer([('numeric',make_pipeline(SimpleImputer(strategy='median',add_indicator=True)),numeric),
                                       ('category',OneHotEncoder(handle_unknown='ignore'),['highway'])])
        regression={'status':'evaluated','labeled_records':int(known.sum()),'train_n':len(tr),'test_n':len(te),
                    'target':'Recorded numeric OSM maxspeed; NOT a verified legal speed or automatic map update.',
                    'models':{}}
        for name,model in [('median',DummyRegressor(strategy='median')),
                          ('random_forest',RandomForestRegressor(n_estimators=100,max_depth=10,random_state=42,n_jobs=2))]:
            estimator=make_pipeline(transformer,model)
            estimator.fit(XR.iloc[tr],yr.iloc[tr])
            prediction=estimator.predict(XR.iloc[te])
            regression['models'][name]={'mae_kmh':float(mean_absolute_error(yr.iloc[te],prediction)),
                                       'rmse_kmh':float(np.sqrt(mean_squared_error(yr.iloc[te],prediction))),
                                       'r2':float(r2_score(yr.iloc[te],prediction))}
        save_json(output/'regression_split.json',{'train_ids':roads.loc[known].iloc[tr].way_id.tolist(),
                                               'test_ids':roads.loc[known].iloc[te].way_id.tolist()})
    # Unsupervised descriptive analysis: no accuracy claimed without reference clusters.
    cluster=DBSCAN(eps=200,min_samples=8).fit_predict(X[['centroid_x_m','centroid_y_m']])
    clean=SimpleImputer(strategy='median').fit_transform(X)
    anomaly=IsolationForest(n_estimators=100,contamination=.03,random_state=42,n_jobs=2).fit_predict(clean)
    summary={'classification':classification,'classification_train_n':len(train),'classification_test_n':len(test),
             'class_support':y.value_counts().to_dict(),'split':'GroupShuffleSplit by road name, unnamed roads by way ID; seed 42; no hyperparameter search.',
             'features':list(X.columns),'target_leakage_policy':'Highway excluded from classification; maxspeed and its aliases excluded from regression features.',
             'regression':regression,'clustering':{'method':'DBSCAN on projected road centroids','eps_m':200,'min_samples':8,
                'clusters':len(set(cluster)-{-1}),'noise_count':int((cluster==-1).sum()),'reference_labels':None},
             'anomalies':{'method':'IsolationForest','suggestions':int((anomaly==-1).sum()),'verified_errors':None},
             'limitations':['Exploratory OSM-label experiments, not production models.',
                            'Road-name groups reduce same-road leakage but nearby roads may still cross splits.',
                            'Geometry/node-count correlations can reflect mapping practices.',
                            'Cluster and anomaly outputs require expert review.']}
    save_json(output/'ml_summary.json',summary)
    save_json(output/'classification_split.json',{'train_ids':roads.iloc[train].way_id.tolist(),'test_ids':roads.iloc[test].way_id.tolist()})
    layers=roads[['way_id','geometry']].copy()
    layers['cluster']=cluster
    layers['ml_review_suggestion']=(anomaly==-1)
    save_json(output/'ml_roads.geojson',layers.to_crs(4326).__geo_interface__)
    return summary
