<template>
  <div class="prediction-history">
    <p v-if="isLoading" class="loading-message">Carregando histórico…</p>
    <p v-else-if="records.length === 0" class="prediction-history__empty">
      Nenhuma predição registrada ainda para esta região — cada consulta ao
      modelo fica salva aqui (ver <code>GET /predictions</code>).
    </p>
    <table v-else class="prediction-history__table">
      <thead>
        <tr>
          <th>Quando</th>
          <th>Nível</th>
          <th>Probabilidade</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="rec in records" :key="rec.id">
          <td class="mono">{{ formatWhen(rec.created_at) }}</td>
          <td>
            <span class="risk-chip" :class="`risk-chip--${rec.risk_level}`">{{ levelLabel(rec.risk_level) }}</span>
          </td>
          <td class="mono">{{ (rec.risk_probability * 100).toFixed(1) }}%</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const props = defineProps({
  region: { type: String, required: true },
  limit: { type: Number, default: 8 },
});

const records = ref([]);
const isLoading = ref(false);

async function fetchHistory() {
  isLoading.value = true;
  try {
    const response = await axios.get(`${API_BASE_URL}/predictions`, {
      params: { region: props.region, limit: props.limit },
    });
    records.value = response.data || [];
  } catch (error) {
    console.error('Erro ao buscar histórico de predições:', error);
    records.value = [];
  } finally {
    isLoading.value = false;
  }
}

function levelLabel(level) {
  return { 0: 'baixo', 1: 'moderado', 2: 'alto' }[level] || '—';
}

function formatWhen(iso) {
  try {
    return new Date(iso).toLocaleString('pt-BR', {
      day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

// `immediate: true` cobre a busca inicial — não precisa de um onMounted à parte.
watch(() => props.region, fetchHistory, { immediate: true });

defineExpose({ fetchHistory });
</script>

<style scoped>
.prediction-history__table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}
.prediction-history__table th {
  text-align: left;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--ink-faint);
  font-weight: 500;
  padding: 0.4rem 0.5rem;
  border-bottom: 1px solid var(--line);
}
.prediction-history__table td {
  padding: 0.5rem;
  border-bottom: 1px solid var(--line);
  color: var(--ink);
}
.prediction-history__table tr:last-child td {
  border-bottom: none;
}
.prediction-history__empty {
  color: var(--ink-soft);
  font-size: 0.85rem;
  line-height: 1.5;
}
.prediction-history__empty code {
  font-family: var(--font-mono);
  background: var(--surface-sunken);
  padding: 0.1rem 0.3rem;
  border-radius: 4px;
}
</style>
