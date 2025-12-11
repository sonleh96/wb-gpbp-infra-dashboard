# GPBP Infrastructure Dashboard

A Streamlit-based geospatial dashboard for visualizing infrastructure sub-components for the **Local Development Tracker (LDT)**, part of the **Geospatial Planning and Budgeting Platform (GPBP)** in Serbia.

## 🎯 Purpose

This dashboard enables stakeholders to **validate infrastructure measures** by visually verifying whether the data accurately reflects ground-truth conditions in Serbian municipalities. It provides interactive exploration of:

- 🚗 **Road Infrastructure** — Road network by classification (trunk, primary, secondary, tertiary, local)
- 🚂 **Rail Infrastructure** — Railway lines, stations, bridges, and tunnels
- 🏫 **Schools & Universities** — Educational facility mapping
- 🏥 **Healthcare Facilities** — Hospitals and clinics distribution

## 📊 Data Source

- **OpenStreetMap (OSM) for Serbia**
- Last updated: **January 1, 2025**

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/wb-gpbp-infra-dashboard.git
cd wb-gpbp-infra-dashboard
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Secrets

This application requires Google Cloud Storage credentials to access the infrastructure data.

**Create the `.streamlit` folder and secrets file:**

```bash
mkdir -p .streamlit
touch .streamlit/secrets.toml
```

**⚠️ Important:** Contact **sonle.h96@gmail.com** to obtain the `secrets.toml` file with the required GCS credentials.

The `secrets.toml` file should have the following structure:

```toml
[gcs]
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

> **Note:** Never commit `secrets.toml` to version control. It should already be in `.gitignore`.

### 5. Run the Application Locally

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`.

---

## 📁 Project Structure

```
wb-gpbp-infra-dashboard/
├── app.py              # Main application entry point
├── home.py             # Home page with dashboard overview
├── roads.py            # Road infrastructure visualization
├── rails.py            # Rail infrastructure visualization
├── schools.py          # Schools & universities visualization
├── hospitals.py        # Healthcare facilities visualization
├── src/
│   ├── utils.py        # Utility functions and data loaders
│   └── gcs.py          # Google Cloud Storage helpers
├── data/               # Local data files (if any)
├── .streamlit/
│   └── secrets.toml    # GCS credentials (not in repo)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## ☁️ Deployment to Streamlit Cloud

### 1. Push to GitHub

Ensure your repository is pushed to GitHub (without the `secrets.toml` file):

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Click **"New app"**
3. Connect your GitHub repository
4. Set the following:
   - **Repository:** `your-org/wb-gpbp-infra-dashboard`
   - **Branch:** `main`
   - **Main file path:** `app.py`

### 3. Configure Secrets in Streamlit Cloud

1. In your app's settings, go to **"Secrets"**
2. Paste the contents of your `secrets.toml` file
3. Click **"Save"**

The app will automatically redeploy with the new secrets.

---

## 🔧 Configuration Options

### Changing the Default Municipality

The dashboard defaults to **Veliko Gradište**. To change this, modify the session state initialization in any page file:

```python
if 'highlight_municipality' not in st.session_state:
    st.session_state.highlight_municipality = "Your Municipality Name"
if 'valid_municipality' not in st.session_state:
    st.session_state.valid_municipality = "Your Municipality Name"
```

### Adjusting Map Height

To change the map display height, modify the `st_folium` call in any visualization page:

```python
st_folium(m, height=800, use_container_width=True, returned_objects=[])
```

---

## 🐛 Troubleshooting

### Map keeps reloading on interaction

Ensure `returned_objects=[]` is set in the `st_folium` call:

```python
st_folium(m, height=1500, use_container_width=True, returned_objects=[])
```

### GCS Authentication Errors

- Verify that `secrets.toml` is correctly placed in `.streamlit/` folder
- Check that the service account has read access to the GCS bucket
- Ensure the `private_key` in secrets has proper newline characters (`\n`)

### Slow Loading Times

The data is cached using `@st.cache_data` decorator. First load may be slow, but subsequent loads should be instant within the same session.

---

## 📬 Contact & Feedback

For questions, access to credentials, or to report data discrepancies:

- **Son Le:** sonle.h96@gmail.com
- **Klaus Kaiser:** kkaiser@worldbank.org

---

## 📄 License

This project is developed by the World Bank for the GPBP initiative.

Data source: © OpenStreetMap contributors
