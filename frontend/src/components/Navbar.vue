<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <span class="brand-mark" aria-hidden="true">
        <svg viewBox="0 0 20 20"><rect width="20" height="20" rx="4" fill="var(--river)"/><rect x="8" y="3" width="4" height="14" fill="var(--surface)"/><rect x="8" y="7" width="4" height="2.6" fill="var(--amber)"/><rect x="8" y="12" width="4" height="2.6" fill="var(--brick)"/></svg>
      </span>
      <h1>PreDis</h1>
      <span class="case-study-tag">Estudo de caso: São José dos Campos</span>
    </div>
    <div class="navbar-status">
      <span class="status-dot" aria-hidden="true"></span>
      <span class="status-text mono">{{ nowLabel }}</span>
    </div>
    <div class="navbar-links">
      <button type="button" class="nav-link nav-link--button" @click="showAbout = true">Sobre</button>
      <a
        href="https://github.com/IsaiasPaulinoSoaresDaSilva/predis"
        target="_blank"
        rel="noopener noreferrer"
        class="nav-link"
      >Contato</a>
    </div>

    <div v-if="showAbout" class="about-overlay" @click.self="showAbout = false">
      <div class="about-modal">
        <h2>Sobre o PreDis</h2>
        <p>
          O <strong>PreDis</strong> é um protótipo de sistema de previsão de
          enchentes que aplica machine learning (ensemble RandomForest +
          GradientBoosting) a dados meteorológicos e fluviométricos reais
          para estimar o risco de inundação.
        </p>
        <p>
          Este estudo de caso aplica o PreDis ao município de
          <strong>São José dos Campos (SP)</strong>, cortado pelo Rio Paraíba
          do Sul e por córregos historicamente associados a alagamentos, como
          referência concreta em vez de uma abordagem genérica por
          macrorregião do país. Chuva real (Open-Meteo Archive) e nível de
          rio real (estação da ANA em SJC) — ver painel "Fontes dos dados".
        </p>
        <button type="button" class="close-button" @click="showAbout = false">Fechar</button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue';

const showAbout = ref(false);
const nowLabel = ref('');

function updateClock() {
  nowLabel.value = new Date().toLocaleString('pt-BR', {
    day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit',
  });
}

let clockInterval = null;
onMounted(() => {
  updateClock();
  clockInterval = setInterval(updateClock, 30000);
});
onBeforeUnmount(() => {
  if (clockInterval) clearInterval(clockInterval);
});
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--surface);
  padding: 0.6rem 2rem;
  border-bottom: 1px solid var(--line);
  gap: 1.5rem;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.brand-mark svg { width: 22px; height: 22px; display: block; }

.navbar-brand h1 {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--river-dark);
  margin: 0;
}

.case-study-tag {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--ink-soft);
  background-color: var(--surface-sunken);
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
}

.navbar-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-right: auto;
  padding-left: 1.5rem;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--river);
  animation: pulse 2.4s infinite ease-in-out;
}
.status-text {
  font-size: 0.75rem;
  color: var(--ink-faint);
}

.navbar-links {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.nav-link {
  text-decoration: none;
  color: var(--ink-soft);
  font-weight: 500;
  font-size: 0.9rem;
  transition: color 0.2s ease;
}

.nav-link--button {
  background: none;
  border: none;
  font-size: 0.9rem;
  font-family: inherit;
  cursor: pointer;
  padding: 0;
}

.nav-link:hover {
  color: var(--river);
}

.about-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(27, 43, 39, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.about-modal {
  background-color: var(--surface);
  border-radius: 10px;
  padding: 2rem;
  max-width: 480px;
  width: 90%;
  box-shadow: 0 10px 30px rgba(27, 43, 39, 0.25);
}

.about-modal h2 {
  color: var(--river-dark);
  margin-top: 0;
}

.about-modal p {
  color: var(--ink);
  line-height: 1.55;
  font-size: 0.92rem;
}

.close-button {
  background-color: var(--river);
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.6rem 1.2rem;
  cursor: pointer;
  font-weight: 600;
  font-family: var(--font-body);
}
.close-button:hover { background-color: var(--river-dark); }

@media (max-width: 768px) {
  .navbar {
    flex-wrap: wrap;
    padding: 0.6rem 1rem;
    row-gap: 0.5rem;
  }
  .navbar-status {
    padding-left: 0;
    margin-right: 0;
    order: 3;
  }
  .case-study-tag { display: none; }
  .navbar-links { margin-left: auto; }
}
</style>
