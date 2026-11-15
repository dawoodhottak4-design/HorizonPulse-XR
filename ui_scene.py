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
    css += "div.stButton > button { background: linear-gradient(90deg, #0064e0, #0081FB) !important; color: #ffffff !important; border: 1px solid #00f5d4 !important; border-radius: 999px !important; font-weight: 700 !important; }"
    st.markdown(tag("style", content=css), unsafe_allow_html=True)

def render_horizon_spatial_scene(devices, mode):
    nodes_payload = []
    core_node = {"x": 0.0, "y": 1.65, "z": -3.0}

    for idx, (name, data) in enumerate(devices.items()):
        ping = float(data["ping"])
        color, ring_color, _, _ = get_node_visuals(ping)
        cx, cy, cz = (float(v) for v in data["pos"].split())
        if idx == 0:
            core_node = {"x": cx, "y": cy, "z": cz}
        nodes_payload.append({
            "name": name.replace("_", " "),
            "ping": ping,
            "qos": data["qos"],
            "color": color,
            "ring": ring_color,
            "x": cx,
            "y": cy,
            "z": cz
        })

    nodes_json = json.dumps(nodes_payload)
    core_json = json.dumps(core_node)
    mode_upper = mode.upper()

    js_code = f"""
    const nodesData = {nodes_json};
    const coreData = {core_json};
    const canvas = document.getElementById('xrCanvas');
    const renderer = new THREE.WebGLRenderer({{ canvas: canvas, antialias: true, alpha: true }});
    renderer.setSize(window.innerWidth, 410);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.xr.enabled = true;

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x030816, 0.06);

    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / 410, 0.1, 100);
    camera.position.set(0, 1.8, 0.8);
    camera.lookAt(0, 1.35, -2.5);

    const ambientLight = new THREE.AmbientLight(0xffffff, 1.1);
    scene.add(ambientLight);
    const pointLight = new THREE.PointLight(0x0081FB, 3.0, 20);
    pointLight.position.set(0, 3, -2);
    scene.add(pointLight);

    const gridHelper = new THREE.GridHelper(10, 24, 0x0081FB, 0x0b1d3a);
    gridHelper.position.set(0, 0, -2.5);
    scene.add(gridHelper);

    const ringGeo = new THREE.RingGeometry(2.6, 2.68, 64);
    const ringMat = new THREE.MeshBasicMaterial({{ color: 0x00f5d4, side: THREE.DoubleSide, transparent: true, opacity: 0.7 }});
    const floorRing = new THREE.Mesh(ringGeo, ringMat);
    floorRing.rotation.x = Math.PI / 2;
    floorRing.position.set(0, 0.02, -2.5);
    scene.add(floorRing);

    const orbMeshes = [];
    const pulses = [];
    const corePos = new THREE.Vector3(coreData.x, coreData.y, coreData.z);

    nodesData.forEach((nd, i) => {{
        const group = new THREE.Group();
        group.position.set(nd.x, nd.y, nd.z);

        const sphereGeo = new THREE.SphereGeometry(0.24, 32, 32);
        const sphereMat = new THREE.MeshStandardMaterial({{
            color: nd.color,
            emissive: nd.color,
            emissiveIntensity: 0.9,
            roughness: 0.2,
            metalness: 0.2
        }});
        const sphere = new THREE.Mesh(sphereGeo, sphereMat);
        group.add(sphere);

        const torusGeo = new THREE.TorusGeometry(0.36, 0.014, 16, 64);
        const torusMat = new THREE.MeshBasicMaterial({{ color: nd.ring }});
        const torus = new THREE.Mesh(torusGeo, torusMat);
        torus.rotation.x = 1.2;
        group.add(torus);

        const lblCanvas = document.createElement('canvas');
        lblCanvas.width = 380;
        lblCanvas.height = 100;
        const ctx = lblCanvas.getContext('2d');
        ctx.fillStyle = 'rgba(5, 14, 32, 0.9)';
        ctx.fillRect(0, 0, 380, 100);
        ctx.strokeStyle = nd.color;
        ctx.lineWidth = 5;
        ctx.strokeRect(2, 2, 376, 96);
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 25px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(nd.name, 190, 40);
        ctx.fillStyle = nd.ring;
        ctx.font = 'bold 21px monospace';
        ctx.fillText(nd.ping + ' ms | ' + nd.qos, 190, 76);

        const tex = new THREE.CanvasTexture(lblCanvas);
        const spriteMat = new THREE.SpriteMaterial({{ map: tex }});
        const sprite = new THREE.Sprite(spriteMat);
        sprite.position.set(0, 0.56, 0);
        sprite.scale.set(1.4, 0.38, 1);
        group.add(sprite);

        scene.add(group);
        orbMeshes.push({{ group: group, sphere: sphere, torus: torus, ping: nd.ping, baseY: nd.y, idx: i }});

        if (i !== 0) {{
            const targetPos = new THREE.Vector3(nd.x, nd.y, nd.z);
            const points = [];
            points.push(corePos);
            points.push(targetPos);
            const lineGeo = new THREE.BufferGeometry().setFromPoints(points);
            const lineMat = new THREE.LineBasicMaterial({{ color: 0x0081FB, transparent: true, opacity: 0.85 }});
            scene.add(new THREE.Line(lineGeo, lineMat));

            const pulseGeo = new THREE.SphereGeometry(0.055, 12, 12);
            const pulseMat = new THREE.MeshBasicMaterial({{ color: 0x00f5d4 }});
            const pulseMesh = new THREE.Mesh(pulseGeo, pulseMat);
            scene.add(pulseMesh);
            pulses.push({{ mesh: pulseMesh, start: corePos, end: targetPos, progress: i * 0.3 }});
        }}
    }});

    let isDragging = false;
    let prevX = 0;
    let angle = 0;
    canvas.addEventListener('mousedown', (e) => {{ isDragging = true; prevX = e.clientX; }});
    window.addEventListener('mouseup', () => {{ isDragging = false; }});
    window.addEventListener('mousemove', (e) => {{
        if (isDragging) {{
            angle += (e.clientX - prevX) * 0.008;
            prevX = e.clientX;
        }}
    }});

    const vrBtn = document.getElementById('vrBtn');
    vrBtn.addEventListener('click', async () => {{
        if (navigator.xr) {{
            try {{
                const session = await navigator.xr.requestSession('immersive-vr', {{ optionalFeatures: ['local-floor', 'hand-tracking'] }});
                renderer.xr.setSession(session);
            }} catch (err) {{
                alert('Enable Meta Immersive Web Emulator extension in Chrome to enter VR mode.');
            }}
        }} else {{
            alert('WebXR not detected. Open in Chrome with Meta Immersive Web Emulator.');
        }}
    }});

    let clock = new THREE.Clock();
    renderer.setAnimationLoop(() => {{
        const t = clock.getElapsedTime();
        floorRing.rotation.z = t * 0.25;

        if (!renderer.xr.isPresenting) {{
            camera.position.x = Math.sin(angle) * 3.4;
            camera.position.z = -2.5 + Math.cos(angle) * 3.4;
            camera.lookAt(0, 1.35, -2.5);
        }}

        orbMeshes.forEach((item) => {{
            item.torus.rotation.z += 0.025;
            item.group.position.y = item.baseY + Math.sin(t * 2.5 + item.idx) * 0.05;
            const pulseSpeed = Math.max(2.5, item.ping / 14.0);
            const s = 1 + Math.sin(t * pulseSpeed) * 0.09;
            item.sphere.scale.set(s, s, s);
        }});

        pulses.forEach((p) => {{
            p.progress = (p.progress + 0.015) % 1;
            p.mesh.position.lerpVectors(p.start, p.end, p.progress);
        }});

        renderer.render(scene, camera);
    }});
    """

    hud_overlay = tag("div", 'style="position:absolute;top:12px;left:14px;background:rgba(0,129,251,0.32);border:1px solid #0081FB;color:#e0f2fe;padding:5px 12px;border-radius:999px;font-family:sans-serif;font-size:12px;font-weight:bold;z-index:10;"', f"♾️ {mode_upper} | DRAG TO ROTATE 360°")
    vr_button = tag("button", 'id="vrBtn" style="position:absolute;bottom:14px;right:14px;background:linear-gradient(90deg,#0064e0,#0081FB);border:1px solid #00f5d4;color:#ffffff;padding:8px 16px;border-radius:999px;font-family:sans-serif;font-size:12px;font-weight:bold;cursor:pointer;box-shadow:0 0 15px rgba(0,129,251,0.7);z-index:10;"', "🥽 ENTER META QUEST VR")
    canvas_el = tag("canvas", 'id="xrCanvas" style="width:100%;height:410px;display:block;"')
    wrapper = tag("div", 'style="position:relative;width:100%;height:410px;background:#030816;border-radius:20px;border:1px solid rgba(0,129,251,0.5);overflow:hidden;"', hud_overlay + vr_button + canvas_el)

    three_cdn = tag("script", 'src="https://unpkg.com"')
    inline_js = tag("script", content=js_code)
    doc = f"{LT}!DOCTYPE html{GT}" + tag("html", content=tag("head", content=three_cdn) + tag("body", 'style="margin:0;overflow:hidden;background:#030816;"', wrapper + inline_js))
    components.html(doc, height=415)
