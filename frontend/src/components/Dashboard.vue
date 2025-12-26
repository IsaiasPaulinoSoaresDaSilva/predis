<template>
  <div class="dashboard-content">
    <main>
       <div class="card">
        <h2>Probabilidade de Risco ({{ selectedRegionName }})</h2>
        <div class="risk-indicator-container">
          <div class="risk-indicator" :style="{ '--risk-color': riskColor, '--pulse-duration': pulseDuration }"></div>
          <span class="risk-level-text">{{ (riskProbability * 100).toFixed(0) }}%</span>
        </div>
        <p v-if="message" class="warning-message">{{ message }}</p>
      </div>
      <div class="card">
        <h2>Tendência de Chuvas (Histórico)</h2>
        <canvas ref="rainfallChartCanvas"></canvas>
      </div>
       <div class="card map-card">
        <Map :selectedRegion="selectedRegion" @region-selected="handleRegionSelection" />
      </div>
      <div class="card xai-card">
        <h2>Fatores de Risco (XAI)</h2>
        <div v-if="featureImportance.precipitacao_mm !== undefined" class="feature-importance">
          <div class="feature">
            <span>Precipitação (mm)</span>
            <div class="bar-container">
              <div class="bar" :style="{ width: (featureImportance.precipitacao_mm * 100) + '%' }"></div>
            </div>
            <span>{{ (featureImportance.precipitacao_mm * 100).toFixed(1) }}%</span>
          </div>
          <div class="feature">
            <span>Nível do Rio (m)</span>
            <div class="bar-container">
              <div class="bar" :style="{ width: (featureImportance.nivel_rio_m * 100) + '%' }"></div>
            </div>
            <span>{{ (featureImportance.nivel_rio_m * 100).toFixed(1) }}%</span>
          </div>
        </div>
        <p v-else class="xai-waiting-message">Aguardando dados para análise...</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, shallowRef } from 'vue';
import Chart from 'chart.js/auto';
import axios from 'axios';
import Map from './Map.vue'; // Importando o componente de Mapa

// --- Props ---
const props = defineProps({
  selectedRegion: String,
  selectedRegionName: String,
});

// --- Emits ---
const emit = defineEmits(['region-selected']);

// --- Refs e Variáveis Reativas ---
const riskProbability = ref(0);
const riskLevel = ref(0); // <-- Adicionado
const featureImportance = ref({});
const message = ref('');
const historicalData = ref([]);
const simulationIndex = ref(0);
const rainfallChartCanvas = ref(null);

const rainfallChart = shallowRef(null);

// --- Propriedades Computadas ---
const riskColor = computed(() => {
  if (riskLevel.value === 2) return 'red';
  if (riskLevel.value === 1) return 'orange';
  return 'var(--primary-green)';
});

const pulseDuration = computed(() => {
  const duration = 1.5 - (riskProbability.value * 1.2);
  return `${Math.max(duration, 0.3)}s`;
});

// --- Funções ---

const handleRegionSelection = (regionId) => {
  emit('region-selected', regionId);
}

const fetchPrediction = async (regionId) => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/predict', {
      region: regionId,
    });
    
    riskProbability.value = response.data.risk_probability;
    riskLevel.value = response.data.risk_level;
    featureImportance.value = response.data.feature_importance;
    message.value = response.data.message;

  } catch (error) {
    console.error("Erro ao buscar predição da API:", error);
    message.value = "Não foi possível conectar ao servidor de previsão.";
    riskProbability.value = 0;
    riskLevel.value = 0;
    featureImportance.value = {};
  }
};

const fetchHistoricalData = async (regionId) => {
  try {
    // Nota: A API backend ainda não suporta busca por região.
    // Por enquanto, sempre buscamos os mesmos dados.
    const response = await axios.get(`http://127.0.0.1:8000/historical_data?region=${regionId}`);
    if (response.data && response.data.length > 0) {
      historicalData.value = response.data;
      initializeChart(response.data);
      simulationIndex.value = 0; // Reinicia a simulação
      if (!simulationInterval) {
        startSimulation();
      }
    } else {
      message.value = "Dados históricos não encontrados ou vazios para esta região.";
      historicalData.value = [];
      if(rainfallChart.value) rainfallChart.value.destroy();
    }
  } catch (error) {
    console.error("Erro ao buscar dados históricos:", error);
    message.value = "Não foi possível carregar os dados históricos do servidor.";
  }
};

const initializeChart = (data) => {
  if (!rainfallChartCanvas.value) return;
  const ctx = rainfallChartCanvas.value.getContext('2d');
  
  if (rainfallChart.value) {
    rainfallChart.value.destroy();
  }

  rainfallChart.value = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map(d => new Date(d.data).toLocaleDateString()),
      datasets: [
        {
          label: 'Precipitação (mm)',
          data: data.map(d => d.precipitacao_mm),
          borderColor: '#007A33',
          backgroundColor: 'rgba(0, 122, 51, 0.1)',
          fill: true,
          tension: 0.4,
        },
        {
          label: 'Nível do Rio (m)',
          data: data.map(d => d.nivel_rio_m),
          borderColor: '#005f87',
          backgroundColor: 'rgba(0, 95, 135, 0.1)',
          fill: true,
          tension: 0.4,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { type: 'linear', display: true, position: 'left', title: { display: true, text: 'Precipitação (mm)'}},
        y1: { type: 'linear', display: true, position: 'right', title: {display: true, text: 'Nível do Rio (m)'}, grid: { drawOnChartArea: false }}
      }
    }
  });
};

let simulationInterval = null;
const startSimulation = () => {
  if (simulationInterval) clearInterval(simulationInterval);

  simulationInterval = setInterval(() => {
    // A cada X segundos, apenas pede uma nova predição para a região atual.
    // O backend é responsável por buscar os dados mais recentes.
    if (props.selectedRegion) {
       fetchPrediction(props.selectedRegion);
    }
  }, 10000); // Aumentando o intervalo para 10s para simular uma atualização mais realista
};

// --- Watchers ---
watch(() => props.selectedRegion, (newRegion) => {
  if (newRegion) {
    // Quando a região muda, busca os dados históricos para o gráfico
    fetchHistoricalData(newRegion);
    // E também busca uma predição imediata para a nova região
    fetchPrediction(newRegion);
  }
}, { immediate: true }); // `immediate: true` garante que rode na primeira vez que o componente é montado

// --- Hook de Ciclo de Vida ---
onMounted(() => {
  // A simulação de atualização periódica começa aqui
  startSimulation();
});
</script>

<style scoped>
.dashboard-content {
  padding: 2rem;
  width: 100%;
  background-color: var(--main-bg-color, #f4f6f8);
}

main {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  grid-template-rows: auto;
  gap: 2rem;
}

.card {
  background-color: var(--card-bg-color, #ffffff);
  border-radius: 8px;
  box-shadow: 0 4px 12px var(--shadow-color, rgba(0, 0, 0, 0.1));
  padding: 1.5rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px var(--shadow-color, rgba(0, 0, 0, 0.1));
}

/* Specific grid placements for larger screens */
@media (min-width: 992px) {
  main {
    grid-template-columns: 1fr 1fr 1fr;
    grid-template-rows: auto auto;
  }
  .card:nth-child(1) { /* Risco */
    grid-column: 1 / 2;
  }
  .card:nth-child(2) { /* Gráfico */
    grid-column: 2 / 4;
    grid-row: 1 / 2;
  }
  .map-card { /* Mapa */
    grid-column: 1 / 2;
    grid-row: 2 / 3;
  }
  .xai-card { /* XAI */
    grid-column: 2 / 4;
    grid-row: 2 / 3;
  }
}

.card h2 {
  font-weight: 400;
  margin-top: 0;
  border-bottom: 2px solid var(--primary-green, #007A33);
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}
/* All other specific styles like .risk-indicator-container, .feature-importance etc. are assumed to be here from previous steps */
.risk-indicator-container{display:flex;justify-content:center;align-items:center;height:150px;position:relative}.risk-indicator{width:100px;height:100px;background-color:var(--risk-color);border-radius:50%;position:relative;animation:pulse var(--pulse-duration) infinite ease-in-out;transition:background-color .5s ease}.risk-level-text{position:absolute;font-size:1.5rem;font-weight:700;color:#fff}.warning-message{text-align:center;font-weight:700;color:#ffa500;margin-top:1rem}.xai-waiting-message{text-align:center;color:#888;margin-top:1rem}.feature-importance .feature{margin-bottom:1rem}.feature-importance .feature span{display:block;margin-bottom:.25rem}.feature-importance .bar-container{background-color:#e0e0e0;border-radius:4px;height:20px;width:100%}.feature-importance .bar{background-color:var(--primary-green);height:100%;border-radius:4px;transition:width .5s ease-in-out}.feature-importance .feature{display:grid;grid-template-columns:120px 1fr 50px;gap:1rem;align-items:center}canvas{max-height:300px}
</style>
