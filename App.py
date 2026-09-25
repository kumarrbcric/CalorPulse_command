"""
CalorPulse Command — Officer Console
A Python web app (Streamlit) for the MoES Extreme Heatwave Early Warning problem statement.

Run locally:
    pip install -r requirements.txt
    streamlit run app.py

Deploy free (no server management):
    1. Push this folder to a GitHub repo.
    2. Go to https://share.streamlit.io -> New app -> pick the repo -> main file: app.py -> Deploy.
    You get a permanent https://<name>.streamlit.app link, free.

Live weather: Open-Meteo (no API key needed).
SMS/WhatsApp: optional Twilio integration. Without credentials, sending is simulated
(logged, not actually delivered) so the app is fully usable out of the box.
"""

import time
from datetime import datetime

import folium
import math
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

# ----------------------------------------------------------------------
# CONFIG / THEME
# ----------------------------------------------------------------------
st.set_page_config(page_title="CalorPulse Command", page_icon="🌡️", layout="wide")

ORANGE1, ORANGE2, AMBER, GREEN, BLUE = "#FF9A3D", "#E5484D", "#F5A524", "#2F8F6B", "#3A6FF0"

st.markdown(f"""
<style>
.stApp {{ background:#FFF3EC; }}
div[data-testid="stMetric"] {{ background:#fff; border-radius:16px; padding:12px; box-shadow:0 2px 8px rgba(60,30,10,.06); }}
.hero {{ border-radius:22px; padding:22px; color:#fff; margin-bottom:14px; }}
.badge {{ background:rgba(255,255,255,.25); border-radius:14px; padding:5px 14px; font-size:12px; font-weight:700; display:inline-block; }}
.strip {{ background:rgba(255,255,255,.22); border-radius:14px; padding:10px 14px; margin-top:12px; font-size:13px; }}
.brand {{ font-size:26px; font-weight:800; color:#1B2A33; }}
.brand small {{ display:block; font-size:12px; font-weight:500; color:#6B7C86; }}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# DATA: real (approximate) ward coordinates per corporation.
# pop65 / outdoor are manual demographic estimates (%), not live data.
# ----------------------------------------------------------------------
REGIONS = {
    "Chennai Corporation": {"center": (13.04, 80.24), "wards": [
        ("Anna Nagar", 13.0850, 80.2101, 14, 22), ("Royapuram", 13.1143, 80.2937, 11, 31),
        ("Madipakkam", 12.9580, 80.1980, 18, 19), ("T. Nagar", 13.0418, 80.2341, 16, 15),
        ("Perungudi", 12.9653, 80.2419, 9, 34), ("Kolathur", 13.1280, 80.2200, 12, 20)]},
    "Madurai Corporation": {"center": (9.93, 78.12), "wards": [
        ("Simmakkal", 9.9195, 78.1193, 13, 25), ("Anna Nagar", 9.9450, 78.1150, 10, 20),
        ("Tallakulam", 9.9300, 78.1250, 15, 18), ("Villapuram", 9.8950, 78.1350, 12, 28),
        ("K.K. Nagar", 9.9100, 78.0950, 11, 17), ("Thiruparankundram", 9.8650, 78.0700, 9, 33)]},
    "Coimbatore Corporation": {"center": (11.02, 76.96), "wards": [
        ("RS Puram", 11.0060, 76.9500, 17, 14), ("Gandhipuram", 11.0165, 76.9650, 10, 22),
        ("Peelamedu", 11.0290, 77.0050, 12, 26), ("Saibaba Colony", 11.0170, 76.9400, 15, 16),
        ("Ukkadam", 10.9930, 76.9560, 13, 29), ("Singanallur", 11.0010, 77.0300, 9, 31)]},
    "Tiruchirappalli Corporation": {"center": (10.79, 78.70), "wards": [
        ("Srirangam", 10.8624, 78.6930, 16, 20), ("Cantonment", 10.7960, 78.6890, 11, 24),
        ("Woraiyur", 10.8250, 78.6800, 13, 22), ("K.Abishekapuram", 10.7700, 78.6600, 9, 30),
        ("Golden Rock", 10.7850, 78.7350, 12, 27), ("Ariyamangalam", 10.8080, 78.7150, 10, 25)]},
    "Salem Corporation": {"center": (11.66, 78.15), "wards": [
        ("Hasthampatti", 11.6690, 78.1460, 15, 18), ("Suramangalam", 11.6600, 78.1250, 10, 26),
        ("Fairlands", 11.6720, 78.1550, 14, 16), ("Ammapet", 11.6850, 78.1650, 9, 32),
        ("Shevapet", 11.6620, 78.1550, 12, 24), ("Kondalampatti", 11.7050, 78.1350, 8, 29)]},
    "Tirunelveli Corporation": {"center": (8.71, 77.75), "wards": [
        ("Palayamkottai", 8.7185, 77.7370, 14, 19), ("Melapalayam", 8.7300, 77.6950, 10, 27),
        ("Vannarpettai", 8.7280, 77.7280, 13, 21), ("Krishnapuram", 8.7500, 77.6900, 9, 31),
        ("Thatchanallur", 8.6950, 77.7200, 11, 25), ("Munsif Court", 8.7130, 77.7400, 12, 20)]},
    "Vellore Corporation": {"center": (12.92, 79.13), "wards": [
        ("Katpadi", 12.9700, 79.1350, 13, 23), ("Sainathapuram", 12.9250, 79.1300, 10, 26),
        ("Gandhi Nagar", 12.9200, 79.1400, 15, 17), ("Thorapadi", 12.9350, 79.1150, 9, 30),
        ("Bagayam", 12.9500, 79.1550, 11, 24), ("Suthanthira Ponvizha Nagar", 12.9150, 79.1250, 12, 21)]},
    "Erode Corporation": {"center": (11.34, 77.72), "wards": [
        ("Surampatti", 11.3500, 77.7350, 14, 20), ("Veerappanchatram", 11.3200, 77.7050, 10, 28),
        ("Periyar Nagar", 11.3400, 77.7200, 12, 22), ("Sathy Road", 11.3550, 77.7450, 15, 16),
        ("Diesel Shed", 11.3300, 77.7500, 9, 31), ("Chithode", 11.4000, 77.7000, 11, 25)]},
}

# ----------------------------------------------------------------------
# THERMAL STRESS FORMULAS
# ----------------------------------------------------------------------
def wbgt(t, rh, sr, ws):
    """Simplified WBGT estimate from air temp, RH, solar radiation, wind speed."""
    return 0.567 * t + 0.393 * (rh / 100 * 6.105 * math.exp(17.27 * t / (237.7 + t))) + 3.94 + sr / 1000 * 1.5 - min(ws / 3.6, 4) * 0.3

def utci(t, rh, ws):
    return t + 0.33 * (rh / 100 * 6.105 * math.exp(17.27 * t / (237.7 + t))) - 0.7 * ws - 4

def heat_index(t, rh):
    tf = t * 9 / 5 + 32
    hi = (-42.379 + 2.049 * tf + 10.143 * rh - 0.225 * tf * rh - 0.00684 * tf * tf
          - 0.05482 * rh * rh + 0.00122 * tf * tf * rh + 0.00085 * tf * rh * rh - 0.00000199 * tf * tf * rh * rh)
    return (hi - 32) * 5 / 9

def risk_level(w):
    if w >= 32: return "Extreme", "#E5484D"
    if w >= 29: return "High", "#F26A2E"
    if w >= 26: return "Moderate", "#F5A524"
    return "Low", "#2F8F6B"

def hero_gradient(w):
    if w >= 32: return "#FF7A5C", "#E5484D"
    if w >= 29: return "#FF9A3D", "#F26A2E"
    if w >= 26: return "#FBC761", "#F5A524"
    return "#6FCF97", "#2F8F6B"

def mortality_risk(w, pop65, outdoor):
    base = max(0, w - 26) * 4
    return min(95, round(base + pop65 * 0.6 + outdoor * 0.3))

# ----------------------------------------------------------------------
# LIVE WEATHER (Open-Meteo, free, no key). Cached 10 min per zone.
# ----------------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner=False)
def fetch_weather(lat, lon):
    url = ("https://api.open-meteo.com/v1/forecast"
           f"?latitude={lat}&longitude={lon}"
           "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation"
           "&daily=temperature_2m_max&forecast_days=5&timezone=auto")
    r = requests.get(url, timeout=10).json()
    c = r["current"]
    return {
        "t": c["temperature_2m"], "rh": c["relative_humidity_2m"],
        "ws": c["wind_speed_10m"], "sr": c["shortwave_radiation"],
        "daily": r["daily"]["temperature_2m_max"], "offline": False,
    }

def get_zone_data(region_name):
    region = REGIONS[region_name]
    rows = []
    for name, lat, lon, pop65, outdoor in region["wards"]:
        try:
            wx = fetch_weather(lat, lon)
        except Exception:
            wx = {"t": 35, "rh": 65, "ws": 5, "sr": 850, "daily": [35] * 5, "offline": True}
        w = wbgt(wx["t"], wx["rh"], wx["sr"], wx["ws"])
        u = utci(wx["t"], wx["rh"], wx["ws"])
        hi = heat_index(wx["t"], wx["rh"])
        mort = mortality_risk(w, pop65, outdoor)
        level, color = risk_level(w)
        rows.append({
            "zone": f"Zone – {name}", "lat": lat, "lon": lon, "pop65": pop65, "outdoor": outdoor,
            "t": wx["t"], "rh": wx["rh"], "ws": wx["ws"], "sr": wx["sr"], "daily": wx["daily"],
            "wbgt": w, "utci": u, "hi": hi, "mortality": mort, "hospitalization": round(mort * 0.9),
            "level": level, "color": color, "offline": wx["offline"],
        })
    return pd.DataFrame(rows)

# ----------------------------------------------------------------------
# OPTIONAL REAL SMS / WHATSAPP VIA TWILIO
# ----------------------------------------------------------------------
def send_via_twilio(sid, token, from_sms, from_wa, to, body, channels):
    from twilio.rest import Client
    client = Client(sid, token)
    results = []
    if "SMS" in channels and to.get("sms"):
        m = client.messages.create(body=body, from_=from_sms, to=to["sms"])
        results.append(f"SMS sent ({m.sid})")
    if "WhatsApp" in channels and to.get("whatsapp"):
        m = client.messages.create(body=body, from_=f"whatsapp:{from_wa}", to=f"whatsapp:{to['whatsapp']}")
        results.append(f"WhatsApp sent ({m.sid})")
    return results

# ----------------------------------------------------------------------
# SESSION STATE
# ----------------------------------------------------------------------
if "log" not in st.session_state:
    st.session_state.log = []
if "resources" not in st.session_state:
    st.session_state.resources = {"cooling_open": 18, "cooling_total": 24, "ambulances": 9, "beds": 42, "staff": 31}
if "selected_zone" not in st.session_state:
    st.session_state.selected_zone = None

# ----------------------------------------------------------------------
# SIDEBAR: region + optional Twilio credentials
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🌡️ CalorPulse Command")
    st.caption("Officer console · Ministry of Earth Sciences")
    region_name = st.selectbox("Corporation / Region", list(REGIONS.keys()))
    st.divider()
    st.markdown("**Real SMS/WhatsApp (optional)**")
    st.caption("Leave blank to keep alert sending simulated (logged only).")
    twilio_sid = st.text_input("Twilio Account SID", type="password")
    twilio_token = st.text_input("Twilio Auth Token", type="password")
    twilio_sms_from = st.text_input("Twilio SMS number", placeholder="+1XXXXXXXXXX")
    twilio_wa_from = st.text_input("Twilio WhatsApp number", placeholder="+14155238886")
    demo_recipient_sms = st.text_input("Demo recipient phone (SMS)", placeholder="+91XXXXXXXXXX")
    demo_recipient_wa = st.text_input("Demo recipient phone (WhatsApp)", placeholder="+91XXXXXXXXXX")
    st.divider()
    if st.button("🔄 Refresh live weather now"):
        fetch_weather.clear()
        st.rerun()

df = get_zone_data(region_name)
if st.session_state.selected_zone not in df["zone"].values:
    st.session_state.selected_zone = df.sort_values("mortality", ascending=False).iloc[0]["zone"]

# ----------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------
st.markdown(f'<div class="brand">🌡️ CalorPulse Command<small>Extreme Heatwave Early Warning &amp; Human Thermal Stress Index · {region_name}</small></div>', unsafe_allow_html=True)
st.write("")

tab_overview, tab_zones, tab_alerts = st.tabs(["🏠 Overview", "📊 Zone Data", "🚨 Alerts"])

# ----------------------------------------------------------------------
# OVERVIEW TAB
# ----------------------------------------------------------------------
with tab_overview:
    z = df[df["zone"] == st.session_state.selected_zone].iloc[0]
    g1, g2 = hero_gradient(z["wbgt"])
    note = ("Emergency response window: act within 15 min" if z["level"] == "Extreme"
            else "Precautionary window: act within 1 hour" if z["level"] == "High"
            else "Routine monitoring, next check in 30 min")
    st.markdown(f"""
    <div class="hero" style="background:linear-gradient(135deg,{g1},{g2});">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div><div style="font-size:13px;opacity:.9;">Selected zone WBGT</div>
            <div style="font-size:48px;font-weight:800;">{z['wbgt']:.1f}°C</div></div>
            <div class="badge">{z['level']}</div>
        </div>
        <div style="font-size:14px;">{z['zone']} — {'offline estimate' if z['offline'] else 'live reading'}</div>
        <div class="strip">⏱ {note}</div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("UTCI °C", f"{z['utci']:.1f}")
    c2.metric("Heat Index °C", f"{z['hi']:.1f}")
    c3.metric("Mortality risk", f"{z['mortality']}%")
    c4.metric("Hospitalization ↑", f"+{z['hospitalization']}%")

    st.markdown("#### 🗺️ GIS Zone Map")
    center = REGIONS[region_name]["center"]
    fmap = folium.Map(location=center, zoom_start=12, tiles="CartoDB positron")
    folium.Marker(center, tooltip="HQ", icon=folium.Icon(color="blue", icon="home")).add_to(fmap)
    for _, row in df.iterrows():
        color = row["color"]
        folium.Circle([row["lat"], row["lon"]], radius=900, color=color, fill=True, fill_opacity=0.25, weight=1).add_to(fmap)
        folium.CircleMarker(
            [row["lat"], row["lon"]], radius=9, color="white", weight=2, fill=True,
            fill_color=color, fill_opacity=1,
            tooltip=f"{row['zone']} · {row['level']} · WBGT {row['wbgt']:.1f}°C · Mortality {row['mortality']}%",
        ).add_to(fmap)
    map_data = st_folium(fmap, height=420, width=None, returned_objects=["last_object_clicked_tooltip"])
    if map_data and map_data.get("last_object_clicked_tooltip"):
        clicked_zone = map_data["last_object_clicked_tooltip"].split(" · ")[0]
        if clicked_zone in df["zone"].values:
            st.session_state.selected_zone = clicked_zone
            st.rerun()
    st.caption("🟢 Low · 🟡 Moderate · 🟠 High · 🔴 Extreme · 🔵 HQ — click a marker to select that zone.")

    st.markdown("#### 🏗️ Resource Readiness")
    r = st.session_state.resources
    rc1, rc2, rc3, rc4 = st.columns(4)
    rc1.metric("Cooling centers open", f"{r['cooling_open']}/{r['cooling_total']}")
    rc2.metric("Ambulances on standby", r["ambulances"])
    rc3.metric("Heat-stroke beds free", r["beds"])
    rc4.metric("Field staff deployed", r["staff"])

# ----------------------------------------------------------------------
# ZONE DATA TAB
# ----------------------------------------------------------------------
with tab_zones:
    st.markdown("#### 📊 Zone Risk Ranking (live)")
    ranked = df.sort_values("mortality", ascending=False)
    for _, row in ranked.iterrows():
        cols = st.columns([0.5, 4, 1.2, 1])
        cols[0].markdown(f"<div style='width:14px;height:14px;border-radius:50%;background:{row['color']};margin-top:8px;'></div>", unsafe_allow_html=True)
        cols[1].markdown(f"**{row['zone']}**  \n<span style='color:#6B7C86;font-size:12px;'>WBGT {row['wbgt']:.1f}° · UTCI {row['utci']:.1f}° · {row['level']}{' · offline est.' if row['offline'] else ''}</span>", unsafe_allow_html=True)
        cols[2].markdown(f"<span style='color:{row['color']};font-weight:800;font-size:16px;'>{row['mortality']}%</span>", unsafe_allow_html=True)
        if cols[3].button("Select", key=f"sel_{row['zone']}"):
            st.session_state.selected_zone = row["zone"]
            st.rerun()

    st.divider()
    z = df[df["zone"] == st.session_state.selected_zone].iloc[0]
    st.markdown(f"#### 📈 5-Day Mortality Risk Forecast — {z['zone']}")
    fc = pd.DataFrame({
        "Day": [f"Day {i+1}" for i in range(len(z["daily"]))],
        "Mortality risk %": [mortality_risk(wbgt(tmax, z["rh"], z["sr"], z["ws"]), z["pop65"], z["outdoor"]) for tmax in z["daily"]],
    }).set_index("Day")
    st.bar_chart(fc, color=ORANGE2)

    st.markdown(f"#### 🧪 Live Weather Inputs — {z['zone']}")
    ic1, ic2, ic3 = st.columns(3)
    ic1.metric("Air temperature", f"{z['t']:.1f} °C")
    ic1.metric("Elderly population (est.)", f"{z['pop65']}%")
    ic2.metric("Relative humidity", f"{z['rh']:.0f}%")
    ic2.metric("Outdoor workers (est.)", f"{z['outdoor']}%")
    ic3.metric("Solar radiation", f"{z['sr']:.0f} W/m²")
    ic3.metric("Wind speed", f"{z['ws']:.1f} km/h")
    if z["offline"]:
        st.warning("Live weather fetch failed for this zone — showing offline fallback estimate.")

# ----------------------------------------------------------------------
# ALERTS TAB
# ----------------------------------------------------------------------
with tab_alerts:
    z = df[df["zone"] == st.session_state.selected_zone].iloc[0]
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(f"#### 📋 Automated Advisory — {z['zone']}")
        adv = ("Extreme risk: open all cooling centers, suspend outdoor labour 11 AM–4 PM, alert hospitals."
               if z["level"] == "Extreme" else
               "High risk: shift outdoor work hours, open key cooling centers, monitor elderly wards."
               if z["level"] == "High" else
               "Moderate risk: issue public advisory, keep cooling centers on standby."
               if z["level"] == "Moderate" else
               "Low risk: routine monitoring, no special action needed.")
        st.info(adv)

        st.checkbox("Open designated cooling centers", value=True, key="a1")
        st.checkbox("Shift outdoor labour hours (before 10 AM / after 5 PM)", value=True, key="a2")
        st.checkbox("Increase power grid capacity (AC/fan load)", key="a3")
        st.checkbox("Alert hospitals · reserve heat-stroke beds", key="a4")

        st.markdown("**Notify departments**")
        d_health = st.checkbox("Public Health department", value=True)
        d_power = st.checkbox("Power / Electricity board", value=True)
        d_labour = st.checkbox("Labour welfare department")
        d_disaster = st.checkbox("Disaster Management field staff", value=True)

        st.markdown("**Broadcast to residents via**")
        ch_sms = st.checkbox("SMS regional broadcast", value=True)
        ch_wa = st.checkbox("WhatsApp alert", value=True)
        ch_app = st.checkbox("Citizen app push (CalorPulse)", value=True)

        esc = st.selectbox("Escalation level", ["Level 1 – Advisory only", "Level 2 – Precautionary action", "Level 3 – Emergency response"], index=1)

        if st.button("📡 Trigger Heat Action Plan", type="primary", use_container_width=True):
            channels = [c for c, on in [("SMS", ch_sms), ("WhatsApp", ch_wa), ("App push", ch_app)] if on]
            depts = [d for d, on in [("Health", d_health), ("Power", d_power), ("Labour", d_labour), ("Disaster Mgmt", d_disaster)] if on]
            body = f"[{esc}] {z['zone']}: {z['level']} heat stress, WBGT {z['wbgt']:.1f}°C. {adv}"
            sent_note = "simulated (no Twilio credentials entered)"
            if twilio_sid and twilio_token and (twilio_sms_from or twilio_wa_from):
                try:
                    results = send_via_twilio(
                        twilio_sid, twilio_token, twilio_sms_from, twilio_wa_from,
                        {"sms": demo_recipient_sms, "whatsapp": demo_recipient_wa}, body, channels)
                    sent_note = "; ".join(results) if results else "no recipient number given"
                except Exception as e:
                    sent_note = f"Twilio error: {e}"
            st.session_state.log.insert(0, {
                "time": datetime.now().strftime("%H:%M:%S"), "zone": z["zone"],
                "channels": ", ".join(channels) or "-", "departments": ", ".join(depts) or "-",
                "escalation": esc, "delivery": sent_note,
            })
            st.session_state.resources["cooling_open"] = min(st.session_state.resources["cooling_total"], st.session_state.resources["cooling_open"] + 1)
            st.session_state.resources["staff"] += 2
            st.success(f"{esc} triggered for {z['zone']} · {sent_note}")

    with col_b:
        st.markdown("#### 🕓 Dispatch Log")
        if st.session_state.log:
            st.dataframe(pd.DataFrame(st.session_state.log), use_container_width=True, hide_index=True)
        else:
            st.caption("No alerts dispatched yet this session.")
