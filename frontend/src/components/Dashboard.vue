<template>
  <div class="dashboard-content">
    <main>
      <!-- Régua de risco (elemento-assinatura) + contexto da região -->
      <div class="card gauge-card">
        <h2>Risco atual — {{ selectedRegionName }}</h2>
        <div class="risk-indicator-container">
          <StaffGauge :probability="riskProbability" :level="riskLevel" size="lg" />
          <div class="risk-readout">
            <span class="risk-level-text mono">{{ (riskProbability * 100).toFixed(0) }}%</span>
            <span class="risk-chip" :class="`risk-chip--${riskLevel}`">{{ riskLevelLabel }}</span>
          </div>
        </div>
        <p v-if="isLoadingPrediction" class="loading-message">Atualizando previsão...</p>
        <p v-else-if="isConnectionError" class="error-message">⚠️ {{ message }}</p>
        <p v-else-if="message" class="warning-message">{{ message }}</p>
      </div>

      <div class="card region-info-card" v-if="regionInfo">
        <h2>Sobre a região</h2>
        <dl class="region-info">
          <dt>Bairros de referência</dt>
          <dd>{{ (regionInfo.bairros_referencia || []).join(', ') || '—' }}</dd>
          <dt>Curso d'água</dt>
          <dd>{{ regionInfo.curso_dagua || '—' }}</dd>
          <dt>Histórico relatado</dt>
          <dd>{{ regionInfo.historico_risco || '—' }}</dd>
        </dl>
      </div>

      <div class="card chart-card">
        <h2>Chuva e nível do rio (histórico real)</h2>
        <p v-if="isLoadingHistorical" class="loading-message">Carregando dados históricos...</p>
        <canvas ref="rainfallChartCanvas"></canvas>
      </div>

      <div class="card map-card">
        <Map :selectedRegion="selectedRegion" @region-selected="handleRegionSelection" />
      </div>

      <div class="card comparison-card">
        <h2>Comparativo entre regiões</h2>
        <RegionComparison
          :regions="regionsList"
          :selectedRegion="selectedRegion"
          @region-selected="handleRegionSelection"
        />
      </div>

      <div class="card xai-card">
        <h2>Fatores de Risco (XAI)</h2>
        <div v-if="topFeatures.length > 0" class="feature-importance">
          <div class="feature" v-for="feat in topFeatures" :key="feat.key">
            <span>{{ feat.label }}</span>
            <div class="bar-container">
              <div class="bar" :style="{ width: (feat.value * 100) + '%' }"></div>
            </div>
            <span class="mono">{{ (feat.value * 100).toFixed(1) }}%</span>
          </div>
        </div>
        <p v-else class="xai-waiting-message">Aguardando dados para análise...</p>
      </div>

      <div class="card history-card">
        <h2>Histórico de predições</h2>
        <PredictionHistory :region="selectedRegion" :limit="8" />
      </div>

      <div class="card sources-card">
        <h2>Fontes dos dados</h2>
        <DataSourceBadges />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, shallowRef } from 'vue';
import Chart from 'chart.js/auto';
import axios from 'axios';
import Map from './Map.vue';
import StaffGauge from './StaffGauge.vue';
import RegionComparison from './RegionComparison.vue';
import PredictionHistory from './PredictionHistory.vue';
import DataSourceBadges from './DataSourceBadges.vue';
import regionsGeoJSON from '../assets/sjc-regions.json';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// --- Props ---
const props = defineProps({
  selectedRegion: String,
  selectedRegionName: String,
});

// --- Emits ---
const emit = defineEmits(['region-selected']);

// Lista de regiões derivada do GeoJSON (id + nome), evita mais uma lista
// hardcoded além das já existentes em App.vue/Sidebar.vue.
const regionsList = regionsGeoJSON.features.map(f => ({ id: f.properties.id, name: f.properties.nome }));

// --- Refs e Variáveis Reativas ---
const riskProbability = ref(0);
const riskLevel = ref(0);
const featureImportance = ref({});
const message = ref('');
const historicalData = ref([]);
const simulationIndex = ref(0);
const rainfallChartCanvas = ref(null);
const isLoadingPrediction = ref(false);
const isLoadingHistorical = ref(false);
const isConnectionError = ref(false); // true só em falha real de rede/servidor,
                                       // diferente de um aviso do backend (ex.: "dados insuficientes")

const rainfallChart = shallowRef(null);

// --- Propriedades Computadas ---
const riskLevelLabel = computed(() => ({ 0: 'baixo', 1: 'moderado', 2: 'alto' }[riskLevel.value] || 'baixo'));

const regionInfo = computed(() => {
  const feature = regionsGeoJSON.features.find(f => f.properties.id === props.selectedRegion);
  return feature ? feature.properties : null;
});

// Rótulos legíveis para as features usadas pelo modelo (ver backend/model.py)
const FEATURE_LABELS = {
  precipitacao_mm: 'Precipitação do dia (mm)',
  nivel_rio_m: 'Nível do rio/córrego (m)',
  precipitacao_acumulada_3d: 'Chuva acumulada (3 dias)',
  precipitacao_max_3d: 'Chuva máxima (3 dias)',
  media_movel_nivel_rio_3d: 'Média móvel do nível do rio (3d)',
  variacao_nivel_rio_1d: 'Variação do nível do rio (1d)',
  subida_rio_14d: 'Subida do rio vs. mínima recente (14d)',
  previsao_chuva_d1: 'Previsão de chuva (d+1)',
  previsao_chuva_d2: 'Previsão de chuva (d+2)',
  previsao_chuva_d3: 'Previsão de chuva (d+3)',
};

// Mostra as features mais relevantes primeiro, ocultando as de importância
// desprezível (ex.: previsões zeradas fora da estação chuvosa)
const topFeatures = computed(() => {
  return Object.entries(featureImportance.value || {})
    .map(([key, value]) => ({ key, value, label: FEATURE_LABELS[key] || key }))
    .filter(f => f.value > 0.005)
    .sort((a, b) => b.value - a.value)
    .slice(0, 6);
});

// --- Funções ---

const handleRegionSelection = (regionId) => {
  emit('region-selected', regionId);
}

const fetchPrediction = async (regionId) => {
  isLoadingPrediction.value = true;
  try {
    const response = await axios.post(`${API_BASE_URL}/predict`, {
      region: regionId,
    });

    riskProbability.value = response.data.risk_probability;
    riskLevel.value = response.data.risk_level;
    featureImportance.value = response.data.feature_importance;
    message.value = response.data.message;
    isConnectionError.value = false;

  } catch (error) {
    console.error("Erro ao buscar predição da API:", error);
    message.value = "Não foi possível conectar ao servidor de previsão. Verifique se o backend está rodando.";
    isConnectionError.value = true;
    riskProbability.value = 0;
    riskLevel.value = 0;
    featureImportance.value = {};
  } finally {
    isLoadingPrediction.value = false;
  }
};

const fetchHistoricalData = async (regionId) => {
  isLoadingHistorical.value = true;
  try {
    const response = await axios.get(`${API_BASE_URL}/historical_data`, { params: { region: regionId } });
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
    isConnectionError.value = true;
  } finally {
    isLoadingHistorical.value = false;
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
          borderColor: '#1F7A6C',
          backgroundColor: 'rgba(31, 122, 108, 0.12)',
          fill: true,
          tension: 0.35,
        },
        {
          label: 'Nível do Rio (m)',
          data: data.map(d => d.nivel_rio_m),
          borderColor: '#B6402E',
          backgroundColor: 'rgba(182, 64, 46, 0.08)',
          fill: true,
          tension: 0.35,
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
  height: 100%;
  overflow-y: auto;
  background-color: var(--bg);
}

main {
  display: grid;
  /* min(300px, 100%) evita que o grid force overflow horizontal em telas
     estreitas — sem isso, uma coluna "mínima" de 300px vaza da viewport
     em qualquer tela menor que isso (ver App.vue/Sidebar.vue para o resto
     do ajuste responsivo). */
  grid-template-columns: repeat(auto-fit, minmax(min(300px, 100%), 1fr));
  grid-template-rows: auto;
  gap: 1.5rem;
}

.card {
  background-color: var(--surface);
  border: 1px solid var(--line);
  border-radius: 10px;
  box-shadow: 0 2px 10px var(--shadow-color);
  padding: 1.5rem;
}

@media (min-width: 992px) {
  main {
    grid-template-columns: repeat(3, 1fr);
  }
  .gauge-card { grid-column: 1 / 2; grid-row: 1 / 2; }
  .region-info-card { grid-column: 1 / 2; grid-row: 2 / 3; }
  .chart-card { grid-column: 2 / 4; grid-row: 1 / 2; }
  .map-card { grid-column: 2 / 3; grid-row: 2 / 3; }
  .comparison-card { grid-column: 3 / 4; grid-row: 2 / 3; }
  .xai-card { grid-column: 1 / 3; }
  .history-card { grid-column: 3 / 4; }
  .sources-card { grid-column: 1 / 4; }
}

.card h2 {
  font-size: 1.05rem;
  font-weight: 600;
  margin-top: 0;
  border-bottom: 2px solid var(--river);
  padding-bottom: 0.6rem;
  margin-bottom: 1rem;
}

.risk-indicator-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1.5rem;
  padding: 0.5rem 0 1rem;
}
.risk-readout {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}
.risk-level-text {
  font-size: 2.4rem;
  font-weight: 600;
  color: var(--ink);
  line-height: 1;
}

.warning-message {
  text-align: center;
  font-weight: 600;
  color: #8A5B1C;
  background: var(--amber-tint);
  border-radius: 6px;
  padding: 0.5rem;
  margin-top: 1rem;
}
.xai-waiting-message { text-align: center; color: var(--ink-faint); margin-top: 1rem; }

.feature-importance .feature {
  display: grid;
  grid-template-columns: 150px 1fr 55px;
  gap: 1rem;
  align-items: center;
  margin-bottom: 0.85rem;
  font-size: 0.85rem;
}
.feature-importance .bar-container {
  background-color: var(--surface-sunken);
  border-radius: 4px;
  height: 14px;
  width: 100%;
  overflow: hidden;
}
.feature-importance .bar {
  background-color: var(--river);
  height: 100%;
  border-radius: 4px;
  transition: width .5s ease-in-out;
}

canvas { max-height: 300px; }

.region-info {
  margin: 0;
  font-size: 0.85rem;
}
.region-info dt {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--ink-faint);
  margin-top: 0.85rem;
}
.region-info dt:first-child { margin-top: 0; }
.region-info dd {
  margin: 0.2rem 0 0 0;
  color: var(--ink-soft);
  line-height: 1.45;
}

.loading-message {
  text-align: center;
  color: var(--ink-faint);
  margin-top: 1rem;
  font-style: italic;
}

.error-message {
  text-align: center;
  font-weight: 600;
  color: var(--brick);
  background-color: var(--brick-tint);
  border-radius: 6px;
  padding: 0.5rem;
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .dashboard-content { padding: 1rem; }
  .risk-indicator-container { flex-wrap: wrap; justify-content: center; }
  .feature-importance .feature { grid-template-columns: 1fr; gap: 0.3rem; }
}
</style>
