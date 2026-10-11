"""Metric geometry checks and conservative barrier-to-road association."""
from pathlib import Path
import geopandas as gpd
from shapely.geometry import LineString, Point
from src.mapqa_data import save_json
from src.osm_values import parse_speed


def geometry_frames(snapshot):
    roads, barriers, excluded = [], [], []
    for element in snapshot['elements']:
        tags = element.get('tags', {})
        if element['type'] == 'way' and tags.get('highway'):
            coordinates = [(p['lon'], p['lat']) for p in element.get('geometry', [])
                           if 'lon' in p and 'lat' in p]
            # Never connect across an omitted coordinate in an incomplete geometry.
            if len(coordinates) < 2 or len(coordinates) != len(element.get('geometry', [])):
                excluded.append({'way_id': element['id'], 'reason': 'missing_geometry'})
                continue
            geometry = LineString(coordinates)
            if geometry.is_empty or not geometry.is_valid or geometry.length == 0:
                excluded.append({'way_id': element['id'], 'reason': 'invalid_geometry'})
                continue
            roads.append({'way_id': str(element['id']), 'tags': tags,
                          'nodes': element.get('nodes', []), 'geometry': geometry})
        elif element['type'] == 'node' and tags.get('barrier') and 'lon' in element and 'lat' in element:
            barriers.append({'node_id': str(element['id']), 'tags': tags,
                             'geometry': Point(element['lon'], element['lat'])})
    if not roads:
        raise ValueError('No valid road geometry in snapshot')
    roads = gpd.GeoDataFrame(roads, crs='EPSG:4326')
    barriers = gpd.GeoDataFrame(barriers, columns=['node_id','tags','geometry'], crs='EPSG:4326')
    metric_crs = roads.estimate_utm_crs()
    if metric_crs is None:
        raise ValueError('Could not select local metric CRS')
    roads = roads.to_crs(metric_crs)
    barriers = barriers.to_crs(metric_crs)
    roads['length_m'] = roads.length
    roads['node_count'] = roads.nodes.map(len)
    roads['centroid_x_m'] = roads.geometry.centroid.x
    roads['centroid_y_m'] = roads.geometry.centroid.y
    return roads, barriers, excluded


def associate_barriers(roads, barriers, max_distance_m=10):
    if max_distance_m <= 0:
        raise ValueError('Association distance must be positive')
    if (roads.crs is None or barriers.crs != roads.crs or not roads.crs.is_projected
            or any(axis.unit_name.lower() not in ('metre','meter') for axis in roads.crs.axis_info)):
        raise ValueError('Association requires identical projected CRS in metres')
    members = {}
    for row in roads.itertuples():
        for node in row.nodes:
            members.setdefault(str(node), []).append(row.way_id)
    byid = roads.set_index('way_id')
    associations = []
    for barrier in barriers.itertuples():
        linked = members.get(barrier.node_id, [])
        if linked:
            for way in linked:
                associations.append({'node_id': barrier.node_id, 'way_id': way,
                                     'method': 'shared_node', 'confirmed_topology': True,
                                     'distance_m': float(barrier.geometry.distance(byid.loc[way].geometry)),
                                     'barrier_type': barrier.tags['barrier']})
        else:
            # GeoPandas nearest spatial join; all equidistant candidates stay visible.
            point = barriers.loc[[barrier.Index], ['node_id', 'geometry']]
            nearest = point.sjoin_nearest(roads[['way_id','geometry']], how='left',
                                         max_distance=max_distance_m, distance_col='distance_m')
            candidates = nearest.dropna(subset=['way_id'])
            for row in candidates.itertuples():
                associations.append({'node_id': barrier.node_id, 'way_id': row.way_id,
                                     'method': 'nearest_candidate', 'confirmed_topology': False,
                                     'distance_m': float(row.distance_m), 'barrier_type': barrier.tags['barrier']})
            if candidates.empty:
                associations.append({'node_id': barrier.node_id, 'way_id': None,
                                     'method': 'unassociated', 'confirmed_topology': False,
                                     'distance_m': None, 'barrier_type': barrier.tags['barrier']})
    return associations


def road_issues(roads, excluded):
    issues = [{'way_id': str(row['way_id']), 'category': row['reason'], 'severity': 'review'} for row in excluded]
    for road in roads.itertuples():
        tags = road.tags
        if road.length_m < 2:
            issues.append({'way_id': road.way_id, 'category': 'very_short_geometry', 'severity': 'review'})
        if not road.geometry.is_simple:
            issues.append({'way_id': road.way_id, 'category': 'self_intersection', 'severity': 'review'})
        speed = parse_speed(tags.get('maxspeed'))
        if tags.get('highway') == 'residential' and speed is not None and speed > 80:
            issues.append({'way_id': road.way_id, 'category': 'unusual_residential_speed', 'severity': 'review'})
        if 'oneway' in tags and tags['oneway'] not in ('yes','no','1','0','true','false','-1','reversible','alternating'):
            issues.append({'way_id': road.way_id, 'category': 'unrecognized_oneway', 'severity': 'review'})
    return issues


def export_geometry(snapshot, output_dir):
    output_dir = Path(output_dir)
    roads, barriers, excluded = geometry_frames(snapshot)
    associations = associate_barriers(roads, barriers)
    issues = road_issues(roads, excluded)
    issues_byid = {}
    for issue in issues:
        issues_byid.setdefault(issue['way_id'], []).append(issue['category'])
    roads['qa_categories'] = roads.way_id.map(lambda way: issues_byid.get(way, []))
    road_geojson = roads.to_crs(4326).__geo_interface__
    barrier_geojson = barriers.to_crs(4326).__geo_interface__
    save_json(output_dir/'roads.geojson', road_geojson)
    save_json(output_dir/'barriers.geojson', barrier_geojson)
    save_json(output_dir/'barrier_associations.json', associations)
    save_json(output_dir/'qa_issues.json', issues)
    summary = {'roads': len(roads), 'barrier_nodes': len(barriers), 'excluded_geometries': len(excluded),
               'metric_crs': str(roads.crs), 'topological_associations': sum(a['confirmed_topology'] for a in associations),
               'nearest_candidates': sum(a['method']=='nearest_candidate' for a in associations),
               'unassociated_barriers': sum(a['method']=='unassociated' for a in associations),
               'qa_issue_count': len(issues), 'spatial_error_taxonomy': ['missing_geometry','invalid_geometry',
                    'very_short_geometry','self_intersection','unusual_residential_speed','unrecognized_oneway',
                    'nearest_candidate','unassociated'],
               'note': 'QA flags are review suggestions, not verified map errors. Nearest is not a confirmed connection.'}
    save_json(output_dir/'geometry_summary.json', summary)
    return roads, barriers, associations, summary
