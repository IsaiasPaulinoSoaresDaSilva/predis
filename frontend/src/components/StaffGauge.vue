<template>
  <svg
    class="staff-gauge"
    :class="`staff-gauge--${size}`"
    viewBox="0 0 60 220"
    role="img"
    :aria-label="`Régua de risco: ${Math.round(probability * 100)}%, nível ${levelLabel}`"
  >
    <!-- Corpo da régua (fundo neutro) -->
    <rect x="18" y="6" width="24" height="208" rx="4" class="staff-gauge__body" />

    <!-- Faixas de risco pintadas (baixo / moderado / alto), como uma
         régua linimétrica real de estação fluviométrica -->
    <rect x="18" y="6" :height="bandHeights.alto" width="24" class="staff-gauge__band staff-gauge__band--alto" />
    <rect x="18" :y="6 + bandHeights.alto" :height="bandHeights.moderado" width="24" class="staff-gauge__band staff-gauge__band--moderado" />
    <rect x="18" :y="6 + bandHeights.alto + bandHeights.moderado" :height="bandHeights.baixo" width="24" rx="0" class="staff-gauge__band staff-gauge__band--baixo" />

    <!-- Marcações (tick marks) a cada 10% -->
    <g class="staff-gauge__ticks">
      <line v-for="t in ticks" :key="t" x1="14" :y1="tickY(t)" x2="18" :y2="tickY(t)" />
    </g>

    <!-- Ponteiro da leitura atual -->
    <g :transform="`translate(0, ${pointerY})`" class="staff-gauge__pointer-group">
      <polygon points="0,0 12,-6 12,6" class="staff-gauge__pointer" :class="levelClass" />
      <line x1="12" y1="0" x2="46" y2="0" class="staff-gauge__pointer-line" :class="levelClass" />
    </g>

    <rect x="18" y="6" width="24" height="208" rx="4" class="staff-gauge__outline" />
  </svg>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  probability: { type: Number, default: 0 },
  level: { type: Number, default: 0 },
  size: { type: String, default: 'lg' }, // 'lg' | 'sm'
});

const TRACK_TOP = 6;
const TRACK_HEIGHT = 208;

// Mesmos limiares (aproximados em % de probabilidade) usados como
// referência visual — as faixas na régua são ilustrativas do range de
// probabilidade, não os limiares exatos do modelo (que combinam várias
// features, não só uma probabilidade escalar).
const bandHeights = {
  alto: TRACK_HEIGHT * 0.25,
  moderado: TRACK_HEIGHT * 0.35,
  baixo: TRACK_HEIGHT * 0.40,
};

const ticks = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100];
function tickY(pct) {
  const clamped = Math.min(Math.max(pct, 0), 100);
  return TRACK_TOP + TRACK_HEIGHT * (1 - clamped / 100);
}

const pointerY = computed(() => tickY(props.probability * 100));

const levelClass = computed(() => `staff-gauge__pointer--${props.level}`);
const levelLabel = computed(() => ({ 0: 'baixo', 1: 'moderado', 2: 'alto' })[props.level] || 'baixo');
</script>

<style scoped>
.staff-gauge {
  width: 60px;
  height: 220px;
  overflow: visible;
}
.staff-gauge--sm {
  width: 30px;
  height: 110px;
}

.staff-gauge__body {
  fill: var(--surface-sunken);
}
.staff-gauge__outline {
  fill: none;
  stroke: var(--ink);
  stroke-opacity: 0.18;
  stroke-width: 1.5;
}
.staff-gauge__band {
  opacity: 0.55;
}
.staff-gauge__band--baixo { fill: var(--river); }
.staff-gauge__band--moderado { fill: var(--amber); }
.staff-gauge__band--alto { fill: var(--brick); }

.staff-gauge__ticks line {
  stroke: var(--ink);
  stroke-opacity: 0.35;
  stroke-width: 1.5;
}

.staff-gauge__pointer-group {
  transition: transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}
.staff-gauge__pointer {
  stroke: var(--surface);
  stroke-width: 1.5;
}
.staff-gauge__pointer-line {
  stroke-width: 2.5;
  stroke-dasharray: 2 2;
}
.staff-gauge__pointer--0, .staff-gauge__pointer-line.staff-gauge__pointer--0 { fill: var(--river-dark); stroke: var(--river-dark); }
.staff-gauge__pointer--1, .staff-gauge__pointer-line.staff-gauge__pointer--1 { fill: #8A5B1C; stroke: #8A5B1C; }
.staff-gauge__pointer--2, .staff-gauge__pointer-line.staff-gauge__pointer--2 { fill: var(--brick); stroke: var(--brick); }
</style>
