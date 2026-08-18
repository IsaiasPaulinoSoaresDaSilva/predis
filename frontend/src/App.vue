<template>
  <div id="app-container">
    <Navbar />
    <div class="main-layout">
      <Sidebar 
        :selectedRegion="selectedRegion"
        @region-selected="handleRegionSelection" 
      />
      <Dashboard 
        :selectedRegion="selectedRegion"
        :selectedRegionName="selectedRegionName"
        @region-selected="handleRegionSelection"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import Navbar from './components/Navbar.vue';
import Sidebar from './components/Sidebar.vue';
import Dashboard from './components/Dashboard.vue';

// Regiões administrativas de São José dos Campos (SP) — estudo de caso do
// PreDis. Ver frontend/src/assets/sjc-regions.json para geometria e
// contexto (bairros de referência, curso d'água, histórico de risco).
const regions = ref([
  { id: 'centro', name: 'Centro' },
  { id: 'norte', name: 'Norte' },
  { id: 'sul', name: 'Sul' },
  { id: 'leste', name: 'Leste' },
  { id: 'oeste', name: 'Oeste' },
  { id: 'sudeste', name: 'Sudeste' },
]);

const selectedRegion = ref('centro'); // Região inicial padrão

const selectedRegionName = computed(() => {
  const found = regions.value.find(r => r.id === selectedRegion.value);
  return found ? found.name : 'Nenhuma';
});

function handleRegionSelection(regionId) {
  selectedRegion.value = regionId;
}
</script>

<style>
#app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

@media (max-width: 768px) {
  #app-container {
    height: auto;
    min-height: 100vh;
  }
}

.main-layout {
  display: flex;
  flex-grow: 1; /* Ocupa o restante da altura */
  overflow: hidden; /* Evita que o conteúdo principal cause scroll na página inteira */
  min-width: 0; /* permite que filhos flex encolham abaixo do conteúdo intrínseco */
}

@media (max-width: 768px) {
  .main-layout {
    flex-direction: column;
    overflow: visible;
  }
}
</style>
