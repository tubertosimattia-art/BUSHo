const routeData = window.routeData || { mode: 'demo', lines: [] };

const state = {
  activeLineIndex: 0,
  activeVariantIndex: 0,
  isNavigating: false,
  isPaused: false,
  voiceEnabled: false,
  gpsStatus: 'waiting',
  currentPosition: null,
  currentSegmentIndex: 0,
  lastAnnouncementKey: null,
  previousStopIndex: -1,
  routeProgress: 0,
  navigatorWatchId: null,
};

const map = L.map('map', {
  zoomControl: true,
  attributionControl: true,
  tap: true,
});

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors',
}).addTo(map);

const routeLayer = L.layerGroup().addTo(map);
const stopLayer = L.layerGroup().addTo(map);
const busLayer = L.layerGroup().addTo(map);

const lineSelect = document.getElementById('lineSelect');
const directionSelect = document.getElementById('directionSelect');
const gpsState = document.getElementById('gpsState');
const currentInstructionEl = document.getElementById('currentInstruction');
const routeSummaryEl = document.getElementById('routeSummary');
const nextStopEl = document.getElementById('nextStopLabel');
const distanceEl = document.getElementById('distanceLabel');
const progressEl = document.getElementById('progressLabel');
const routeBadgeEl = document.getElementById('routeBadge');
const demoBadgeEl = document.getElementById('demoBadge');
const startButton = document.getElementById('startButton');
const pauseButton = document.getElementById('pauseButton');
const resumeButton = document.getElementById('resumeButton');
const voiceButton = document.getElementById('voiceButton');

const demoCenter = [41.9028, 12.4964];
map.setView(demoCenter, 12);

function getActiveLine() {
  return routeData.lines?.[state.activeLineIndex] || routeData.lines?.[0];
}

function getActiveVariant() {
  const activeLine = getActiveLine();
  return activeLine?.variants?.[state.activeVariantIndex] || activeLine?.variants?.[0];
}

function safeDistanceKm(lat1, lon1, lat2, lon2) {
  const toRad = (value) => (value * Math.PI) / 180;
  const R = 6371;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function setGpsStatus(status, message) {
  state.gpsStatus = status;
  gpsState.textContent = message;
  gpsState.className = 'status-value';
  if (status === 'ok') gpsState.classList.add('ok');
  if (status === 'error') gpsState.classList.add('error');
  if (status === 'waiting') gpsState.classList.add('waiting');
}

function buildSelectOptions() {
  const lineData = routeData.lines || [];
  lineSelect.innerHTML = '';
  lineData.forEach((line, index) => {
    const option = document.createElement('option');
    option.value = index;
    option.textContent = line.name || `Linea ${index + 1}`;
    lineSelect.appendChild(option);
  });

  if (lineData.length > 0) {
    state.activeLineIndex = 0;
    lineSelect.value = '0';
  }

  syncDirections();
}

function syncDirections() {
  const line = getActiveLine();
  const directionSelectEl = directionSelect;
  directionSelectEl.innerHTML = '';

  if (!line || !line.variants || !line.variants.length) {
    return;
  }

  line.variants.forEach((variant, index) => {
    const option = document.createElement('option');
    option.value = index;
    option.textContent = variant.direction || `Direzione ${index + 1}`;
    directionSelectEl.appendChild(option);
  });

  directionSelectEl.value = String(state.activeVariantIndex);
  renderRoute();
}

function renderRoute() {
  const line = getActiveLine();
  const variant = getActiveVariant();
  if (!line || !variant) return;

  routeBadgeEl.textContent = line.name || 'Linea';
  demoBadgeEl.classList.toggle('hidden', routeData.mode !== 'demo');
  routeSummaryEl.textContent = `${variant.direction || 'Percorso'} • ${variant.stops?.length || 0} fermate`;

  routeLayer.clearLayers();
  stopLayer.clearLayers();
  busLayer.clearLayers();

  if (variant.path && variant.path.length) {
    const polyline = L.polyline(variant.path, {
      color: '#58d5ff',
      weight: 7,
      opacity: 0.95,
      smoothFactor: 1,
    });
    polyline.addTo(routeLayer);
  }

  const stops = variant.stops || [];
  stops.forEach((stop, index) => {
    const marker = L.marker([stop.lat, stop.lon], {
      icon: L.divIcon({
        html: `<div class="stop-marker ${index === state.previousStopIndex ? 'completed' : ''}">${index + 1}</div>`,
        className: 'custom-stop-icon',
        iconSize: [30, 30],
      }),
    });
    marker.bindPopup(`${index + 1}. ${stop.name}`);
    marker.addTo(stopLayer);
  });

  const bounds = L.latLngBounds(variant.path || [[41.9028, 12.4964]]);
  map.fitBounds(bounds.pad(0.2));

  if (state.currentPosition) {
    updateBusMarker(state.currentPosition);
  } else {
    const startPoint = variant.path?.[0] || [41.9028, 12.4964];
    updateBusMarker({ lat: startPoint[0], lng: startPoint[1] });
  }

  const nextStop = getNextStop();
  updateHUD();

  if (!state.isNavigating && !state.isPaused) {
    currentInstructionEl.textContent = variant.instructions?.[0]?.turn || 'Percorso pronto';
  }
}

function getNextStop() {
  const variant = getActiveVariant();
  if (!variant || !variant.stops) return null;
  const stops = variant.stops;
  const currentLat = state.currentPosition?.lat ?? stops[0]?.lat;
  const currentLng = state.currentPosition?.lng ?? stops[0]?.lon;

  if (currentLat == null || currentLng == null) return stops[0] || null;

  let bestStop = stops[0];
  let bestDistance = Number.MAX_VALUE;
  stops.forEach((stop, index) => {
    const distance = safeDistanceKm(currentLat, currentLng, stop.lat, stop.lon);
    if (distance < bestDistance) {
      bestDistance = distance;
      bestStop = stop;
    }
  });

  return bestStop;
}

function updateBusMarker(position) {
  busLayer.clearLayers();
  const busIcon = L.marker([position.lat, position.lng], {
    icon: L.divIcon({
      className: 'bus-marker-wrap',
      html: '<div class="bus-marker"></div>',
      iconSize: [40, 40],
      iconAnchor: [20, 20],
    }),
  });
  busIcon.addTo(busLayer);
}

function maybeSpeak(text) {
  if (!state.voiceEnabled || !('speechSynthesis' in window)) {
    return;
  }

  const normalized = text.trim();
  if (!normalized) return;

  const key = normalized.toLowerCase();
  if (state.lastAnnouncementKey === key) return;
  state.lastAnnouncementKey = key;

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(normalized);
  utterance.lang = 'it-IT';
  utterance.rate = 1.0;
  utterance.pitch = 1.1;
  window.speechSynthesis.speak(utterance);
}

function updateHUD() {
  const variant = getActiveVariant();
  const stops = variant?.stops || [];
  const current = state.currentPosition || { lat: stops[0]?.lat || demoCenter[0], lng: stops[0]?.lon || demoCenter[1] };

  let nextStop = null;
  let nextDistance = Number.MAX_VALUE;
  stops.forEach((stop, index) => {
    const distance = safeDistanceKm(current.lat, current.lng, stop.lat, stop.lon);
    if (distance < nextDistance) {
      nextDistance = distance;
      nextStop = { ...stop, index };
    }
  });

  if (nextStop) {
    nextStopEl.textContent = `${nextStop.name}`;
    distanceEl.textContent = `${nextStop.index === 0 ? '0.1' : nextDistance.toFixed(1)} km`;
    const currentIndex = Math.max(0, Math.min(nextStop.index, stops.length - 1));
    const instruction = variant.instructions?.[currentIndex]?.turn || 'prosegui dritto';
    currentInstructionEl.textContent = instruction;
  } else {
    nextStopEl.textContent = '—';
    distanceEl.textContent = '—';
  }

  const total = Math.max(1, stops.length - 1);
  const progress = Math.min(100, Math.round((Math.max(0, nextStop?.index || 0) / total) * 100));
  progressEl.textContent = `${progress}%`;
  state.routeProgress = progress;

  if (nextStop && nextDistance < 0.15 && nextStop.index !== state.previousStopIndex) {
    state.previousStopIndex = nextStop.index;
    const message = `Fermata ${nextStop.name}. Attenzione alla prossima fermata.`;
    maybeSpeak(message);
  }
}

function startNavigation() {
  state.isNavigating = true;
  state.isPaused = false;
  const variant = getActiveVariant();
  const firstStop = variant?.stops?.[0];

  if (!state.currentPosition && firstStop) {
    state.currentPosition = { lat: firstStop.lat, lng: firstStop.lon };
  }

  if (!navigator.geolocation) {
    setGpsStatus('error', 'GPS non supportato');
  } else {
    setGpsStatus('waiting', 'richiesta posizione');
    navigator.geolocation.getCurrentPosition(
      (position) => {
        state.currentPosition = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        };
        updateBusMarker(state.currentPosition);
        setGpsStatus('ok', 'GPS attivo');
        updateHUD();
      },
      () => {
        setGpsStatus('error', 'permesso negato');
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
    );
  }

  if (variant?.instructions?.[0]) {
    currentInstructionEl.textContent = variant.instructions[0].turn;
    maybeSpeak(`Navigazione avviata. ${variant.instructions[0].turn}.`);
  }
}

function pauseNavigation() {
  state.isPaused = true;
  state.isNavigating = false;
  currentInstructionEl.textContent = 'Navigazione in pausa';
}

function resumeNavigation() {
  state.isPaused = false;
  state.isNavigating = true;
  currentInstructionEl.textContent = 'Navigazione ripresa';
  maybeSpeak('Navigazione ripresa.');
}

function toggleVoice() {
  state.voiceEnabled = !state.voiceEnabled;
  voiceButton.classList.toggle('active', state.voiceEnabled);
  voiceButton.textContent = state.voiceEnabled ? 'VOCE ON' : 'VOCE';
  maybeSpeak(state.voiceEnabled ? 'Sintesi vocale attivata.' : 'Sintesi vocale disattivata.');
}

function simulateProgress() {
  const variant = getActiveVariant();
  if (!variant || !variant.path || !variant.path.length) return;

  if (!state.isNavigating || state.isPaused) return;

  const path = variant.path;
  let index = state.currentSegmentIndex;
  if (index >= path.length - 1) {
    index = 0;
  }

  const nextPoint = path[index + 1] || path[0];
  state.currentPosition = {
    lat: nextPoint[0],
    lng: nextPoint[1],
  };
  state.currentSegmentIndex = index + 1;
  updateBusMarker(state.currentPosition);
  updateHUD();
}

function bindEvents() {
  startButton.addEventListener('click', startNavigation);
  pauseButton.addEventListener('click', pauseNavigation);
  resumeButton.addEventListener('click', resumeNavigation);
  voiceButton.addEventListener('click', toggleVoice);

  lineSelect.addEventListener('change', (event) => {
    state.activeLineIndex = Number(event.target.value);
    state.activeVariantIndex = 0;
    syncDirections();
  });

  directionSelect.addEventListener('change', (event) => {
    state.activeVariantIndex = Number(event.target.value);
    renderRoute();
  });

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        state.currentPosition = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        };
        setGpsStatus('ok', 'GPS attivo');
        updateBusMarker(state.currentPosition);
      },
      () => setGpsStatus('error', 'permesso negato'),
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
    );
  } else {
    setGpsStatus('error', 'GPS non supportato');
  }
}

buildSelectOptions();
renderRoute();
bindEvents();
setInterval(simulateProgress, 3000);
