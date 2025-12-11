import pandas as pd
import folium
import streamlit as st
from folium import GeoJson, FeatureGroup, CircleMarker, PolyLine
from streamlit_folium import st_folium

from src.utils import normalize, find_municipality_match, load_poly, load_roads

st.header("Road Infrastructure")
st.markdown("")
st.markdown("")

roads = load_roads()
poly = load_poly()
roads = roads.to_crs(poly.crs)
roads = roads.sjoin(poly, how='inner', predicate='intersects').drop(columns=['index_right'])

# --- Global Sidebar: Municipality Selector ---
if 'highlight_municipality' not in st.session_state:
    st.session_state.highlight_municipality = "Veliko Gradište"
if 'valid_municipality' not in st.session_state:
    st.session_state.valid_municipality = "Veliko Gradište"
with st.sidebar:
    st.markdown("### 🔎 Municipality selector")
    st.text_input(
        "Highlight a municipality (you can type partial or accent-free name, e.g., sabac or Nis):",
        value=st.session_state.highlight_municipality,
        placeholder="e.g., sabac or Nis",
        key="highlight_municipality"
    )
    name_lookup = {normalize(s): s for s in poly["Municipality"].unique()}
    if st.session_state.highlight_municipality.strip():
        matches = find_municipality_match(st.session_state.highlight_municipality, name_lookup)

        if len(matches) == 1:
            st.session_state.valid_municipality = matches[0]
            st.success(f"✅ Highlighted Municipality: **{st.session_state.valid_municipality}**")
            
        elif len(matches) > 1:
            st.info(f"Found multiple matches: {', '.join(matches[:])}... (showing: **{st.session_state.valid_municipality}**)")
        else:
            st.warning(f"No match found. Try typing part of the name or removing accents. (showing: **{st.session_state.valid_municipality}**)")
            
            
municipality = st.session_state.valid_municipality

roads = roads.to_crs(epsg=3857)

total_length = roads.length.sum() / 1000
total_trunk = roads[roads['fclass'] == 'trunk'].length.sum() / 1000
total_primary = roads[roads['fclass'] == 'primary'].length.sum() / 1000
total_secondary = roads[roads['fclass'] == 'secondary'].length.sum() / 1000
total_tertiary = roads[roads['fclass'] == 'tertiary'].length.sum() / 1000
total_link = roads[roads['fclass'].isin(["trunk_link", "primary_link", "secondary_link", "tertiary_link"])].length.sum() / 1000
total_local = roads[roads['fclass'].isin(["residential", "unclassified", "service"])].length.sum() / 1000
total_bridges = len(roads[roads['bridge'] == 'T'])
total_tunnels = len(roads[roads['tunnel'] == 'T'])


muni_roads = roads[roads['Municipality'] == municipality]
muni_length = (muni_roads.length.sum() / 1000) if not muni_roads.empty else 0
muni_trunk = (muni_roads[muni_roads['fclass'] == 'trunk'].length.sum() / 1000) if not muni_roads.empty else 0
muni_primary = (muni_roads[muni_roads['fclass'] == 'primary'].length.sum() / 1000) if not muni_roads.empty else 0
muni_secondary = (muni_roads[muni_roads['fclass'] == 'secondary'].length.sum() / 1000) if not muni_roads.empty else 0
muni_tertiary = (muni_roads[muni_roads['fclass'] == 'tertiary'].length.sum() / 1000) if not muni_roads.empty else 0
muni_link = (muni_roads[muni_roads['fclass'].isin(["trunk_link", "primary_link", "secondary_link", "tertiary_link"])].length.sum() / 1000) if not muni_roads.empty else 0
muni_local = (muni_roads[muni_roads['fclass'].isin(["residential", "unclassified", "service"])].length.sum() / 1000) if not muni_roads.empty else 0
muni_bridges = len(muni_roads[muni_roads['bridge'] == 'T']) if not muni_roads.empty else 0
muni_tunnels = len(muni_roads[muni_roads['tunnel'] == 'T']) if not muni_roads.empty else 0

col1, col2 = st.columns(2)
with col1:
    st.subheader("**National overview**")
    st.markdown(f"**Total Road length:** {total_length:.2f} km")
    st.markdown(f'<span style="color: #c43b3b; font-weight: bold;">Trunk roads:</span> {total_trunk:.2f} km', unsafe_allow_html=True)
    st.markdown(f'<span style="color: #f08a24; font-weight: bold;">Primary roads:</span> {total_primary:.2f} km', unsafe_allow_html=True)
    st.markdown(f'<span style="color: #f0c419; font-weight: bold;">Secondary roads:</span> {total_secondary:.2f} km', unsafe_allow_html=True)
    st.markdown(f'<span style="color: blue; font-weight: bold;">Tertiary roads:</span> {total_tertiary:.2f} km', unsafe_allow_html=True)
    st.markdown(f'<span style="color: pink; font-weight: bold;">Link roads:</span> {total_link:.2f} km', unsafe_allow_html=True)
    st.markdown(f'<span style="color: brown; font-weight: bold;">Local roads:</span> {total_local:.2f} km', unsafe_allow_html=True)
    st.markdown(f'<span style="color: #2a9d8f; font-weight: bold;">Bridges:</span> {total_bridges}', unsafe_allow_html=True)
    st.markdown(f'<span style="color: #6c757d; font-weight: bold;">Tunnels:</span> {total_tunnels}', unsafe_allow_html=True)
    
with col2:
    st.subheader(f"**{municipality} overview**")
    st.markdown(f"**Total Road length:** {muni_length:.2f} km")
    st.markdown(f'<span style="color: #c43b3b; font-weight: bold;">Trunk roads:</span> {muni_trunk:.2f} km', unsafe_allow_html=True)
    st.markdown(f'<span style="color: #f08a24; font-weight: bold;">Primary roads:</span> {muni_primary:.2f} km', unsafe_allow_html=True)
    st.markdown(f'<span style="color: #f0c419; font-weight: bold;">Secondary roads:</span> {muni_secondary:.2f} km', unsafe_allow_html=True)
    st.markdown(f'<span style="color: blue; font-weight: bold;">Tertiary roads:</span> {muni_tertiary:.2f} km', unsafe_allow_html=True)
    st.markdown(f'<span style="color: pink; font-weight: bold;">Link roads:</span> {muni_link:.2f} km', unsafe_allow_html=True)
    st.markdown(f'<span style="color: brown; font-weight: bold;">Local roads:</span> {muni_local:.2f} km', unsafe_allow_html=True)
    st.markdown(f'<span style="color: #2a9d8f; font-weight: bold;">Bridges:</span> {muni_bridges}', unsafe_allow_html=True)
    st.markdown(f'<span style="color: #6c757d; font-weight: bold;">Tunnels:</span> {muni_tunnels}', unsafe_allow_html=True)
    
st.markdown("")
st.markdown("")

roads = roads.to_crs(poly.crs)

poly_plot = poly[poly['Municipality'] == municipality]
roads_plot = roads.sjoin(poly_plot, how='inner', predicate='intersects')
roads_plot['bridge'] = roads_plot['bridge'].replace({'T': 'Yes', 'F': 'No'})
roads_plot['tunnel'] = roads_plot['tunnel'].replace({'T': 'Yes', 'F': 'No'})

# Convert to WGS84 for Folium
poly_wgs84 = poly_plot.to_crs("EPSG:4326")
roads_wgs84 = roads_plot.to_crs("EPSG:4326")

# Simplify geometries to reduce coordinate count (tolerance in degrees, ~100m)
roads_wgs84 = roads_wgs84.copy()
roads_wgs84['geometry'] = roads_wgs84.geometry.simplify(tolerance=0.001, preserve_topology=True)

# Calculate map center from bounding box
bounds = poly_wgs84.total_bounds
center_lat = (bounds[1] + bounds[3]) / 2
center_lon = (bounds[0] + bounds[2]) / 2

# Create base map
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=12,
    tiles='CartoDB positron'
)

# --- Road layer configuration ---
road_config = {
    "Local Roads": {
        "fclass": ["residential", "unclassified", "service"],
        "color": "brown",
        "weight": 1,
        "show": True
    },
    "Link Roads": {
        "fclass": ["trunk_link", "primary_link", "secondary_link", "tertiary_link"],
        "color": "pink",
        "weight": 1.5,
        "show": True
    },
    "Tertiary Roads": {
        "fclass": ["tertiary"],
        "color": "blue",
        "weight": 2,
        "show": True
    },
    "Secondary Roads": {
        "fclass": ["secondary"],
        "color": "#f0c419",
        "weight": 2.5,
        "show": True
    },
    "Primary Roads": {
        "fclass": ["primary"],
        "color": "#f08a24",
        "weight": 3.5,
        "show": True
    },
    "Trunk Roads": {
        "fclass": ["trunk"],
        "color": "#c43b3b",
        "weight": 4,
        "show": True
    },
    
}

# Style function factory for roads (handles bridge/tunnel coloring)
def make_style_function(default_color, weight):
    def style_function(feature):
        props = feature.get('properties', {})
        is_bridge = props.get('bridge', 'No') == 'Yes'
        is_tunnel = props.get('tunnel', 'No') == 'Yes'
        
        if is_bridge:
            color = '#2a9d8f'
        elif is_tunnel:
            color = '#6c757d'
        else:
            color = default_color
        
        return {
            'color': color,
            'weight': weight,
            'opacity': 0.85
        }
    return style_function

# --- Layer 1: District Boundaries ---
boundaries_layer = FeatureGroup(name='District Boundaries', show=True)
folium.GeoJson(
    poly_wgs84,
    style_function=lambda x: {
        'fillColor': 'transparent',
        'color': '#333333',
        'weight': 1,
        'fillOpacity': 0
    }
).add_to(boundaries_layer)
boundaries_layer.add_to(m)

# --- Layer 2: Roads by class (using GeoJson for performance) ---
for layer_name, config in road_config.items():
    # Filter roads for this layer
    layer_roads = roads_wgs84[roads_wgs84['fclass'].isin(config['fclass'])]
    
    if layer_roads.empty:
        continue
    
    # Create feature group
    layer = FeatureGroup(name=layer_name, show=config['show'])
    
    # Add GeoJson with style function and popup
    folium.GeoJson(
        layer_roads,
        style_function=make_style_function(config['color'], config['weight']),
        tooltip=folium.GeoJsonTooltip(
            fields=['fclass', 'bridge', 'tunnel'],
            aliases=['Class:', 'Bridge:', 'Tunnel:'],
            localize=True
        ),
        popup=folium.GeoJsonPopup(
            fields=['fclass', 'bridge', 'tunnel'],
            aliases=['<b>Class</b>', '<b>Bridge</b>', '<b>Tunnel</b>'],
            localize=True
        )
    ).add_to(layer)
    
    layer.add_to(m)
    # print(f"Added {layer_name}: {len(layer_roads)} segments")

# Add layer control
folium.LayerControl(collapsed=False).add_to(m)

# --- Custom Legend ---
legend_html = '''
<div style="position: fixed; top: 30px; left: 10%; transform: translateX(-50%); z-index: 9999;
            background: rgba(255,255,255,0.95); padding: 12px 16px; border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.25); font-family: Arial, sans-serif; font-size: 12px;">
    <h4 style="margin: 0 0 10px 0; color: #333; border-bottom: 1px solid #ddd; padding-bottom: 6px;">Legend</h4>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 30px; height: 4px; background: #c43b3b; margin-right: 8px;"></span>Trunk
    </div>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 30px; height: 3.5px; background: #f08a24; margin-right: 8px;"></span>Primary
    </div>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 30px; height: 2.5px; background: #f0c419; margin-right: 8px;"></span>Secondary
    </div>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 30px; height: 2px; background: blue; margin-right: 8px;"></span>Tertiary
    </div>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 30px; height: 1.5px; background: pink; margin-right: 8px;"></span>Links
    </div>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 30px; height: 1px; background: brown; margin-right: 8px;"></span>Local
    </div>
    <hr style="margin: 8px 0; border: none; border-top: 1px solid #ddd;">
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 30px; height: 3px; background: #2a9d8f; margin-right: 8px;"></span>🌉 Bridge
    </div>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 30px; height: 3px; background: #6c757d; margin-right: 8px;"></span>🚇 Tunnel
    </div>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 30px; height: 3px; background: black; margin-right: 8px;"></span>District Boundaries
    </div>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Add title
title_html = '''
<div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%); z-index: 9999;
            background: rgba(255,255,255,0.9); padding: 10px 20px; border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2); font-family: Arial, sans-serif;">
    <h3 style="margin: 0; color: #333;">Serbia – National Road Network via OSM</h3>
    <p style="margin: 5px 0 0 0; font-size: 12px; color: #666;">Toggle layers • Click roads for details</p>
</div>
'''
m.get_root().html.add_child(folium.Element(title_html))

st_folium(m, height=1500, use_container_width=True, returned_objects=[])