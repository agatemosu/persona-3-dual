// Tile definitions & procedural styling
let TILE_DEFS = {};

// Helper: Converts HSL color values to a Hex string for the canvas/UI
function hslToHex(h, s, l) {
    l /= 100;
    const a = s * Math.min(l, 1 - l) / 100;
    const f = n => {
        const k = (n + h / 30) % 12;
        const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
        return Math.round(255 * color).toString(16).padStart(2, '0');
    };
    return `#${f(0)}${f(8)}${f(4)}`;
}

// Helper: Takes any string and consistently turns it into the exact same Hex color
function generateDeterministicColor(seedString) {
    let hash = 0;
    for (let i = 0; i < seedString.length; i++) {
        hash = seedString.charCodeAt(i) + ((hash << 5) - hash);
    }
    // Extract a hue from the hash (0-360 degrees)
    const h = Math.abs(hash) % 360;
    // Keep saturation (70%) and lightness (45%) consistent so UI buttons remain legible
    return hslToHex(h, 70, 45);
}

async function loadTileDefinitions() {
    try {
        const response = await fetch('../../tile_map.json');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();

        // Sort keys alphabetically to guarantee deterministic order on all systems
        const sortedKeys = Object.keys(data.TILE_MAP_META).sort();
        // The standard top-row keyboard layout
        const shortcuts = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'];

        sortedKeys.forEach((code, index) => {
            const metaLabel = data.TILE_MAP_META[code];
            // Seed the generator with both code and label to prevent color collisions
            const baseColor = generateDeterministicColor(code + metaLabel);

            TILE_DEFS[code] = {
                // Format the string from "NO_COLLISION" to "No Collision"
                label: metaLabel.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()), 
                shortLabel: metaLabel.split('—')[0].trim().toLowerCase(),
                mapValue: data.TILE_MAP[code],
                key: index < shortcuts.length ? shortcuts[index] : '', // Assign 1-0, then leave blank
                bg: baseColor + '40', // Append '40' for hex transparency on the background
                border: baseColor,
                textColor: '#ffffff'
            };
        });
    } catch (error) {
        console.error("Failed to load tile_map.json. Did you run a local server?", error);
        alert("Failed to load tile definitions from JSON. Check console for details.");
    }
}

// State
let params = {
    tileSize: 0.0625,
    offsetX: 1.75, offsetZ: 1.3125,
    width: 56, height: 12,
    name: 'map', audio: '',
    scale: 1.0, centered: true
};
let tileData = new Array(56 * 12).fill('w');
let currentTool = 'w';
let isPainting = false;
let paintErase = false;
let currentView = 'top';

// Three.js
let scene, camera, renderer;
let rawModelGroup = null; 
let modelGroup, gridGroup, tileGroup;
let groundRaycaster;
let groundMesh;
let tileCanvasEl, tileCanvasCtx, tileTex, tilePlane;
let wireMaterial, solidMaterial;
let showWire = true, showSolid = false;
let showGrid = true, showModel = true;
let viewSize = 2.5;
let panX = 0, panZ = 0;
let isSpaceDown = false, isPanning = false;
let lastMX = 0, lastMY = 0;

function initThree() {
    const canvas = document.getElementById('three-canvas');
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setClearColor(0x0d0d0f, 1);
    renderer.sortObjects = true;

    scene = new THREE.Scene();

    const vp = document.getElementById('viewport');
    const asp = vp.clientWidth / vp.clientHeight;
    camera = new THREE.OrthographicCamera(-viewSize * asp, viewSize * asp, viewSize, -viewSize, -1000, 1000);
    setView('top');

    scene.add(new THREE.AmbientLight(0xffffff, 0.7));
    const sun = new THREE.DirectionalLight(0xffffee, 0.6);
    sun.position.set(2, 5, 3);
    scene.add(sun);

    modelGroup = new THREE.Group(); scene.add(modelGroup);
    gridGroup = new THREE.Group(); scene.add(gridGroup);
    tileGroup = new THREE.Group(); scene.add(tileGroup);

    wireMaterial = new THREE.MeshBasicMaterial({ color: 0x6688aa, wireframe: true, transparent: true, opacity: 0.55 });
    solidMaterial = new THREE.MeshLambertMaterial({ color: 0x7799bb, transparent: true, opacity: 0.45, side: THREE.DoubleSide });

    groundMesh = new THREE.Mesh(
        new THREE.PlaneGeometry(10000, 10000),
        new THREE.MeshBasicMaterial({ visible: false, side: THREE.DoubleSide })
    );
    groundMesh.rotation.x = -Math.PI / 2;
    scene.add(groundMesh);
    groundRaycaster = new THREE.Raycaster();

    setupEvents(canvas);
    rebuildGrid();
    rebuildTileLayer();
    resetCamera();

    window.addEventListener('resize', onResize);
    onResize();
    animate();
}

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

function onResize() {
    const vp = document.getElementById('viewport');
    renderer.setSize(vp.clientWidth, vp.clientHeight);
    updateCameraFrustum();
}

function updateCameraFrustum() {
    const vp = document.getElementById('viewport');
    const asp = vp.clientWidth / vp.clientHeight;
    camera.left = -viewSize * asp + panX;
    camera.right = viewSize * asp + panX;
    camera.top = viewSize - panZ;
    camera.bottom = -viewSize - panZ;
    camera.updateProjectionMatrix();
}

function resetCamera() {
    const { tileSize, offsetX, offsetZ, width, height } = params;
    panX = (width * tileSize) / 2 - offsetX;
    panZ = (height * tileSize) / 2 - offsetZ;
    viewSize = Math.max(width * tileSize, height * tileSize) * 0.7;
    updateCameraFrustum();
}

function setView(view) {
    currentView = view;
    document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active-btn'));
    document.getElementById('btn-view-' + view).classList.add('active-btn');
    document.getElementById('paint-warning').style.display = (view === 'top') ? 'none' : 'block';

    if (view === 'top') {
        camera.position.set(0, 50, 0); camera.up.set(0, 0, -1);
    } else if (view === 'front') {
        camera.position.set(0, 0, 50); camera.up.set(0, 1, 0);
    } else if (view === 'back') {
        camera.position.set(0, 0, -50); camera.up.set(0, 1, 0);
    } else if (view === 'left') {
        camera.position.set(-50, 0, 0); camera.up.set(0, 1, 0);
    } else if (view === 'right') {
        camera.position.set(50, 0, 0); camera.up.set(0, 1, 0);
    }
    camera.lookAt(0, 0, 0);
    updateCameraFrustum();
}

// Grid
function rebuildGrid() {
    gridGroup.clear();
    const { tileSize: ts, offsetX: ox, offsetZ: oz, width: W, height: H } = params;
    const x0 = -ox, x1 = W * ts - ox;
    const z0 = -oz, z1 = H * ts - oz;
    const Y = 0.03;

    const verts = [];
    for (let x = 0; x <= W; x++) {
        const wx = x * ts - ox;
        verts.push(wx, Y, z0, wx, Y, z1);
    }
    for (let z = 0; z <= H; z++) {
        const wz = z * ts - oz;
        verts.push(x0, Y, wz, x1, Y, wz);
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
    gridGroup.add(new THREE.LineSegments(geo, new THREE.LineBasicMaterial({ color: 0x2a2a3a })));

    const bv = [
        x0, Y + 0.01, z0, x1, Y + 0.01, z0,
        x1, Y + 0.01, z0, x1, Y + 0.01, z1,
        x1, Y + 0.01, z1, x0, Y + 0.01, z1,
        x0, Y + 0.01, z1, x0, Y + 0.01, z0,
    ];
    const bgeo = new THREE.BufferGeometry();
    bgeo.setAttribute('position', new THREE.Float32BufferAttribute(bv, 3));
    gridGroup.add(new THREE.LineSegments(bgeo, new THREE.LineBasicMaterial({ color: 0xf0a030 })));

    gridGroup.visible = showGrid;
}

// Tile Layer
function rebuildTileLayer() {
    tileGroup.clear();
    const { tileSize: ts, offsetX: ox, offsetZ: oz, width: W, height: H } = params;

    tileCanvasEl = document.createElement('canvas');
    tileCanvasEl.width = W;
    tileCanvasEl.height = H;
    tileCanvasCtx = tileCanvasEl.getContext('2d');

    tileTex = new THREE.CanvasTexture(tileCanvasEl);
    tileTex.magFilter = THREE.NearestFilter;
    tileTex.minFilter = THREE.NearestFilter;
    tileTex.flipY = true;

    const ww = W * ts, wh = H * ts;
    const geo = new THREE.PlaneGeometry(ww, wh);
    const mat = new THREE.MeshBasicMaterial({ map: tileTex, transparent: true, opacity: 0.72, depthTest: false, depthWrite: false });
    tilePlane = new THREE.Mesh(geo, mat);
    tilePlane.rotation.x = -Math.PI / 2;
    tilePlane.position.set(ww / 2 - ox, 0.04, wh / 2 - oz);
    tilePlane.renderOrder = 1;
    tileGroup.add(tilePlane);

    redrawTiles();
}

function redrawTiles() {
    if (!tileCanvasCtx) return;
    const { width: W, height: H } = params;
    const ctx = tileCanvasCtx;
    ctx.clearRect(0, 0, W, H);
    for (let z = 0; z < H; z++) {
        for (let x = 0; x < W; x++) {
            const type = tileData[z * W + x];
            if (type === 'w') continue;
            const def = TILE_DEFS[type];
            if (!def) continue;
            ctx.fillStyle = def.border;
            ctx.fillRect(x, z, 1, 1);
        }
    }
    if (tileTex) tileTex.needsUpdate = true;
}

// Mouse & Keyboard Events
function setupEvents(canvas) {
    canvas.addEventListener('wheel', e => {
        e.preventDefault();
        viewSize *= (e.deltaY > 0 ? 1.08 : 0.92);
        viewSize = Math.max(0.03, Math.min(30, viewSize));
        updateCameraFrustum();
    }, { passive: false });

    canvas.addEventListener('mousedown', e => {
        lastMX = e.clientX; lastMY = e.clientY;
        if (e.button === 1 || (e.button === 0 && isSpaceDown)) {
            isPanning = true; canvas.style.cursor = 'grabbing'; return;
        }
        if ((e.button === 0 || e.button === 2) && currentView === 'top') {
            isPainting = true;
            paintErase = (e.button === 2);
            paintAt(e);
        }
    });

    canvas.addEventListener('mousemove', e => {
        if (isPanning) {
            const dx = e.clientX - lastMX;
            const dy = e.clientY - lastMY;
            lastMX = e.clientX; lastMY = e.clientY;
            const vp = document.getElementById('viewport');
            const asp = vp.clientWidth / vp.clientHeight;
            panX -= dx / vp.clientWidth * viewSize * asp * 2;
            panZ += dy / vp.clientHeight * viewSize * 2;
            updateCameraFrustum();
        } else if (isPainting && currentView === 'top') {
            paintAt(e);
        }
        hoverAt(e);
    });

    window.addEventListener('mouseup', () => {
        isPainting = false;
        isPanning = false;
        canvas.style.cursor = isSpaceDown ? 'grab' : 'crosshair';
    });

    canvas.addEventListener('contextmenu', e => e.preventDefault());

    window.addEventListener('keydown', e => {
        if (e.code === 'Space' && !e.repeat) { isSpaceDown = true; canvas.style.cursor = 'grab'; }
        for (const [k, def] of Object.entries(TILE_DEFS)) {
            if (e.key === def.key) { selectTool(k); return; }
        }
        if (e.key === 'g' || e.key === 'G') toggleGrid();
    });
    window.addEventListener('keyup', e => {
        if (e.code === 'Space') { isSpaceDown = false; canvas.style.cursor = 'crosshair'; }
    });

    canvas.style.cursor = 'crosshair';
}

function getWorldPos(e) {
    const canvas = document.getElementById('three-canvas');
    const rect = canvas.getBoundingClientRect();
    const ndcX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    const ndcY = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    groundRaycaster.setFromCamera(new THREE.Vector2(ndcX, ndcY), camera);
    const hits = groundRaycaster.intersectObject(groundMesh);
    return hits.length ? hits[0].point : null;
}

function worldToTile(wx, wz) {
    const { tileSize: ts, offsetX: ox, offsetZ: oz, width: W, height: H } = params;
    const tx = Math.floor((wx + ox) / ts);
    const tz = Math.floor((wz + oz) / ts);
    return { tx, tz, valid: tx >= 0 && tx < W && tz >= 0 && tz < H };
}

function paintAt(e) {
    const pt = getWorldPos(e);
    if (!pt) return;
    const { tx, tz, valid } = worldToTile(pt.x, pt.z);
    if (!valid) return;
    const type = paintErase ? 'w' : currentTool;
    const idx = tz * params.width + tx;
    if (tileData[idx] !== type) {
        tileData[idx] = type;
        redrawTiles();
    }
}

function hoverAt(e) {
    const pt = getWorldPos(e);
    if (!pt) {
        document.getElementById('s-tile').textContent = '—';
        document.getElementById('s-world').textContent = '—';
        document.getElementById('s-type').textContent = '—';
        return;
    }
    document.getElementById('s-world').textContent = `(${pt.x.toFixed(4)}, ${pt.z.toFixed(4)})`;
    const { tx, tz, valid } = worldToTile(pt.x, pt.z);
    if (!valid) {
        document.getElementById('s-tile').textContent = 'out of bounds';
        document.getElementById('s-type').textContent = '—';
        return;
    }
    const type = tileData[tz * params.width + tx];
    document.getElementById('s-tile').textContent = `(${tx}, ${tz})`;
    document.getElementById('s-type').textContent = `${type} — ${TILE_DEFS[type]?.label || '?'}`;
}

// UI events
const paramInputs = document.querySelectorAll('#p-offsetx, #p-offsetz, #p-width, #p-height, #p-name, #p-scale, #p-center');
paramInputs.forEach(input => {
    input.addEventListener('input', () => {
        document.getElementById('btn-apply').classList.add('needs-apply');
    });
    input.addEventListener('change', () => {
        document.getElementById('btn-apply').classList.add('needs-apply');
    });
});

// Palette UI
function buildPalette() {
    const el = document.getElementById('palette');
    el.innerHTML = '';
    for (const [k, def] of Object.entries(TILE_DEFS)) {
        const btn = document.createElement('div');
        btn.className = 'tile-btn' + (k === currentTool ? ' active' : '');
        btn.id = `tb-${k}`;
        btn.style.cssText = `background:${def.bg}; border-color:${def.border}; color:${def.textColor}`;
        btn.innerHTML = `<div class="tile-key">[${def.key || '-'}]</div><div class="tile-code">${k}</div><div class="tile-name">${def.shortLabel}</div>`;
        btn.onclick = () => selectTool(k);
        el.appendChild(btn);
    }
}

function selectTool(k) {
    if (!TILE_DEFS[k]) return;
    currentTool = k;
    document.querySelectorAll('.tile-btn').forEach(b => b.classList.remove('active'));
    const btn = document.getElementById(`tb-${k}`);
    if (btn) btn.classList.add('active');
    const def = TILE_DEFS[k];
    const indicator = document.getElementById('s-tool');
    indicator.textContent = k;
    indicator.style.background = def.border;
    indicator.style.color = def.bg;
}

// Parameters
function readParamInputs() {
    return {
        tileSize: parseFloat(document.getElementById('p-tilesize').value) || 0.0625,
        offsetX: parseFloat(document.getElementById('p-offsetx').value) || 0,
        offsetZ: parseFloat(document.getElementById('p-offsetz').value) || 0,
        width: Math.max(1, parseInt(document.getElementById('p-width').value) || 56),
        height: Math.max(1, parseInt(document.getElementById('p-height').value) || 12),
        name: document.getElementById('p-name').value.trim() || 'map',
        audio: document.getElementById('p-audio').value.trim() || '',
        scale: parseFloat(document.getElementById('p-scale').value) || 1.0,
        centered: document.getElementById('p-center').checked
    };
}

function applyParams() {
    const p = readParamInputs();
    const newTiles = new Array(p.width * p.height).fill('w');
    const copyW = Math.min(p.width, params.width);
    const copyH = Math.min(p.height, params.height);
    for (let z = 0; z < copyH; z++) {
        for (let x = 0; x < copyW; x++) {
            newTiles[z * p.width + x] = tileData[z * params.width + x] || 'w';
        }
    }

    const requiresTransformUpdate = (p.scale !== params.scale || p.centered !== params.centered);
    params = p;
    tileData = newTiles;
    rebuildGrid();
    rebuildTileLayer();

    if (requiresTransformUpdate && rawModelGroup) {
        applyModelTransforms();
    }

    updateMapInfo();
    updateComputed();
    document.getElementById('btn-apply').classList.remove('needs-apply');
}

function autoSize() {
    const p = readParamInputs();
    const w = Math.round((p.offsetX * 2) / p.tileSize);
    const h = Math.round((p.offsetZ * 2) / p.tileSize);
    document.getElementById('p-width').value = w;
    document.getElementById('p-height').value = h;
}

function updateComputed() {
    const { tileSize: ts, width: W, height: H } = params;
    document.getElementById('world-computed').textContent =
        `${W}×${H} tiles  ·  ${(W * ts).toFixed(4)}×${(H * ts).toFixed(4)} world units`;
}

function updateMapInfo() {
    document.getElementById('map-info').innerHTML =
        `<strong>${params.name}</strong> · ${params.width}×${params.height}`;
}

// Toggles
function toggleGrid() {
    showGrid = !showGrid;
    gridGroup.visible = showGrid;
    const btn = document.getElementById('grid-btn');
    btn.textContent = `Grid: ${showGrid ? 'ON' : 'OFF'}`;
    btn.classList.toggle('active-btn', showGrid);
}
function toggleModel() {
    showModel = !showModel;
    modelGroup.visible = showModel;
    document.getElementById('model-btn').textContent = `Model: ${showModel ? 'ON' : 'OFF'}`;
}
function toggleWire() {
    showWire = !showWire;
    modelGroup.traverse(c => { if (c.isMesh && c._isWire) c.visible = showWire; });
    document.getElementById('wire-btn').textContent = `Wire: ${showWire ? 'ON' : 'OFF'}`;
}
function toggleSolid() {
    showSolid = !showSolid;
    modelGroup.traverse(c => { if (c.isMesh && c._isSolid) c.visible = showSolid; });
    document.getElementById('solid-btn').textContent = `Solid: ${showSolid ? 'ON' : 'OFF'}`;
}
function fillAll(type) {
    tileData.fill(type);
    redrawTiles();
}

// Model Loading
document.getElementById('obj-input').addEventListener('change', e => {
    const file = e.target.files[0]; if (!file) return;
    const url = URL.createObjectURL(file);
    document.getElementById('no-model-hint').style.display = 'none';

    const loader = new THREE.OBJLoader();
    loader.load(url, obj => {
        rawModelGroup = obj;
        applyModelTransforms();
        URL.revokeObjectURL(url);
        e.target.value = '';
    }, undefined, err => {
        alert('Failed to load .obj: ' + err.message);
        URL.revokeObjectURL(url);
    });
});

function applyModelTransforms() {
    modelGroup.clear();

    rawModelGroup.traverse(child => {
        if (child.isMesh) {
            const wire = new THREE.Mesh(child.geometry, wireMaterial.clone());
            const solid = new THREE.Mesh(child.geometry, solidMaterial.clone());
            wire._isWire = true;
            solid._isSolid = true;
            wire.visible = showWire;
            solid.visible = showSolid;
            modelGroup.add(wire);
            modelGroup.add(solid);
        }
    });

    const s = params.scale;
    modelGroup.scale.set(s, s, s);

    if (params.centered) {
        let bbox = new THREE.Box3().setFromObject(rawModelGroup);
        let center = new THREE.Vector3();
        bbox.getCenter(center);
        modelGroup.position.set(-center.x * s, -bbox.min.y * s, -center.z * s);
    } else {
        modelGroup.position.set(0, 0, 0);
    }
}

function matchDefine(text, pattern) {
    const m = text.match(pattern);
    return m ? parseFloat(m[1]) : null;
}

document.getElementById('jmap-input').addEventListener('change', e => {
    const file = e.target.files[0]; if (!file) return;
    const reader = new FileReader();
    reader.onload = ev => {
        parseJmap(ev.target.result);
        e.target.value = '';
    };
    reader.readAsText(file);
});

function parseJmap(text) {
    const lines = text.split('\n');
    const dataLines = [];
    let audio = '';
    let w = 0, h = 0;
    for (const line of lines) {
        const t = line.trim();
        if (!t || t.startsWith('#')) {
            const audioM = t.match(/@audio\s+(.+)/);
            if (audioM) audio = audioM[1].trim();
            const sizeM = t.match(/(\d+)x(\d+)/);
            if (sizeM) { w = parseInt(sizeM[1]); h = parseInt(sizeM[2]); }

            // Procedurally assign a color if the jmap file has a custom tile type not in the JSON
            const tileMatch = t.match(/#\s+([a-z0-9])\s*=\s*([^()]+)\s*(?:\(([^)]+)\))?/i);
            if (tileMatch && tileMatch[1] !== 'w') {
                let code = tileMatch[1];
                if (!TILE_DEFS[code]) {
                    const parsedLabel = tileMatch[3] || tileMatch[2].trim();
                    const baseColor = generateDeterministicColor(code + parsedLabel);
                    
                    TILE_DEFS[code] = {
                        label: parsedLabel,
                        shortLabel: tileMatch[2].trim(),
                        key: '', // Unassigned shortcut for ad-hoc runtime tiles
                        bg: baseColor + '40', 
                        border: baseColor, 
                        textColor: '#ffffff'
                    };
                }
            }
            continue;
        }
        dataLines.push(t.split(',').map(s => s.trim()));
    }

    if (dataLines.length === 0) { alert('No tile data found in .jmap'); return; }
    const actualH = dataLines.length;
    const actualW = dataLines[0].length;

    document.getElementById('p-width').value = actualW;
    document.getElementById('p-height').value = actualH;
    if (audio) document.getElementById('p-audio').value = audio;

    applyParams();
    buildPalette(); 

    for (let z = 0; z < actualH; z++) {
        for (let x = 0; x < actualW; x++) {
            const type = (dataLines[z][x] || 'w');
            if (TILE_DEFS[type] || type === 'w') tileData[z * actualW + x] = type;
        }
    }
    redrawTiles();
    alert(`Loaded .jmap: ${actualW}×${actualH} tiles`);
}

// Export
function exportJmap() {
    const { width: W, height: H, name, audio } = params;
    const lines = [];
    lines.push(`# ${name} collision map  ${W}x${H}`);
    lines.push(`#`);
    if (audio) lines.push(`# @audio ${audio}`);
    lines.push(`#`);
    lines.push(`# Tile key:`);
    for (const [k, def] of Object.entries(TILE_DEFS)) {
        lines.push(`#   ${k} = ${def.shortLabel} (${def.label})`);
    }
    lines.push(``);
    for (let z = 0; z < H; z++) {
        const row = [];
        for (let x = 0; x < W; x++) row.push(tileData[z * W + x] || 'w');
        lines.push(row.join(', '));
    }
    downloadFile(`${name}.jmap`, lines.join('\n'), 'text/plain');
}

function downloadFile(filename, text, mime) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([text], { type: mime }));
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// Run on page load
async function init() {
    await loadTileDefinitions();
    buildPalette();
    
    // Safety fallback
    if (TILE_DEFS['w']) {
        selectTool('w');
    } else {
        const firstTool = Object.keys(TILE_DEFS)[0];
        if (firstTool) selectTool(firstTool);
    }
    
    updateComputed();
    updateMapInfo();
    initThree();
}

init();