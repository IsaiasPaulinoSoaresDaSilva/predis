# Changelog do Projeto de Previsão de Desastres

Este arquivo documenta as principais mudanças e marcos no desenvolvimento do projeto.

## Fase 7: Dados reais, ensemble e redesign completo (Atual)

*   **[FEITO] Dados reais em vez de sintéticos:**
    *   Testamos a API pública do INMET (`apitempo.inmet.gov.br`) na
        prática: o endpoint de metadados funciona, mas o de dados retorna
        vazio para qualquer estação/período — indisponível de fato, apesar
        de documentada. Descobrimos também que a estação citada no código
        antigo (A755) não é de SJC, é de Barueri.
    *   Precipitação real passou a vir da **Open-Meteo Archive API** (ERA5),
        por coordenada exata de cada região — `INMETConnector` foi
        renomeado para [`PrecipitationConnector`](backend/connectors/precipitation_connector.py)
        para refletir a fonte real.
    *   Nível de rio real passou a vir da **única estação telemétrica real
        da ANA dentro de São José dos Campos** (`58128200`, Rio Jaguari —
        achada consultando o inventário público `HidroInventario` da ANA),
        via [`ANAConnector`](backend/connectors/ana_connector.py) reescrito.
        Como é uma estação de barragem única para a cidade toda, a
        *anomalia* do sinal real é escalada por um fator de exposição
        documentado por região — nunca fingindo 6 medições independentes.
    *   Ambos os conectores combinam um histórico-base real (CSV, gerado por
        `backend/scripts/generate_sjc_data.py` contra as APIs reais) com uma
        janela recente buscada ao vivo (cache TTL 30 min), com fallback
        gracioso para o CSV se a API estiver fora do ar.
    *   Limiares de risco em `feature_engineering.py` recalibrados sobre a
        distribuição real (a correlação chuva-local vs. nível-da-barragem é
        fraca, então os limiares usam OR em vez de AND entre os sinais).
    *   Ver `CASE_STUDY_SJC.md` (seção 3) para a tabela completa e honesta de
        real vs. derivado.

*   **[FEITO] Ensemble de 2 modelos:**
    *   `backend/model.py`: `VotingClassifier` (voto suave) combinando
        `RandomForestClassifier` + `GradientBoostingClassifier`, em vez de
        um único modelo.
    *   Validação cruzada estratificada (5 folds) reportando AUC, além do
        holdout 75/25 tradicional.
    *   `feature_importances_` do ensemble calculada manualmente (média dos
        dois modelos) e persistida no `.joblib`, já que `VotingClassifier`
        não expõe esse atributo nativamente — `main.py` ajustado.

*   **[FEITO] Redesign completo do frontend:**
    *   Nova identidade visual ("painel de instrumento hidrológico" —
        réguas linimétricas, paleta terra+água, tipografia Space
        Grotesk/IBM Plex) em [style.css](frontend/src/style.css).
    *   Novo componente-assinatura [`StaffGauge.vue`](frontend/src/components/StaffGauge.vue):
        régua de nível vertical substituindo o indicador circular genérico.
    *   Novos componentes: [`RegionComparison.vue`](frontend/src/components/RegionComparison.vue)
        (comparativo ao vivo das 6 regiões), [`PredictionHistory.vue`](frontend/src/components/PredictionHistory.vue)
        (histórico persistido, antes coletado mas nunca exibido no
        frontend), [`DataSourceBadges.vue`](frontend/src/components/DataSourceBadges.vue)
        (transparência de proveniência dos dados).
    *   Painel "Sobre a região" passou a usar os metadados do GeoJSON
        (bairros, curso d'água, histórico) que já existiam mas nunca eram
        mostrados fora do popup do mapa.
    *   Responsividade mobile corrigida (sidebar vira seletor horizontal,
        grid nunca estoura a viewport, navbar quebra em duas linhas).
    *   8 novos testes de componente (StaffGauge, RegionComparison,
        PredictionHistory) — 18 testes de frontend no total.

## Fase 5: Persistência, Robustez, Testes e Infraestrutura

Execução das Fases 2 a 5 do `IMPLEMENTATION_PLAN.md`, na sequência.

*   **[FEITO] Persistência (Fase 2):**
    *   Criado `backend/database.py` (SQLite, biblioteca padrão) para
        persistir cada predição feita via `/predict`.
    *   Novo endpoint `GET /predictions` (filtro opcional por região, limite
        configurável) expõe o histórico já persistido.

*   **[FEITO] Robustez de backend (Fase 3):**
    *   Cache em memória com TTL de 10 min no `OpenMeteoConnector` — o
        dashboard faz polling a cada 10s por região, e sem cache isso batia a
        API pública repetidamente sem necessidade.
    *   `/predict` agora trata `KeyError`/`ValueError`/exceções genéricas
        separadamente, com mensagens específicas e log (`logger.exception`)
        em vez de um único `except Exception` genérico.
    *   CORS configurável via env var `ALLOWED_ORIGINS` (padrão `*` para
        desenvolvimento local).
    *   **Refatoração**: a engenharia de features estava duplicada entre
        `model.py` (treino) e `main.py` (inferência) — extraída para
        `backend/feature_engineering.py`, único lugar que define `FEATURES`,
        `add_rolling_features`, `compute_risk`. Um bug real foi introduzido e
        corrigido durante essa refatoração (uso de `groupby().apply()` que
        descartava a coluna de agrupamento em versões recentes do pandas) —
        pego graças à suíte de testes abaixo, antes de chegar à Fase 1 de novo.
    *   Suíte `pytest` (`backend/tests/`, 22 testes): engenharia de
        features, conectores, `DataManager`, endpoints da API via
        `TestClient` (com stub do `OpenMeteoConnector`, sem depender de rede).

*   **[FEITO] Frontend: testes e estados de loading/erro (Fase 4):**
    *   `vitest` + `@vue/test-utils` configurados (`frontend/vitest.config.js`),
        10 testes cobrindo `Sidebar`, `App` e `Dashboard` (incluindo mock de
        `axios` e `chart.js/auto`).
    *   `Dashboard.vue`: estados de loading (`isLoadingPrediction`,
        `isLoadingHistorical`) e erro de conexão (`isConnectionError`)
        diferenciados visualmente de um aviso comum do backend.
    *   URL da API extraída para uma constante (`VITE_API_URL`/fallback),
        eliminando duas URLs hardcoded repetidas.

*   **[FEITO] Infraestrutura (Fase 5):**
    *   `backend/Dockerfile` (+ `docker-entrypoint.sh`, que treina o modelo
        automaticamente no primeiro boot se ele não existir) e
        `frontend/Dockerfile` (multi-stage, build Vite + Nginx).
    *   `docker-compose.yml` sobe os dois serviços, com volume nomeado
        (`predis-data`) persistindo modelo treinado e histórico de predições.
    *   `.github/workflows/ci.yml`: roda `pytest` (com treino do modelo) e
        `vitest` + build do frontend em push/PR para `main`.
    *   Validado de ponta a ponta com `docker compose up --build`: treino
        automático no primeiro boot, `/predict`, `/predictions` e frontend
        (Nginx, porta 8080) testados via HTTP real e no navegador.

## Fase 4: Estudo de Caso — São José dos Campos

Pivô de prioridade definido pelo orientador: substituir a divisão genérica em
5 macrorregiões do Brasil por um estudo de caso municipal único e
defensável academicamente. Ver `IMPLEMENTATION_PLAN.md` (seção 6.1) e
`CASE_STUDY_SJC.md` para o racional completo e os resultados.

*   **[FEITO] Nova geografia — 6 regiões de São José dos Campos:**
    *   Substituído `frontend/src/assets/brazil-regions.json` (5 macrorregiões
        do Brasil, geometria genérica) por `frontend/src/assets/sjc-regions.json`,
        com as 6 regiões administrativas reais do município (Centro, Norte,
        Sul, Leste, Oeste, Sudeste), cada uma com bairros de referência, curso
        d'água associado e histórico de risco levantados via pesquisa
        (ver fontes em `CASE_STUDY_SJC.md`).
    *   `Map.vue` agora exibe um popup por região com esse contexto ao clicar.
    *   `App.vue`/`Sidebar.vue` atualizados para a nova lista de regiões; mapa
        recentralizado em São José dos Campos.

*   **[FEITO] Dados históricos por região (sintéticos, calibrados):**
    *   Criado `backend/scripts/generate_sjc_data.py`, que gera um dataset por
        região (`backend/historical_data/<região>.csv`) cobrindo dez/2023–fev/2024
        (pico da estação chuvosa), calibrado para refletir o risco relativo
        relatado publicamente entre regiões (Leste/Sul mais expostas,
        Norte/Oeste menos).
    *   `INMETConnector`/`ANAConnector` reescritos para ler o CSV da região
        selecionada, em vez de sempre retornar o mesmo arquivo genérico —
        resolvendo a lacuna identificada na auditoria (regiões antes só
        diferiam pela previsão de chuva, não pelo histórico).
    *   Removido `backend/historical_data.csv` (arquivo único genérico,
        substituído pelo diretório `backend/historical_data/`).

*   **[FEITO] Backend adaptado ao estudo de caso:**
    *   `DataManager.location_map` agora mapeia as 6 regiões de SJC, com
        coordenadas reais (aproximadas) usadas na chamada real à API da
        Open-Meteo.
    *   Nova feature `subida_rio_14d` (nível do rio menos a mínima dos
        últimos 14 dias), adotada no lugar de um limiar absoluto de nível —
        necessária porque as regiões representam cursos d'água de portes
        diferentes (Rio Paraíba do Sul vs. córregos menores).
    *   `model.py` agora treina um único modelo sobre as 6 regiões
        combinadas (540 dias-região), com engenharia de features calculada
        por região (`groupby`) para não misturar séries nas bordas.
    *   `main.py` (`/predict`) espelha exatamente a mesma engenharia de
        features do treino, incluindo `subida_rio_14d`.

*   **[FEITO] Frontend — XAI generalizado:**
    *   `Dashboard.vue` antes só exibia a importância de 2 features fixas
        (precipitação e nível do rio). Como o novo modelo tem 10 features —
        e a mais importante passou a ser `subida_rio_14d` (~38%) — o painel
        agora lista dinamicamente as features mais relevantes, com rótulos
        legíveis.
    *   Corrigido bug de CSS pré-existente: `.main-layout` tinha
        `overflow: hidden` sem scroll em `.dashboard-content`, tornando os
        cards de mapa/XAI inacessíveis em telas menores.

*   **[FEITO] Narrativa do estudo de caso:**
    *   Criado `CASE_STUDY_SJC.md` com contexto, área de estudo, transparência
        sobre o que é real vs. simulado nos dados, metodologia, resultados
        (relatório de classificação, distribuição de risco por região) e
        limitações — pronto para uso na apresentação ao orientador.

## Fase 3: Estabilização e Alinhamento de Base

*   **[FEITO] Correção de bugs de documentação:**
    *   Corrigido o comando de treino do modelo em `README.md` e
        `TESTING_GUIDE.md`: `python backend/model.py` falhava com
        `ModuleNotFoundError: No module named 'backend'` porque o script usa
        imports absolutos. O comando correto é `python -m backend.model`,
        executado a partir da raiz do projeto.
    *   Alinhada a versão mínima de Python entre `README.md` e
        `INSTALL_GUIDE.md` (ambos agora pedem 3.10+).
    *   Corrigida a mensagem de boas-vindas da API documentada em
        `TESTING_GUIDE.md` para bater com o texto real de `backend/main.py`.

*   **[FEITO] Navbar funcional:**
    *   O link "Sobre" agora abre um modal com uma descrição real do PreDis e
        do estudo de caso. O link "Contato" aponta para o repositório do
        projeto no GitHub. Antes, ambos eram `href="#"` sem destino.

*   **[FEITO] Documentação da arquitetura de conectores (retroativa):**
    *   Documentando aqui, pela primeira vez, uma evolução de arquitetura que
        já existia no código mas nunca havia sido registrada no changelog:
        os dados de precipitação e nível de rio passaram a ser buscados via
        uma camada de **conectores** (`backend/connectors/`) — `INMETConnector`
        e `ANAConnector` (simulados, lendo de `historical_data.csv`) e
        `OpenMeteoConnector` (integração **real** com a API pública da
        Open-Meteo para previsão de chuva de 3 dias).
    *   Um `DataManager` (`backend/data_management/data_manager.py`) orquestra
        os três conectores por região (`location_map`), une os dados
        históricos e anexa as colunas de previsão (`previsao_chuva_d1/d2/d3`)
        usadas como features pelo modelo.

## Fase 2: Refinamento com IA e Dados Reais

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
