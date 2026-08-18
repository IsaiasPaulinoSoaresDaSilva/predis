<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h3>Regiões de SJC</h3>
      <p class="sidebar-subtitle">Estudo de caso: São José dos Campos</p>
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
  { id: 'centro', name: 'Centro' },
  { id: 'norte', name: 'Norte' },
  { id: 'sul', name: 'Sul' },
  { id: 'leste', name: 'Leste' },
  { id: 'oeste', name: 'Oeste' },
  { id: 'sudeste', name: 'Sudeste' },
]);

</script>

<style scoped>
.sidebar {
  width: 230px;
  background-color: var(--surface);
  padding: 1.5rem 1rem;
  border-right: 1px solid var(--line);
  display: flex;
  flex-direction: column;
}

.sidebar-header h3 {
  margin: 0 0 0.25rem 0;
  color: var(--river-dark);
  font-weight: 700;
  font-size: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--river);
}

.sidebar-subtitle {
  margin: 0.5rem 0 1.25rem 0;
  font-size: 0.75rem;
  color: var(--ink-faint);
}

.region-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.region-item {
  padding: 0.75rem 1rem;
  margin-bottom: 0.35rem;
  border-radius: 6px;
  border-left: 3px solid transparent;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease;
  font-weight: 500;
  font-size: 0.92rem;
  color: var(--ink);
}

.region-item:hover {
  background-color: var(--surface-sunken);
}

.region-item.active {
  background-color: var(--river-tint);
  border-left-color: var(--river);
  color: var(--river-dark);
  font-weight: 700;
}

@media (max-width: 768px) {
  .sidebar {
    width: auto;
    border-right: none;
    border-bottom: 1px solid var(--line);
    padding: 1rem;
  }
  .sidebar-header { display: none; }
  .region-list {
    display: flex;
    gap: 0.5rem;
    overflow-x: auto;
    padding-bottom: 0.25rem;
    -webkit-overflow-scrolling: touch;
  }
  .region-item {
    margin-bottom: 0;
    white-space: nowrap;
    border-left: none;
    border-bottom: 3px solid transparent;
    border-radius: 6px 6px 0 0;
  }
  .region-item.active {
    border-left-color: transparent;
    border-bottom-color: var(--river);
  }
}
</style>
