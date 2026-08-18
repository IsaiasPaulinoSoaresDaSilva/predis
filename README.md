# PreDis 🌦️ - Flood Prediction System

**[English]** | [Português](#predis---sistema-de-previsão-de-enchentes)

---

**PreDis** is a functional prototype of a disaster prediction system, focused on floods in Brazil. As a case study, it is currently applied to **São José dos Campos (SP)** — see [`CASE_STUDY_SJC.md`](./CASE_STUDY_SJC.md) for the full write-up. The project uses data from various sources, applies a machine learning model to calculate flood risk, and displays the information on an interactive dashboard.

## ✨ Features

-   🗺️ **Interactive Map**: Visualize São José dos Campos' 6 administrative regions (Centro, Norte, Sul, Leste, Oeste, Sudeste) and select one for risk analysis.
-   📈 **Weather forecast + simulated historical data**: Real 3-day rainfall forecast from the public Open-Meteo API; historical rainfall/river-level data is currently a calibrated simulation (INMET/ANA integration is future work — see `IMPLEMENTATION_PLAN.md`).
-   🧠 **AI Model**: A machine learning model that predicts the probability of floods based on historical and forecast data.
-   📊 **Dynamic Dashboard**: View risk probability, historical data charts, and explainable-AI (XAI) risk factors in a clean and intuitive interface.
-   🌐 **Full-Stack**: Built with a robust Python backend (FastAPI) and a modern Vue.js frontend.

## 🚀 Tech Stack

-   **Backend**: Python, FastAPI, Pandas, Scikit-Learn
-   **Frontend**: Vue.js 3, Vite, Leaflet.js, Chart.js
-   **Data Sources**: INMET, ANA, OpenMeteo

## 📦 Installation and Setup

### Prerequisites

-   [Node.js](https://nodejs.org/en/) (v20 or higher — required by the test suite, vitest)
-   [Python](https://www.python.org/downloads/) (v3.10 or higher)
-   `venv` for Python environment management

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd predis
```

### 2. Backend Setup 🐍

```bash
# Create and activate a virtual environment inside backend/
cd backend
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Go back to the project root — the training script must run as a module
# from the root because it uses absolute imports (`backend.xxx`)
cd ..

# Train the model (run this only once)
python -m backend.model
```

### 3. Frontend Setup 🎨

```bash
# Navigate to the frontend directory
cd ../frontend

# Install dependencies
npm install
```

## ▶️ Running the Application

You need to run the backend and frontend servers in separate terminals.

### 1. Run the Backend Server

-   Make sure you are in the `predis/backend` directory and the virtual environment is activated.
-   Run the command from the **root of the project**:

```bash
# From the project's root directory (`predis/`)
python -m uvicorn backend.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### 2. Run the Frontend Server

-   Make sure you are in the `predis/frontend` directory.

```bash
npm run dev
```

The application will be accessible at `http://localhost:5173` (or another port indicated in the terminal).

### 🐳 Alternative: Docker Compose

```bash
docker compose up --build
```

This builds and starts both services: the backend at `http://localhost:8000`
(training the model automatically on first boot if needed) and the frontend
at `http://localhost:8080`. Predictions and the trained model persist in a
named volume (`predis-data`) across restarts. See `docker-compose.yml`,
`backend/Dockerfile` and `frontend/Dockerfile`.

### ✅ Running the tests

```bash
# Backend (from the project root, venv activated)
python -m pytest backend/tests -v

# Frontend
cd frontend && npm run test
```

---

# PreDis 🌦️ - Sistema de Previsão de Enchentes

[English](#predis---flood-prediction-system) | **[Português]**

---

O **PreDis** é um protótipo funcional de um sistema de previsão de desastres, com foco em enchentes no Brasil. Como estudo de caso, está atualmente aplicado ao município de **São José dos Campos (SP)** — veja [`CASE_STUDY_SJC.md`](./CASE_STUDY_SJC.md) para o relato completo. O projeto utiliza dados de diversas fontes, aplica um modelo de machine learning para calcular o risco e exibe as informações em um dashboard interativo.

## ✨ Funcionalidades

-   🗺️ **Mapa Interativo**: Visualize as 6 regiões administrativas de São José dos Campos (Centro, Norte, Sul, Leste, Oeste, Sudeste) e selecione uma para análise de risco.
-   📈 **Previsão real + histórico simulado**: Previsão real de chuva para 3 dias via API pública Open-Meteo; os dados históricos de chuva/nível de rio são, por ora, uma simulação calibrada (integração com INMET/ANA é trabalho futuro — ver `IMPLEMENTATION_PLAN.md`).
-   🧠 **Modelo de IA**: Um modelo de machine learning que prevê a probabilidade de enchentes com base em dados históricos e de previsão.
-   📊 **Dashboard Dinâmico**: Veja a probabilidade de risco, gráficos de dados históricos e os fatores de risco explicáveis (XAI) em uma interface limpa e intuitiva.
-   🌐 **Full-Stack**: Construído com um backend robusto em Python (FastAPI) e um frontend moderno em Vue.js.

## 🚀 Tecnologias Utilizadas

-   **Backend**: Python, FastAPI, Pandas, Scikit-Learn
-   **Frontend**: Vue.js 3, Vite, Leaflet.js, Chart.js
-   **Fontes de Dados**: INMET, ANA, OpenMeteo

## 📦 Instalação e Configuração

### Pré-requisitos

-   [Node.js](https://nodejs.org/en/) (v20 ou superior — exigido pela suíte de testes, vitest)
-   [Python](https://www.python.org/downloads/) (v3.10 ou superior)
-   `venv` para gerenciamento de ambientes Python

### 1. Clone o repositório

```bash
git clone <url-do-seu-repositorio>
cd predis
```

### 2. Configuração do Backend 🐍

```bash
# Crie e ative um ambiente virtual dentro de backend/
cd backend
python -m venv venv
source venv/bin/activate  # No Windows, use `venv\Scripts\activate`

# Instale as dependências
pip install -r requirements.txt

# Volte para a raiz do projeto — o script de treino precisa rodar como
# módulo a partir da raiz, pois usa imports absolutos (`backend.xxx`)
cd ..

# Treine o modelo (execute apenas uma vez)
python -m backend.model
```

### 3. Configuração do Frontend 🎨

```bash
# Navegue até o diretório do frontend
cd ../frontend

# Instale as dependências
npm install
```

## ▶️ Executando a Aplicação

Você precisará executar os servidores de backend e frontend em terminais separados.

### 1. Executar o Servidor Backend

-   Certifique-se de que você está no diretório `predis/backend` e que o ambiente virtual está ativado.
-   Execute o comando a partir da **raiz do projeto**:

```bash
# A partir do diretório raiz do projeto (`predis/`)
python -m uvicorn backend.main:app --reload
```

A API estará disponível em `http://127.0.0.1:8000`.

### 2. Executar o Servidor Frontend

-   Certifique-se de que você está no diretório `predis/frontend`.

```bash
npm run dev
```

A aplicação estará acessível em `http://localhost:5173` (ou outra porta indicada no terminal).

### 🐳 Alternativa: Docker Compose

```bash
docker compose up --build
```

Isso builda e sobe os dois serviços: o backend em `http://localhost:8000`
(treinando o modelo automaticamente no primeiro boot, se necessário) e o
frontend em `http://localhost:8080`. Predições e o modelo treinado persistem
em um volume nomeado (`predis-data`) entre restarts. Ver `docker-compose.yml`,
`backend/Dockerfile` e `frontend/Dockerfile`.

### ✅ Rodando os testes

```bash
# Backend (a partir da raiz do projeto, com o venv ativado)
python -m pytest backend/tests -v

# Frontend
cd frontend && npm run test
```
