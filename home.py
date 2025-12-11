import streamlit as st

st.header("Welcome to the GPBP Infrastructure Dashboard")

st.markdown("""
This dashboard provides **geospatial visualization of infrastructure sub-components** for the **Local Development Tracker (LDT)**, part of the
**Geospatial Planning and Budgeting Platform (GPBP)** in Serbia.

The primary purpose is to **validate infrastructure measures** by allowing stakeholders to visually 
verify whether the data accurately reflects ground-truth conditions in their municipalities.
""")

# --- Purpose Section ---
st.subheader("🎯 Purpose")

st.markdown("""
We want to present these results to local stakeholders (starting with **Veliko Gradište**) as a way 
of checking if our infrastructure measures are anywhere near reality. This tool enables:

- **Visual validation** of infrastructure data using local knowledge
- **Interactive exploration** of infrastructure assets by municipality
- **Breakdown** of different infrastructure layers (roads, rails, schools, health facilities)
""")

st.divider()
# --- Data Source Section ---
st.subheader("📊 Data Source")

st.info("""
**OpenStreetMap (OSM) for Serbia**  
Last updated: **January 1, 2025**

OpenStreetMap is a collaborative, open-source mapping project that provides freely available 
geographic data. The data used in this dashboard has been processed and filtered to extract 
infrastructure-relevant features for Serbian municipalities.
""")

st.divider()
# --- Infrastructure Components Section ---
st.subheader("🗺️ Infrastructure Components")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 🚗 Road Infrastructure
    Overview of the road network per GPBP LDT, including:
    - **Trunk roads** – Major national highways
    - **Primary roads** – Main arterial roads
    - **Secondary roads** – Regional connectors
    - **Tertiary roads** – Local connectors
    - **Local roads** – Residential, unclassified, and service roads
    - **Bridges & Tunnels** – Special infrastructure segments
    
    *Useful for assessing connectivity and local road network coverage.*
    """)

with col2:
    st.markdown("""
    #### 🚂 Rail Infrastructure
    Railway network visualization including:
    - **Railway lines** – Track segments with bridge/tunnel indicators
    - **Train stations** – Passenger rail stations
    
    *Helpful for understanding rail connectivity within municipalities.*
    """)

col3, col4 = st.columns(2)
with col3:
    st.markdown("""
    #### 🏫 Schools
    Educational facility mapping:
    - **Schools** – Primary and secondary educational institutions
    - **Universities** – Higher education institutions
    
    *Displays count and location of educational facilities per municipality.*
    """)
    
with col4:
    st.markdown("""
    #### 🏥 Healthcare Facilities
    Health infrastructure mapping:
    - **Hospitals** – Major healthcare facilities
    - **Clinics** – Smaller healthcare centers
    
    *Shows distribution and count of healthcare access points.*
    """)

st.divider()
# --- How to Use Section ---
st.subheader("🔍 How to Use This Dashboard")

st.markdown("""
1. **Select a municipality** using the sidebar selector (supports partial and accent-free search)
2. **Navigate** between infrastructure layers using the sidebar menu
3. **Interact with the map**:
   - Toggle layers on/off using the layer control
   - Hover over features to see quick info
   - Click on features for detailed information (name, type, coordinates)
4. **Validate** whether the displayed infrastructure matches your local knowledge
""")

# --- Default Municipality ---
st.subheader("📍 Default View: Veliko Gradište")

st.markdown("""
The dashboard defaults to **Veliko Gradište** as the initial municipality for demonstration 
and validation purposes. You can switch to any other Serbian municipality using the sidebar selector.
""")

st.divider()
# --- Feedback Section ---
st.subheader("💬 Feedback")

st.markdown("""
If you notice discrepancies between the displayed data and actual infrastructure on the ground, 
please document:
- **What is missing** (e.g., roads, schools, or facilities not shown)
- **What is incorrect** (e.g., misclassified roads, wrong locations)
- **What is outdated** (e.g., recently built infrastructure not yet in OSM)

This feedback is essential for improving the accuracy of our infrastructure assessments.

Please send your feedback to kkaiser@worldbank.org or sonle.h96@gmail.com.
""")