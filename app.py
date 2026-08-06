# run with streamlit run app.py
import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import time
import random
import re
import base64
import html
from pathlib import Path
from urllib.parse import unquote, urlparse
from shapely import wkt
from shapely.geometry import Point
import tab5_blog_replacement

st.set_page_config(
    page_title="Illegal Sand Mining in India",
    page_icon="🏜️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@300;400;600&display=swap');

    html, body, [class*="css"] { font-family: 'Source Sans 3', sans-serif; }
    .stApp { background-color: #f9f5ef; }

    [data-testid="stSidebar"] { background-color: #1c1a17; color: #e8dcc8; }
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span { color: #c9b99a !important; font-family: 'Source Sans 3', sans-serif; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2 {
        color: #e8a838 !important;
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        border-bottom: 1px solid #3a3530;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        background-color: #1c1a17;
        border-radius: 8px 8px 0 0;
        padding: 4px 4px 0 4px;
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        color: #9a8c78;
        border-radius: 6px 6px 0 0;
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.9rem;
        letter-spacing: 0.04em;
        font-weight: 600;
        padding: 8px 20px;
        border: none;
    }
    .stTabs [aria-selected="true"] { background-color: #e8a838 !important; color: #1c1a17 !important; }
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #f9f5ef;
        border: 1px solid #e0d5c4;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 1.5rem;
    }

    h1 {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.4rem !important;
        font-weight: 900 !important;
        color: #1c1a17 !important;
        letter-spacing: -0.01em;
        line-height: 1.1;
    }
    h2 { font-family: 'Playfair Display', serif !important; color: #2e2b26 !important; font-size: 1.6rem !important; }
    h3 {
        font-family: 'Source Sans 3', sans-serif !important;
        color: #5a4e3c !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    p, li { color: #3a3530; line-height: 1.75; }

    [data-testid="stMetric"] {
        background-color: #fff8ee;
        border: 1px solid #e0d5c4;
        border-left: 4px solid #e8a838;
        border-radius: 6px;
        padding: 1rem 1.25rem;
    }
    [data-testid="stMetricLabel"] { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: #7a6e5e !important; }
    [data-testid="stMetricValue"] { font-family: 'Playfair Display', serif; font-size: 2rem !important; color: #1c1a17 !important; }

    hr { border-color: #e0d5c4; }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #f0ebe0; }
    ::-webkit-scrollbar-thumb { background: #c9b99a; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# Original quotes
QUOTES = [
    "Sand is the second most exploited resource in the world, after water.",
    "If you remove sand from the river, you are digging your own grave. — Dinesh Kumar Mishra",
    "Unchecked sand extraction causes irreversible damage to river ecosystems. — Bidyut Mohanty",
    "It is a big challenge to stop illegal sand mining, because money drives everything. — S. Chandrasekhar",
    "We never know the worth of water until the well is dry. — Thomas Fuller",
    "Rivers are the soul of our civilization, and sand is their body.",
    "Over the years, India's rivers have been badly affected by unrestricted sand mining. — National Green Tribunal",
    "Mining jumped 14.7× after the PMAY-U housing scheme launched in 2015.",
]

def show_loading_page():
    st.markdown("<h1 style='text-align:center; margin-top:3rem;'> 🏜️Illegal Sand Mining in India</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#7a6e5e; font-size:1.1rem;'>Loading data & preparing your dashboard…</p>", unsafe_allow_html=True)
    quote_placeholder = st.empty()
    progress_bar = st.progress(0)
    for i in range(101):
        if i % 12 == 0:
            quote = random.choice(QUOTES)
            quote_placeholder.markdown(
                f"<blockquote style='border-left:4px solid #e8a838; padding:0.5rem 1rem; "
                f"color:#5a4e3c; font-style:italic; background:#fff8ee; border-radius:0 6px 6px 0;'>"
                f"{quote}</blockquote>",
                unsafe_allow_html=True
            )
        progress_bar.progress(i)
        time.sleep(0.04)
    st.success("✅ Data loaded successfully.")


# Geometry parsing — handles WKT, raw "lat,lon", and GeoJSON strings
def parse_geom_to_latlon(geom_val):
    """
    Try every known format for the geom column and return (lat, lon) or (nan, nan).
    Handles:
      - WKT:          POINT (lon lat)  /  POINT(lon lat)
      - raw pair:     "lat,lon"  or  "lon,lat"  (heuristic: lat is between -90..90 & lon -180..180)
      - GeoJSON str:  {"type":"Point","coordinates":[lon,lat]}
    """
    if pd.isna(geom_val) or str(geom_val).strip() == '':
        return np.nan, np.nan

    s = str(geom_val).strip()

    # ── WKT POINT ────────────────────────────────────────────────────
    wkt_match = re.match(r'POINT\s*\(\s*(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s*\)', s, re.IGNORECASE)
    if wkt_match:
        lon, lat = float(wkt_match.group(1)), float(wkt_match.group(2))
        return lat, lon

    # ── Two bare numbers (lat,lon or lon,lat) ────────────────────────
    pair_match = re.match(r'^\s*(-?\d+\.?\d*)\s*[,\s]\s*(-?\d+\.?\d*)\s*$', s)
    if pair_match:
        a, b = float(pair_match.group(1)), float(pair_match.group(2))
        # India bounding box heuristic: lat 6–36, lon 68–98
        if 6 <= a <= 36 and 68 <= b <= 98:
            return a, b
        if 6 <= b <= 36 and 68 <= a <= 98:
            return b, a
        return a, b   # best guess

    # ── GeoJSON-like string ───────────────────────────────────────────
    coord_match = re.search(r'"coordinates"\s*:\s*\[\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)', s)
    if coord_match:
        lon, lat = float(coord_match.group(1)), float(coord_match.group(2))
        return lat, lon

    # ── Try shapely wkt as last resort ───────────────────────────────
    try:
        geom = wkt.loads(s)
        return geom.y, geom.x
    except Exception:
        pass

    return np.nan, np.nan


# Data loading
@st.cache_data
def load_data():
    mining_df = pd.read_csv("data/final_unified_geo_data_rows.csv")

    # Parse geometry into lat/lon regardless of source format
    if 'geom' in mining_df.columns:
        latlon = mining_df['geom'].apply(parse_geom_to_latlon)
        mining_df['latitude']  = latlon.apply(lambda x: x[0])
        mining_df['longitude'] = latlon.apply(lambda x: x[1])
    elif 'latitude' in mining_df.columns and 'longitude' in mining_df.columns:
        mining_df['latitude']  = pd.to_numeric(mining_df['latitude'],  errors='coerce')
        mining_df['longitude'] = pd.to_numeric(mining_df['longitude'], errors='coerce')
    else:
        mining_df['latitude']  = np.nan
        mining_df['longitude'] = np.nan

    mining_df = mining_df.dropna(subset=['latitude', 'longitude'])

    india_gdf = gpd.read_file("india_district.geojson")

    court_df      = pd.read_csv("data/indiasandwatch/court_docs.csv",  header=1)
    news_df       = pd.read_csv("data/indiasandwatch/news_reports.csv", header=1)
    mining_obs_df = pd.read_csv("data/indiasandwatch/mining_obs.csv",   header=1)

    def parse_location(loc):
        if pd.isna(loc):
            return pd.Series([np.nan, np.nan])
        match = re.search(r"(-?\d+\.\d+),\s*(-?\d+\.\d+)", str(loc))
        if match:
            return pd.Series([float(match.group(1)), float(match.group(2))])
        return pd.Series([np.nan, np.nan])

    mining_obs_df[['latitude', 'longitude']] = mining_obs_df['Location'].apply(parse_location)
    mining_obs_df = mining_obs_df.dropna(subset=['latitude', 'longitude'])

    return mining_df, india_gdf, court_df, news_df, mining_obs_df


URL_PATTERN = re.compile(r'https?://[^\s"\'<>]+')
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif'}
LOCAL_MEDIA_DIR = Path('rough_manya/mining_pictures')


def extract_urls(value):
    if value is None:
        return []

    if isinstance(value, np.ndarray):
        value = value.tolist()

    if isinstance(value, (list, tuple, set)):
        values = [str(v) for v in value if v is not None and not pd.isna(v)]
    else:
        if pd.isna(value):
            return []
        values = [str(value)]

    urls = []
    for text in values:
        urls.extend(URL_PATTERN.findall(text))
    return [u.strip() for u in urls if u.strip()]


def render_media_html(value):
    urls = extract_urls(value)
    if not urls:
        return ''

    html_parts = []
    preview_added = False
    for url in urls:
        try:
            parsed = urlparse(url)
            filename = Path(unquote(parsed.path)).name
        except Exception:
            filename = Path(url).name

        local_file = LOCAL_MEDIA_DIR / filename
        ext = local_file.suffix.lower() if local_file.exists() else Path(filename).suffix.lower()
        is_image = ext in IMAGE_EXTS

        if local_file.exists() and local_file.is_file() and is_image:
            if not preview_added:
                try:
                    image_bytes = local_file.read_bytes()
                    mime_type = 'image/jpeg' if ext != '.png' else 'image/png'
                    html_parts.append(
                        f"<a href='{url}' target='_blank'>"
                        f"<img src='data:{mime_type};base64,{base64.b64encode(image_bytes).decode()}' "
                        "style='max-width:260px; max-height:180px; display:block; margin-top:8px; border-radius:4px;'/>"
                        "</a>"
                    )
                    preview_added = True
                except Exception:
                    html_parts.append(f"<div><a href='{url}' target='_blank'>Photo: {filename}</a></div>")
            else:
                html_parts.append(f"<div><a href='{url}' target='_blank'>Photo: {filename}</a></div>")
        elif is_image:
            html_parts.append(
                f"<a href='{url}' target='_blank'>"
                f"<img src='{url}' style='max-width:260px; max-height:180px; display:block; margin-top:8px; border-radius:4px;'/>"
                "</a>"
            )
            preview_added = True
        else:
            html_parts.append(f"<div style='margin-top:6px;'><a href='{url}' target='_blank'>Link: {html.escape(filename)}</a></div>")

    return ''.join(html_parts)


@st.cache_data
def load_report_text():
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        return "PyPDF2 is not installed. Install it to view report text."

    reader = PdfReader('report.pdf')
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ''
        pages.append(f"--- PAGE {i+1} ---\n{text}")
    return "\n\n".join(pages)


# Incident count per district — spatial join with name-match fallback
# +
def build_state_counts(mining_df, india_gdf):

    india_gdf = india_gdf.copy()

    # Find state column in shapefile
    state_field = next((c for c in ['state', 'STATE', 'NAME_1'] if c in india_gdf.columns), None)

    if state_field is None or 'state' not in mining_df.columns:
        india_gdf['incident_count'] = 0
        return india_gdf

    # Normalize names
    mining_states = (
        mining_df['state']
        .dropna()
        .str.strip()
        .str.lower()
    )

    counts = mining_states.value_counts()

    india_gdf['incident_count'] = (
        india_gdf[state_field]
        .str.strip()
        .str.lower()
        .map(counts)
        .fillna(0)
        .astype(int)
    )

    return india_gdf

def get_state_gdf(india_gdf):

    state_field = next((c for c in ['state', 'STATE', 'NAME_1'] if c in india_gdf.columns), None)

    if state_field is None:
        return india_gdf

    # Dissolve into state-level polygons
    state_gdf = india_gdf.dissolve(by=state_field, as_index=False)

    return state_gdf, state_field

def build_state_color_counts(mining_df, india_gdf):

    india_gdf = india_gdf.copy()

    state_field = next((c for c in ['state', 'STATE', 'NAME_1'] if c in india_gdf.columns), None)

    if state_field is None or 'state' not in mining_df.columns:
        india_gdf['state_color_count'] = 0
        return india_gdf

    # count incidents per state
    state_counts = (
        mining_df['state']
        .dropna()
        .str.strip()
        .str.lower()
        .value_counts()
    )

    # assign same state count to all districts in that state
    india_gdf['state_color_count'] = (
        india_gdf[state_field]
        .str.strip()
        .str.lower()
        .map(state_counts)
        .fillna(0)
        .astype(int)
    )

    return india_gdf
def build_incident_counts_all(mining_df, news_df, court_df, mining_obs_df, india_gdf):
    india_gdf = india_gdf.copy()

    dist_field = next((c for c in ['district', 'DISTRICT', 'dtname', 'NAME_2'] if c in india_gdf.columns), None)

    # master dictionary: district → count
    district_counts = {}

    def add_counts(series):
        for k, v in series.items():
            district_counts[k] = district_counts.get(k, 0) + int(v)

    # ─────────────────────────────
    # 1. mining_df (spatial → district)
    # ─────────────────────────────
    try:
        pts = gpd.GeoDataFrame(
            mining_df,
            geometry=gpd.points_from_xy(mining_df['longitude'], mining_df['latitude']),
            crs='EPSG:4326'
        )

        gdf = india_gdf.to_crs('EPSG:4326')

        joined = gpd.sjoin(pts, gdf[[dist_field, 'geometry']], how='left', predicate='within')

        mining_counts = (
            joined[dist_field]
            .dropna()
            .str.strip().str.lower()
            .value_counts()
        )

        add_counts(mining_counts)

    except Exception:
        pass

    # ─────────────────────────────
    # 2. news_df
    # ─────────────────────────────
    if 'District' in news_df.columns:
        news_counts = (
            news_df['District']
            .dropna()
            .str.strip().str.lower()
            .value_counts()
        )
        add_counts(news_counts)

    # ─────────────────────────────
    # 3. court_df
    # ─────────────────────────────
    if 'District' in court_df.columns:
        court_counts = (
            court_df['District']
            .dropna()
            .str.strip().str.lower()
            .value_counts()
        )
        add_counts(court_counts)

    # ─────────────────────────────
    # 4. mining_obs_df (spatial)
    # ─────────────────────────────
    try:
        pts_obs = gpd.GeoDataFrame(
            mining_obs_df,
            geometry=gpd.points_from_xy(mining_obs_df['longitude'], mining_obs_df['latitude']),
            crs='EPSG:4326'
        )

        joined_obs = gpd.sjoin(pts_obs, gdf[[dist_field, 'geometry']], how='left', predicate='within')

        obs_counts = (
            joined_obs[dist_field]
            .dropna()
            .str.strip().str.lower()
            .value_counts()
        )

        add_counts(obs_counts)

    except Exception:
        pass

    # ─────────────────────────────
    # FINAL MAP BACK TO GEOJSON
    # ─────────────────────────────
    india_gdf['incident_count'] = (
        india_gdf[dist_field]
        .str.strip().str.lower()
        .map(district_counts)
        .fillna(0)
        .astype(int)
    )

    return india_gdf


def normalize_text(value):
    if pd.isna(value):
        return None
    text = str(value).strip()
    return text.lower() if text else None


def build_centroid_maps(india_gdf):
    dist_field = next((c for c in ['district', 'DISTRICT', 'dtname', 'NAME_2'] if c in india_gdf.columns), None)
    state_field = next((c for c in ['state', 'STATE', 'NAME_1'] if c in india_gdf.columns), None)

    district_centroids = {}
    if dist_field is not None:
        for _, row in india_gdf.dropna(subset=[dist_field]).iterrows():
            name = normalize_text(row[dist_field])
            if name and hasattr(row.geometry, 'centroid') and not row.geometry.is_empty:
                centroid = row.geometry.centroid
                district_centroids[name] = (centroid.y, centroid.x)

    state_centroids = {}
    if state_field is not None:
        try:
            state_gdf = india_gdf[[state_field, 'geometry']].dissolve(by=state_field)
            for state_name, row in state_gdf.iterrows():
                name = normalize_text(state_name)
                if name and hasattr(row.geometry, 'centroid') and not row.geometry.is_empty:
                    centroid = row.geometry.centroid
                    state_centroids[name] = (centroid.y, centroid.x)
        except Exception:
            pass

    return district_centroids, state_centroids


def resolve_feature_coordinates(row, district_centroids, state_centroids):
    lat = row.get('latitude') if 'latitude' in row else None
    lon = row.get('longitude') if 'longitude' in row else None
    if pd.notna(lat) and pd.notna(lon):
        try:
            return float(lat), float(lon)
        except Exception:
            pass

    district = normalize_text(row.get('District') or row.get('district') or row.get('Sub district / Tehsil'))
    if district and district in district_centroids:
        return district_centroids[district]

    state = normalize_text(row.get('State') or row.get('States'))
    if state and state in state_centroids:
        return state_centroids[state]

    return None, None


def aggregate_records_to_centroids(df, district_col, state_col, district_centroids, state_centroids, url_cols=None):
    if df is None or len(df) == 0:
        return []

    group_cols = [c for c in [district_col, state_col] if c in df.columns]
    if not group_cols:
        return []

    grouped = df.assign(**{
        c: df[c].astype(str).str.strip()
        for c in group_cols
    }).groupby(group_cols, dropna=False)

    markers = []
    for key, group in grouped:
        row_values = dict(zip(group_cols, key)) if isinstance(key, tuple) else {group_cols[0]: key}
        district = normalize_text(row_values.get(district_col)) if district_col in row_values else None
        state = normalize_text(row_values.get(state_col)) if state_col in row_values else None

        latlon = None
        if district and district in district_centroids:
            latlon = district_centroids[district]
        elif state and state in state_centroids:
            latlon = state_centroids[state]

        if not latlon:
            continue

        urls = []
        if url_cols:
            for col in url_cols:
                if col in group.columns:
                    for text in group[col].dropna().astype(str).tolist():
                        urls.extend(extract_urls(text))
            urls = sorted(set(urls))
            # Filter out invalid URLs containing 'undefined'
            urls = [u for u in urls if 'undefined' not in u]

        markers.append({
            'lat': latlon[0],
            'lon': latlon[1],
            'count': int(len(group)),
            'district': row_values.get(district_col, ''),
            'state': row_values.get(state_col, ''),
            'urls': urls,
        })

    return markers

# +
# Map builder
# +
def create_map(mining_df, news_df, court_df, mining_obs_df, india_gdf):

    m = folium.Map(location=[22.5, 78.9], zoom_start=5,
                   tiles='CartoDB positron', attr='© CartoDB')
    m.fit_bounds([[6.5, 68.1], [35.5, 97.4]])

    india_gdf = build_incident_counts_all(
    mining_df, news_df, court_df, mining_obs_df, india_gdf)
    india_gdf = build_state_color_counts(mining_df, india_gdf)

    district_centroids, state_centroids = build_centroid_maps(india_gdf)

    dist_field  = next((c for c in ['district', 'DISTRICT', 'dtname', 'NAME_2'] if c in india_gdf.columns), None)
    state_field = next((c for c in ['state', 'STATE', 'NAME_1'] if c in india_gdf.columns), None)

    # Give every row a stable string key for Choropleth binding
    india_gdf = india_gdf.reset_index(drop=True)
    india_gdf['_id'] = india_gdf.index.astype(str)

    # ── Choropleth layer (handles data binding reliably) ─────────────
    folium.Choropleth(
    geo_data=india_gdf,
    name='District Shading',
    data=india_gdf,
    columns=[india_gdf.index, 'incident_count'],
    key_on='feature.id',   # 👈 important
    fill_color='YlOrRd',
    fill_opacity=0.65,
    line_opacity=0.3,
    nan_fill_color='#f5efe3',
    legend_name='Mining Incidents per District',
).add_to(m)

    # ── Invisible GeoJson overlay just for hover tooltips ─────────────
    tooltip_fields, tooltip_aliases = [], []
    if dist_field:
        tooltip_fields.append(dist_field);  tooltip_aliases.append('District:')
    if state_field:
        tooltip_fields.append(state_field); tooltip_aliases.append('State:')
    # tooltip_fields.append('incident_count'); tooltip_aliases.append('Incidents:')

    folium.GeoJson(
        india_gdf,
        name='District Tooltips',
        style_function=lambda _: {
            'fillColor': 'transparent', 'color': 'transparent',
            'weight': 0, 'fillOpacity': 0,
        },
        highlight_function=lambda _: {
            'fillColor': '#922b21', 'color': '#1c1a17',
            'weight': 2, 'fillOpacity': 0.25,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            localize=True, sticky=True, labels=True,
            style=(
                "background-color: #1c1a17; color: #e8dcc8; "
                "font-family: 'Source Sans 3', sans-serif; "
                "font-size: 13px; padding: 8px 12px; border-radius: 4px;"
            ),
        ),
    ).add_to(m)

    # Mining observation markers
    if mining_obs_df is not None and len(mining_obs_df) > 0:
        cluster_obs = MarkerCluster(name='Mining Observations').add_to(m)
        for _, row in mining_obs_df.iterrows():
            title = html.escape(str(row.get('Title', row.get('title', 'Mining Observation'))))
            desc  = str(row.get('Notes from the location', row.get('description', '')))
            desc_html = html.escape(desc).replace('\n', '<br>') if desc else ''
            media_html = render_media_html(row.get('Pictures'))
            if not media_html:
                media_html = render_media_html(row.get('PDF'))
            desc_block = f"<br><div style='margin-top:6px; color:#555; font-size:12px;'>{desc_html}</div>" if desc_html else ''
            popup_html = (
                f"<div style='font-family:sans-serif; min-width:220px;'>"
                f"<b style='color:#c98a1a;'>⚠ Mining Obs</b><br>"
                f"<span style='font-size:13px;'>{title}</span>"
                f"{desc_block}"
                f"{media_html}"
                f"</div>"
            )
            tooltip_text = str(title)[:60]
            if media_html:
                tooltip_text += ' 📷'
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_html, max_width=450),
                tooltip=tooltip_text,
                icon=folium.Icon(color='orange', icon='exclamation-sign', prefix='glyphicon'),
            ).add_to(cluster_obs)

    # Unified geo markers
    if len(mining_df) > 0:
        cluster_unified = MarkerCluster(name='Verified Incidents').add_to(m)
        for _, row in mining_df.iterrows():
            desc  = str(row.get('description', row.get('raw_location', 'N/A')))
            desc_html = html.escape(desc).replace('\n', '<br>')
            state = row.get('state', '')
            popup_html = (
                f"<div style='font-family:sans-serif; min-width:220px;'>"
                f"<b style='color:#c0392b;'>🔴 Mining Incident</b><br>"
                f"{'<small>📍 ' + html.escape(str(state)) + '</small><br>' if state else ''}"
                f"<div style='margin-top:6px; color:#555; font-size:12px;'>{desc_html}</div>"
                f"</div>"
            )
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_html, max_width=450),
                tooltip=str(row.get('district', row.get('state', 'Incident')))[:60],
                icon=folium.Icon(color='red', icon='map-marker', prefix='glyphicon'),
            ).add_to(cluster_unified)

    # News report group markers by location to avoid hundreds of overlapping centroid points
    if len(news_df) > 0:
        cluster_news = MarkerCluster(name='News Reports').add_to(m)
        news_markers = aggregate_records_to_centroids(
            news_df, 'District', 'States', district_centroids, state_centroids,
            url_cols=['PDF']
        )
        for marker in news_markers:
            title = f"News reports: {marker['count']}"
            media_html = render_media_html(marker.get('urls'))
            popup_html = (
                f"<div style='font-family:sans-serif; min-width:220px;'>"
                f"<b style='color:#2978b5;'>📰 News Report</b><br>"
                f"<small>{marker['count']} item(s) in {marker['district'] or marker['state']}</small><br>"
                f"{'<small>📍 ' + html.escape(str(marker['district'])) + '</small><br>' if marker['district'] else ''}"
                f"{'<small>' + html.escape(str(marker['state'])) + '</small><br>' if marker['state'] else ''}"
                f"{media_html}"
                f"</div>"
            )
            folium.Marker(
                location=[marker['lat'], marker['lon']],
                popup=folium.Popup(popup_html, max_width=450),
                tooltip=title,
                icon=folium.Icon(color='blue', icon='info-sign', prefix='glyphicon'),
            ).add_to(cluster_news)

    # Court report group markers by location to avoid hundreds of overlapping centroid points
    if len(court_df) > 0:
        cluster_court = MarkerCluster(name='Court Reports').add_to(m)
        court_markers = aggregate_records_to_centroids(
            court_df, 'District', 'State', district_centroids, state_centroids,
            url_cols=['PDF']
        )
        for marker in court_markers:
            title = f"Court reports: {marker['count']}"
            media_html = render_media_html(marker.get('urls'))
            popup_html = (
                f"<div style='font-family:sans-serif; min-width:220px;'>"
                f"<b style='color:#238636;'>⚖ Court Report</b><br>"
                f"<small>{marker['count']} item(s) in {marker['district'] or marker['state']}</small><br>"
                f"{'<small>📍 ' + html.escape(str(marker['district'])) + '</small><br>' if marker['district'] else ''}"
                f"{'<small>' + html.escape(str(marker['state'])) + '</small><br>' if marker['state'] else ''}"
                f"{media_html}"
                f"</div>"
            )
            folium.Marker(
                location=[marker['lat'], marker['lon']],
                popup=folium.Popup(popup_html, max_width=450),
                tooltip=title,
                icon=folium.Icon(color='green', icon='ok-sign', prefix='glyphicon'),
            ).add_to(cluster_court)

    folium.LayerControl().add_to(m)
    return m


# +
# Main
# +
def main():
    if 'loaded' not in st.session_state:
        show_loading_page()
        st.session_state.loaded = True
        st.rerun()

    mining_df, india_gdf, court_df, news_df, mining_obs_df = load_data()

    # ── Static sidebar ────────────────────────────────────────────────
    st.sidebar.markdown("## Map Legend")
    st.sidebar.markdown("""
<div style='color:#e8dcc8; font-size:0.88rem; line-height:1.8;'>

<div style='margin-bottom:14px;'>
<div style='font-size:0.72rem; letter-spacing:0.08em; text-transform:uppercase; color:#7a6e5e; margin-bottom:6px;'>District shading</div>
<div style='display:flex; align-items:center; gap:10px; margin:5px 0;'>
  <div style='width:14px;height:14px;border-radius:3px;background:#c0392b;opacity:0.7;flex-shrink:0;'></div>
  <span>High incident density</span>
</div>
<div style='display:flex; align-items:center; gap:10px; margin:5px 0;'>
  <div style='width:14px;height:14px;border-radius:3px;background:#c0392b;opacity:0.35;flex-shrink:0;'></div>
  <span>Moderate incidents</span>
</div>
<div style='display:flex; align-items:center; gap:10px; margin:5px 0;'>
  <div style='width:14px;height:14px;border-radius:3px;background:#e8a838;opacity:0.15;flex-shrink:0;'></div>
  <span>No recorded incidents</span>
</div>
</div>

<div style='margin-bottom:14px;'>
<div style='font-size:0.72rem; letter-spacing:0.08em; text-transform:uppercase; color:#7a6e5e; margin-bottom:6px;'>Markers</div>
<div style='display:flex; align-items:center; gap:10px; margin:5px 0;'>
  <span style='font-size:1rem;'>🔴</span><span>Verified mining incident</span>
</div>
<div style='display:flex; align-items:center; gap:10px; margin:5px 0;'>
  <span style='font-size:1rem;'>🟠</span><span>Field observation</span>
</div>
<div style='display:flex; align-items:center; gap:10px; margin:5px 0;'>
  <span style='font-size:1rem;'>🔵</span><span>News report</span>
</div>
<div style='display:flex; align-items:center; gap:10px; margin:5px 0;'>
  <span style='font-size:1rem;'>🟢</span><span>Court report</span>
</div>
</div>

</div>
""", unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Data on Map")
    st.sidebar.markdown("""
<div style='color:#c9b99a; font-size:0.88rem; line-height:2;'>

<div style='font-size:0.72rem; letter-spacing:0.08em; text-transform:uppercase; color:#7a6e5e; margin-bottom:2px;'>Boundaries</div>
India district polygons<br>
<span style='color:#7a6e5e; font-size:0.82rem;'>Hover any district to see its incident count</span>

<br>

<div style='font-size:0.72rem; letter-spacing:0.08em; text-transform:uppercase; color:#7a6e5e; margin-bottom:2px; margin-top:8px;'>Verified incidents</div>
2,212 geo-coded cases · 2001–2026<br>
<span style='color:#7a6e5e; font-size:0.82rem;'>Source: IndiaSandWatch unified dataset</span>

<br>

<div style='font-size:0.72rem; letter-spacing:0.08em; text-transform:uppercase; color:#7a6e5e; margin-bottom:2px; margin-top:8px;'>Field observations</div>
375 on-ground observation points<br>
<span style='color:#7a6e5e; font-size:0.82rem;'>Source: IndiaSandWatch mining_obs</span>

<br>

<div style='font-size:0.72rem; letter-spacing:0.08em; text-transform:uppercase; color:#7a6e5e; margin-bottom:2px; margin-top:8px;'>Coverage</div>
28+ states · 36 states/UTs total

</div>
""", unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<small style='color:#6a5f4f;'>Clusters expand on click · Layer control top-right of map</small>",
        unsafe_allow_html=True
    )

    # ── Tabs ──────────────────────────────────────────────────────────
    tab1, tab5, tab2, tab3, tab4 = st.tabs(["Illegal Sand Mining Map", "Blog", "Correlations", "Study on Sand Mining", "Research Narrative"])

    with tab1:
        st.markdown(
            "<h1>Illegal Sand Mining Interactive Map</h1>"
            "<p style='color:#7a6e5e; margin-top:-0.5rem; font-size:1.05rem;'>"
            "Hover over any district to see its recorded incident count. "
            "Click clusters to expand individual markers.</p>",
            unsafe_allow_html=True
        )

        c2, c3, c4 = st.columns(3)
        # c1.metric("Total Incidents", "2,212")
        c2.metric("States Affected", "28+")
        c3.metric("Top State", "Bihar")
        c4.metric("Post-PMAY Surge", "14.7×")

        st.markdown("<br>", unsafe_allow_html=True)

        m = create_map(mining_df, news_df, court_df, mining_obs_df, india_gdf)
        st_folium(m, width="100%", height=580, returned_objects=[])

    with tab2:
        st.markdown("<h1>Visualization Gallery</h1>", unsafe_allow_html=True)

        st.markdown("### Correlation Heatmap of Indicators")
        try:
            st.image("outputs/correlation_heatmap_indicators.png", width="stretch")
        except Exception:
            st.info("Image not found: outputs/correlation_heatmap_indicators.png")

        st.markdown("""
**What it shows:** Correlations between mining, construction, and socioeconomic indicators.

**How to read:** Red = positive correlation, blue = negative. Stronger colour = stronger relationship.

**Key finding:** Mining incidents correlate strongly with PMAY construction scale, but weakly with poverty or literacy rates, illegal mining is demand-driven, not desperation-driven.
        """)

        st.divider()

        gallery_items = [
            ("Mining Observations Heatmap",     "outputs/heatmap_mining_observations.png",
             "Density of mining observations across India.",
             "Darker areas = higher mining activity. Bihar and UP dominate.",
             "Mining hotspots are in economically vulnerable supply states."),
            ("Geographic Distribution by State", "outputs/geographic_distribution_bars.png",
             "Bar chart of mining incidents by state.",
             "Bar height = number of incidents. Bihar leads with 193.",
             "Mining concentrates in supply states, not demand/construction states."),
            ("Dilapidated Housing Choropleth",   "outputs/choropleth_housing_dilapidated.html",
             "Dilapidated housing percentage by state.",
             "Darker shading = higher share of poor housing stock.",
             "Poor housing states have more mining, but PMAY mediates the link."),
            ("Crime Intensity Heatmap",          "outputs/heatmap_crime_intensity.png",
             "Crime rates across Indian cities.",
             "Darker = higher crime intensity.",
             "Crime hotspots often overlap with mining areas."),
            ("Temporal Surge in Mining",         "sangam_ganga_figures/fig_temporal_surge.png",
             "Annual illegal mining incidents 2010–2025, split pre/post-PMAY.",
             "Blue = pre-2015 baseline, red = post-launch surge.",
             "Mining rose from 13/year pre-2015 to 191/year post-2015, a 14.7× increase."),
            ("Event Study: PMAY Impact",         "sangam_ganga_figures/fig_event_study.png",
             "DiD coefficients showing effect of high-PMAY states over time.",
             "Dots above zero post-2015 = significant mining increase after PMAY launch.",
             "Confirms causal impact of housing policy on illegal extraction."),
            ("Synthetic Control: Uttar Pradesh", "sangam_ganga_figures/fig_synthetic_control.png",
             "Actual UP mining vs. synthetic counterfactual.",
             "Gap post-2015 shows the causal PMAY effect on UP mining.",
             "UP mining is +158% above the counterfactual without PMAY."),
            ("Ganga Conductivity Time Series",   "sangam_ganga_figures/fig_ganga_sangam_timeseries.png",
             "Water quality sensors showing conductivity during dry seasons.",
             "Peaks in Nov–Feb coincide with peak mining and low water levels.",
             "Mining correlates with riverbed disturbance and water degradation."),
            ("Spatial Clusters: Construction vs Mining", "sangam_ganga_figures/fig_spatial_clusters.png",
             "Side-by-side: PMAY allocation vs mining incidents by state.",
             "Visual decoupling, mining and construction occur in different states.",
             "Supply and demand are spatially separated across state borders."),
        ]

        for title, path, desc, reading, insight in gallery_items:
            st.markdown(f"### {title}")
            try:
                if path.endswith('.html'):
                    st.components.v1.html(open(path).read(), height=420)
                else:
                    st.image(path, width="stretch")
            except Exception:
                st.info(f"📂 File not found: {path}")
            col_a, col_b, col_c = st.columns(3)
            col_a.markdown(f"**What it shows**\n\n{desc}")
            col_b.markdown(f"**How to read**\n\n{reading}")
            col_c.markdown(f"**Key finding**\n\n{insight}")
            st.divider()

    with tab3:
        st.markdown("<h1>Project Results & Findings</h1>", unsafe_allow_html=True)
        st.markdown("""
## Executive Summary

This study analysed illegal sand mining in India using spatial statistics, causal inference, and environmental monitoring.
The central finding: the 2015 PMAY-U housing scheme caused a **14.7× surge** in illegal mining, with extraction spatially
decoupled from construction demand, occurring primarily in economically vulnerable supply states.

---

## Key Findings

### 1. Causal Impact of Construction Policy
- **Difference-in-Differences:** High-PMAY states saw 158% more mining post-2015
- **Event Study:** Parallel trends hold pre-2015; mining diverges sharply after PMAY launch
- **Synthetic Control:** UP mining is +158% above its counterfactual without PMAY
- **Regression:** PMAY scale explains 58% of mining variance; socioeconomic factors are secondary

### 2. Spatial Patterns & Hotspots
- **Top states:** Bihar (193 incidents), Uttar Pradesh (48), West Bengal (48), Madhya Pradesh (43)
- **Spatial decoupling:** Bivariate Moran's I = 0.033 (p = 0.42), no co-clustering with construction
- **KDE analysis:** Hotspots concentrated in the Gangetic plain and central India
- **LISA:** Significant local spatial autocorrelation in mining clusters

### 3. Environmental Impacts
- Conductivity spikes at Ganga/Sangam sensors during dry seasons (Nov–Feb) correlate with peak mining
- Mining coincides with WQI deterioration and ecosystem stress
- Illegal extraction threatens aquifer recharge in riverbed sponges

### 4. Economic & Social Dimensions
- Crime hotspots spatially coincide with mining areas
- Poverty and literacy have weak direct effects; construction demand, not desperation, drives mining
- Urbanisation shows no significant independent effect

### 5. Methodological Approach
- **Spatial statistics:** Moran's I, LISA, GWR, KDE
- **Causal inference:** DiD, event studies, synthetic controls, IV regression
- **Machine learning:** Random Forest (PMAY most predictive feature)
- **Time series:** Seasonal decomposition, Granger causality

---

## Data Sources

| Dataset | Coverage | Scale |
|---|---|---|
| Mining incidents (IndiaSandWatch) | 2001–2026 | 2,212 verified cases |
| PMAY-U allocations | 2015–2024 | State / district |
| Economic indicators (Census 2011) | Literacy, BPL, urbanisation | State |
| Ganga/Sangam water sensors | 2019–2020 | Point locations |
| IPC crime statistics | 54 urban centres | City |
| Geographic coverage | 36 states/UTs | 375 mining obs. points |

---

## Policy Implications

**Immediate actions:**
1. Develop legal sand mining infrastructure in high-demand states to reduce illegal supply pressure
2. Focus enforcement on Bihar, UP, and MP, the primary sand mafia hotspots
3. Implement real-time river quality monitoring at active mining sites
4. Invest in economic alternatives for communities dependent on informal extraction

**Long-term reforms:**
1. Strengthen environmental clearances and monitoring for sand permits
2. Create a national sand supply coordination policy to address inter-state decoupling
3. Deploy satellite monitoring and AI for real-time illegal mining detection
4. Involve local communities in sustainable extraction governance

---

## Limitations & Future Research

- District-level analysis would reveal finer spatial patterns
- Pre-2015 mining data is sparse, a longer time series would sharpen causal estimates
- Sand mafia economics and enforcement failures warrant dedicated ethnographic research
- Experimental evaluation of alternative sand supply interventions is needed

---

*Research conducted using rigorous statistical methods across spatial analysis, causal inference, and environmental monitoring.*
        """)


    with tab4:
        st.markdown("<h1>Research Narrative & Evidence Bank</h1>", unsafe_allow_html=True)
        st.markdown(
            "<p style='color:#5a4e3c; font-size:1rem; margin-top:-0.5rem;'>"
            "This page stitches together the full story from our dataset, maps, causal checks, and environmental validation. "
            "Every output figure and spatial analysis piece is placed in context so the evidence is visible and readable." 
            "</p>",
            unsafe_allow_html=True
        )

        st.markdown("## What we studied")
        st.markdown("""
- 2,212 verified mining incidents from IndiaSandWatch
- 375 ground-observed field reports
- State and district housing allocations from PMAY-U
- Census-derived socioeconomic indicators
- IPC crime intensity and urban crime rates
- Ganga and Sangam water sensor time series
- State and district geography from India shapefiles
- `classification.ipynb` for model-based classification of mining exposure, signal validation, and systematic risk scoring
""")

        st.markdown("## How the evidence was built")
        st.markdown("""
We built this blog from a hybrid research architecture: structured mining and socioeconomic data were stored in a unified relational schema, while spatial boundaries were handled as GeoJSON through GeoPandas. A dedicated normalization pipeline aligned state and district spelling variants across government datasets, India Sand Watch records, and shapefiles so that every merge and spatial join could proceed reliably.

The study combines five analytical modules:
- Kernel density estimation (KDE) to reveal the two dominant extraction corridors along the Gangetic plains and the Central India plateau.
- Spatial statistics (Moran’s I, LISA hotspots) to test geographic clustering and identify cross-border mining belts.
- Regression and causal inference (OLS, spatial models, DiD, IV, synthetic control) to test whether PMAY-U construction demand amplifies illegal mining.
- Socioeconomic correlation analysis to quantify how poverty, housing quality, marginal employment, and police strength relate to mining intensity.
- NLP-based field classification and water-quality monitoring to validate the illegal mining signal at the point and in the river.
""")

        st.markdown("## Key techniques and findings")
        st.markdown("""
### Geospatial density and clustering
We used KDE on 373 geo-coded mining observations with a 0.08-degree bandwidth. The resulting intensity surface exposed two corridors:
1. The Gangetic Plains: a high-density ribbon along the Ganga and its tributaries in Bihar, eastern Uttar Pradesh, and West Bengal.
2. The Central India Plateau: a second corridor across Madhya Pradesh and Rajasthan, anchored by the Chambal and Narmada rivers.

A mining-to-monitoring ratio map further showed that northeastern districts have high incident density but low groundwater monitoring station coverage, suggesting likely under-detection.

Global Moran’s I on state-level mining counts was 0.121 with p=0.108, indicating only marginal positive clustering. That same result is important: it means mining is not purely random, but its spatial pattern is less rigid than a classic contagion process.

Local Indicators of Spatial Association (LISA) then identified concrete hotspots. High-High clusters emerged in Goa, Gujarat, Madhya Pradesh, and Rajasthan, forming a geographically contiguous corridor consistent with cross-border sand mafia operations. Low-High and High-Low outliers highlighted states like Chhattisgarh, Jharkhand, and Assam, reflecting local drivers distinct from the main belt.
""")

        st.markdown("""
### Spatial regression and water-quality validation
We began with an OLS baseline relating log-transformed mining intensity to crime rate, PM2.5, and PM10. The model explained only 15.8% of the variance, with PM10 the strongest environmental predictor. Lagrange Multiplier diagnostics did not find strong spatial dependence, so we also estimated Spatial Lag and Spatial Error models; neither improved materially over OLS.

The real insight came from Geographically Weighted Regression (GWR). By allowing coefficients to vary across space, GWR raised explained variance to 54.5% and revealed that groundwater contamination near mining sites is highly local. In Bihar, every monitoring station showed a negative local coefficient on distance to mining, confirming that proximity to extraction corresponds with elevated Total Dissolved Solids.

The river case study used 99,000 one-minute Ganga and Sangam sensor readings. Dry-season conductivity at Prayagraj averaged 478 µS/cm versus 276 µS/cm during monsoon, a 1.73× increase with Cohen’s d=1.78 and p<0.001. This matches the seasonal mining window when river levels fall and sand becomes accessible.
""")

        st.markdown("""
### Causal analysis of PMAY demand
The temporal incident series offers the clearest policy signal. Mining counts rose from an average of 13 incidents per year before 2015 to 191 per year after PMAY-U launched, a 14.7× jump. A Mann-Whitney test confirms that this change is statistically significant.

A Difference-in-Differences design then compares high-PMAY states against low-PMAY states, controlling for state and year fixed effects. The estimated treatment effect is +1.057 in log-mining units (p<0.001), which translates to roughly 188% more mining in high-PMAY states relative to their pre-2015 trend.

To address potential selection bias, we instrument PMAY scale with central government financial assistance. The first stage is strong (F=16.40, p<0.001), and the 2SLS estimate remains positive and large at +0.631, reinforcing the conclusion that construction demand is a real driver.

A synthetic control for Uttar Pradesh provides an additional counterfactual. The actual post-2015 trajectory exceeds the synthetic profile by +0.948 log-mining units, or about 158% excess mining. Together, these causal checks paint a consistent picture: PMAY-U construction demand amplified illegal sand extraction.
""")

        st.markdown("""
### Socioeconomic and enforcement signals
We also traced the social and governance contours of the problem.
- States with poorer housing quality have higher mining intensity. Among the top mining states, the housing quality index correlates at r=–0.75 with mining.
- Dilapidated housing rates correlate positively with mining at r=+0.51.
- Marginal worker share is the strongest socioeconomic predictor, with r=+0.612. This suggests that illegal mining is a labor supply avenue for seasonal and informal workers.
- Police-to-mining ratios vary dramatically. Madhya Pradesh and Gujarat have 15–45× more mining per officer than Maharashtra, Tamil Nadu, and Andhra Pradesh, pointing to structural enforcement gaps rather than absolute incidence levels.

The overall picture is structural: poverty and poor housing are part of the context, but the data show that government construction demand and weak enforcement are the operational triggers.
""")

        st.markdown("""
### NLP classification and illegal mining risk scoring
`classification.ipynb` is the NLP and machine learning heart of this story. We built a rule-based scoring system for the 375 field observations, combining:
- operational signals (mentions of JCBs, excavators, pumps, trucks),
- risk signals (night activity, high-volume extraction, repeated daily operations), and
- legal signals derived from court documents (explicit references to illegal mining, lack of clearance, lease violations).

The classifier labels 121 observations (32%) as highly likely illegal and 254 (68%) as possibly illegal. The highest absolute counts are in Uttar Pradesh, Madhya Pradesh, West Bengal, and Bihar. The highest proportional risk rates are in Goa and Himachal Pradesh.

A Random Forest site-location classifier reinforces the same geography: ROC-AUC is 0.965, with longitude and latitude far more important than environmental variables. Crime rate ranks third, ahead of PM10 and PM2.5, showing that governance context matters as much as pollutant exposure.
""")

        st.markdown("""
### What the report concludes
The report’s consolidated narrative is that illegal sand mining in India is national in scale but corridor-focused. Two river-based belts account for most confirmed incidents, and the strongest causal evidence links the surge after 2015 to PMAY-U construction demand.

The research also finds that:
- enforcement failure is structural, not incidental,
- socioeconomic vulnerability shapes the labor supply,
- field-level classification and court-document extraction both point to an environmental and legal pattern of illegal extraction, and
- river water quality metrics validate the mining signal with a strong dry-season contamination cycle.
""")

        st.markdown("## The thesis")
        st.markdown("""
The data shows a clear narrative: illegal sand mining in India is not primarily a story of poverty. It is a story of construction demand, supply-state extraction, and river corridor stress.

Our strongest findings are:
- PMAY-driven housing policy sharply amplified illegal extraction.
- Mining hotspots are spatially decoupled from the states that consume the sand.
- Environmental sensors confirm the river-quality signal of extraction.
- Spatial statistics and machine learning both identify the same policy-driven pattern.
""")

        def render_asset(title, path, caption, detail=None):
            st.markdown(f"#### {title}")
            if detail:
                st.markdown(detail)
            if path.endswith('.html'):
                try:
                    html_code = open(path, 'r', encoding='utf-8').read()
                    st.components.v1.html(html_code, height=460)
                except Exception:
                    st.info(f"File not found or failed to render: {path}")
            else:
                try:
                    st.image(path, width="stretch")
                except Exception:
                    st.info(f"File not found: {path}")
            st.markdown(f"*{caption}*")

        st.markdown("## Core evidence")
        render_asset(
            "Mining Incident Heatmap",
            "outputs/heatmap_mining_observations.png",
            "Density of verified mining incidents across India, highlighting river corridors and high-activity districts.",
            detail="This figure is the first visual anchor of the report: confirmed mining points concentrate along the Ganga and Chambal systems, not evenly across the country. It shows how illegal extraction is geographically focused on river corridors and vulnerable hydrological basins."
        )
        render_asset(
            "State Mining Distribution",
            "outputs/geographic_distribution_bars.png",
            "The state-level breakdown shows Bihar, UP and MP as the top extraction states, not the states with the biggest PMAY demand.",
            detail="This chart underlines the core spatial mismatch in the report: the states that extract the most sand are not always the same states that receive the largest PMAY housing allocations. This decoupling is a key part of the construction demand story."
        )
        render_asset(
            "Crime Intensity and Mining",
            "outputs/heatmap_crime_intensity.png",
            "Crime hotspots overlap with mining pressure zones, suggesting intertwined enforcement and social risk dynamics.",
            detail="The report uses crime intensity as a proxy for enforcement environment. When mining clusters overlap with crime hotspots, it suggests that illegal extraction is thriving in jurisdictions with weaker law-and-order capacity."
        )
        render_asset(
            "Housing Stock and Mining Risk",
            "outputs/housing_stacked_bars.png",
            "Dilapidated housing states appear in the same broad regions as mining, but the driver remains construction policy rather than poverty alone.",
            detail="This figure shows the structural inequality dimension of the problem: states with poor housing stock are also often the states with elevated mining activity. The report interprets this as evidence that demand for cheap construction material is linked to vulnerable housing markets."
        )
        render_asset(
            "Dilapidated Housing Choropleth",
            "outputs/choropleth_housing_dilapidated.html",
            "A state-level visualization of poor housing stock that helps place mining pressure in its policy context.",
            detail="The choropleth makes it easier to see the geography of housing distress. The report connects these poor housing states to elevated sand demand, but also emphasizes that policy-driven construction funding is the proximate trigger."
        )

        st.markdown("## The policy trigger")
        render_asset(
            "Temporal Surge after PMAY",
            "sangam_ganga_figures/fig_temporal_surge.png",
            "Annual mining incidents before and after the 2015 PMAY launch. The jump to a 14.7× higher rate is the most visible signal in the dataset.",
            detail="The report uses this figure to anchor the causal narrative. Pre-2015 annual mining averaged 13 incidents; post-2015 it averaged 191. That magnitude of increase is the first strong evidence that a policy-driven demand shock occurred."
        )
        render_asset(
            "Event Study Evidence",
            "sangam_ganga_figures/fig_event_study.png",
            "Difference-in-differences results showing mining diverging in high-PMAY states after the policy launch.",
            detail="This chart tests the parallel trends assumption and shows that high-PMAY states began to diverge after 2015. The report interprets the flat pre-policy coefficients as evidence that the treatment effect is not driven by prior divergence."
        )
        render_asset(
            "Synthetic Control for UP",
            "sangam_ganga_figures/fig_synthetic_control.png",
            "Uttar Pradesh mining compared to a synthetic counterfactual, isolating the impact of PMAY.",
            detail="For one of the most heavily affected states, the report builds a synthetic control to ask what UP’s mining trajectory would have looked like without the policy-induced construction surge. The post-2015 gap is interpreted as approximately 158% excess mining."
        )
        render_asset(
            "Construction vs Mining Clusters",
            "sangam_ganga_figures/fig_spatial_clusters.png",
            "A spatial comparison showing that mining supply states do not always coincide with construction demand states.",
            detail="This figure illustrates the key spatial mismatch. It supports the report’s finding that illegal sand typically comes from supply-side states, while PMAY demand is concentrated elsewhere, creating interstate extraction pressure."
        )

        st.markdown("## Spatial statistics and maps")
        render_asset(
            "Moran's I spatial autocorrelation",
            "sangam_ganga_figures/fig_morans_i.png",
            "Global spatial autocorrelation confirms clustering, but the strongest signal comes from state-level policy pressure.",
            detail="The report describes Moran’s I as only marginally positive (I=0.121, p=0.108), meaning the mining distribution is somewhat clustered but not strongly so. This allows us to focus on specific hotspot clusters rather than broad regional contagion."
        )
        render_asset(
            "LISA hotspot analysis",
            "sangam_ganga_figures/fig_lisa_hotspots.png",
            "Local indicators of spatial association reveal the precise river-basin clusters that carry the highest mining risk.",
            detail="This map identifies High-High clusters in Goa, Gujarat, Madhya Pradesh, and Rajasthan, forming a contiguous belt along major rivers such as the Chambal. It also flags outliers in Assam, Chhattisgarh, and Jharkhand."
        )
        render_asset(
            "KDE mining density",
            "sangam_ganga_figures/fig_kde_maps.png",
            "Kernel density estimates of mining points, showing the geographic core of extraction.",
            detail="The KDE surface reveals two distinct concentration corridors: one along the Gangetic plains and a second across Central India. The report uses this as evidence that illegal mining is tied to river systems rather than being evenly distributed."
        )
        render_asset(
            "GWR coefficient patterns",
            "sangam_ganga_figures/fig_gwr_coefficients.png",
            "Geographically weighted regression reveals where the PMAY-mining relationship is strongest.",
            detail="GWR allows coefficients to vary in space. The report finds a global R2 of 0.545, much higher than OLS, underscoring that the mining-water relationship is locally heterogeneous. Bihar and West Bengal show the strongest local contamination signals."
        )
        render_asset(
            "Spatial regression diagnostics",
            "sangam_ganga_figures/fig_spatial_regression.png",
            "Regression results that account for spatial dependence and policy covariates.",
            detail="This figure complements the spatial models discussion. In the report, Spatial Lag and Spatial Error models do not beat OLS, which supports the conclusion that state-level policy and geography explain most of the pattern."
        )

        st.markdown("## Environmental validation")
        render_asset(
            "River conductivity and mining seasonality",
            "sangam_ganga_figures/fig_conductivity_mining_seasonal.png",
            "Sensor evidence linking conductivity spikes to peak mining months.",
            detail="The report describes the dry-season conductivity increase at Prayagraj: 478 µS/cm versus 276 µS/cm during monsoon. That 1.73× rise, with a very large effect size and p<0.001, is the strongest environmental signal in the analysis."
        )
        render_asset(
            "Ganga / Sangam cross-sensor time series",
            "sangam_ganga_figures/fig_ganga_sangam_timeseries.png",
            "Water-quality sensor data confirm that river stress rises during mining season.",
            detail="Cross-sensor correlation is high for WQI, DO, and temperature, validating the data’s reliability. The report notes that conductivity diverges more because the Sangam sensor captures both the Ganga and Yamuna."
        )
        render_asset(
            "Seasonal river patterns",
            "sangam_ganga_figures/fig_ganga_seasonal.png",
            "Seasonal decomposition of river measurements shows consistent dry-season stress aligned with mining activity.",
            detail="The seasonal decomposition separates trend, seasonality, and residuals. The report uses this to show that the dry-season conductivity signal is persistent and not just an artefact of short-term fluctuations."
        )
        render_asset(
            "Sensor correlation matrix",
            "sangam_ganga_figures/fig_sensor_correlation.png",
            "Correlations across sensors that link mining activity with water-quality metrics.",
            detail="The correlation matrix confirms that the two river sensors are largely consistent, with WQI correlation at 0.891 and DO at 0.973, while conductivity is more variable across sites."
        )

        st.markdown("## Machine learning & feature evidence")
        render_asset(
            "Random Forest policy importance",
            "sangam_ganga_figures/fig_random_forest.png",
            "A model-based assessment showing that PMAY and related policy variables are the top predictors of mining incidence.",
            detail="The report presents a Random Forest classifier with ROC-AUC of 0.965 ± 0.014. Longitude and latitude are the strongest predictors, followed by crime rate, PM10, and PM2.5, demonstrating that geography and enforcement context matter most."
        )
        render_asset(
            "Feature importance breakdown",
            "sangam_ganga_figures/fig_rf_importance.png",
            "Permutation and model importances that reinforce the policy-driven story.",
            detail="The feature importance ranking shows that crime rate outranks both air quality measures, suggesting that governance and rule-of-law conditions are as important as environmental stress in determining where illegal mining occurs."
        )
        render_asset(
            "Feature distributions",
            "sangam_ganga_figures/fig_feature_distributions.png",
            "Distributional patterns of key variables used in the analysis.",
            detail="The report uses these distributions to validate that the core predictors are well-behaved and to inspect whether outliers could be driving the machine learning results."
        )
        render_asset(
            "Supplemental spatial diagnostics",
            "spatial_figures/fig_feature_distributions.png",
            "Additional feature distributions from the spatial diagnostics folder.",
            detail="These supplemental plots provide a second look at the variables used in the spatial analysis, reinforcing the robustness of the geographic and policy signals."
        )
        render_asset(
            "Spatial sensitivity checks",
            "spatial_figures/fig_focus_sensitivity.png",
            "Checks for robustness across spatial bandwidth and model settings.",
            detail="The report includes sensitivity analyses to show that the main spatial patterns are not an artifact of a particular bandwidth choice in KDE or a single model specification."
        )
        render_asset(
            "Spatial KDE focus",
            "spatial_figures/fig_focus_kde.png",
            "A focused KDE layer showing the densest mining clusters.",
            detail="This closer look confirms the two principal extraction corridors and helps distinguish the densest hotspots from the broader riverine belt."
        )
        render_asset(
            "GWR focus results",
            "spatial_figures/fig_focus_gwr.png",
            "Geographically weighted regression focus results for the strongest mining clusters.",
            detail="The focused GWR results isolate the strongest local effects and show where the mining-proximity / water-quality relationship is most pronounced."
        )
        render_asset(
            "Spatial regression overview",
            "spatial_figures/fig_spatial_regression.png",
            "Additional spatial regression diagnostics from the spatial analysis folder.",
            detail="These diagnostics support the report’s claim that the data are spatially structured but not so strongly that simple regression is invalid, making the causal and descriptive analysis more reliable."
        )
        render_asset(
            "Spatial Moran analysis",
            "spatial_figures/fig_morans_i.png",
            "Another view of the global spatial autocorrelation in the mining dataset.",
            detail="A second Moran’s I view reinforces the main finding: there is positive clustering, but it is not overwhelming, so the hotspot story is focused on specific corridors rather than the whole country."
        )
        render_asset(
            "Spatial LISA hotspots",
            "spatial_figures/fig_lisa_hotspots.png",
            "Extra local hotspot validation from the spatial figures folder.",
            detail="This additional LISA visualization offers a comparable view of local hotspots and supports the same set of High-High and Low-High state clusters described in the main report."
        )

        st.markdown("## Full visual evidence gallery")
        gallery = [
            (
                "outputs/correlation_heatmap_indicators.png",
                "Correlation heatmap of key indicators.",
                "This heatmap highlights how mining intensity co-varies with economic, environmental, and governance indicators across states. It is a useful visual summary of the report's cross-sectional analysis."
            ),
            (
                "outputs/heatmap_household_conditions.png",
                "Household condition heatmap from the outputs folder.",
                "The report uses this map to show that poor housing conditions are geographically correlated with mining activity, reinforcing the idea that the problem is structurally linked to inequality."
            ),
            (
                "sangam_ganga_figures/fig_ols_coefficients.png",
                "OLS coefficient summary from the river and mining models.",
                "This figure summarizes the baseline regression results and shows that environmental and crime variables alone explain only a modest share of mining variance."
            ),
            (
                "sangam_ganga_figures/fig_kumbh_mela_effect.png",
                "Kumbh Mela effect diagnostics computed during the analysis.",
                "The report treats the Kumbh Mela period as a confounding event. This image demonstrates how seasonal and event-related noise was identified and separated from the mining signal."
            ),
        ]
        for path, caption, detail in gallery:
            file_title = path.split('/')[-1].replace('_', ' ').replace('.png', '').title()
            st.markdown(f"#### {file_title}")
            try:
                st.image(path, width="stretch")
            except Exception:
                st.info(f"File not found: {path}")
            if detail:
                st.markdown(detail)
            st.markdown(f"*{caption}*")

        st.markdown("## What this means for India")
        st.markdown("""
The evidence is clear: illegal sand mining is not an isolated environmental problem. It is a systemic outcome of rapid housing policy and construction demand.

The most actionable implications are:
1. Create legal sand supply channels in demand states so extraction pressure does not shift to vulnerable river basins.
2. Target enforcement in the primary supply states of Bihar, UP, and MP where extraction is concentrated.
3. Couple housing policy with sustainable material policy and river monitoring.
4. Use spatial analysis and sensor data together to make enforcement proactive rather than reactive.
""")

    with tab5:
        tab5_blog_replacement.render_blog_tab()

if __name__ == "__main__":
    main()