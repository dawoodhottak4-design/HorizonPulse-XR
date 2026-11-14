import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import pandas as pd
import numpy as np
import json
import random

# ==========================================
# 1. META HORIZON OS SPATIAL UI STYLING
# ==========================================
st.set_page_config(
    page_title="HorizonPulse XR | Meta Spatial Lifestyle & AI Net-Core",
    page_icon="♾️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Meta Horizon OS Deep Spatial Void & Signature Blue/Cyan Glow */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #002b5b 0%, #050a18 45%, #02040a 100%);
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Meta Quest / Horizon OS Frosted Spatial Panel */
    .horizon-panel {
        background: linear-gradient(145deg, rgba(16, 28, 54, 0.72), rgba(8, 15, 32, 0.85));
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 129, 251, 0.35);
        border-top: 1px solid rgba(0, 245, 212, 0.5);
        border-radius: 24px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 12px 40px rgba(0, 129, 251, 0.15), inset 0 0 20px rgba(0, 129, 251, 0.05);
    }

    /* Meta Infinity Pill Badge */
    .meta-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(90deg, rgba(0, 129, 251, 0.25), rgba(0, 245, 212, 0.2));
        border: 1px solid #0081FB;
        color: #7dd3fc;
        padding: 5px 14px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Agent Pills */
    .agent-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.4px;
        margin-bottom: 6px;
    }
    .tag-intent { background: rgba(0, 129, 251, 0.22); color: #60a5fa; border: 1px solid #0081FB; }
    .tag-telecom { background: rgba(0, 245, 212, 0.18); color: #2dd4bf; border: 1px solid #00f5d4; }
    .tag-lifestyle { background: rgba(192, 132, 252, 0.2); color: #e879f9; border: 1px solid #c084fc; }

    /* Custom Buttons matching Horizon OS */
    .stButton > button {
        border-radius: 999px !important;
        border: 1px solid rgba(0, 129, 251, 0.5) !important;
        background: linear-gradient(90deg, #0064e0, #0081FB) !important;
        color: white !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(0, 129, 251, 0.65) !important;
        transform: translateY(-1px);
    }

    h1, h2, h3 {
        background: linear-gradient(90deg, #ffffff, #38bdf8, #00f5d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. TELECOM TELEMETRY & SESSION STATE
# ==========================================
if "devices" not in st.session_state:
    st.session_state.devices = {
        "Fiber_ONT_Core":   {"ip": "192.168.1.1",  "ping": 3.8,  "jitter": 0.4, "rssi": -40, "qos": "Ultra-Low Latency", "pos": "0 1.65 -3.0"},
        "Quest_Spatial_UI": {"ip": "192.168.1.10", "ping": 9.4,  "jitter": 0.9, "rssi": -46, "qos": "XR Priority",       "pos": "-1.45 1.45 -2.4"},
        "Horizon_Cinema":   {"ip": "192.168.1.15", "ping": 16.2, "jitter": 1.8, "rssi": -54, "qos": "Standard",          "pos": "1.45 1.45 -2.4"},
        "Ambient_IoT_Mesh": {"ip": "192.168.1.22", "ping": 21.5, "jitter": 2.4, "rssi": -60, "qos": "Background",        "pos": "0 0.85 -2.1"}
    }

if "lifestyle_mode" not in st.session_state:
    st.session_state.lifestyle_mode = "Horizon Connected Flow"

if "ping_history" not in st.session_state:
    st.session_state.ping_history = pd.DataFrame(
        np.random.uniform(4, 18, size=(20, 4)),
        columns=list(st.session_state.devices.keys())
    )

if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []

def update_telemetry():
    new_row = {}
    for dev, stats in st.session_state.devices.items():
        fluctuation = random.uniform(-1.2, 1.6)
        current_ping = max(1.5, round(stats["ping"] + fluctuation, 1))
        st.session_state.devices[dev]["ping"] = current_ping
        st.session_state.devices[dev]["jitter"] = round(abs(fluctuation) * 0.5 + 0.2, 2)
        new_row[dev] = current_ping
    new_df = pd.DataFrame([new_row])
    st.session_state.ping_history = pd.concat([st.session_state.ping_history.iloc[1:], new_df], ignore_index=True)

# ==========================================
# 3. GROQ WHISPER + MULTI-AGENT CORE
# ==========================================
def transcribe_audio_groq(api_key, audio_bytes):
    client = Groq(api_key=api_key)
    return client.audio.transcriptions.create(
        file=("voice_command.wav", audio_bytes),
        model="whisper-large-v3-turbo",
        response_format="text"
    )

def run_multi_agent_pipeline(api_key, user_command):
    client = Groq(api_key=api_key)
    telemetry_snapshot = json.dumps(st.session_state.devices, indent=2)

    system_prompt = f"""
    You are the Multi-Agent Spatial Intelligence of 'HorizonPulse XR', built for Meta Horizon OS.
    Embody Meta's vision: bringing people closer together through seamless, zero-lag spatial lifestyle and intelligent connectivity.
    Coordinate 3 internal agents:
    1. [Presence Orchestrator]: Interprets human lifestyle & social/work intent.
    2. [Telecom Net-Guard]: Optical fiber & Wi-Fi 6E/7 RF engineer. Inspects live telemetry:
    {telemetry_snapshot}
    3. [Spatial Lifestyle Coach]: Shapes the room environment ('Deep Work Sanctuary', 'Social Spatial Cinema', 'Zen Wellness Space', or 'Horizon Connected Flow').

    Respond ONLY in valid JSON with these keys:
    {{
        "orchestrator_thought": "Intent & social/lifestyle context",
        "net_guard_action": "RF/Optical/QoS action taken",
        "lifestyle_mode": "Updated spatial mode name",
        "heal_network": true or false,
        "priority_device": "Exact device key to prioritize or 'None'",
        "spatial_voice_reply": "Warm, concise response (max 2 sentences) for Meta Quest HUD."
    }}
    """

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_command}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    result = json.loads(completion.choices.message.content)
    st.session_state.lifestyle_mode = result.get("lifestyle_mode", st.session_state.lifestyle_mode)

    if result.get("heal_network", False):
        for dev in st.session_state.devices:
            st.session_state.devices[dev]["ping"] = round(random.uniform(3.5, 11.0), 1)
            st.session_state.devices[dev]["jitter"] = round(random.uniform(0.2, 0.9), 2)
            st.session_state.devices[dev]["rssi"] = random.randint(-48, -39)

    prio = result.get("priority_device", "None")
    if prio in st.session_state.devices:
        for dev in st.session_state.devices:
            st.session_state.devices[dev]["qos"] = "XR Boosted" if dev == prio else "Eco-Throttled"
            if dev == prio:
                st.session_state.devices[dev]["ping"] = round(random.uniform(3.0, 6.5), 1)

    st.session_state.agent_logs.insert(0, {"command": user_command, "result": result})
    return result

# ==========================================
# 4. META HORIZON OS 3D SPATIAL ENVIRONMENT
# ==========================================
def render_horizon_spatial_scene(devices, mode):
    orbs_html = ""
    for name, data in devices.items():
        ping = data["ping"]
        if ping 
            <!-- Core Spatial Node -->
            <a-sphere radius="0.19" color="{color}"
                material="emissive: {color}; emissiveIntensity: 0.75; opacity: 0.9; transparent: true"
                animation="property: scale; to: 1.14 1.14 1.14; dir: alternate; dur: {dur}; loop: true">
            </a-sphere>
            <!-- Gyroscopic Horizon Ring -->
            <a-torus color="{ring_color}" radius="0.28" radius-tubular="0.008" rotation="75 0 0"
                animation="property: rotation; to: 75 360 0; dur: 5000; loop: true; easing: linear">
            </a-torus>
            <!-- Floating Spatial Label -->
            <a-plane position="0 0.42 0" width="1.15" height="0.32" color="#081226" opacity="0.82"></a-plane>
            <a-text value="{label}" align="center" position="0 0.42 0.01" scale="0.55 0.55 0.55" color="#e0f2fe"></a-text>
        
        """

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://aframe.io"></script>
    </head>
    <body style="margin: 0; overflow: hidden; border-radius: 20px; border: 1px solid rgba(0,129,251,0.4);">
        <a-scene embedded style="height: 410px; width: 100%;" webxr="optionalFeatures: hand-tracking, local-floor;">
            <a-sky color="#030816"></a-sky>
            
            <!-- Horizon Spatial Floor Grid -->
