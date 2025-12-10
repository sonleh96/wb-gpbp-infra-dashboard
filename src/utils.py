import unicodedata
import difflib
from typing import Dict, List

from google.oauth2 import service_account
from google.cloud import storage
import streamlit as st

from src.gcs import read_geojson_from_gcs


# --- Initialization ---
@st.cache_resource
def init_gcs_client():
    """Initialize Google Cloud Storage client using credentials from Streamlit secrets."""
    creds_dict = {
        "type": "service_account",
        "project_id": st.secrets["gcs"]["project_id"],
        "private_key_id": st.secrets["gcs"]["private_key_id"],
        "private_key": st.secrets["gcs"]["private_key"], 
        "client_email": st.secrets["gcs"]["client_email"],
        "client_id": st.secrets["gcs"]["client_id"],
        "auth_uri": st.secrets["gcs"]["auth_uri"],
        "token_uri": st.secrets["gcs"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["gcs"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["gcs"]["client_x509_cert_url"],
        "universe_domain": "googleapis.com"
    }
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    return storage.Client(credentials=credentials)

storage_client = init_gcs_client()

@st.cache_data
def load_poly():
    """Load municipality polygons (cached)."""
    return read_geojson_from_gcs(storage_client, "wb-gpbp-infra-dashboard", "shapefiles/muni_poly_final.geojson") 


@st.cache_data
def load_rails():
    """Load railway lines (cached)."""
    return read_geojson_from_gcs(storage_client, "wb-gpbp-infra-dashboard", "shapefiles/rails_final.geojson")


@st.cache_data
def load_stations():
    """Load train stations (cached)."""
    return read_geojson_from_gcs(storage_client, "wb-gpbp-infra-dashboard", "shapefiles/stations_final.geojson")


@st.cache_data
def load_roads():
    """Load roads (cached)."""
    return read_geojson_from_gcs(storage_client, "wb-gpbp-infra-dashboard", "shapefiles/roads_final.geojson")

def normalize(text):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', str(text))
        if not unicodedata.combining(c)
    ).lower().strip()
    

def find_municipality_match(input_text: str, name_lookup: Dict[str, str]) -> List[str]:
    """
    Find municipality matches using fuzzy matching.
    
    Args:
        input_text: User input text
        name_lookup: Dictionary mapping normalized names to actual names
        
    Returns:
        List of matched municipality names
    """
    norm_input = normalize(input_text)
    
    # 1️⃣ Check for exact match first
    if norm_input in name_lookup:
        return [name_lookup[norm_input]]
    
    # 2️⃣ Find substring matches
    matches = [v for k, v in name_lookup.items() if norm_input in k]
    
    # 3️⃣ If no substring matches, find close fuzzy matches
    if not matches:
        all_norms = list(name_lookup.keys())
        close_keys = difflib.get_close_matches(norm_input, all_norms, n=3, cutoff=0.6)
        matches = [name_lookup[k] for k in close_keys]
    
    return matches