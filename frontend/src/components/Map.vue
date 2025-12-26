<template>
  <div class="map-container card">
    <div id="leaflet-map"></div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, watch } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import regionsGeoJSON from '../assets/brazil-regions.json';

const props = defineProps({
  selectedRegion: String
});
const emit = defineEmits(['region-selected']);

let map = null;
let geoJsonLayer = null;

// --- Estilos do Mapa ---
const defaultStyle = {
  color: "#007A33",
  weight: 2,
  opacity: 0.8,
  fillColor: "#007A33",
  fillOpacity: 0.2
};

const hoverStyle = {
  fillColor: "#007A33",
  fillOpacity: 0.5,
  weight: 3,
};

const selectedStyle = {
  fillColor: "#007A33",
  fillOpacity: 0.7,
  color: "#004d20",
  weight: 4,
};


// --- Funções do Mapa ---

function onEachFeature(feature, layer) {
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
  }).setView([-14.2350, -51.9253], 4); // Centro do Brasil

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
  background-color: #aadaff; /* Cor de "oceano" */
}
</style>
