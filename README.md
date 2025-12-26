# PreDis 🌦️ - Flood Prediction System

**[English]** | [Português](#predis---sistema-de-previsão-de-enchentes)

---

**PreDis** is a functional prototype of a disaster prediction system, focused on floods in Brazil. The project uses data from various sources, applies a machine learning model to calculate flood risk, and displays the information on an interactive dashboard.

## ✨ Features

-   🗺️ **Interactive Map**: Visualize Brazilian regions and select areas for risk analysis.
-   📈 **Real-time Data**: Connects to public APIs like INMET and ANA to get the latest weather and river data.
-   🧠 **AI Model**: A machine learning model that predicts the probability of floods based on historical and real-time data.
-   📊 **Dynamic Dashboard**: View risk probability, historical data charts, and alerts in a clean and intuitive interface.
-   🌐 **Full-Stack**: Built with a robust Python backend (FastAPI) and a modern Vue.js frontend.

## 🚀 Tech Stack

-   **Backend**: Python, FastAPI, Pandas, Scikit-Learn
-   **Frontend**: Vue.js 3, Vite, Leaflet.js, Chart.js
-   **Data Sources**: INMET, ANA, OpenMeteo

## 📦 Installation and Setup

### Prerequisites

-   [Node.js](https://nodejs.org/en/) (v18 or higher)
-   [Python](https://www.python.org/downloads/) (v3.10 or higher)
-   `venv` for Python environment management

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd predis
```

### 2. Backend Setup 🐍

```bash
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Train the model (run this only once)
python model.py
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

---

# PreDis 🌦️ - Sistema de Previsão de Enchentes

[English](#predis---flood-prediction-system) | **[Português]**

---

O **PreDis** é um protótipo funcional de um sistema de previsão de desastres, com foco em enchentes no Brasil. O projeto utiliza dados de diversas fontes, aplica um modelo de machine learning para calcular o risco e exibe as informações em um dashboard interativo.

## ✨ Funcionalidades

-   🗺️ **Mapa Interativo**: Visualize as regiões do Brasil e selecione áreas para análise de risco.
-   📈 **Dados em Tempo Real**: Conecta-se a APIs públicas como INMET e ANA para obter os dados meteorológicos e fluviométricos mais recentes.
-   🧠 **Modelo de IA**: Um modelo de machine learning que prevê a probabilidade de enchentes com base em dados históricos e em tempo real.
-   📊 **Dashboard Dinâmico**: Veja a probabilidade de risco, gráficos de dados históricos e alertas em uma interface limpa e intuitiva.
-   🌐 **Full-Stack**: Construído com um backend robusto em Python (FastAPI) e um frontend moderno em Vue.js.

## 🚀 Tecnologias Utilizadas

-   **Backend**: Python, FastAPI, Pandas, Scikit-Learn
-   **Frontend**: Vue.js 3, Vite, Leaflet.js, Chart.js
-   **Fontes de Dados**: INMET, ANA, OpenMeteo

## 📦 Instalação e Configuração

### Pré-requisitos

-   [Node.js](https://nodejs.org/en/) (v18 ou superior)
-   [Python](https://www.python.org/downloads/) (v3.10 ou superior)
-   `venv` para gerenciamento de ambientes Python

### 1. Clone o repositório

```bash
git clone <url-do-seu-repositorio>
cd predis
```

### 2. Configuração do Backend 🐍

```bash
# Navegue até o diretório do backend
cd backend

# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows, use `venv\Scripts\activate`

# Instale as dependências
pip install -r requirements.txt

# Treine o modelo (execute apenas uma vez)
python model.py
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
