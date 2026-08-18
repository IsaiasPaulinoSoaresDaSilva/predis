# Plano de Implementação — PreDis

> **Status:** rascunho inicial, em construção conjunta.
> Este documento nasce do panorama levantado em 17/08/2026 (ver seção 8) e será
> ajustado à medida que novos insights forem incorporados. Nada aqui é definitivo
> até ser validado em conversa.

---

## 1. Objetivo deste plano

Organizar em fases o trabalho necessário para levar o PreDis do estado atual de
**protótipo funcional com dados simulados** para uma versão mais robusta,
confiável e regionalmente coerente — sem perder de vista que o projeto pode ter
escopo de portfólio/demo, então cada fase deve ser avaliada quanto a
custo x benefício antes de ser puxada para execução.

## 2. Princípios norteadores

- **Incremental**: cada fase deve deixar o projeto rodável e demonstrável.
- **Não regredir**: o que já funciona (pipeline de ML, dashboard, mapa) não pode
  quebrar enquanto evoluímos a base de dados/infra.
- **Documentar em paralelo**: `CHANGELOG.md`, `README.md`, `INSTALL_GUIDE.md` e
  `TESTING_GUIDE.md` são atualizados junto com o código, não depois.
- **Priorizar o que destrava valor real primeiro**: o estudo de caso municipal
  e a confiabilidade dos dados vêm antes de polimento de UI ou infraestrutura.
- **Foco acadêmico**: a partir da orientação recebida (seção 6.1), o projeto
  passa a ter como entregável central um **estudo de caso aplicado** — não só
  um protótipo genérico de 5 macrorregiões.

## 3. Fases propostas (rascunho — sujeito a revisão)

### Fase 0 — Estabilização e alinhamento de base ✅ concluída (17/08/2026)
Objetivo: eliminar inconsistências encontradas na auditoria antes de construir
coisas novas em cima delas.

- [x] Treinar e validar o modelo e confirmar que `disaster_model.joblib` é
      gerado corretamente nesta cópia.
- [x] Alinhar versões de pré-requisitos entre `README.md` e `INSTALL_GUIDE.md`
      (ambos agora pedem Python 3.10+).
- [x] Corrigir mensagem de boas-vindas da API para bater entre código e docs.
- [x] Resolver os links mortos da `Navbar.vue` — "Sobre" agora abre um modal
      informativo, "Contato" aponta para o repositório no GitHub.
- [x] Atualizar `CHANGELOG.md` com a arquitetura de `connectors/` +
      `DataManager` e a integração real com Open-Meteo (Fase 3 do changelog).
- [x] **Bônus encontrado durante a execução**: corrigido bug real de comando —
      `python backend/model.py` falhava (`ModuleNotFoundError`); o correto é
      `python -m backend.model`. Corrigido em `README.md` e `TESTING_GUIDE.md`.

**Critério de aceite:** `INSTALL_GUIDE.md` + `TESTING_GUIDE.md` executados do
zero, sem nenhuma divergência entre o que está escrito e o que acontece. ✅

---

### Fase 1 — Estudo de caso: São José dos Campos ✅ concluída (17/08/2026)
Objetivo: substituir a abstração genérica de "5 macrorregiões do Brasil" por
um **estudo de caso municipal único e defensável academicamente** — São José
dos Campos (SP). Isso absorveu e substituiu a antiga proposta de
"regionalização por macrorregião": em vez de tornar as 5 regiões do Brasil
mais reais, o esforço de dados/fidelidade foi concentrado neste único
município, com granularidade das 6 regiões administrativas oficiais.

- [x] Levantada a geografia do município: 6 regiões administrativas oficiais
      (Centro, Norte, Sul, Leste, Oeste, Sudeste), bairros historicamente
      associados a alagamento por região, e cursos d'água relevantes (Rio
      Paraíba do Sul, Rio Jaguari, Rio Comprido/Ribeirão Vidoca) — ver fontes
      em `CASE_STUDY_SJC.md`.
- [x] Substituído `brazil-regions.json` por `sjc-regions.json`, com as 6
      regiões como unidades de seleção no mapa (geometria esquemática, não
      GIS oficial) e popup com contexto real por região.
- [x] Gerados datasets históricos sintéticos por região
      (`backend/scripts/generate_sjc_data.py`), calibrados para refletir o
      risco relativo relatado publicamente (Leste/Sul mais expostas). Dados
      oficiais do INMET/ANA para SJC continuam como trabalho futuro (estação
      INMET candidata identificada: A755, não confirmada oficialmente).
- [x] `DataManager`/`location_map` adaptados para as 6 regiões de SJC, com
      coordenadas reais usadas na chamada real à API Open-Meteo.
- [x] Modelo retreinado sobre as 6 regiões combinadas (98% de acurácia no
      teste; distribuição de risco por região coerente com o histórico
      pesquisado — ver `CASE_STUDY_SJC.md`, seção 5).
- [x] Narrativa do estudo de caso redigida em `CASE_STUDY_SJC.md` (contexto,
      área de estudo, transparência dados reais vs. simulados, metodologia,
      resultados, limitações, próximos passos).

**Critério de aceite:** ✅ o dashboard, ao abrir, apresenta o cenário de São
José dos Campos com dados coerentes com o município, testado ponta a ponta
(backend + frontend rodando, seleção de região sincronizada entre mapa e
barra lateral); `CASE_STUDY_SJC.md` pronto para apresentação.

---

### Fase 2 — Persistência e histórico real ✅ concluída (18/08/2026)
Objetivo: sair do modelo "tudo calculado on-the-fly" para ter rastro de
predições e permitir séries temporais reais.

- [x] Banco escolhido: SQLite (biblioteca padrão, sem dependência extra) —
      adequado à simplicidade de protótipo/estudo de caso.
- [x] Tabela de predições (região, timestamp, risco, probabilidade,
      feature_importance, mensagem) — `backend/database.py`.
- [x] Endpoint `GET /predictions` (filtro por região + limite) para
      consultar o histórico já persistido.

**Critério de aceite:** ✅ reiniciar o backend não apaga o histórico —
persistido em `backend/data/predis.db` (volume Docker em produção/local).

---

### Fase 3 — Robustez de backend ✅ concluída (18/08/2026)
Objetivo: tornar a API resiliente a falhas externas e testável.

- [x] Cache TTL (10 min) para chamadas à Open-Meteo no `OpenMeteoConnector`.
- [x] Suíte `pytest` (22 testes): `feature_engineering`, conectores,
      `DataManager`, endpoints via `TestClient` — `backend/tests/`.
- [x] Tratamento de erro granular em `/predict` (`KeyError`/`ValueError`/
      exceção genérica, cada um com mensagem e log específicos).
- [x] CORS configurável via `ALLOWED_ORIGINS` (env var; padrão `*` em dev).
- [x] **Extra**: eliminada duplicação real de código — engenharia de
      features estava copiada entre `model.py` e `main.py`; extraída para
      `backend/feature_engineering.py`, testada isoladamente.

**Critério de aceite:** ✅ suíte de testes rodando (`pytest`/CI), falha de
rede na Open-Meteo não derruba `/predict` (fallback já existia no
`DataManager`, agora coberto por teste).

---

### Fase 4 — Frontend: qualidade e experiência ✅ concluída (18/08/2026)
Objetivo: melhorar confiabilidade percebida e cobertura de testes no cliente.

- [x] `vitest` + `@vue/test-utils` configurados; 10 testes (`Sidebar`, `App`,
      `Dashboard`, com mocks de `axios`/`chart.js`).
- [x] Estados de loading (`isLoadingPrediction`/`isLoadingHistorical`) e erro
      de conexão (`isConnectionError`, estilizado distinto de um aviso comum
      do backend) — antes só havia uma mensagem de texto genérica.
- [x] UX do dashboard já reflete dados realmente distintos por região da
      Fase 1 (herdado, sem trabalho extra necessário aqui).

**Critério de aceite:** ✅ testes rodando (`npm run test`), loading/erro
visíveis e diferenciados em todas as chamadas assíncronas do Dashboard.

---

### Fase 5 — Infraestrutura e entrega ✅ concluída (18/08/2026)
Objetivo: facilitar rodar e demonstrar o projeto.

- [x] `backend/Dockerfile` (+ `docker-entrypoint.sh`, treina o modelo
      automaticamente no primeiro boot se ausente) e `frontend/Dockerfile`
      (multi-stage: build Vite + Nginx).
- [x] `docker-compose.yml` — dois serviços + volume nomeado `predis-data`
      persistindo modelo e histórico de predições.
- [x] `.github/workflows/ci.yml` — `pytest` (com treino do modelo) e
      `vitest` + build do frontend em push/PR.
- [ ] (Opcional, não feito) Deploy de demo pública.

**Critério de aceite:** ✅ `docker compose up --build` valido de ponta a
ponta neste ambiente — treino automático no primeiro boot, `/predict`,
`/predictions` e frontend (porta 8080) testados via HTTP real e no navegador.
Nota operacional: durante a validação, o disco do Mac ficou cheio por causa
do disco virtual do Docker Desktop (28GB, acumulado de outros projetos) — o
usuário migrou o "Disk image location" do Docker Desktop para um SSD externo
para resolver. Não é um problema do PreDis, mas fica registrado aqui como
contexto do ambiente de desenvolvimento.

---

### Fase 6 — Direção futura (conceitual): modelagem em grafo 🔭
Objetivo: **não é uma fase de implementação agora** — é um espaço para
amadurecer, como trabalho futuro ou seção de discussão do artigo/apresentação,
a ideia trazida na seção 6.2 (grafo da rede hidrográfica, travessia/caminho
mínimo para propagação de risco, particionamento espacial). Decidido em
17/08/2026 que, por ora, fica registrada como **direção conceitual**, sem
compromisso de engenharia — a Fase 1 segue com a abordagem tabular atual
(`DataManager` + `RandomForestClassifier`) aplicada a São José dos Campos.

- [ ] (Futuro) Esboçar como a bacia/drenagem de SJC poderia ser modelada como
      grafo (vértices = sub-bacias/bairros, arestas = conexão hidrológica).
- [ ] (Futuro) Avaliar se BFS/Dijkstra sobre esse grafo agrega valor preditivo
      real (propagação montante→jusante) frente ao modelo tabular atual.
- [ ] (Futuro) Se a ideia amadurecer, discutir particionamento espacial como
      seção metodológica do artigo — sem necessariamente implementar
      computação distribuída de fato, a menos que o escopo do projeto mude.

**Critério de aceite:** nenhum por enquanto — esta fase só ganha critérios de
aceite se for promovida de "conceitual" para "em execução" numa próxima rodada
de decisão.

---

### Fase 7 — Dados reais, ensemble e redesign ✅ concluída (18/08/2026)
Objetivo: substituir dados sintéticos por reais onde tecnicamente viável,
reduzir vazamento/simplismo do modelo com um segundo classificador, e refazer
o frontend como um dashboard mais rico e com identidade visual própria.
Disparada por pedido direto do usuário em 18/08/2026.

- [x] Testar a API pública do INMET na prática — achado: endpoint de dados
      indisponível (retorna vazio), apesar de documentado. Registrado como
      limitação, não contornado silenciosamente.
- [x] Precipitação real via Open-Meteo Archive API, por coordenada real de
      cada região (`PrecipitationConnector`, renomeado de `INMETConnector`).
- [x] Nível de rio real via a única estação telemétrica real da ANA dentro
      de SJC (`58128200`, Rio Jaguari), com anomalia escalada por exposição
      regional documentada (`ANAConnector` reescrito).
- [x] Ambos os conectores com fallback gracioso para CSV local (agora
      snapshot real, não mais sintético) quando a API está fora do ar.
- [x] Limiares de risco recalibrados sobre a distribuição real dos dados.
- [x] Ensemble RandomForest + GradientBoosting (`VotingClassifier`, voto
      suave) substituindo o RandomForest único, com validação cruzada
      estratificada reportando AUC.
- [x] Redesign completo do frontend: nova identidade visual, componente
      StaffGauge (régua de nível), comparativo entre regiões, histórico de
      predições exposto na UI, transparência de fontes de dados,
      responsividade mobile corrigida.
- [x] `CASE_STUDY_SJC.md` atualizado com a tabela real de proveniência dos
      dados e os números reais de distribuição de risco/validação cruzada.

**Critério de aceite:** ✅ `pytest` (25 testes) e `vitest` (18 testes)
passando; build de produção do frontend sem erros; modelo retreinado com
dados reais e validado via `/predict` real no navegador.

---

## 4. Dependências entre fases

```
Fase 0 (estabilização)
   │
   ▼
Fase 1 (estudo de caso: São José dos Campos) ──► Fase 4 (frontend, UX do caso)
   │
   ▼
Fase 2 (persistência)
   │
   ▼
Fase 3 (robustez backend) ──► Fase 5 (infra/CI/Docker)

Fase 6 (grafo — conceitual/futuro): sem posição fixa no fluxo,
avaliada em paralelo como direção de pesquisa, não bloqueia as demais.
```

Fase 0 é pré-requisito de tudo. Fase 1 agora é o coração do projeto (prioridade
do orientador) e deve ser puxada logo após a Fase 0. Fases 1 e 2 podem ser
paralelizadas se houver mais de uma pessoa trabalhando. Fase 5 fecha o ciclo,
mas partes dela (ex.: Dockerfile do backend) podem começar cedo se fizer
sentido. Fase 6 é intencionalmente desconectada do fluxo principal — é uma
linha de pesquisa/discussão, não um bloqueio de entrega.

## 5. Riscos e pontos em aberto

- **Dados específicos de São José dos Campos**: precisa confirmar se há
  estação INMET/ANA com dados públicos acessíveis para o município, e se
  existe histórico de alagamentos documentado (Defesa Civil/prefeitura) para
  dar mais legitimidade ao estudo de caso.
- **Escopo do projeto**: não está definido se o PreDis é portfólio/demo ou algo
  com ambição de uso real — isso muda a prioridade das Fases 3 e 5.
- **Modelo de ML**: `RandomForestClassifier` com regras de limiar fixas
  (`precipitacao_acumulada_3d > 150`, etc.) — validados para um cenário
  genérico, precisam ser recalibrados/justificados para a realidade
  hidrológica específica de São José dos Campos.
- **Ideia do grafo (Fase 6)**: risco de "scope creep" acadêmico — vale manter
  como seção de discussão/trabalho futuro a menos que agregue valor preditivo
  comprovado frente à abordagem tabular atual.

## 6. Insights do usuário (a preencher em conjunto)

> Espaço reservado para os pontos que você trouxer na conversa. Vamos discutir
> aqui e ajustar as fases acima antes de fechar a versão definitiva do plano.

### 6.1 Prioridade do orientador (17/08/2026)

> "Diversos estudos apresentam e aplicam sistemas de predição de inundações,
> inclusive no Brasil. Assim, eu sugiro que nós apresentemos um estudo de caso
> aplicando o PREDIS para a predição de chuvas, associadas a um cenário de
> inundação, em um município (e.g. São José dos Campos). Fiquem à vontade para
> realizar modificações e sugerir novos tópicos."

**Leitura**: pivô de "5 macrorregiões genéricas do Brasil" para **um estudo de
caso municipal único**, com narrativa acadêmica (comparável a outros trabalhos
publicados sobre predição de inundação no Brasil). Isso muda granularidade
geográfica (macrorregião → município/bairro/bacia) e a exigência de dados
(precisa de dados plausíveis/reais específicos do município escolhido).

**Status**: ✅ decidido (17/08/2026) — São José dos Campos (SP) confirmado como
município do estudo de caso. Incorporado como Fase 1 revisada acima.

### 6.2 Pensamentos sobre modelagem em grafo

> "grafo percorre vertices e arestas / percorre aresta (liga dois vertices) /
> busca exploratoria pelo minimo de distancia / aresta é questao logica /
> seccionar o grafo, quebrar o mapa em varios pedaços, quebrar o grafo, e
> trabalhar em cada parte, e todos esses dados resolvidos independentemente
> precisam se comunicar / zip e compressao de modelos e grafos de
> processamento de alto desempenho"

**Leitura/síntese proposta** (para validarmos juntos): representar a bacia
hidrográfica/rede de drenagem do município como um **grafo** — vértices como
pontos de interesse (sub-bacias, bairros, estações, cruzamentos de rios) e
arestas como conexões hidrológicas (direção do fluxo de água) ou condições
lógicas (ex.: "se sub-bacia A transborda, propaga risco para B"). A partir
disso:

- **Travessia/caminho mínimo**: usar busca (BFS/Dijkstra) para simular como o
  risco de enchente se propaga de montante para jusante, ou para calcular
  rotas de evacuação até pontos seguros.
- **Particionamento do grafo**: dividir o mapa/grafo em pedaços (por bairro,
  sub-bacia ou célula de grade), processar cada parte de forma independente e
  depois reconciliar os resultados nas fronteiras — padrão clássico de
  computação distribuída sobre grafos (ex.: estilo Pregel/GraphX), útil se
  quisermos escalar para múltiplos municípios ou aumentar a resolução espacial.
- **Compressão**: técnicas de compressão do modelo treinado e da estrutura do
  grafo para desempenho em escala (representações esparsas, serialização
  eficiente).

**Status**: ✅ decidido (17/08/2026) — fica como **direção futura/conceitual**
(Fase 6), não como núcleo técnico da implementação atual. O particionamento do
grafo, especificamente, foi classificado como **framing conceitual para o
artigo/apresentação**, não como requisito de engenharia distribuída de verdade.
A Fase 1 segue com a abordagem tabular atual (`DataManager` + Random Forest)
aplicada a São José dos Campos.

## 7. Definição de fases finais

Consolidado a partir da rodada de decisões de 17/08/2026:

1. **Fase 0 — Estabilização** ✅ — pré-requisito, concluída.
2. **Fase 1 — Estudo de caso: São José dos Campos** ✅ — prioridade #1,
   absorveu a antiga "regionalização por macrorregião", concluída.
3. **Fase 2 — Persistência** ✅, **Fase 3 — Robustez de backend** ✅,
   **Fase 4 — Frontend** ✅, **Fase 5 — Infraestrutura** ✅ — todas
   concluídas em 18/08/2026 (ver seção 3 para detalhes de cada uma).
4. **Fase 6 — Modelagem em grafo** — segue fora do fluxo principal, como
   direção futura/seção de discussão, sem critérios de aceite por ora.

**Status geral (18/08/2026): todas as fases com escopo de implementação
definido (0–5) estão concluídas e validadas** — testes de backend (pytest,
22) e frontend (vitest, 10) passando, aplicação validada tanto localmente
quanto via `docker compose up --build`. Só a Fase 6 (conceitual) e os próximos passos listados em
`CASE_STUDY_SJC.md` (seção 7, integração com dados oficiais do INMET/ANA)
seguem em aberto.

> Este plano continua aberto a novos insights — se surgir mais alguma ideia
> (sua ou do orientador), ela entra na seção 6 antes de mexer nas fases acima.

## 8. Referência: panorama da auditoria (17/08/2026)

Resumo do que foi levantado antes deste plano, para contexto:

- Backend: FastAPI + `RandomForestClassifier`, arquitetura de `connectors/`
  (INMET/ANA simulados via CSV local, Open-Meteo real) orquestrada por
  `DataManager`.
- Frontend: Vue 3 + Vite, mapa Leaflet com 5 regiões fixas, dashboard com
  polling de 10s, gráfico Chart.js de dois eixos, XAI simples via feature
  importance.
- `disaster_model.joblib` não versionado (gitignored) — precisa ser treinado
  a cada clone novo.
- CHANGELOG desatualizado em relação à arquitetura de conectores já existente
  no código.
- Nenhum teste automatizado, nenhuma infraestrutura de containers/CI.
- CORS aberto (`allow_origins=["*"]`), sem persistência de dados.
