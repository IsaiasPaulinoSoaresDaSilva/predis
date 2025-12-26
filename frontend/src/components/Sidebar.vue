<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h3>Regiões</h3>
    </div>
    <ul class="region-list">
      <li 
        v-for="region in regions" 
        :key="region.id"
        class="region-item"
        :class="{ active: region.id === selectedRegion }"
        @click="$emit('region-selected', region.id)"
      >
        {{ region.name }}
      </li>
    </ul>
  </aside>
</template>

<script setup>
import { ref } from 'vue';

defineProps({
  selectedRegion: String
});

defineEmits(['region-selected']);

const regions = ref([
  { id: 'sul', name: 'Região Sul' },
  { id: 'sudeste', name: 'Região Sudeste' },
  { id: 'centro-oeste', name: 'Região Centro-Oeste' },
  { id: 'nordeste', name: 'Região Nordeste' },
  { id: 'norte', name: 'Região Norte' },
]);

</script>

<style scoped>
.sidebar {
  width: 250px;
  background-color: #ffffff;
  padding: 1.5rem;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.sidebar-header h3 {
  margin: 0 0 1rem 0;
  color: var(--primary-green, #007A33);
  font-weight: 700;
  border-bottom: 2px solid var(--primary-green, #007A33);
  padding-bottom: 0.5rem;
}

.region-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.region-item {
  padding: 0.8rem 1rem;
  margin-bottom: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s ease, color 0.3s ease;
  font-weight: 500;
}

.region-item:hover {
  background-color: #f0f0f0;
}

.region-item.active {
  background-color: var(--primary-green, #007A33);
  color: #ffffff;
  font-weight: 700;
}
</style>
