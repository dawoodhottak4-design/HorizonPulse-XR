import streamlit as st
import math

LT = chr(60)
GT = chr(62)

def tag(name, attrs="", content=""):
    sp = " " if attrs else ""
    return f"{LT}{name}{sp}{attrs}{GT}{content}{LT}/{name}{GT}"

def get_node_visuals(ping_val):
    p_int = int(ping_val)
    if p_int in range(0, 31):
        return "#0081FB", "#00f5d4", "2.4s", "🔵"
    elif p_int in range(31, 91):
        return "#f59e0b", "#fde047", "1.0s", "🟡"
    else:
        return "#ff0055", "#ff758f", "0.35s", "🔴"

def inject_horizon_css():
    css = ".stApp { background: radial-gradient(circle at 15% 15%, #002b5b 0%, #050a18 45%, #02040a 100%); color: #f1f5f9; }"
    css += ".horizon-panel { background: rgba(12, 22, 44, 0.88); border: 1px solid #0081FB; border-top: 1px solid #00f5d4; border-radius: 20px; padding: 18px; margin-bottom: 14px; box-shadow: 0 8px 32px rgba(0, 129, 251, 0.25); }"
    css += ".meta-pill { display: inline-block; background: linear-gradient(90deg, rgba(0, 129, 251, 0.35), rgba(0, 245, 212, 0.25)); border: 1px solid #0081FB; color: #7dd3fc; padding: 5px 14px; border-radius: 999px; font-size: 0.8rem; font-weight: 600; }"
    css += ".agent-tag { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 700; margin-bottom: 5px; background: rgba(0, 245, 212, 0.2); color: #2dd4bf; border: 1px solid #00f5d4; }"
    css += "h1, h2, h3 { color: #38bdf8 !important; }"
    css += "div.stButton button { background: linear-gradient(90deg, #0064e0, #0081FB) !important; color: #ffffff !important; border: 1px solid #00f5d4 !important; border-radius: 999px !important; font-weight: 700 !important; }"
    css += "div[data-testid='stMetricValue'] { color: #ffffff !important; font-weight: 700 !important; }"
    css += "div[data-testid='stMetricLabel'] { color: #93c5fd !important; }"
    css += "@keyframes pulseOrb { 0%, 100% { transform: scale(1); opacity: 0.95; } 50% { transform: scale(1.12); opacity: 1; } }"
    css += "@keyframes dashFlow { to { stroke-dashoffset: -40; } }"
    css += ".opt-beam { stroke-dasharray: 8 6; animation: dashFlow 1.2s linear infinite; }"
    st.markdown(tag("style", content=css), unsafe_allow_html=True)

def render_horizon_spatial_scene(devices, mode):
    coords_map = {
        "Fiber_ONT_Core":   (350, 95),
        "Quest_Spatial_UI": (145, 225),
        "Horizon_Cinema":   (555, 225),
        "Ambient_IoT_Mesh": (350, 305)
    }

    svg_parts = []
    # Defs for 3D radial gradients & glow
    g_bg = tag("radialGradient", 'id="spaceBg" cx="50%" cy="45%" r="65%"',
               tag("stop", 'offset="0%" stop-color="#0b2859"') +
               tag("stop", 'offset="100%" stop-color="#020612"'))
    svg_parts.append(tag("defs", content=g_bg))

    # Background + 3D Perspective Floor Grid
    svg_parts.append(tag("rect", 'width="700" height="390" rx="18" fill="url(#spaceBg)" stroke="#0081FB" stroke-width="1.5"'))
    svg_parts.append(tag("ellipse", 'cx="350" cy="275" rx="290" ry="88" fill="none" stroke="rgba(0,129,251,0.35)" stroke-width="1.5"'))
    svg_parts.append(tag("ellipse", 'cx="350" cy="275" rx="195" ry="56" fill="none" stroke="rgba(0,245,212,0.35)" stroke-width="1.2" stroke-dasharray="6 4"'))
    svg_parts.append(tag("line", 'x1="60" y1="275" x2="640" y2="275" stroke="rgba(0,129,251,0.22)" stroke-width="1"'))
    svg_parts.append(tag("line", 'x1="350" y1="185" x2="350" y2="365" stroke="rgba(0,129,251,0.22)" stroke-width="1"'))

    # Top Spatial HUD Pill inside 3D Room
    svg_parts.append(tag("rect", 'x="18" y="16" width="330" height="28" rx="14" fill="rgba(0,129,251,0.28)" stroke="#0081FB" stroke-width="1"'))
    svg_parts.append(tag("text", 'x="183" y="34" fill="#e0f2fe" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle"', f"♾️ {mode.upper()} | SPATIAL MESH"))

    # Draw Optical Fiber Light Beams from Fiber_ONT_Core to other nodes
    cx0, cy0 = coords_map["Fiber_ONT_Core"]
    for name, data in devices.items():
        if name != "Fiber_ONT_Core" and name in coords_map:
            tx, ty = coords_map[name]
            color, _, _, _ = get_node_visuals(float(data["ping"]))
            svg_parts.append(tag("line", f'x1="{cx0}" y1="{cy0}" x2="{tx}" y2="{ty}" stroke="{color}" stroke-width="3" opacity="0.35"'))
            svg_parts.append(tag("line", f'x1="{cx0}" y1="{cy0}" x2="{tx}" y2="{ty}" stroke="#00f5d4" stroke-width="2" class="opt-beam"'))

    # Draw 3D Glowing Device Orbs
    for idx, (name, data) in enumerate(devices.items()):
        ping = float(data["ping"])
        color, ring_color, dur, _ = get_node_visuals(ping)
        nx, ny = coords_map.get(name, (350, 200))
        grad_id = f"orbGrad_{idx}"

        orb_grad = tag("radialGradient", f'id="{grad_id}" cx="35%" cy="30%" r="70%"',
                       tag("stop", 'offset="0%" stop-color="#ffffff"') +
                       tag("stop", f'offset="35%" stop-color="{color}"') +
                       tag("stop", 'offset="100%" stop-color="#030816"'))
        svg_parts.append(tag("defs", content=orb_grad))

        # Outer Halo + Gyroscopic Ring + 3D Sphere
        svg_parts.append(tag("circle", f'cx="{nx}" cy="{ny}" r="42" fill="{color}" opacity="0.18"'))
        svg_parts.append(tag("ellipse", f'cx="{nx}" cy="{ny}" rx="38" ry="13" fill="none" stroke="{ring_color}" stroke-width="1.8" transform="rotate(-14 {nx} {ny})"'))
        svg_parts.append(tag("circle", f'cx="{nx}" cy="{ny}" r="22" fill="url(#{grad_id})" stroke="{ring_color}" stroke-width="1.5"'))

        # Floating Glass Label Badge above Orb
        lbl_y = ny - 58
        svg_parts.append(tag("rect", f'x="{nx - 76}" y="{lbl_y}" width="152" height="36" rx="9" fill="rgba(5,14,32,0.9)" stroke="{color}" stroke-width="1.3"'))
        svg_parts.append(tag("text", f'x="{nx}" y="{lbl_y + 15}" fill="#ffffff" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle"', name.replace("_", " ")))
        svg_parts.append(tag("text", f'x="{nx}" y="{lbl_y + 29}" fill="{ring_color}" font-family="monospace" font-size="10.5" font-weight="bold" text-anchor="middle"', f"{ping} ms | {data['qos']}"))

    # Bottom Right Meta Quest XR Ready Badge
    svg_parts.append(tag("rect", 'x="485" y="346" width="195" height="30" rx="15" fill="rgba(0,129,251,0.35)" stroke="#00f5d4" stroke-width="1.2"'))
    svg_parts.append(tag("text", 'x="582" y="365" fill="#ffffff" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle"', "🥽 META HORIZON XR READY"))

    svg_full = tag("svg", 'viewBox="0 0 700 390" style="width:100%;height:auto;border-radius:18px;box-shadow:0 10px 35px rgba(0,129,251,0.28);"', "".join(svg_parts))
    st.markdown(svg_full, unsafe_allow_html=True)
