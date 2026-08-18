<template>
  <div class="map-container card">
    <div id="leaflet-map"></div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, watch } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import regionsGeoJSON from '../assets/sjc-regions.json';

const props = defineProps({
  selectedRegion: String
});
const emit = defineEmits(['region-selected']);

let map = null;
let geoJsonLayer = null;

// --- Estilos do Mapa ---
const defaultStyle = {
  color: "#1F7A6C",
  weight: 2,
  opacity: 0.8,
  fillColor: "#1F7A6C",
  fillOpacity: 0.18
};

const hoverStyle = {
  fillColor: "#1F7A6C",
  fillOpacity: 0.45,
  weight: 3,
};

// Nota: propositalmente NÃO usamos as cores de risco (teal/âmbar/tijolo)
// aqui — a seleção no mapa é neutra, para não sugerir visualmente que a
// região selecionada tem um nível de risco específico.
const selectedStyle = {
  fillColor: "#1B2B27",
  fillOpacity: 0.35,
  color: "#1B2B27",
  weight: 4,
};


// --- Funções do Mapa ---

function onEachFeature(feature, layer) {
  const props = feature.properties;
  const bairros = (props.bairros_referencia || []).join(', ');
  layer.bindPopup(`
    <strong>${props.nome}</strong><br/>
    <em>Bairros de referência:</em> ${bairros}<br/>
    <em>Curso d'água:</em> ${props.curso_dagua || '—'}<br/>
    <em>Histórico:</em> ${props.historico_risco || '—'}
  `);

  layer.on({
    mouseover: (e) => {
      const l = e.target;
      if (feature.properties.id !== props.selectedRegion) {
        l.setStyle(hoverStyle);
      }
    },
    mouseout: (e) => {
       if (feature.properties.id !== props.selectedRegion) {
        geoJsonLayer.resetStyle(e.target);
      }
    },
    click: (e) => {
      emit('region-selected', feature.properties.id);
      map.fitBounds(e.target.getBounds());
    }
  });
}

function highlightSelectedRegion(regionId) {
  if (!geoJsonLayer) return;
  geoJsonLayer.eachLayer(layer => {
    if (layer.feature.properties.id === regionId) {
      layer.setStyle(selectedStyle);
      layer.bringToFront();
    } else {
      layer.setStyle(defaultStyle);
    }
  });
}

// --- Ciclo de Vida ---
onMounted(() => {
  map = L.map('leaflet-map', {
    zoomControl: false,
    attributionControl: false
  }).setView([-23.1794, -45.8869], 11); // Centro de São José dos Campos (SP)

  geoJsonLayer = L.geoJSON(regionsGeoJSON, {
    style: defaultStyle,
    onEachFeature: onEachFeature
  }).addTo(map);

  map.fitBounds(geoJsonLayer.getBounds());

  // Garante que a região selecionada inicialmente seja destacada
  highlightSelectedRegion(props.selectedRegion);
});

onBeforeUnmount(() => {
  if (map) {
    map.remove();
  }
});

watch(() => props.selectedRegion, (newRegionId) => {
  highlightSelectedRegion(newRegionId);
});

</script>

<style scoped>
.map-container {
  padding: 0;
  overflow: hidden; /* Garante que o mapa fique contido no card */
}

#leaflet-map {
  width: 100%;
  height: 100%;
  min-height: 350px; /* Altura mínima para o mapa ser visível */
  background-color: #DCE9E4; /* Cor de "oceano", alinhada à paleta */
}
</style>
