import './style.css';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const $ = (id) => document.getElementById(id);
const repo = 'https://github.com/tiansongyu/open-console-cad';
const raw = `${repo}/raw/refs/heads/main/devices`;
const devices = {
  switch: { title: 'Nintendo Switch', prefix: 'Switch', count: 654, size: '9.9 MB', iterations: 14 },
  switch2: { title: 'Nintendo Switch 2', prefix: 'Switch2', count: 799, size: '13.4 MB', iterations: 15 },
};
const descriptions = {
  assembled: '完整手持装配，保留独立外壳、显示组件和内部模块。',
  internal: '移开后壳与屏蔽板，从背面观察电池、主板、散热与手柄内部。内部布局为近似示意。',
  exploded: '沿装配层展开主机，使用滑块查看各层的相对关系。爆炸位移仅用于展示。',
  controllers: '独立查看左右手柄；展开后可观察按键、摇杆、电池和主板。',
  dock: '查看底座外形与插接槽；移动滑块展开后盖、主板和前面板。',
  accessories: '非充电握把与两套腕带。绳圈为展示摆放，不代表实际使用姿态。',
};
const groups = {
  assembled: ['Tablet','Display','TabletInternal','JoyLeft','JoyRight','JoyMountL','JoyMountR','JoyRailL','JoyRailR','JoyInternalL','JoyInternalR'],
  exploded: ['Tablet','Display','TabletInternal'],
  controllers: ['JoyLeft','JoyRight','JoyMountL','JoyMountR','JoyRailL','JoyRailR','JoyInternalL','JoyInternalR'],
  dock: ['Dock','DockInternal'], accessories: ['Grip','StrapL','StrapR'],
};
const hiddenInternal = new Set(['TabletRear','Kickstand','StandFoot','StandFoot-1','StandFoot1','RearNintendoMark','RearModelMark','RearEMIShield','JoyLRear','JoyRRear']);
const query = new URLSearchParams(location.search);
let device = devices[query.get('device')] ? query.get('device') : 'switch';
let view = descriptions[query.get('view')] ? query.get('view') : 'assembled';
let amount = view === 'exploded' ? 1 : 0;
let renderer, controls, root, meshes = [], ready = false, request = 0;
const cache = new Map();
const scene = new THREE.Scene(); scene.background = new THREE.Color('#eef1f5');
const camera = new THREE.PerspectiveCamera(38, 1, 0.001, 100);
const loader = new GLTFLoader();
const timer = new THREE.Timer(); timer.connect(document);
const errors = $('error');

function updateLinks() {
  const d = devices[device];
  $('model-title').textContent = d.title;
  $('scene-description').textContent = descriptions[view];
  $('download-cad').href = `${raw}/${device}/output/${d.prefix}_Complete.FCStd`;
  $('download-pdf').href = `${raw}/${device}/output/drawings/${d.prefix}_Drawings.pdf`;
  $('download-glb').href = `./models/${device}.glb`;
  $('download-glb').download = `${device}.glb`;
  document.querySelectorAll('[data-device]').forEach(b => { const active = b.dataset.device === device; b.classList.toggle('selected',active); b.setAttribute('aria-pressed',String(active)); });
  document.querySelectorAll('[data-scene]').forEach(b => b.setAttribute('aria-pressed',String(b.dataset.scene === view)));
  const params = new URLSearchParams({device, view});
  history.replaceState(null,'',`${location.pathname}?${params}${location.hash}`);
  $('explode').value = String(Math.round(amount * 100)); $('explode-value').textContent = `${Math.round(amount * 100)}%`;
  $('explode').disabled = !ready;
  const gallery = [['hero','正面装配'],['rear','背面结构'],['internal','主要内部布局'],['exploded','主机分层爆炸'],['dock','底座外观']];
  $('gallery-grid').replaceChildren(...gallery.map(([file,title]) => {
    const link = document.createElement('a'); link.className = 'gallery-card'; link.href = `./images/${device}/${file}.webp`; link.target = '_blank'; link.rel = 'noopener';
    const image = document.createElement('img'); image.src = link.href; image.alt = `${d.title} · ${title}`; image.loading = 'lazy'; image.width = 1200; image.height = 700;
    const caption = document.createElement('div'); caption.className = 'gallery-caption';
    const text = document.createElement('span'); text.textContent = title;
    const label = document.createElement('span'); label.textContent = 'CAD 实体渲染 ↗'; caption.append(text,label); link.append(image,caption); return link;
  }));
}
function resize() {
  if (!renderer) return;
  const box = $('stage').getBoundingClientRect();
  renderer.setSize(box.width,box.height,false); camera.aspect = box.width / box.height; camera.updateProjectionMatrix(); if (ready) fit(false);
}
function fit(reset = true) {
  if (!ready) return;
  root.updateMatrixWorld(true);
  const bounds = new THREE.Box3(); meshes.filter(m => m.visible).forEach(m => bounds.expandByObject(m));
  if (bounds.isEmpty()) return;
  const center = bounds.getCenter(new THREE.Vector3()), size = bounds.getSize(new THREE.Vector3());
  const radius = size.length()/2;
  let normal;
  if (reset) normal = new THREE.Vector3(...(view === 'internal' ? [.15,.1,-2.6] : view === 'exploded' ? [1.7,.2,-1] : [.5,.35,2.5]));
  else normal = camera.position.clone().sub(controls.target);
  const fov = THREE.MathUtils.degToRad(camera.fov);
  normal.normalize();
  const right = new THREE.Vector3().crossVectors(camera.up,normal).normalize();
  const up = new THREE.Vector3().crossVectors(normal,right).normalize();
  let distance = .01;
  for (const x of [bounds.min.x,bounds.max.x]) for (const y of [bounds.min.y,bounds.max.y]) for (const z of [bounds.min.z,bounds.max.z]) {
    const corner = new THREE.Vector3(x,y,z).sub(center), depth = corner.dot(normal);
    distance = Math.max(distance,depth+Math.abs(corner.dot(right))/Math.tan(fov/2)/camera.aspect,depth+Math.abs(corner.dot(up))/Math.tan(fov/2));
  }
  distance *= 1.15;
  controls.target.copy(center); camera.position.copy(center).add(normal.normalize().multiplyScalar(distance));
  camera.near = Math.max(.0001,distance / 2000); camera.far = distance*30; camera.updateProjectionMatrix();
  controls.minDistance = Math.max(.005,radius*.15); controls.maxDistance = distance*5; controls.update();
}
function applyView(reset = true) {
  if (!ready) return;
  const allowed = groups[view === 'internal' ? 'assembled' : view];
  for (const mesh of meshes) {
    mesh.visible = allowed.includes(mesh.userData.assembly) && !(view === 'internal' && hiddenInternal.has(mesh.userData.partId));
    mesh.position.copy(mesh.userData.origin).addScaledVector(mesh.userData.offset, amount);
  }
  const count = meshes.filter(m => m.visible).length;
  $('mesh-info').textContent = `${count} 个可见组件 / 全套 ${devices[device].count}`;
  $('canvas').setAttribute('aria-label',`${devices[device].title}，${view}，${count} 个组件。拖动旋转，滚轮缩放，方向键旋转，加减键缩放。`);
  fit(reset);
}
function failure(message) {
  ready = false; $('loading').hidden = true; errors.hidden = false; $('error-message').textContent = message; $('explode').disabled = true;
}
async function loadDevice() {
  const token = ++request, selected = device;
  ready = false; $('loading').hidden = false; errors.hidden = true; updateLinks();
  if (root) { scene.remove(root); root = null; meshes = []; }
  if (!renderer) { failure('当前浏览器无法创建 WebGL 画布。请启用硬件加速或更换浏览器；下方效果图与下载仍可使用。'); return; }
  $('loading').textContent = `正在加载 ${devices[selected].title} · ${devices[selected].size}`;
  try {
    if (!cache.has(selected)) cache.set(selected,loader.loadAsync(`./models/${selected}.glb`,e => {
      if (token === request && e.total) $('loading').textContent = `正在加载 ${devices[selected].title} · ${Math.round(e.loaded / e.total*100)}%`;
    }).catch(error => { cache.delete(selected); throw error; }));
    const gltf = await cache.get(selected);
    if (token !== request) return;
    root = gltf.scene; meshes = [];
    root.traverse(mesh => {
      if (!mesh.isMesh || !mesh.userData.assembly) return;
      if (!mesh.userData.origin) { mesh.userData.origin = mesh.position.clone(); mesh.userData.offset = new THREE.Vector3(...mesh.userData.explodeOffset); }
      meshes.push(mesh);
    });
    if (meshes.length !== devices[selected].count) throw new Error('组件清单与模型不一致');
    scene.add(root); ready = true; $('loading').hidden = true; updateLinks(); applyView();
  } catch (error) {
    if (token === request) failure(`模型加载失败，请检查网络后重试。${error.message || ''}`);
  }
}
try {
  renderer = new THREE.WebGLRenderer({canvas:$('canvas'),antialias:true,alpha:false});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.75));
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.1;
  const pmrem = new THREE.PMREMGenerator(renderer), room = new RoomEnvironment();
  const environment = pmrem.fromScene(room,.04); scene.environment = environment.texture; room.dispose(); pmrem.dispose();
  scene.add(new THREE.HemisphereLight(0xffffff,0x778397,0.8));
  const key = new THREE.DirectionalLight(0xffffff,2.0); key.position.set(2,3,4); scene.add(key);
  controls = new OrbitControls(camera,$('canvas')); controls.enableDamping = true; controls.dampingFactor = .09; controls.autoRotateSpeed = .7;
  $('canvas').addEventListener('keydown',e => {
    if (['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)) {
      const spherical = new THREE.Spherical().setFromVector3(camera.position.clone().sub(controls.target));
      spherical.theta += e.key === 'ArrowLeft' ? -.12 : e.key === 'ArrowRight' ? .12 : 0;
      spherical.phi += e.key === 'ArrowUp' ? -.12 : e.key === 'ArrowDown' ? .12 : 0;
      spherical.makeSafe(); camera.position.setFromSpherical(spherical).add(controls.target); e.preventDefault();
    }
    if (e.key === '+' || e.key === '=') { camera.position.sub(controls.target).multiplyScalar(.9).add(controls.target); e.preventDefault(); }
    if (e.key === '-') { camera.position.sub(controls.target).multiplyScalar(1.1).add(controls.target); e.preventDefault(); }
  });
  new ResizeObserver(resize).observe($('stage')); resize();
  renderer.setAnimationLoop(() => { timer.update(); const delta = Math.min(timer.getDelta(),.1); if (document.hidden) return; controls.update(delta); renderer.render(scene,camera); });
  $('canvas').addEventListener('webglcontextlost',e => { e.preventDefault(); failure('WebGL 上下文已中断，请点击重新加载。下方效果图仍可使用。'); $('retry').onclick = () => location.reload(); });
} catch (e) { console.warn('WebGL unavailable:',e.message); }

document.querySelectorAll('[data-device]').forEach(button => button.addEventListener('click',() => {
  if (button.dataset.device === device && ready) { $('viewer').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'}); return; }
  device = button.dataset.device; amount = view === 'exploded' ? 1 : 0; loadDevice();
}));
document.querySelectorAll('[data-scene]').forEach(button => button.addEventListener('click',() => { view = button.dataset.scene; amount = view === 'exploded' ? 1 : 0; updateLinks(); applyView(); }));
$('explode').addEventListener('input',e => { amount = Number(e.target.value)/100; $('explode-value').textContent = `${e.target.value}%`; applyView(false); });
$('reset').addEventListener('click',() => fit(true));
$('rotate').addEventListener('click',() => { if (!controls) return; controls.autoRotate = !controls.autoRotate; $('rotate').setAttribute('aria-pressed',String(controls.autoRotate)); });
$('retry').addEventListener('click',loadDevice);
$('fullscreen').addEventListener('click',async () => {
  try { if (document.fullscreenElement) await document.exitFullscreen(); else await $('stage').requestFullscreen(); }
  catch { $('fullscreen').textContent = '浏览器不支持全屏'; }
});
if (!$('stage').requestFullscreen) $('fullscreen').hidden = true;
loadDevice();
