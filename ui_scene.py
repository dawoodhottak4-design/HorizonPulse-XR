import streamlit as st
import streamlit.components.v1 as components
import json

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
    css += ".horizon-panel { background: rgba(12, 22, 44, 0.88); border: 1px solid #0081FB; border-top: 1px solid #00f5d4; border-radius: 20px; padding: 18px; margin-bottom: 14px; box-shadow: 0 8px 32px rgba(0, 129, 251, 0.25); }"
    css += ".meta-pill { display: inline-block; background: linear-gradient(90deg, rgba(0, 129, 251, 0.35), rgba(0, 245, 212, 0.25)); border: 1px solid #0081FB; color: #7dd3fc; padding: 5px 14px; border-radius: 999px; font-size: 0.8rem; font-weight: 600; }"
    css += ".agent-tag { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 700; margin-bottom: 5px; background: rgba(0, 245, 212, 0.2); color: #2dd4bf; border: 1px solid #00f5d4; }"
    css += "h1, h2, h3 { color: #38bdf8 !important; }"
    css += "div.stButton button { background: linear-gradient(90deg, #0064e0, #0081FB) !important; color: #ffffff !important; border: 1px solid #00f5d4 !important; border-radius: 999px !important; font-weight: 700 !important; }"
    st.markdown(tag("style", content=css), unsafe_allow_html=True)

def render_horizon_spatial_scene(devices, mode):
    nodes_payload = []
    for idx, (name, data) in enumerate(devices.items()):
        ping = float(data["ping"])
        color, ring_color, _, _ = get_node_visuals(ping)
        cx, cy, cz = (float(v) for v in data["pos"].split())
        nodes_payload.append({
            "name": name.replace("_", " "),
            "ping": ping,
            "qos": data["qos"],
            "color": color,
            "ring": ring_color,
            "x": cx,
            "y": cy,
            "z": cz + 2.5
        })

    nodes_json = json.dumps(nodes_payload)
    mode_upper = mode.upper()

    js_code = f"""
    const nodes = {nodes_json};
    const canvas = document.getElementById('xrCanvas');
    const ctx = canvas.getContext('2d');

    function resize() {{
        canvas.width = canvas.parentElement.clientWidth || 700;
        canvas.height = 410;
    }}
    resize();
    window.addEventListener('resize', resize);

    let rotY = 0;
    let isDragging = false;
    let lastX = 0;

    canvas.addEventListener('mousedown', (e) => {{ isDragging = true; lastX = e.clientX; }});
    window.addEventListener('mouseup', () => {{ isDragging = false; }});
    window.addEventListener('mousemove', (e) => {{
        if (isDragging) {{
            rotY += (e.clientX - lastX) * 0.008;
            lastX = e.clientX;
        }}
    }});

    function project3D(x, y, z) {{
        const cosR = Math.cos(rotY);
        const sinR = Math.sin(rotY);
        const rx = x * cosR - z * sinR;
        const rz = x * sinR + z * cosR;
        const fov = 420;
        const dist = 4.2 + rz;
        const scale = fov / Math.max(1.2, dist);
        const sx = canvas.width / 2 + rx * scale;
        const sy = canvas.height / 2 + (1.35 - y) * scale;
        return {{ x: sx, y: sy, scale: scale, z: rz }};
    }}

    let t = 0;
    function draw() {{
        t += 0.025;
        if (!isDragging) rotY += 0.003;

        const w = canvas.width;
        const h = canvas.height;
        ctx.clearRect(0, 0, w, h);

        // Deep Space Gradient Background
        const bgGrad = ctx.createRadialGradient(w/2, h/2, 20, w/2, h/2, w*0.7);
        bgGrad.addColorStop(0, '#091b3a');
        bgGrad.addColorStop(1, '#020612');
        ctx.fillStyle = bgGrad;
        ctx.fillRect(0, 0, w, h);

        // Draw 3D Spatial Horizon Floor Grid
        ctx.strokeStyle = 'rgba(0, 129, 251, 0.22)';
        ctx.lineWidth = 1;
        for (let gx = -3; gx !== 4; gx++) {{
            const p1 = project3D(gx * 0.9, 0.2, -2.5);
            const p2 = project3D(gx * 0.9, 0.2, 2.5);
            ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y); ctx.stroke();
        }}
        for (let gz = -3; gz !== 4; gz++) {{
            const p1 = project3D(-2.7, 0.2, gz * 0.8);
            const p2 = project3D(2.7, 0.2, gz * 0.8);
            ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y); ctx.stroke();
        }}

        // Horizon Floor Concentric Ring
        ctx.strokeStyle = 'rgba(0, 245, 212, 0.35)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        for (let a = 0; a !== 65; a++) {{
            const ang = (a / 64) * Math.PI * 2;
            const pt = project3D(Math.cos(ang) * 2.1, 0.22, Math.sin(ang) * 2.1);
            if (a === 0) ctx.moveTo(pt.x, pt.y);
            else ctx.lineTo(pt.x, pt.y);
        }}
        ctx.stroke();

        // Project all nodes
        const projected = nodes.map((nd, idx) => {{
            const bobY = nd.y + Math.sin(t * 1.6 + idx) * 0.08;
            const p = project3D(nd.x, bobY, nd.z);
            return {{ ...nd, px: p.x, py: p.y, sc: p.scale, pz: p.z, idx: idx }};
        }});

        const core = projected;

        // Draw Optical Fiber Light Beams & Moving Data Packets
        projected.forEach((nd, i) => {{
            if (i !== 0) {{
                ctx.strokeStyle = nd.color;
                ctx.globalAlpha = 0.55;
                ctx.lineWidth = 2.5;
                ctx.beginPath();
                ctx.moveTo(core.px, core.py);
                ctx.lineTo(nd.px, nd.py);
                ctx.stroke();
                ctx.globalAlpha = 1.0;

                // Animated Optical Pulse Packet
                const prog = (t * 0.5 + i * 0.33) % 1;
                const lx = core.px + (nd.px - core.px) * prog;
                const ly = core.py + (nd.py - core.py) * prog;
                ctx.fillStyle = '#00f5d4';
                ctx.beginPath();
                ctx.arc(lx, ly, 4.5, 0, Math.PI * 2);
                ctx.fill();
            }}
        }});

        // Sort back-to-front for proper 3D depth
        const sorted = [...projected].sort((a, b) => b.pz - a.pz);

        sorted.forEach((nd) => {{
            const baseR = Math.max(18, nd.sc * 0.24);
            const pulseFreq = Math.max(2.0, nd.ping / 18.0);
            const r = baseR + Math.sin(t * pulseFreq) * 3.5;

            // Outer Glow Halo
            const halo = ctx.createRadialGradient(nd.px, nd.py, r * 0.2, nd.px, nd.py, r * 2.3);
            halo.addColorStop(0, nd.color);
            halo.addColorStop(1, 'rgba(0,0,0,0)');
            ctx.fillStyle = halo;
            ctx.beginPath();
            ctx.arc(nd.px, nd.py, r * 2.3, 0, Math.PI * 2);
            ctx.fill();

            // Gyroscopic Orbit Ring
            ctx.strokeStyle = nd.ring;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.ellipse(nd.px, nd.py, r * 1.55, r * 0.55, Math.sin(t + nd.idx) * 0.4, 0, Math.PI * 2);
            ctx.stroke();

            // 3D Shaded Sphere Core
            const sph = ctx.createRadialGradient(nd.px - r*0.3, nd.py - r*0.3, r*0.1, nd.px, nd.py, r);
            sph.addColorStop(0, '#ffffff');
            sph.addColorStop(0.35, nd.color);
            sph.addColorStop(1, '#040b1a');
            ctx.fillStyle = sph;
            ctx.beginPath();
            ctx.arc(nd.px, nd.py, r, 0, Math.PI * 2);
            ctx.fill();

            // Floating Spatial HUD Tag
            const boxW = 148;
            const boxH = 42;
            const bx = nd.px - boxW / 2;
            const by = nd.py - r - 52;

            ctx.fillStyle = 'rgba(6, 16, 36, 0.88)';
            ctx.strokeStyle = nd.color;
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.roundRect(bx, by, boxW, boxH, 10);
            ctx.fill();
            ctx.stroke();

            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 11px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(nd.name, nd.px, by + 16);

            ctx.fillStyle = nd.ring;
            ctx.font = 'bold 11px monospace';
            ctx.fillText(nd.ping + ' ms | ' + nd.qos, nd.px, by + 33);
        }});

        requestAnimationFrame(draw);
    }}
    draw();

    const vrBtn = document.getElementById('vrBtn');
    vrBtn.addEventListener('click', async () => {{
        if (navigator.xr) {{
            try {{
                await navigator.xr.requestSession('immersive-vr', {{ optionalFeatures: ['local-floor', 'hand-tracking'] }});
                alert('Meta Quest WebXR Session Connected!');
            }} catch (err) {{
                alert('Meta Immersive Web Emulator Ready! Select Meta Quest 3 in your Chrome Extension panel.');
            }}
        }} else {{
            alert('Open in Chrome with Meta Immersive Web Emulator extension enabled.');
        }}
    }});
    """

    hud_overlay = tag("div", 'style="position:absolute;top:12px;left:14px;background:rgba(0,129,251,0.35);border:1px solid #0081FB;color:#e0f2fe;padding:5px 12px;border-radius:999px;font-family:sans-serif;font-size:12px;font-weight:bold;z-index:10;"', f"♾️ {mode_upper} | DRAG TO ROTATE 360°")
    vr_button = tag("button", 'id="vrBtn" style="position:absolute;bottom:14px;right:14px;background:linear-gradient(90deg,#0064e0,#0081FB);border:1px solid #00f5d4;color:#ffffff;padding:8px 16px;border-radius:999px;font-family:sans-serif;font-size:12px;font-weight:bold;cursor:pointer;box-shadow:0 0 15px rgba(0,129,251,0.7);z-index:10;"', "🥽 ENTER META QUEST VR")
    canvas_el = tag("canvas", 'id="xrCanvas" style="width:100%;height:410px;display:block;cursor:grab;"')
