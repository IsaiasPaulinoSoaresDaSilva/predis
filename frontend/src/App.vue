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

const regions = ref([
  { id: 'sul', name: 'Região Sul' },
  { id: 'sudeste', name: 'Região Sudeste' },
  { id: 'centro-oeste', name: 'Região Centro-Oeste' },
  { id: 'nordeste', name: 'Região Nordeste' },
  { id: 'norte', name: 'Região Norte' },
]);

const selectedRegion = ref('sudeste'); // Região inicial padrão

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

.main-layout {
  display: flex;
  flex-grow: 1; /* Ocupa o restante da altura */
  overflow: hidden; /* Evita que o conteúdo principal cause scroll na página inteira */
}
</style>
