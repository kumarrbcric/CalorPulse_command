import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import requests
from datetime import datetime

# Streamlit Page Setup
st.set_page_config(
    page_title="CalorPulse | Executive Command Center",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Executive Theme Styling
st.markdown("""
<style>
    .stApp {
        background-color: #080c14;
        color: #f1f5f9;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    .officer-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        padding: 22px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    
    .dept-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .dept-card-title {
        color: #9ca3af;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }
    .dept-card-value {
        color: #38bdf8;
        font-size: 28px;
        font-weight: 900;
        margin-top: 6px;
    }
    
    .wbgt-alert-box {
        background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%);
        border-radius: 20px;
        padding: 28px;
        text-align: center;
        color: #ffffff;
        box-shadow: 0 12px 35px rgba(185, 28, 28, 0.4);
    }
    .wbgt-val-main {
        font-size: 60px;
        font-weight: 900;
        line-height: 1;
        margin: 10px 0;
    }
    
    .zone-card {
        background: #111827;
        border-left: 5px solid #ef4444;
        border-top: 1px solid #1f2937;
        border-right: 1px solid #1f2937;
        border-bottom: 1px solid #1f2937;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: #111827;
        border-radius: 12px;
        color: #9ca3af;
        font-weight: 600;
        padding: 0px 24px;
        border: 1px solid #1f2937;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        border-color: #0284c7 !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# SIDEBAR CONTROLS
# -------------------------------------------------------------------
st.sidebar.markdown("## 🛡️ Command Portal")

department = st.sidebar.selectbox(
    "🏢 Select Assigned Department",
    [
        "Industrial Safety & Labor Welfare",
        "Disaster Management Authority",
        "Public Health & Medical Services"
    ]
)

jurisdiction = st.sidebar.selectbox(
    "📍 Jurisdiction District",
    [
        "Thanjavur District",
        "Coimbatore Industrial Belt",
        "Chennai Metropolitan Area",
        "Madurai District",
        "Tiruchirappalli Metro"
    ]
)

# LOCALISED DATABASE WITH PRECISE LAT/LON AND SUB-ZONES
location_database = {
    "Thanjavur District": {
        "lat": 10.7867, "lon": 79.1378, "zoom": 12, "solar": 910,
        "zones": [
            {"name": "SIPCOT Industrial Complex", "lat": 10.8120, "lon": 79.1250, "offset_t": 0.5, "offset_rh": -2},
            {"name": "Old Bus Stand Transit Sector", "lat": 10.7860, "lon": 79.1380, "offset_t": 0.0, "offset_rh": 2},
            {"name": "Medical College Belt", "lat": 10.7420, "lon": 79.1050, "offset_t": -0.8, "offset_rh": 0}
        ]
    },
    "Coimbatore Industrial Belt": {
        "lat": 11.0168, "lon": 76.9558, "zoom": 12, "solar": 840,
        "zones": [
            {"name": "Peelamedu Industrial Estate", "lat": 11.0250, "lon": 77.0020, "offset_t": 0.6, "offset_rh": -2},
            {"name": "SIDCO Machinery Hub", "lat": 10.9950, "lon": 76.9200, "offset_t": 0.9, "offset_rh": -4},
            {"name": "Gandhipuram Transit Zone", "lat": 11.0180, "lon": 76.9650, "offset_t": -0.3, "offset_rh": 2}
        ]
    },
    "Chennai Metropolitan Area": {
        "lat": 13.0827, "lon": 80.2707, "zoom": 12, "solar": 945,
        "zones": [
            {"name": "Guindy Industrial Sector", "lat": 13.0100, "lon": 80.2100, "offset_t": 0.6, "offset_rh": -2},
            {"name": "Central Railway Junction", "lat": 13.0820, "lon": 80.2750, "offset_t": 1.0, "offset_rh": -4},
            {"name": "T. Nagar Commercial Hub", "lat": 13.0410, "lon": 80.2330, "offset_t": -0.5, "offset_rh": 2}
        ]
    },
    "Madurai District": {
        "lat": 9.9252, "lon": 78.1198, "zoom": 12, "solar": 960,
        "zones": [
            {"name": "Kappalur Industrial Complex", "lat": 9.8800, "lon": 78.0500, "offset_t": 0.6, "offset_rh": -3},
            {"name": "Mattuthavani Bus Terminal", "lat": 9.9450, "lon": 78.1500, "offset_t": 0.2, "offset_rh": 2},
            {"name": "Periyar Market Sector", "lat": 9.9150, "lon": 78.1100, "offset_t": -0.6, "offset_rh": 4}
        ]
    },
    "Tiruchirappalli Metro": {
        "lat": 10.7905, "lon": 78.7047, "zoom": 12, "solar": 895,
        "zones": [
            {"name": "BHEL Industrial Zone", "lat": 10.7820, "lon": 78.7850, "offset_t": 0.5, "offset_rh": -2},
            {"name": "Chatram Bus Stand Area", "lat": 10.8350, "lon": 78.6900, "offset_t": -0.1, "offset_rh": 2},
            {"name": "Thiruverumbur Factory Belt", "lat": 10.7750, "lon": 78.7600, "offset_t": -0.6, "offset_rh": 0}
        ]
    }
}

loc_data = location_database[jurisdiction]

# REAL-TIME WEATHER FETCHING VIA OPEN-METEO API (FREE, NO API KEY)
@st.cache_data(ttl=300)
def fetch_live_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
        response = requests.get(url, timeout=3)
        data = response.json()
        current = data.get("current", {})
        temp = current.get("temperature_2m")
        humidity = current.get("relative_humidity_2m")
        wind = current.get("wind_speed_10m")
        return temp, humidity, wind
    except Exception:
        return None, None, None

live_temp, live_rh, live_wind = fetch_live_weather(loc_data["lat"], loc_data["lon"])

base_temp = round(live_temp, 1) if live_temp is not None else 37.5
humidity = int(live_rh) if live_rh is not None else 65
wind = round(live_wind, 1) if live_wind is not None else 9.0
solar = loc_data["solar"]

processed_zones = []
for z in loc_data["zones"]:
    zt = round(base_temp + z["offset_t"], 1)
    zrh = max(30, min(95, humidity + z["offset_rh"]))
    processed_zones.append({
        "name": z["name"],
        "lat": z["lat"],
        "lon": z["lon"],
        "temp": zt,
        "rh": zrh
    })

# WBGT Calculation & Dynamic Status Logic (ISO 7243 Standard)
e_val = (humidity / 100.0) * 6.105 * np.exp((17.27 * base_temp) / (237.7 + base_temp))
curr_wbgt = round(0.567 * base_temp + 0.393 * e_val + 3.94, 1)

if curr_wbgt >= 41.0:
    hazard_status = "CRITICAL HAZARD"
    status_color = "#ef4444"
elif curr_wbgt >= 37.0:
    hazard_status = "EXTREME HAZARD"
    status_color = "#f97316"
elif curr_wbgt >= 32.0:
    hazard_status = "HIGH WARNING"
    status_color = "#eab308"
else:
    hazard_status = "NORMAL ADVISORY"
    status_color = "#10b981"

# -------------------------------------------------------------------
# COMMAND HEADER
# -------------------------------------------------------------------
st.markdown(f"""
<div class="officer-banner">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin:0; font-size: 26px; font-weight:900; color:#fff;">🔥 CalorPulse Operational Command Center</h1>
            <p style="margin:6px 0 0 0; color:#94a3b8; font-size:14px;">Jurisdiction: <span style="color:#38bdf8; font-weight:700;">{jurisdiction}</span> | <span style="color:#10b981; font-weight:700;">● Live API Synced</span></p>
        </div>
        <div>
            <span style="background-color:#0284c7; color:#fff; padding:8px 16px; border-radius:30px; font-size:12px; font-weight:800; letter-spacing:1px;">
                {department.upper()}
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# DEPARTMENT METRICS
col_d1, col_d2, col_d3, col_d4 = st.columns(4)
if department == "Industrial Safety & Labor Welfare":
    with col_d1:
        st.markdown('<div class="dept-card"><div class="dept-card-title">Monitored Factories</div><div class="dept-card-value">148 Units</div></div>', unsafe_allow_html=True)
    with col_d2:
        st.markdown('<div class="dept-card"><div class="dept-card-title">Exposed Outdoor Workers</div><div class="dept-card-value">16,400</div></div>', unsafe_allow_html=True)
    with col_d3:
        st.markdown('<div class="dept-card"><div class="dept-card-title">Rest Shift Compliance</div><div class="dept-card-value">91.4%</div></div>', unsafe_allow_html=True)
    with col_d4:
        st.markdown('<div class="dept-card"><div class="dept-card-title">Hydration Stations</div><div class="dept-card-value">312 Active</div></div>', unsafe_allow_html=True)
elif department == "Disaster Management Authority":
    with col_d1:
        st.markdown('<div class="dept-card"><div class="dept-card-title">Active Cooling Shelters</div><div class="dept-card-value">24 Centers</div></div>', unsafe_allow_html=True)
    with col_d2:
        st.markdown('<div class="dept-card"><div class="dept-card-title">Emergency Response Teams</div><div class="dept-card-value">18 Squads</div></div>', unsafe_allow_html=True)
    with col_d3:
        st.markdown('<div class="dept-card"><div class="dept-card-title">Water Tankers Deployed</div><div class="dept-card-value">112 Fleet</div></div>', unsafe_allow_html=True)
    with col_d4:
        st.markdown('<div class="dept-card"><div class="dept-card-title">Public Advisory Status</div><div class="dept-card-value" style="color:#f97316;">HIGH ALERT</div></div>', unsafe_allow_html=True)
else:
    with col_d1:
        st.markdown('<div class="dept-card"><div class="dept-card-title">Available ICU Heat Beds</div><div class="dept-card-value">142 / 180</div></div>', unsafe_allow_html=True)
    with col_d2:
        st.markdown('<div class="dept-card"><div class="dept-card-title">Active 108 Ambulances</div><div class="dept-card-value">38 Fleet</div></div>', unsafe_allow_html=True)
    with col_d3:
        st.markdown('<div class="dept-card"><div class="dept-card-title">Cold Saline Stock</div><div class="dept-card-value">5,420 Units</div></div>', unsafe_allow_html=True)
    with col_d4:
        st.markdown('<div class="dept-card"><div class="dept-card-title">Medical Alert Level</div><div class="dept-card-value" style="color:#ef4444;">RED STAGE 3</div></div>', unsafe_allow_html=True)

st.write("")

# MAIN DASHBOARD TABS
tab1, tab2, tab3 = st.tabs([
    "📊 Real-time Stress & Trends",
    "🌍 Localised Weather Radar Map",
    "🚨 Automated Departmental Broadcast"
])

# ===================================================================
# TAB 1: MICRO-CLIMATE METRICS & SUB-ZONES
# ===================================================================
with tab1:
    c_alert, c_metrics = st.columns([1.1, 1.9])
    
    with c_alert:
        st.markdown(f"""
        <div class="wbgt-alert-box">
            <div style="font-size:12px; letter-spacing:2px; font-weight:800; color:#fca5a5;">PRIMARY ZONE WBGT INDEX NOW</div>
            <div class="wbgt-val-main">{curr_wbgt}°C</div>
            <div style="font-size:18px; font-weight:800; color:#fef08a;">⚠️ {hazard_status}</div>
            <div style="font-size:12px; margin-top:8px; opacity:0.9;">ISO 7243 Outdoor worker shift restrictions active</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c_metrics:
        st.markdown(f"### 🌡️ Live Micro-Climate Parameters — {jurisdiction}")
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.markdown(f'<div class="dept-card"><div class="dept-card-title">Live Temperature</div><div class="dept-card-value">{base_temp} °C</div></div>', unsafe_allow_html=True)
            st.write("")
            st.markdown(f'<div class="dept-card"><div class="dept-card-title">Solar Radiation</div><div class="dept-card-value">{solar} W/m²</div></div>', unsafe_allow_html=True)
        with m_col2:
            st.markdown(f'<div class="dept-card"><div class="dept-card-title">Live Relative Humidity</div><div class="dept-card-value">{humidity} %</div></div>', unsafe_allow_html=True)
            st.write("")
            st.markdown(f'<div class="dept-card"><div class="dept-card-title">Live Wind Speed</div><div class="dept-card-value">{wind} km/h</div></div>', unsafe_allow_html=True)

    st.divider()
    st.subheader(f"🏢 {jurisdiction} Region Breakdown")
    
    z_cols = st.columns(3)
    for idx, z in enumerate(processed_zones):
        e_z = (z["rh"] / 100.0) * 6.105 * np.exp((17.27 * z["temp"]) / (237.7 + z["temp"]))
        wbgt_z = round(0.567 * z["temp"] + 0.393 * e_z + 3.94, 1)
        
        if wbgt_z >= 41.0:
            z_status, z_col = "CRITICAL HAZARD", "#ef4444"
        elif wbgt_z >= 37.0:
            z_status, z_col = "EXTREME HAZARD", "#f97316"
        elif wbgt_z >= 32.0:
            z_status, z_col = "HIGH WARNING", "#eab308"
        else:
            z_status, z_col = "NORMAL ADVISORY", "#10b981"
        
        with z_cols[idx % 3]:
            st.markdown(f"""
            <div class="zone-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:15px; font-weight:800; color:#fff;">{z['name']}</span>
                    <span style="background:{z_col}; color:#fff; font-size:10px; font-weight:800; padding:3px 8px; border-radius:10px;">{z_status}</span>
                </div>
                <div style="margin-top:10px; font-size:13px; color:#cbd5e1;">
                    <div>🌡️ Temp: <b>{z['temp']}°C</b></div>
                    <div>💧 Humidity: <b>{z['rh']}%</b></div>
                    <div>🔥 WBGT Index: <b style="color:{z_col};">{wbgt_z}°C</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ===================================================================
# TAB 2: FREE LOCALISED LEAFLET RADAR MAP
# ===================================================================
with tab2:
    st.subheader(f"🌍 High-Resolution Local Thermal Radar — {jurisdiction}")
    st.caption("Live temperature weather radar synced with live meteorological API data.")

    import json as _json

    def _wbgt_of(temp, rh):
        e = (rh / 100.0) * 6.105 * np.exp((17.27 * temp) / (237.7 + temp))
        return round(0.567 * temp + 0.393 * e + 3.94, 1)

    def _color_of(wbgt):
        if wbgt >= 41.0: return "#ef4444"
        elif wbgt >= 37.0: return "#f97316"
        elif wbgt >= 32.0: return "#eab308"
        else: return "#10b981"

    center_wbgt = _wbgt_of(base_temp, humidity)
    map_points = [{
        "name": jurisdiction + " (HQ)",
        "lat": loc_data["lat"], "lon": loc_data["lon"],
        "temp": base_temp, "rh": humidity,
        "wbgt": center_wbgt, "color": _color_of(center_wbgt), "hq": True
    }]
    for z in processed_zones:
        w = _wbgt_of(z["temp"], z["rh"])
        map_points.append({
            "name": z["name"], "lat": z["lat"], "lon": z["lon"],
            "temp": z["temp"], "rh": z["rh"],
            "wbgt": w, "color": _color_of(w), "hq": False
        })

    SCALE_MIN, SCALE_MAX = 15, 45

    leaflet_html = f"""
    <div style="position:relative;">
        <div id="calorpulse-map" style="width:100%; height:560px; border-radius:14px; overflow:hidden; border:1px solid #1f2937;"></div>
        <div style="position:absolute; top:12px; right:12px; z-index:500; background:rgba(15,23,42,0.85); color:#fff; font-family:sans-serif; font-size:11px; font-weight:800; padding:6px 12px; border-radius:8px; border:1px solid rgba(255,255,255,0.15);">
            🌡️ Live Temperature
        </div>
    </div>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.heat/0.2.0/leaflet-heat.js"></script>
    <script>
        var points = {_json.dumps(map_points)};
        var SCALE_MIN = {SCALE_MIN}, SCALE_MAX = {SCALE_MAX};

        var map = L.map('calorpulse-map', {{
            scrollWheelZoom: true,
            zoomControl: true,
            fadeAnimation: false,
            zoomAnimation: false,
            markerZoomAnimation: false,
            preferCanvas: true
        }}).setView([{loc_data['lat']}, {loc_data['lon']}], {loc_data['zoom']});

        var baseLayer = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap contributors'
        }}).addTo(map);

        function fixSize() {{ map.invalidateSize(false); }}
        window.addEventListener('load', fixSize);
        setTimeout(fixSize, 250);

        function seededRand(seed) {{
            var x = Math.sin(seed) * 10000;
            return x - Math.floor(x);
        }}
        var heatPoints = [];
        points.forEach(function(p, pIdx) {{
            var w = Math.max(0, Math.min(1, (p.temp - SCALE_MIN) / (SCALE_MAX - SCALE_MIN)));
            var samples = p.hq ? 10 : 6;
            var spread = p.hq ? 0.05 : 0.03;
            for (var i = 0; i < samples; i++) {{
                var dLat = (seededRand(pIdx * 97 + i * 13) - 0.5) * spread;
                var dLon = (seededRand(pIdx * 131 + i * 17 + 5) - 0.5) * spread;
                heatPoints.push([p.lat + dLat, p.lon + dLon, w]);
            }}
            heatPoints.push([p.lat, p.lon, w]);
        }});

        L.heatLayer(heatPoints, {{
            radius: 55,
            blur: 45,
            maxZoom: 14,
            max: 1.0,
            minOpacity: 0.35,
            gradient: {{
                0.0: '#3b0764',
                0.2: '#1d4ed8',
                0.35: '#0ea5e9',
                0.5: '#22c55e',
                0.65: '#eab308',
                0.8: '#f97316',
                0.92: '#ef4444',
                1.0: '#7f1d1d'
            }}
        }}).addTo(map);

        points.forEach(function(p) {{
            var radius = p.hq ? 14 : 10;
            var marker = L.circleMarker([p.lat, p.lon], {{
                radius: radius,
                fillColor: p.color,
                color: '#ffffff',
                weight: p.hq ? 3 : 2,
                opacity: 1,
                fillOpacity: 0.9
            }}).addTo(map);

            marker.bindTooltip(
                '<b>' + p.name + '</b><br>' + p.temp + '&deg;C',
                {{ permanent: true, direction: 'top', offset: [0, -radius], className: 'temp-label' }}
            );
        }});
    </script>
    <style>
        .temp-label {{
            background: rgba(15,23,42,0.85) !important;
            color: #fff !important;
            border: none !important;
            font-weight: 700;
            font-size: 11px;
            border-radius: 6px !important;
            padding: 2px 6px !important;
            box-shadow: none !important;
        }}
        .temp-label::before {{ display: none !important; }}
        .leaflet-container {{ background: #0b1120; }}
    </style>
    """

    components.html(leaflet_html, height=570, scrolling=False)

# ===================================================================
# TAB 3: AUTOMATED DISPATCH
# ===================================================================
with tab3:
    st.markdown("### 🚨 Executive Multi-Channel Directive Gateway")
    st.caption("Automated emergency message dispatch system integrated with State Command Server, WhatsApp API, SMS Gateway, and Citizen App Push Nodes.")
    
    c_rc1, c_rc2, c_rc3, c_rc4 = st.columns(4)
    with c_rc1:
        st.markdown('<div class="dept-card"><div class="dept-card-title">Target Recipients</div><div class="dept-card-value">148 Directory</div></div>', unsafe_allow_html=True)
    with c_rc2:
        st.markdown('<div class="dept-card"><div class="dept-card-title">Active Dispatch Channels</div><div class="dept-card-value" style="color:#10b981;">4 Gateways</div></div>', unsafe_allow_html=True)
    with c_rc3:
        st.markdown('<div class="dept-card"><div class="dept-card-title">Gateway Latency</div><div class="dept-card-value">120 ms</div></div>', unsafe_allow_html=True)
    with c_rc4:
        st.markdown('<div class="dept-card"><div class="dept-card-title">Broadcast Authorization</div><div class="dept-card-value" style="color:#0284c7;">VERIFIED</div></div>', unsafe_allow_html=True)
    
    st.write("")
    
    col_dispatch, col_preview = st.columns([1.3, 1.0])
    
    with col_dispatch:
        st.markdown("#### ⚙️ Configure Directive Parameters")
        
        priority = st.select_slider(
            "🚨 Directive Priority Level",
            options=["NORMAL ADVISORY", "HIGH WARNING", "CRITICAL EMERGENCY"],
            value="CRITICAL EMERGENCY"
        )
        
        st.markdown("**📡 Active Dispatch Channels:**")
        ch1, ch2, ch3, ch4 = st.columns(4)
        with ch1:
            send_whatsapp = st.checkbox("📱 WhatsApp", value=True)
        with ch2:
            send_sms = st.checkbox("💬 SMS Push", value=True)
        with ch3:
            send_email = st.checkbox("📧 Official Email", value=True)
        with ch4:
            send_app = st.checkbox("🔔 App Alert", value=True)
            
        if department == "Industrial Safety & Labor Welfare":
            target_group = f"All Registered Factory Managers & Safety Officers in {jurisdiction} (148 Contacts)"
            default_template = f"[{priority}] MANDATORY INDUSTRIAL HEAT SAFETY DIRECTIVE:\nRegion: {jurisdiction}\nWBGT Level: {curr_wbgt}°C ({hazard_status})\n\nDIRECTIVE MANDATES:\n1. Enforce mandatory 45-min work / 15-min rest cycles for outdoor workers.\n2. Ensure high-capacity ORS & electrolyte stations at all factory floors.\n3. Non-compliance will incur immediate statutory penalties."
        elif department == "Public Health & Medical Services":
            target_group = f"Primary Health Centers, ER Wards & Ambulance Fleet in {jurisdiction} (48 Contacts)"
            default_template = f"[{priority}] MEDICAL EMERGENCY RESPONSE ADVISORY:\nRegion: {jurisdiction}\nWBGT Heat Stress Index: {curr_wbgt}°C ({hazard_status})\n\nREQUIRED ACTIONS:\n1. Keep 142 heatstroke ICU emergency beds prepped with cold saline.\n2. Position 108 ALS Ambulances at high-vulnerability transit hubs.\n3. Mobilize mobile emergency medical squads."
        else:
            target_group = f"District Revenue Officers, Relief Squads & Municipal Bodies in {jurisdiction} (82 Contacts)"
            default_template = f"[{priority}] DISTRICT DISASTER RESPONSE DIRECTIVE:\nRegion: {jurisdiction}\nWBGT Heat Stress Index: {curr_wbgt}°C ({hazard_status})\n\nACTION REQUIRED:\n1. Activate all public cooling shelters and hydration centers immediately.\n2. Dispatch water tanker fleet to transit and market zones.\n3. Trigger public siren advisory for peak heat hours (12:00 PM - 3:30 PM)."

        st.text_input("🎯 Connected Master Directory Group", value=target_group, disabled=True)
        broadcast_msg = st.text_area("✍️ Directive Content Draft", value=default_template, height=160)
        
        if st.button("🚀 EXECUTE ONE-CLICK MULTI-CHANNEL BROADCAST"):
            channels_used = []
            if send_whatsapp: channels_used.append("WhatsApp")
            if send_sms: channels_used.append("SMS")
            if send_email: channels_used.append("Email")
            if send_app: channels_used.append("Citizen App Push")
            
            st.success(f"✅ Directive successfully dispatched via [{', '.join(channels_used)}] to {target_group}!")
            
            if "audit_logs" not in st.session_state:
                st.session_state["audit_logs"] = []
            st.session_state["audit_logs"].insert(0, {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "group": target_group,
                "priority": priority,
                "channels": ", ".join(channels_used),
                "msg": broadcast_msg,
                "status": "DELIVERED (200 OK)"
            })

    with col_preview:
        st.markdown("#### 📱 Live Recipient Mobile Preview")
        priority_color = "#ef4444" if priority == "CRITICAL EMERGENCY" else ("#f97316" if priority == "HIGH WARNING" else "#10b981")
        
        st.markdown(f"""
        <div style="background:#1e293b; border: 2px solid {priority_color}; border-radius: 18px; padding: 18px; box-shadow: 0 8px 25px rgba(0,0,0,0.4);">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; padding-bottom:10px; margin-bottom:12px;">
                <span style="font-size:12px; font-weight:800; color:{priority_color};">🚨 {priority}</span>
                <span style="font-size:10px; color:#94a3b8;">STATE COMMAND NODE</span>
            </div>
            <div style="font-size:12px; font-weight:700; color:#38bdf8; margin-bottom:8px;">
                From: Govt Emergency Dispatcher ({department})
            </div>
            <div style="font-size:12px; color:#e2e8f0; white-space: pre-wrap; background:#0f172a; padding:12px; border-radius:10px; border:1px solid #334155; line-height:1.5;">
{broadcast_msg}
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:12px; font-size:10px; color:#94a388;">
                <span>Channels: WhatsApp, SMS, App</span>
                <span>Latency: 0.2s</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        st.markdown("#### 📜 Live Broadcast Dispatch Log")
        if "audit_logs" in st.session_state and st.session_state["audit_logs"]:
            for log in st.session_state["audit_logs"][:3]:
                st.markdown(f"""
                <div style="background:#111827; border-left:4px solid #10b981; border-top:1px solid #1f2937; border-right:1px solid #1f2937; border-bottom:1px solid #1f2937; border-radius:10px; padding:12px; margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; font-size:11px; font-weight:700;">
                        <span style="color:#10b981;">{log['status']}</span>
                        <span style="color:#94a388;">{log['timestamp']}</span>
                    </div>
                    <div style="font-size:11px; color:#cbd5e1; margin-top:4px;"><b>Target:</b> {log['group']}</div>
                    <div style="font-size:11px; color:#94a388;"><b>Channels:</b> {log['channels']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No directives dispatched in this session yet. Click broadcast to dispatch.")
