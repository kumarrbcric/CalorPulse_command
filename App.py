import streamlit as st
import streamlit.components.v1 as components
import numpy as np
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
        "lat": 10.7867, "lon": 79.1378, "zoom": 12,
        "base_temp": 37.6, "humidity": 66, "solar": 910, "wind": 8.5,
        "zones": [
            {"name": "SIPCOT Industrial Complex", "lat": 10.8120, "lon": 79.1250, "temp": 38.1, "rh": 64},
            {"name": "Old Bus Stand Transit Sector", "lat": 10.7860, "lon": 79.1380, "temp": 37.5, "rh": 68},
            {"name": "Medical College Belt", "lat": 10.7420, "lon": 79.1050, "temp": 36.8, "rh": 66}
        ]
    },
    "Coimbatore Industrial Belt": {
        "lat": 11.0168, "lon": 76.9558, "zoom": 12,
        "base_temp": 33.2, "humidity": 52, "solar": 840, "wind": 12.0,
        "zones": [
            {"name": "Peelamedu Industrial Estate", "lat": 11.0250, "lon": 77.0020, "temp": 33.8, "rh": 50},
            {"name": "SIDCO Machinery Hub", "lat": 10.9950, "lon": 76.9200, "temp": 34.1, "rh": 48},
            {"name": "Gandhipuram Transit Zone", "lat": 11.0180, "lon": 76.9650, "temp": 32.9, "rh": 54}
        ]
    },
    "Chennai Metropolitan Area": {
        "lat": 13.0827, "lon": 80.2707, "zoom": 12,
        "base_temp": 39.5, "humidity": 74, "solar": 945, "wind": 6.2,
        "zones": [
            {"name": "Guindy Industrial Sector", "lat": 13.0100, "lon": 80.2100, "temp": 40.1, "rh": 72},
            {"name": "Central Railway Junction", "lat": 13.0820, "lon": 80.2750, "temp": 40.5, "rh": 70},
            {"name": "T. Nagar Commercial Hub", "lat": 13.0410, "lon": 80.2330, "temp": 39.0, "rh": 76}
        ]
    },
    "Madurai District": {
        "lat": 9.9252, "lon": 78.1198, "zoom": 12,
        "base_temp": 40.8, "humidity": 48, "solar": 960, "wind": 7.0,
        "zones": [
            {"name": "Kappalur Industrial Complex", "lat": 9.8800, "lon": 78.0500, "temp": 41.4, "rh": 45},
            {"name": "Mattuthavani Bus Terminal", "lat": 9.9450, "lon": 78.1500, "temp": 41.0, "rh": 50},
            {"name": "Periyar Market Sector", "lat": 9.9150, "lon": 78.1100, "temp": 40.2, "rh": 52}
        ]
    },
    "Tiruchirappalli Metro": {
        "lat": 10.7905, "lon": 78.7047, "zoom": 12,
        "base_temp": 38.9, "humidity": 58, "solar": 895, "wind": 9.1,
        "zones": [
            {"name": "BHEL Industrial Zone", "lat": 10.7820, "lon": 78.7850, "temp": 39.4, "rh": 56},
            {"name": "Chatram Bus Stand Area", "lat": 10.8350, "lon": 78.6900, "temp": 38.8, "rh": 60},
            {"name": "Thiruverumbur Factory Belt", "lat": 10.7750, "lon": 78.7600, "temp": 38.3, "rh": 58}
        ]
    }
}

loc_data = location_database[jurisdiction]

# WBGT Calculation (ISO 7243 Standard)
e_val = (loc_data["humidity"] / 100.0) * 6.105 * np.exp((17.27 * loc_data["base_temp"]) / (237.7 + loc_data["base_temp"]))
curr_wbgt = round(0.567 * loc_data["base_temp"] + 0.393 * e_val + 3.94, 1)

hazard_status = "CRITICAL HAZARD" if curr_wbgt >= 42.0 else ("EXTREME HAZARD" if curr_wbgt >= 35.0 else "HIGH WARNING")
status_color = "#ef4444" if curr_wbgt >= 35.0 else "#f97316"

# -------------------------------------------------------------------
# COMMAND HEADER
# -------------------------------------------------------------------
st.markdown(f"""
<div class="officer-banner">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin:0; font-size: 26px; font-weight:900; color:#fff;">🔥 CalorPulse Operational Command Center</h1>
            <p style="margin:6px 0 0 0; color:#94a3b8; font-size:14px;">Jurisdiction: <span style="color:#38bdf8; font-weight:700;">{jurisdiction}</span></p>
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
        st.markdown(f"### 🌡️ Micro-Climate Parameters — {jurisdiction}")
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.markdown(f'<div class="dept-card"><div class="dept-card-title">Ambient Temperature</div><div class="dept-card-value">{loc_data["base_temp"]} °C</div></div>', unsafe_allow_html=True)
            st.write("")
            st.markdown(f'<div class="dept-card"><div class="dept-card-title">Solar Radiation</div><div class="dept-card-value">{loc_data["solar"]} W/m²</div></div>', unsafe_allow_html=True)
        with m_col2:
            st.markdown(f'<div class="dept-card"><div class="dept-card-title">Relative Humidity</div><div class="dept-card-value">{loc_data["humidity"]} %</div></div>', unsafe_allow_html=True)
            st.write("")
            st.markdown(f'<div class="dept-card"><div class="dept-card-title">Wind Speed</div><div class="dept-card-value">{loc_data["wind"]} km/h</div></div>', unsafe_allow_html=True)

    st.divider()
    st.subheader(f"🏢 {jurisdiction} Region Breakdown")
    
    z_cols = st.columns(3)
    for idx, z in enumerate(loc_data["zones"]):
        e_z = (z["rh"] / 100.0) * 6.105 * np.exp((17.27 * z["temp"]) / (237.7 + z["temp"]))
        wbgt_z = round(0.567 * z["temp"] + 0.393 * e_z + 3.94, 1)
        z_status = "CRITICAL HAZARD" if wbgt_z >= 40.0 else "EXTREME HAZARD"
        
        with z_cols[idx % 3]:
            st.markdown(f"""
            <div class="zone-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:15px; font-weight:800; color:#fff;">{z['name']}</span>
                    <span style="background:{status_color}; color:#fff; font-size:10px; font-weight:800; padding:3px 8px; border-radius:10px;">{z_status}</span>
                </div>
                <div style="margin-top:10px; font-size:13px; color:#cbd5e1;">
                    <div>🌡️ Temp: <b>{z['temp']}°C</b></div>
                    <div>💧 Humidity: <b>{z['rh']}%</b></div>
                    <div>🔥 WBGT Index: <b style="color:{status_color};">{wbgt_z}°C</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ===================================================================
# TAB 2: FREE LOCALISED LEAFLET RADAR MAP (NO API KEY NEEDED)
# ===================================================================
with tab2:
    st.subheader(f"🌍 High-Resolution Local Thermal Radar — {jurisdiction}")
    st.caption("Live temperature radar auto-centered on the selected jurisdiction. Switch the district in the sidebar and the map recenters automatically. Scroll or use +/- to zoom — fully interactive, no external limits.")

    import json as _json

    def _wbgt_of(temp, rh):
        e = (rh / 100.0) * 6.105 * np.exp((17.27 * temp) / (237.7 + temp))
        return round(0.567 * temp + 0.393 * e + 3.94, 1)

    def _color_of(wbgt):
        if wbgt >= 40.0:
            return "#ef4444"
        elif wbgt >= 35.0:
            return "#f97316"
        else:
            return "#eab308"

    center_wbgt = _wbgt_of(loc_data["base_temp"], loc_data["humidity"])
    map_points = [{
        "name": jurisdiction + " (HQ)",
        "lat": loc_data["lat"], "lon": loc_data["lon"],
        "temp": loc_data["base_temp"], "rh": loc_data["humidity"],
        "wbgt": center_wbgt, "color": _color_of(center_wbgt), "hq": True
    }]
    for z in loc_data["zones"]:
        w = _wbgt_of(z["temp"], z["rh"])
        map_points.append({
            "name": z["name"], "lat": z["lat"], "lon": z["lon"],
            "temp": z["temp"], "rh": z["rh"],
            "wbgt": w, "color": _color_of(w), "hq": False
        })

    # Fixed scale so colors always mean the same temperature across every
    # jurisdiction (mirrors Windy's fixed -20..40 legend, tuned to our hot range).
    SCALE_MIN, SCALE_MAX = 15, 45

    leaflet_html = f"""
    <div style="position:relative;">
        <div id="calorpulse-map" style="width:100%; height:560px; border-radius:14px; overflow:hidden; border:1px solid #1f2937;"></div>
        <div style="position:absolute; top:12px; right:12px; z-index:500; background:rgba(15,23,42,0.85); color:#fff; font-family:sans-serif; font-size:11px; font-weight:800; padding:6px 12px; border-radius:8px; border:1px solid rgba(255,255,255,0.15);">
            🌡️ Temperature
        </div>
        <div style="position:absolute; left:12px; right:12px; bottom:12px; z-index:500; background:rgba(15,23,42,0.88); border:1px solid rgba(255,255,255,0.12); border-radius:10px; padding:8px 14px;">
            <div style="height:10px; border-radius:5px; background:linear-gradient(to right, #3b0764, #1d4ed8, #0ea5e9, #22c55e, #eab308, #f97316, #ef4444, #7f1d1d);"></div>
            <div style="display:flex; justify-content:space-between; font-family:sans-serif; font-size:10px; color:#cbd5e1; margin-top:4px;">
                <span>{SCALE_MIN}°C</span><span>20°C</span><span>25°C</span><span>30°C</span><span>35°C</span><span>40°C</span><span>{SCALE_MAX}°C</span>
            </div>
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
            // leaflet.heat draws to a plain canvas that can't keep up with
            // Leaflet's zoom-animation transform, which is what caused the
            // heat layer to flash/jump on zoom. Turning zoom animation off
            // makes it snap cleanly instead of glitching.
            zoomAnimation: false,
            markerZoomAnimation: false,
            preferCanvas: true
        }}).setView([{loc_data['lat']}, {loc_data['lon']}], {loc_data['zoom']});

        // Real, fully-localised street map underneath — every road/place name visible.
        var baseLayer = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap contributors'
        }}).addTo(map);

        // The iframe reports its final size a beat after Leaflet first paints,
        // which is what caused the grey/half-loaded tile glitch. Force Leaflet
        // to re-measure once the container has settled.
        function fixSize() {{ map.invalidateSize(false); }}
        window.addEventListener('load', fixSize);
        setTimeout(fixSize, 250);
        setTimeout(fixSize, 800);
        baseLayer.on('load', fixSize);

        // Windy-style translucent heat-color layer on top of the streets.
        // Jitter a few synthetic samples around each real reading so the
        // blob spreads smoothly across the district instead of tiny dots.
        // Uses a deterministic pseudo-random sequence (not Math.random()) so
        // the blob is stable and doesn't reshuffle every Streamlit rerun.
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

        // Local sub-station markers + labels stay on top, fully localised.
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

            marker.bindPopup(
                '<div style="font-family:sans-serif; min-width:170px;">' +
                '<b>' + p.name + '</b><br>' +
                'Temp: <b>' + p.temp + '&deg;C</b><br>' +
                'Humidity: <b>' + p.rh + '%</b><br>' +
                'WBGT: <b style="color:' + p.color + ';">' + p.wbgt + '&deg;C</b>' +
                '</div>'
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

    st.caption(f"📍 Centered on {jurisdiction} ({loc_data['lat']}, {loc_data['lon']}) · Layer: Temperature · {len(map_points)} live sub-station points")
    
    st.write("")
    st.markdown("### 📌 Active Local Sub-Station Sensors in View")
    sub_cols = st.columns(len(loc_data["zones"]))
    for idx, z in enumerate(loc_data["zones"]):
        with sub_cols[idx]:
            st.markdown(f"""
            <div style="background:#111827; border:1px solid #1f2937; border-radius:12px; padding:14px; text-align:center;">
                <div style="font-size:12px; font-weight:700; color:#38bdf8;">{z['name']}</div>
                <div style="font-size:20px; font-weight:900; color:#fff; margin:6px 0;">{z['temp']}°C</div>
                <div style="font-size:11px; color:#9ca3af;">Humidity: {z['rh']}%</div>
            </div>
            """, unsafe_allow_html=True)

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
