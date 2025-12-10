import pandas as pd
import geopandas as gpd
import folium
import streamlit as st
from folium import FeatureGroup, CircleMarker, PolyLine
from streamlit_folium import st_folium

from src.utils import normalize, find_municipality_match, load_poly, load_rails, load_stations

st.set_page_config(
    page_title="Rail Infrastructure",
    page_icon="🚂",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.header("Rail Infrastructure")


rails = load_rails()
stations = load_stations()
poly = load_poly()

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

poly_plot = poly[poly['Municipality'] == municipality]
rails_plot = rails.sjoin(poly_plot, how='inner', predicate='intersects')
stations_plot = stations.sjoin(poly_plot, how='inner', predicate='intersects')
if not stations.empty:
    stations_wgs84 = stations_plot.to_crs("EPSG:4326")
else:
    stations_wgs84 = gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")

# Convert to WGS84 (lat/lon) for Folium
poly_wgs84 = poly_plot.to_crs("EPSG:4326")
rails_wgs84 = rails_plot.to_crs("EPSG:4326")
stations_wgs84 = stations_plot.to_crs("EPSG:4326") if not stations.empty else stations

# Calculate map center from bounding box
bounds = poly_wgs84.total_bounds  # [minx, miny, maxx, maxy]
center_lat = (bounds[1] + bounds[3]) / 2
center_lon = (bounds[0] + bounds[2]) / 2

# Create base map
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=12,
    tiles='CartoDB positron'
)

# --- Layer 1: District Boundaries ---
boundaries_layer = FeatureGroup(name='District Boundaries', show=True)
folium.GeoJson(
    poly_wgs84,
    style_function=lambda x: {
        'fillColor': 'transparent',
        'color': '#333333',
        'weight': 1,
        'fillOpacity': 0
    },
    tooltip=folium.GeoJsonTooltip(fields=['Municipality'] if 'Municipality' in poly_wgs84.columns else [])
).add_to(boundaries_layer)
boundaries_layer.add_to(m)

# --- Layer 2: Railway Lines ---
railways_layer = FeatureGroup(name='Railway Lines', show=True)
for idx, row in rails_wgs84.iterrows():
    geom = row.geometry
    
    # Get bridge/tunnel info
    is_bridge = row.get('bridge', 'F') == 'T'
    is_tunnel = row.get('tunnel', 'F') == 'T'
    
    # Build popup HTML
    popup_parts = []
    if is_bridge:
        popup_parts.append("🌉 <b>Bridge</b>")
    if is_tunnel:
        popup_parts.append("🚇 <b>Tunnel</b>")
    if not popup_parts:
        popup_parts.append("🛤️ Regular track")
    
    popup_html = "<br>".join(popup_parts)
    popup = folium.Popup(popup_html, max_width=150)
    
    # Color by type: teal=bridge, gray=tunnel, red=regular
    if is_bridge:
        color = '#2a9d8f'
    elif is_tunnel:
        color = '#6c757d'
    else:
        color = '#e63946'
    
    if geom.geom_type == 'LineString':
        coords = [(lat, lon) for lon, lat in geom.coords]
        PolyLine(
            coords,
            color=color,
            weight=3,
            opacity=0.9,
            popup=popup
        ).add_to(railways_layer)
    elif geom.geom_type == 'MultiLineString':
        for line in geom.geoms:
            coords = [(lat, lon) for lon, lat in line.coords]
            PolyLine(
                coords,
                color=color,
                weight=3,
                opacity=0.9,
                popup=popup
            ).add_to(railways_layer)
railways_layer.add_to(m)

# --- Layer 3: Train Stations ---
stations_layer = FeatureGroup(name='Train Stations', show=True)
if not stations_wgs84.empty:
    for idx, row in stations_wgs84.iterrows():
        name = row['name'] if 'name' in stations_wgs84.columns and pd.notna(row['name']) else 'Unknown Station'
        CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=3,
            color='#1d3557',
            fill=True,
            fill_color='#457b9d',
            fill_opacity=0.9,
            popup=folium.Popup(f"<b>{name}</b>", max_width=200),
            tooltip=name
        ).add_to(stations_layer)
stations_layer.add_to(m)

# Add layer control (toggle layers on/off)
folium.LayerControl(collapsed=False).add_to(m)

# --- Custom Legend ---
legend_html = '''
<div style="position: fixed; top: 30px; left: 50px; z-index: 9999;
            background: rgba(255,255,255,0.95); padding: 12px 16px; border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.25); font-family: Arial, sans-serif; font-size: 12px;">
    <h4 style="margin: 0 0 10px 0; color: #333; border-bottom: 1px solid #ddd; padding-bottom: 6px;">Map Legend</h4>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 30px; height: 3px; background: #e63946; margin-right: 8px;"></span>Railway Line
    </div>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 12px; height: 12px; background: #457b9d; border: 2px solid #1d3557; border-radius: 50%; margin-right: 8px; margin-left: 9px;"></span>Train Station
    </div>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 30px; height: 3px; background: #333333; margin-right: 8px;"></span>District Boundary
    </div>
    <hr style="margin: 8px 0; border: none; border-top: 1px solid #ddd;">
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 30px; height: 3px; background: #2a9d8f; margin-right: 8px;"></span>🌉 Bridge
    </div>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 30px; height: 3px; background: #6c757d; margin-right: 8px;"></span>🚇 Tunnel
    </div>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Add title
title_html = f'''
<div style="position: fixed; top: 10px; left: 30%; transform: translateX(-50%); z-index: 9999;
            background: rgba(255,255,255,0.9); padding: 10px 20px; border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2); font-family: Arial, sans-serif;">
    <h3 style="margin: 0; color: #1d3557;">{municipality} – Railway Network via OSM</h3>
    <p style="margin: 5px 0 0 0; font-size: 12px; color: #666;">Toggle layers using the control on the right</p>
</div>
'''
m.get_root().html.add_child(folium.Element(title_html))

st_folium(m, height=1500, use_container_width=True)