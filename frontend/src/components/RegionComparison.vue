<template>
  <div class="region-comparison">
    <button
      v-for="r in regions"
      :key="r.id"
      type="button"
      class="region-comparison__item"
      :class="{ 'region-comparison__item--active': r.id === selectedRegion }"
      @click="$emit('region-selected', r.id)"
    >
      <StaffGauge
        size="sm"
        :probability="readings[r.id]?.risk_probability ?? 0"
        :level="readings[r.id]?.risk_level ?? 0"
      />
      <span class="region-comparison__name">{{ r.name }}</span>
      <span
        v-if="readings[r.id]"
        class="risk-chip mono"
        :class="`risk-chip--${readings[r.id].risk_level}`"
      >{{ Math.round(readings[r.id].risk_probability * 100) }}%</span>
      <span v-else class="region-comparison__loading">…</span>
    </button>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue';
import axios from 'axios';
import StaffGauge from './StaffGauge.vue';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
const REFRESH_MS = 60000; // bem mais espaçado que o polling da região em foco (10s)

const props = defineProps({
  regions: { type: Array, required: true },
  selectedRegion: String,
});
defineEmits(['region-selected']);

const readings = ref({});

async function fetchAll() {
  const regionIds = props.regions.map(r => r.id);
  const results = await Promise.allSettled(
    regionIds.map(id => axios.post(`${API_BASE_URL}/predict`, { region: id }))
  );
  results.forEach((result, i) => {
    if (result.status === 'fulfilled') {
      readings.value = { ...readings.value, [regionIds[i]]: result.value.data };
    }
  });
}

let interval = null;

onMounted(() => {
  fetchAll();
  interval = setInterval(fetchAll, REFRESH_MS);
});

onBeforeUnmount(() => {
  if (interval) clearInterval(interval);
});
</script>

<style scoped>
.region-comparison {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(84px, 1fr));
  gap: 0.75rem;
}

.region-comparison__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.75rem 0.5rem;
  cursor: pointer;
  font-family: var(--font-body);
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.region-comparison__item:hover {
  border-color: var(--river);
  transform: translateY(-2px);
}

.region-comparison__item--active {
  border-color: var(--river);
  background: var(--river-tint);
}

.region-comparison__name {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--ink);
}

.region-comparison__loading {
  font-family: var(--font-mono);
  color: var(--ink-faint);
  font-size: 0.75rem;
}
</style>
