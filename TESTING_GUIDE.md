# Guia de Execução e Testes

Este guia fornece as instruções para treinar o modelo de IA, iniciar os servidores de backend e frontend, e verificar se a aplicação está funcionando corretamente.

## Pré-requisitos

- Certifique-se de que você seguiu todos os passos do `INSTALL_GUIDE.md` e que todas as dependências foram instaladas.
- Para os comandos de backend, o ambiente virtual (`venv`) deve estar ativado.

## 1. Treinar o Modelo de Inteligência Artificial

Este passo só precisa ser executado uma vez (ou sempre que os dados em `backend/historical_data/*.csv` forem atualizados — um arquivo por região do estudo de caso de São José dos Campos, ver `backend/scripts/generate_sjc_data.py`).

O script `model.py` irá ler os dados históricos, treinar um modelo de classificação e salvá-lo como `disaster_model.joblib`.

**Comando (execute na raiz do projeto, com o venv do backend ativado):**

```bash
python3 -m backend.model
```

> ⚠️ Rodar como `python3 backend/model.py` **não funciona** — o script usa
> imports absolutos (`from backend.data_management...`) e precisa ser
> executado como módulo (`-m`) a partir da raiz do projeto.

**Verificação:**
- O terminal deve exibir o relatório de classificação do modelo e "Modelo treinado com features de previsão e salvo com sucesso...".
- Um novo arquivo `disaster_model.joblib` deve aparecer em `backend/data/`
  (junto com `predis.db`, criado no primeiro request — ambos ignorados pelo
  git).

## 2. Iniciar o Servidor Backend

O servidor backend, construído com FastAPI, é responsável por fazer as previsões e servir os dados históricos.

**Comando (execute na raiz do projeto):**

```bash
uvicorn backend.main:app --reload
```

**Verificação:**
- O terminal mostrará logs do Uvicorn, indicando que o servidor está rodando.
- A mensagem "Application startup complete" deve aparecer.
- O servidor estará escutando em `http://127.0.0.1:8000`.
- Você pode abrir este endereço no seu navegador e verá a mensagem: `{"message":"Bem-vindo à API do PreDis — Estudo de Caso: São José dos Campos (SP)"}`.

## 3. Iniciar o Servidor Frontend

O servidor frontend, servido pelo Vite, compila e disponibiliza a interface do usuário.

**Abra um novo terminal** para este passo, mantendo o terminal do backend em execução.

**Comandos:**

```bash
# Navegue até a pasta do frontend
cd frontend

# Inicie o servidor de desenvolvimento
npm run dev
```

**Verificação:**
- O terminal mostrará a URL local onde a aplicação está rodando (geralmente `http://localhost:5173` ou um número de porta similar).
- Abra essa URL no seu navegador.

## 4. Teste Funcional da Aplicação

Ao abrir a URL do frontend no navegador, você deve ver o dashboard do PreDis
com a tag "Estudo de caso: São José dos Campos" no topo.

**Verifique os seguintes pontos:**

1.  **Regiões de SJC:** a barra lateral deve listar as 6 regiões administrativas
    de São José dos Campos (Centro, Norte, Sul, Leste, Oeste, Sudeste).
2.  **Carregamento Inicial:** O gráfico de "Tendência de Chuvas" deve ser
    populado com os dados históricos de dez/2023–fev/2024 da região selecionada.
3.  **Mapa:** o card do mapa deve mostrar as 6 regiões; clicar em uma delas
    seleciona a região (sincronizado com a barra lateral) e abre um popup com
    bairros de referência, curso d'água e histórico de risco.
4.  **Atualização periódica:** a cada 10 segundos, o card "Probabilidade de
    Risco" atualiza seu valor percentual e o círculo indicador pulsa,
    podendo mudar de cor (verde, laranja, ou vermelho) conforme o risco.
5.  **XAI:** o card "Fatores de Risco" deve listar as features mais
    relevantes para a previsão atual (ex.: "Subida do rio vs. mínima recente
    (14d)", "Chuva acumulada (3 dias)"), não apenas precipitação e nível do rio.
6.  **Ausência de Erros:** Verifique o console do navegador (pressione F12) e
    os terminais do backend e frontend para garantir que não há mensagens de
    erro sendo exibidas.
