import streamlit as st
import streamlit.components.v1 as components

LT = chr(60)
GT = chr(62)

def tag(name, attrs="", content=""):
    sp = " " if attrs else ""
    return f"{LT}{name}{sp}{attrs}{GT}{content}{LT}/{name}{GT}"

def get_node_visuals(ping_val):
    p_int = int(ping_val)
    if p_int in range(0, 31):
        return "#0081FB", "#00f5d4", "2400", "🔵"
    elif p_int in range(31, 91):
        return "#f59e0b", "#fde047", "900", "🟡"
    else:
        return "#ff0055", "#ff758f", "300", "🔴"

def inject_horizon_css():
    css = ".stApp { background: radial-gradient(circle at 15% 15%, #002b5b 0%, #050a18 45%, #02040a 100%); color: #f1f5f9; }"
    css += ".horizon-panel { background: rgba(12, 22, 44, 0.82); border: 1px solid #0081FB; border-radius: 20px; padding: 18px; margin-bottom: 14px; }"
    css += ".meta-pill { display: inline-block; background: rgba(0, 129, 251, 0.25); border: 1px solid #0081FB; color: #7dd3fc; padding: 4px 12px; border-radius: 999px; font-size: 0.8rem; font-weight: 600; }"
    css += ".agent-tag { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 700; margin-bottom: 5px; background: rgba(0, 245, 212, 0.18); color: #2dd4bf; border: 1px solid #00f5d4; }"
    css += "h1, h2, h3 { color: #38bdf8 !important; }"
    st.markdown(tag("style", content=css), unsafe_allow_html=True)

def render_horizon_spatial_scene(devices, mode):
    parts = []
    parts.append(tag("a-sky", 'color="#030816"'))
    parts.append(tag("a-circle", 'position="0 0 -2.5" rotation="-90 0 0" radius="4.5" color="#071329"'))
    parts.append(tag("a-ring", 'position="0 0.01 -2.5" rotation="-90 0 0" radius-inner="2.8" radius-outer="2.83" color="#0081FB"'))
    parts.append(tag("a-ring", 'position="0 0.01 -2.5" rotation="-90 0 0" radius-inner="4.2" radius-outer="4.23" color="#00f5d4"'))
    parts.append(tag("a-text", f'value="HORIZON PULSE XR | {mode.upper()}" position="0 2.35 -2.95" align="center" color="#00f5d4" width="4.2"'))
    parts.append(tag("a-entity", 'line="start: 0 1.65 -3.0; end: -1.45 1.45 -2.4; color: #0081FB"'))
    parts.append(tag("a-entity", 'line="start: 0 1.65 -3.0; end: 1.45 1.45 -2.4; color: #0081FB"'))
    parts.append(tag("a-entity", 'line="start: 0 1.65 -3.0; end: 0 0.85 -2.1; color: #00f5d4"'))

    for name, data in devices.items():
        ping = float(data["ping"])
        color, ring_color, dur, _ = get_node_visuals(ping)
        pos = data["pos"]
        label = f"{name.replace('_', ' ')} ({ping} ms)"
        s = tag("a-sphere", f'radius="0.19" color="{color}" animation="property: scale; to: 1.15 1.15 1.15; dir: alternate; dur: {dur}; loop: true"')
        t = tag("a-torus", f'color="{ring_color}" radius="0.28" radius-tubular="0.008" rotation="75 0 0" animation="property: rotation; to: 75 360 0; dur: 5000; loop: true"')
        tx = tag("a-text", f'value="{label}" align="center" position="0 0.42 0" scale="0.6 0.6 0.6" color="#ffffff"')
        parts.append(tag("a-entity", f'position="{pos}"', s + t + tx))

    cam = tag("a-camera", 'look-controls wasd-controls', tag("a-cursor", 'color="#00f5d4"'))
    lh = tag("a-entity", 'hand-tracking-controls="hand: left; modelColor: #0081FB"')
    rh = tag("a-entity", 'hand-tracking-controls="hand: right; modelColor: #00f5d4"')
    parts.append(tag("a-entity", 'position="0 1.6 0"', cam + lh + rh))

    scr = tag("script", 'src="https://aframe.io"')
    scn = tag("a-scene", 'embedded style="height: 400px; width: 100%;" webxr="optionalFeatures: hand-tracking, local-floor;"', "".join(parts))
    doc = f"{LT}!DOCTYPE html{GT}" + tag("html", content=tag("head", content=scr) + tag("body", 'style="margin:0;overflow:hidden;"', scn))
    components.html(doc, height=405)
