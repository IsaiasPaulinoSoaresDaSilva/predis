# Changelog do Projeto de Previsão de Desastres

Este arquivo documenta as principais mudanças e marcos no desenvolvimento do projeto.

## Fase 2: Refinamento com IA e Dados Reais (Atual)

*   **[FEITO] Criação de Documentação:**
    *   Adicionado `INSTALL_GUIDE.md` com instruções detalhadas para configuração do ambiente.
    *   Adicionado `TESTING_GUIDE.md` com o passo a passo para treinar o modelo, rodar os servidores e testar a aplicação.
    *   Adicionado `CHANGELOG.md` para rastrear o progresso do desenvolvimento.

*   **[FEITO] Refinamento do Frontend:**
    *   O componente `App.vue` foi refatorado para consumir dados reais do backend.
    *   Adicionado um novo endpoint de `GET /historical_data` para popular o gráfico.
    *   A simulação em tempo real agora percorre os dados históricos, enviando dados sequenciais para o modelo de IA.
    *   A visualização do XAI (Feature Importance) foi melhorada com barras de progresso para maior clareza.
    *   O gráfico principal agora exibe tanto a precipitação quanto o nível do rio, com eixos Y distintos.
    *   A paleta de cores e o design foram ajustados para maior profissionalismo.

*   **[FEITO] Desenvolvimento do Modelo de IA:**
    *   Criado o script `model.py` utilizando `scikit-learn` e `pandas`.
    *   O script treina um modelo `RandomForestClassifier` para prever o risco com base em limiares de precipitação e nível do rio.
    *   O modelo treinado e as features utilizadas são salvos no arquivo `disaster_model.joblib` para persistência.

*   **[FEITO] Atualização da API Backend:**
    *   A API `main.py` agora carrega o `disaster_model.joblib`.
    *   O endpoint `POST /predict` foi modificado para usar o modelo de IA treinado, retornando a probabilidade de risco (`risk_probability`) e a importância real das features.
    *   Adicionado um novo endpoint `GET /historical_data` para servir o arquivo `historical_data.csv` ao frontend.

*   **[FEITO] Simulação de Dados Históricos:**
    *   Criado o arquivo `backend/historical_data.csv` com 30 dias de dados plausíveis de precipitação e nível do rio para permitir o desenvolvimento offline.

*   **[FEITO] Pesquisa de Fontes de Dados:**
    *   Investigadas as APIs e portais de dados da Agência Nacional de Águas (ANA) e do Instituto Nacional de Meteorologia (INMET).
    *   Conclusão: APIs oficiais para tempo real requerem solicitação de acesso. A estratégia adotada foi usar dados históricos estáticos para o protótipo, com um plano de integrar APIs da comunidade no futuro.

---

## Fase 1: Criação do Protótipo Inicial

*   **[FEITO] Estrutura do Projeto:**
    *   Criados os diretórios `backend` e `frontend`.

*   **[FEITO] Backend Inicial (Simulado):**
    *   Desenvolvido um servidor `FastAPI` em `backend/main.py`.
    *   Criado um endpoint `POST /predict` que simulava a lógica de um modelo de IA com regras simples e dados aleatórios.
    *   O endpoint retornava um `risk_level` e uma `feature_importance` simulada.
    *   Adicionado middleware CORS para permitir a comunicação com o frontend.

*   **[FEITO] Frontend Inicial (Vue.js):**
    *   Configurado um projeto Vue.js 3 com Vite manualmente (`package.json`, `vite.config.js`, etc.).
    *   Desenvolvido o componente `App.vue` com uma estética "Clean White & Green".
    *   Implementado um gráfico de série temporal com `Chart.js` para mostrar dados de chuva simulados.
    *   Criada uma animação de "círculo pulsante" para indicar o nível de risco, com a cor e a velocidade da pulsação variando conforme o risco.
    *   Implementada a lógica para buscar dados do backend a cada 5 segundos e atualizar a UI.
    *   Adicionado um arquivo `style.css` com a estilização global do dashboard.
