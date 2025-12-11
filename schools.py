import pandas as pd
import geopandas as gpd
import folium
import streamlit as st
from folium import FeatureGroup, CircleMarker, PolyLine
from streamlit_folium import st_folium

from src.utils import normalize, find_municipality_match, load_poly, load_schools, extract_name


st.set_page_config(
    page_title="Schools",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.header("Schools")

schools = load_schools()
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
schools_plot = schools.sjoin(poly_plot, how='inner', predicate='intersects')

# Check if municipality was found
if poly_plot.empty:
    # Try to find similar municipality names
    available = poly['Municipality'].unique()
    print(f"ERROR: Municipality '{municipality}' not found!")
    print(f"\nAvailable municipalities containing 'Veliko':")
    matches = [m for m in available if 'Veliko' in str(m)]
    if matches:
        for m in matches:
            print(f"  - {m}")
    else:
        print(f"\nFirst 10 available municipalities:")
        for m in list(available)[:10]:
            print(f"  - {m}")
    raise ValueError(f"Municipality '{municipality}' not found in the data. Please check the spelling.")

schools_plot = schools.sjoin(poly_plot, how='inner', predicate='intersects')

# Convert to WGS84 (lat/lon) for Folium
poly_wgs84 = poly_plot.to_crs("EPSG:4326")
schools_wgs84 = schools_plot.to_crs("EPSG:4326") if not schools_plot.empty else schools_plot

# Calculate map center from bounding box
if poly_wgs84.empty:
    raise ValueError("Cannot create map: polygon data is empty after filtering.")
    
bounds = poly_wgs84.total_bounds  # [minx, miny, maxx, maxy]
center_lat = (bounds[1] + bounds[3]) / 2
center_lon = (bounds[0] + bounds[2]) / 2

# Validate that bounds are not NaN
if pd.isna(center_lat) or pd.isna(center_lon):
    raise ValueError(f"Invalid bounds calculated. Municipality '{municipality}' may not exist in the data.")

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

# --- Layer 2: Schools ---
schools_layer = FeatureGroup(name='Schools', show=True)
universities_layer = FeatureGroup(name='Universities', show=True)

if not schools_wgs84.empty:
    for idx, row in schools_wgs84.iterrows():
        # Extract name and type
        name = row['name'] if 'name' in schools_wgs84.columns and pd.notna(row['name']) else 'Unknown'
        school_type = row['type'] if 'type' in schools_wgs84.columns and pd.notna(row['type']) else 'Not specified'
        
        # Determine if it's a university or school
        is_university = 'university' in str(school_type).lower()
        
        # Set colors based on type
        if is_university:
            fill_color = '#9b59b6'  # Purple for universities
            border_color = '#6c3483'
            radius = 7
        else:
            fill_color = '#e63946'  # Red for schools
            border_color = '#1d3557'
            radius = 7
        
        # Create popup HTML with name (shown on click)
        lat = row.geometry.y
        lon = row.geometry.x
        popup_html = f"<b>{name}</b><br>{school_type.capitalize()}<br>📍 {lat:.5f}, {lon:.5f}"
        popup = folium.Popup(popup_html, max_width=250)
        
        marker = CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=radius,
            color=border_color,
            fill=True,
            fill_color=fill_color,
            fill_opacity=0.8,
            popup=popup,
            tooltip=school_type  # Show type on hover
        )
        
        # Add to appropriate layer
        if is_university:
            marker.add_to(universities_layer)
        else:
            marker.add_to(schools_layer)

schools_layer.add_to(m)
universities_layer.add_to(m)

# Add layer control (toggle layers on/off)
folium.LayerControl(collapsed=False).add_to(m)

# --- Custom Legend ---
legend_html = '''
<div style="position: fixed; top: 30px; left: 50px; z-index: 9999;
            background: rgba(255,255,255,0.95); padding: 12px 16px; border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.25); font-family: Arial, sans-serif; font-size: 12px;">
    <h4 style="margin: 0 0 10px 0; color: #333; border-bottom: 1px solid #ddd; padding-bottom: 6px;">Map Legend</h4>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 12px; height: 12px; background: #e63946; border: 2px solid #1d3557; border-radius: 50%; margin-right: 8px; margin-left: 9px;"></span>School
    </div>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 14px; height: 14px; background: #9b59b6; border: 2px solid #6c3483; border-radius: 50%; margin-right: 8px; margin-left: 8px;"></span>University
    </div>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 30px; height: 3px; background: #333333; margin-right: 8px;"></span>District Boundary
    </div>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Add title
title_html = f'''
<div style="position: fixed; top: 10px; left: 70%; transform: translateX(-50%); z-index: 9999;
            background: rgba(255,255,255,0.9); padding: 10px 20px; border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2); font-family: Arial, sans-serif;">
    <h3 style="margin: 0; color: #1d3557;">{municipality} – Schools & Universities</h3>
    <p style="margin: 5px 0 0 0; font-size: 12px; color: #666;">Toggle layers using the control on the right</p>
</div>
'''
m.get_root().html.add_child(folium.Element(title_html))

st_folium(m, height=1500, use_container_width=True)