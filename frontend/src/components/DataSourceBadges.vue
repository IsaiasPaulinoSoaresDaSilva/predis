<template>
  <ul class="data-sources">
    <li v-for="s in sources" :key="s.label" class="data-sources__item">
      <span class="data-sources__dot" :class="`data-sources__dot--${s.kind}`"></span>
      <div>
        <p class="data-sources__label">{{ s.label }}</p>
        <p class="data-sources__detail">{{ s.detail }}</p>
      </div>
      <span class="data-sources__tag mono">{{ s.tagText }}</span>
    </li>
  </ul>
</template>

<script setup>
// Transparência de proveniência dos dados — ver backend/connectors/ e
// IMPLEMENTATION_PLAN.md para o racional completo de cada fonte.
const sources = [
  {
    label: 'Precipitação',
    detail: 'Open-Meteo Archive (ERA5), por coordenada real de cada região.',
    kind: 'real',
    tagText: 'real',
  },
  {
    label: 'Nível do rio',
    detail: 'Estação real da ANA em SJC (Rio Jaguari) + calibração de exposição por região.',
    kind: 'derived',
    tagText: 'real + calibrado',
  },
  {
    label: 'Previsão (3 dias)',
    detail: 'Open-Meteo Forecast, ao vivo, por coordenada real.',
    kind: 'real',
    tagText: 'real',
  },
];
</script>

<style scoped>
.data-sources {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.data-sources__item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: start;
  gap: 0.6rem;
}

.data-sources__dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  margin-top: 0.35rem;
}
.data-sources__dot--real { background: var(--river); }
.data-sources__dot--derived { background: var(--amber); }

.data-sources__label {
  margin: 0;
  font-weight: 600;
  font-size: 0.88rem;
  color: var(--ink);
}
.data-sources__detail {
  margin: 0.15rem 0 0 0;
  font-size: 0.78rem;
  color: var(--ink-soft);
  line-height: 1.4;
}

.data-sources__tag {
  font-size: 0.68rem;
  color: var(--ink-faint);
  white-space: nowrap;
  padding-top: 0.2rem;
}
</style>
