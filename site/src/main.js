import './style.css';
import catalog from './catalog.json';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const $ = (id) => document.getElementById(id);
const repo = 'https://github.com/tiansongyu/open-console-cad';
const raw = `${repo}/raw/refs/heads/main/devices`;
const devices = Object.fromEntries(catalog.map(d => [d.id,d]));
const query = new URLSearchParams(location.search);
let device = devices[query.get('device')] ? query.get('device') : 'switch';
let view = devices[device].views[query.get('view')] ? query.get('view') : 'assembled';
let amount = devices[device].views[view].explode || 0;
let opening = devices[device].views[view].opening ?? devices[device].opening ?? 180;
let poseData = null, tabsDevice = null;
let renderer, controls, root, meshes = [], ready = false, request = 0;
const cache = new Map();
const scene = new THREE.Scene(); scene.background = new THREE.Color('#eef1f5');
const camera = new THREE.PerspectiveCamera(38, 1, 0.001, 100);
const loader = new GLTFLoader();
const timer = new THREE.Timer(); timer.connect(document);
const errors = $('error');

function buildCards() {
  $('collection-label').textContent = `THE COLLECTION / 01—${String(catalog.length).padStart(2,'0')}`;
  $('collection-stats').replaceChildren();
  for (const text of [`${catalog.length} 款设备`,`${catalog.reduce((n,d)=>n+d.count,0).toLocaleString('en-US')} 个组件`,`${catalog.reduce((n,d)=>n+d.pages,0)} 页 A3 图纸`]) {
    const line=document.createElement('span'); line.textContent=text; line.style.display='block'; $('collection-stats').append(line);
  }
  $('device-list').replaceChildren(...catalog.map((d,i) => {
    const card=document.createElement('button'); card.className='device-card'; card.dataset.device=d.id; card.setAttribute('aria-pressed','false');
    const top=document.createElement('div'); top.className='card-top';
    const number=document.createElement('span'); number.textContent=`${String(i+1).padStart(2,'0')} / ${d.model}`;
    const arrow=document.createElement('span'); arrow.className='card-arrow'; arrow.textContent='↗';top.append(number,arrow);
    const img=document.createElement('img');img.src=`./images/${d.id}/hero.webp`;img.alt=d.title+' CAD 模型';
    const bottom=document.createElement('div');bottom.className='card-bottom';const words=document.createElement('div');
    const title=document.createElement('h2');title.textContent=d.title;const detail=document.createElement('p');detail.textContent=`${d.model} · ${d.count} 个组件`;words.append(title,detail);
    const tag=document.createElement('span');tag.className='tag';tag.textContent=`${d.iterations} 轮设计`;bottom.append(words,tag);card.append(top,img,bottom);return card;
  }));
}
function buildTabs() {
  if (tabsDevice===device) return;
  tabsDevice=device;
  $('scene-tabs').replaceChildren(...Object.entries(devices[device].views).map(([id,definition]) => {
    const button=document.createElement('button');button.dataset.scene=id;button.textContent=definition.label;button.setAttribute('aria-pressed','false');return button;
  }));
}
function updateLinks() {
  const d = devices[device]; buildTabs();
  $('model-title').textContent = d.title;
  $('scene-description').textContent = d.views[view].description;
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
  const hinged=d.family==='clamshell'; $('hinge-control').hidden=!hinged; $('opening').disabled=!ready;
  $('opening').max=String(d.opening||180); $('opening').value=String(opening); $('opening-value').textContent=`${opening}°`;
  const gallery = d.gallery;
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
  if (reset) normal = new THREE.Vector3(...(devices[device].views[view].normal || [.5,.35,2.5]));
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
  const definition=devices[device].views[view], allowed=definition.groups, excluded=new Set(definition.exclude||[]);
  const hinge=poseData?.type==='hinge';
  const pivot=new THREE.Vector3(...(hinge ? poseData.pivot_mm.map(v=>v/1000) : [0,0,0]));
  const q=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(...(poseData?.axis||[1,0,0])),THREE.MathUtils.degToRad(hinge ? poseData.default_opening-opening : 0));
  for (const mesh of meshes) {
    mesh.visible=allowed.includes(mesh.userData.assembly) && !excluded.has(mesh.userData.partId);
    const position=mesh.userData.origin.clone(), offset=mesh.userData.offset.clone();
    mesh.quaternion.identity();
    if (hinge && mesh.userData.poseGroup===poseData.group) {position.sub(pivot).applyQuaternion(q).add(pivot);offset.applyQuaternion(q);mesh.quaternion.copy(q);}
    mesh.position.copy(position).addScaledVector(offset,amount);
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
  $('loading').textContent = `正在加载 ${devices[selected].title} · ${(devices[selected].bytes/1e6).toFixed(1)} MB`;
  try {
    if (!cache.has(selected)) cache.set(selected,loader.loadAsync(`./models/${selected}.glb`,e => {
      if (token === request && e.total) $('loading').textContent = `正在加载 ${devices[selected].title} · ${Math.round(e.loaded / e.total*100)}%`;
    }).catch(error => { cache.delete(selected); throw error; }));
    const gltf = await cache.get(selected);
    if (token !== request) return;
    root = gltf.scene; meshes = []; poseData = gltf.asset?.extras?.pose || null;
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

buildCards();
$('device-list').addEventListener('click',event => {
  const button=event.target.closest('[data-device]');if(!button)return;
  if(button.dataset.device===device && ready){$('viewer').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});return;}
  device=button.dataset.device;if(!devices[device].views[view])view='assembled';
  amount=devices[device].views[view].explode||0;opening=devices[device].views[view].opening??devices[device].opening??180;loadDevice();
});
$('scene-tabs').addEventListener('click',event => {
  const button=event.target.closest('[data-scene]');if(!button)return;view=button.dataset.scene;
  amount=devices[device].views[view].explode||0;opening=devices[device].views[view].opening??devices[device].opening??180;updateLinks();applyView();
});
$('opening').addEventListener('input',event => {
  opening=Number(event.target.value);$('opening-value').textContent=`${opening}°`;
  if(view==='closed' && opening>0){view='assembled';updateLinks();}applyView(false);
});
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
