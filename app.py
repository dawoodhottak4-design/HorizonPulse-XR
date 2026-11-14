import streamlit as st
from groq import Groq
import pandas as pd
import numpy as np
import json
import random
from ui_scene import tag, get_node_visuals, inject_horizon_css, render_horizon_spatial_scene

st.set_page_config(page_title="HorizonPulse XR", page_icon="♾️", layout="wide")
inject_horizon_css()

if "devices" not in st.session_state:
    st.session_state.devices = {
        "Fiber_ONT_Core":   {"ip": "192.168.1.1",  "ping": 3.8,  "rssi": -40, "qos": "Ultra-Low Latency", "pos": "0 1.65 -3.0"},
        "Quest_Spatial_UI": {"ip": "192.168.1.10", "ping": 9.4,  "rssi": -46, "qos": "XR Priority",       "pos": "-1.45 1.45 -2.4"},
        "Horizon_Cinema":   {"ip": "192.168.1.15", "ping": 16.2, "rssi": -54, "qos": "Standard",          "pos": "1.45 1.45 -2.4"},
        "Ambient_IoT_Mesh": {"ip": "192.168.1.22", "ping": 21.5, "rssi": -60, "qos": "Background",        "pos": "0 0.85 -2.1"}
    }

if "lifestyle_mode" not in st.session_state:
    st.session_state.lifestyle_mode = "Horizon Connected Flow"

if "ping_history" not in st.session_state:
    st.session_state.ping_history = pd.DataFrame(np.random.uniform(4, 18, size=(20, 4)), columns=list(st.session_state.devices.keys()))

if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []

def update_telemetry():
    row = {}
    for dev, stats in st.session_state.devices.items():
        val = max(1.5, round(stats["ping"] + random.uniform(-1.2, 1.5), 1))
        st.session_state.devices[dev]["ping"] = val
        row[dev] = val
    st.session_state.ping_history = pd.concat([st.session_state.ping_history.iloc[1:], pd.DataFrame([row])], ignore_index=True)

def run_agents(api_key, cmd):
    client = Groq(api_key=api_key)
    snap = json.dumps(st.session_state.devices)
    sys_msg = f"You are HorizonPulse XR Multi-Agent AI for Meta Horizon OS. Telemetry: {snap}. Return ONLY JSON with keys: orchestrator_thought, net_guard_action, lifestyle_mode, heal_network (bool), priority_device, spatial_voice_reply."
    res = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": cmd}],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    data = json.loads(res.choices.message.content)
    st.session_state.lifestyle_mode = data.get("lifestyle_mode", st.session_state.lifestyle_mode)
    if data.get("heal_network", False):
        for d in st.session_state.devices:
            st.session_state.devices[d]["ping"] = round(random.uniform(3.5, 11.0), 1)
            st.session_state.devices[d]["rssi"] = random.randint(-48, -39)
    st.session_state.agent_logs.insert(0, {"command": cmd, "result": data})

with st.sidebar:
    st.markdown(tag("div", 'class="meta-pill"', "♾️ META HORIZON OS EDITION"), unsafe_allow_html=True)
    st.title("HorizonPulse XR")
    if "GROQ_API_KEY" in st.secrets:
        groq_key = st.secrets["GROQ_API_KEY"]
        st.success("🔐 Groq Key Loaded via Secrets")
    else:
        groq_key = st.text_input("🔑 Groq API Key", type="password")
    st.caption("Model: `openai/gpt-oss-120b` + `whisper-large-v3-turbo`")
    st.divider()
    if st.button("⚡ Simulate Optical Lag", use_container_width=True):
        st.session_state.devices["Quest_Spatial_UI"]["ping"] = 192.0
        st.session_state.devices["Horizon_Cinema"]["ping"] = 235.0
        st.toast("Latency Spike Injected!", icon="🚨")
    if st.button("🔄 Sync Live Ping", use_container_width=True):
        update_telemetry()

st.markdown(tag("div", 'class="meta-pill"', "♾️ META PRESENCE PLATFORM & HORIZON OS"), unsafe_allow_html=True)
st.title(f"HorizonPulse XR — {st.session_state.lifestyle_mode}")
update_telemetry()

col1, col2 = st.columns([1.4, 1])
with col1:
    st.subheader("🥽 3D Spatial Room & Optical Mesh (WebXR)")
    render_horizon_spatial_scene(st.session_state.devices, st.session_state.lifestyle_mode)
    m_cols = st.columns(4)
    for i, (dev, st_data) in enumerate(st.session_state.devices.items()):
        p = float(st_data["ping"])
        _, _, _, ic = get_node_visuals(p)
        m_cols[i].metric(f"{ic} {dev.replace('_', ' ')}", f"{p} ms", f"{st_data['rssi']} dBm")
    st.line_chart(st.session_state.ping_history, height=180)

with col2:
    st.subheader("🎙️ Presence Voice & AI Command")
    audio = st.audio_input("Speak via Groq Whisper")
    txt = st.text_input("Or type command:", placeholder="e.g., Fix Wi-Fi lag and set Deep Work mode")
    prompt = None
    if audio and groq_key:
        client = Groq(api_key=groq_key)
        prompt = client.audio.transcriptions.create(file=("cmd.wav", audio.getvalue()), model="whisper-large-v3-turbo", response_format="text")
        st.success(f"🗣️ {prompt}")
    if st.button("♾️ Activate Horizon Agents", use_container_width=True) and txt:
        prompt = txt
    if prompt and groq_key:
        with st.spinner("🧠 Agents running on openai/gpt-oss-120b..."):
            run_agents(groq_key, prompt)
            st.rerun()

    st.subheader("🧠 Multi-Agent Reasoning Logs")
    for item in st.session_state.agent_logs[:3]:
        r = item["result"]
        body = tag("div", content=f"<b>Command:</b> {item['command']}") + tag("span", 'class="agent-tag"', "♾️ Orchestrator & Net-Guard") + tag("div", content=f"{r.get('orchestrator_thought', '')} | {r.get('net_guard_action', '')}") + tag("div", 'style="color:#00f5d4;margin-top:6px;"', f"💬 {r.get('spatial_voice_reply', '')}")
        st.markdown(tag("div", 'class="horizon-panel"', body), unsafe_allow_html=True)
