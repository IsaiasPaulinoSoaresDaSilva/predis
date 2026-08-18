# Guia de Instalação e Configuração do Ambiente

Este guia descreve os passos necessários para configurar o ambiente de desenvolvimento e instalar todas as dependências do projeto de Previsão de Desastres.

## Pré-requisitos

Antes de começar, garanta que você tenha os seguintes softwares instalados em seu sistema:

1.  **Python:** Versão 3.10 ou superior. Você pode verificar sua versão com `python3 --version`.
2.  **Node.js e npm:** Versão 20 ou superior (exigido pela suíte de testes, vitest). Você pode verificar sua versão com `node -v` e `npm -v`.
3.  **pip:** O gerenciador de pacotes do Python, geralmente instalado junto com o Python.

## Passo a Passo

### 1. Clonar o Repositório

Primeiro, clone este repositório para a sua máquina local (se ainda não o fez).

```bash
git clone <URL_DO_REPOSITORIO>
cd <NOME_DA_PASTA_DO_PROJETO>
```

### 2. Configurar o Backend (Python)

O backend é responsável pela lógica de IA e por servir os dados.

**a. Crie um Ambiente Virtual (Recomendado)**

É uma boa prática isolar as dependências do projeto. Na raiz do projeto, execute:

```bash
python3 -m venv venv
```

**b. Ative o Ambiente Virtual**

*   **macOS/Linux:**
    ```bash
source venv/bin/activate
    ```
*   **Windows:**
    ```bash
.\venv\Scripts\activate
    ```

**c. Instale as Dependências do Python**

Com o ambiente virtual ativado, instale as bibliotecas necessárias a partir do arquivo `requirements.txt`.

```bash
pip install -r backend/requirements.txt
```

As principais bibliotecas instaladas serão `fastapi`, `uvicorn`, `scikit-learn`, `pandas` e `joblib`.

### 3. Configurar o Frontend (Vue.js)

O frontend é a interface com o usuário, construída com Vue.js.

**a. Navegue até a pasta do frontend**

```bash
cd frontend
```

**b. Instale as Dependências do Node.js**

Execute o `npm install` para baixar todas as bibliotecas necessárias definidas no `package.json`.

```bash
npm install
```

As principais dependências são `vue`, `vite`, `axios` e `chart.js`.

**c. Volte para a raiz do projeto (opcional)**

```bash
cd ..
```

---

**Ambiente Configurado!**

Ao final destes passos, seu ambiente estará pronto. Você pode agora prosseguir para o treinamento do modelo e execução da aplicação, conforme descrito no `TESTING_GUIDE.md`.
