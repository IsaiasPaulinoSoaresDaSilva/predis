# Estudo de Caso — PreDis aplicado a São José dos Campos (SP)

> Documento de apoio à apresentação/orientação, produzido a partir da
> prioridade definida pelo orientador (ver `IMPLEMENTATION_PLAN.md`, seção
> 6.1): substituir a abordagem genérica por macrorregiões do Brasil por um
> estudo de caso municipal único e defensável academicamente.

## 1. Contexto e motivação

Diversos trabalhos aplicam sistemas de predição de inundação a cidades
brasileiras específicas. Seguindo essa linha, o PreDis passou a ser
demonstrado sobre um caso concreto — o município de **São José dos Campos
(SP)** — em vez de uma divisão artificial em 5 macrorregiões do país, que não
permitia validar a ferramenta contra um contexto geográfico e hidrológico
real.

São José dos Campos foi escolhida por:

- Ser cortada pelo **Rio Paraíba do Sul** e por afluentes relevantes (Rio
  Jaguari, Rio Comprido/Ribeirão Vidoca), com histórico documentado de
  alagamentos em reportagens locais.
- Ter uma **divisão administrativa oficial em 6 regiões** (Centro, Norte,
  Sul, Leste, Oeste, Sudeste), o que mapeia naturalmente para a seleção de
  área que o PreDis já oferecia — sem precisar inventar uma geografia.
- Ter um serviço formal de **Defesa Civil** para inundação/alagamento, o que
  dá um ponto de contato institucional real para eventual validação futura.

## 2. Área de estudo

| Região | Bairros de referência (histórico de alagamento) | Curso d'água |
|---|---|---|
| Centro | Centro, Vila Adyana, Jardim Satélite | Rio Paraíba do Sul (canal principal) |
| Norte | Jardim Satélite (porção norte), Distrito de São Francisco Xavier | Represa/Rio Jaguari |
| Sul | Parque Interlagos, Jardim São Judas Tadeu | Córregos afluentes do Paraíba do Sul |
| Leste | Jardim Nova Detroit, Monte Castelo, Novo Horizonte, Santa Maria | Rio Comprido / Ribeirão Vidoca |
| Oeste | Urbanova, Jardim das Colinas | Córregos afluentes menores |
| Sudeste | Jardim Morumbi, Torrão de Ouro | Córregos afluentes, divisa com Jacareí |

A geometria usada no mapa (`frontend/src/assets/sjc-regions.json`) é
**esquemática/simplificada** — retângulos aproximados por região, no mesmo
espírito do protótipo original (que já usava retângulos para as
macrorregiões do Brasil) — e não um levantamento cartográfico oficial de
limites de bairro. Cada região carrega no GeoJSON metadados reais
(`bairros_referencia`, `curso_dagua`, `historico_risco`) usados no popup do
mapa.

**Fontes consultadas para grounding do estudo de caso:**
- [Chuva causa enchentes em bairros de São José dos Campos — Life Informa](https://informa.life/chuva-desta-sexta-feira-volta-a-causar-enchentes-em-bairros-de-sao-jose-dos-campos/)
- [Inundação e Alagamento — Defesa Civil, Prefeitura de SJC](https://www.sjc.sp.gov.br/carta-de-servicos/cidadaos/protecao-ao-cidadao/defesa-civil/inundacao-e-alagamento/)
- [Rio Comprido (Paraíba do Sul) — Wikipedia](https://en.wikipedia.org/wiki/Comprido_River_(Para%C3%ADba_do_Sul))
- [Lista de bairros de São José dos Campos — Wikipédia](https://pt.wikipedia.org/wiki/Lista_de_bairros_de_S%C3%A3o_Jos%C3%A9_dos_Campos)
- [Diagnóstico Síntese, Plano Diretor de SJC (dez/2017) — divisão em 6 regiões administrativas](https://www.sjc.sp.gov.br/media/2hqcjibh/22_sintese_diagnostico_tecnico.pdf)
- [Coordenadas geográficas de São José dos Campos — geografos.com.br](https://www.geografos.com.br/cidades-sao-paulo/sao-jose-dos-campos.php)

## 3. Natureza dos dados — o que é real e o que é derivado

**Atualizado em 18/08/2026** — o projeto passou de dados 100% sintéticos
para dados reais onde tecnicamente viável. É importante deixar explícito,
para a apresentação, **o que cada parte do sistema realmente representa**:

| Componente | Real ou derivado? | Detalhe |
|---|---|---|
| Localização geográfica das 6 regiões (lat/lon) | **Real** (aproximado) | Coordenadas plausíveis dentro do município, usadas de fato para consultar as APIs. |
| Previsão de chuva (`previsao_chuva_d1/d2/d3`) | **Real** | Chamada em tempo real à API pública da [Open-Meteo](https://open-meteo.com/) para a lat/lon de cada região. |
| Precipitação histórica por região | **Real** | [Open-Meteo Archive API](https://open-meteo.com/en/docs/historical-weather-api) (reanálise ERA5), consultada por coordenada exata de cada região — não é mais sintética. A API pública do INMET foi testada (`apitempo.inmet.gov.br`) e seu endpoint de dados está indisponível na prática (retorna vazio para qualquer estação/período), então a Open-Meteo Archive foi usada como fonte real no lugar. |
| Nível de rio/córrego por região | **Real + calibração regional, documentada** | Deriva da **única estação telemétrica real da ANA dentro de SJC** (código `58128200`, Rio Jaguari — achada consultando o inventário público da ANA). Como é uma estação de barragem (não há estação pública por bairro), a *anomalia* desse sinal real é escalada por um fator de exposição por região (mesma calibração pública de risco relativo já usada — Leste/Sul mais expostas, Norte/Oeste menos). Ver `backend/connectors/ana_connector.py` para o racional completo — não fingimos 6 medições reais independentes. |
| Bairros de referência / curso d'água / histórico textual no mapa | **Real**, baseado nas fontes da seção 2 | Não é uma lista exaustiva nem substitui um levantamento oficial da Defesa Civil. |
| Pontos de alagamento específicos (endereços, datas exatas de eventos) | **Não incluído** | Ver seção 6 (limitações) — integrar registros oficiais da Defesa Civil é trabalho futuro. |

Os arquivos `backend/historical_data/<região>.csv` continuam existindo, mas
mudaram de papel: eram a fonte de dados sintéticos, agora são um **snapshot
real** (gerado por `backend/scripts/generate_sjc_data.py` contra as APIs
reais) usado como base de treino e como *fallback offline* dos conectores
reais quando a Open-Meteo/ANA estão fora do ar — nunca mais dados
inventados.

## 4. Metodologia

1. **Coleta por região**: `DataManager` busca, para a região selecionada,
   precipitação real (`PrecipitationConnector`, Open-Meteo Archive), nível
   de rio real+calibrado (`ANAConnector`, estação real da ANA em SJC) e
   previsão real de 3 dias (`OpenMeteoConnector`, API Open-Meteo forecast).
   Cada conector combina o histórico-base (CSV, real) com uma janela recente
   buscada ao vivo, com fallback gracioso se a API estiver indisponível.
2. **Engenharia de features** (calculada por região, para não misturar
   séries nas bordas): chuva acumulada e máxima em 3 dias, média móvel do
   nível do rio, variação diária do nível, e **`subida_rio_14d`**: a
   diferença entre o nível atual e a mínima dos últimos 14 dias. Essa
   feature foi introduzida especificamente para o estudo de caso
   multi-região: como Centro/Leste ficam às margens do Rio Paraíba do Sul
   (maior) e Sul/Oeste têm córregos menores, um limiar *absoluto* de nível
   não é comparável entre regiões — a subida relativa à própria mínima
   recente, sim.
3. **Definição de risco**: `risco = 0` (baixo), `1` (moderado), `2` (alto),
   por limiares sobre chuva acumulada, `subida_rio_14d` e previsão de chuva
   (ver `backend/feature_engineering.py`). Recalibrados em 18/08/2026 sobre
   a distribuição real dos dados — a correlação entre chuva local e o nível
   da única estação real da ANA é fraca (é uma barragem, seu nível reflete
   a operação do reservatório, não só a chuva local), então os limiares
   usam OR entre os sinais em vez de exigir que ambos disparem juntos.
4. **Treinamento**: **ensemble de 2 classificadores** — `RandomForestClassifier`
   (bagging) + `GradientBoostingClassifier` (boosting), combinados por voto
   suave (`VotingClassifier`, `voting='soft'`) — em vez de um único modelo,
   sobre as **6 regiões combinadas** (~660 dias-região), com validação
   cruzada estratificada (5 folds) além do split holdout 75/25.

## 5. Resultados

Distribuição de risco por região no dataset de treino (dados reais, estação
chuvosa mais recente concluída — dez/2025 a fev/2026, ~110 dias/região):

| Região | Baixo (0) | Moderado (1) | Alto (2) |
|---|---|---|---|
| Centro  | 62 | 36 | 13 |
| Norte   | 64 | 40 | 7  |
| Sul     | 51 | 40 | 20 |
| Leste   | 50 | 37 | 24 |
| Oeste   | 78 | 27 | 6  |
| Sudeste | 65 | 36 | 10 |

Isso reproduz, a partir de dados reais, o padrão esperado pela literatura de
imprensa consultada: **Leste e Sul concentram os dias de risco
moderado/alto**, coerente com os relatos de alagamento mais graves (água
atingindo ~1m em residências no Jardim Nova Detroit, região Leste); **Oeste
e Norte apresentam bem menos risco**, coerente com o menor volume de
relatos de imprensa para essas regiões.

Validação cruzada estratificada (5 folds, ensemble RandomForest+GradientBoosting):

```
AUC macro (one-vs-rest): ~0.998
              precision    recall  f1-score   support
           0       0.99      0.99      0.99       370
           1       0.98      0.98      0.98       216
           2       0.96      0.97      0.97        80
    accuracy                           0.99       666
```

A alta acurácia/AUC é esperada e **não deve ser lida como validação contra a
realidade** — o alvo (`risco`) é derivado por regra a partir de um subconjunto
das próprias features usadas para treinar (vazamento de informação
estrutural), então o modelo está aprendendo a recuperar essa regra, não um
fenômeno físico observado de forma independente. Isso vale mesmo com dados
reais de entrada — a métrica alta reflete a formulação do problema, não
prova preditiva contra enchentes reais. Uma melhoria genuína de AUC exigiria
rótulos de risco vindos de ocorrências reais documentadas (ex.: registros da
Defesa Civil), não de um limiar sobre as próprias features de entrada — ver
seção 6. O valor do experimento está na arquitetura (pipeline de coleta real
→ features → ensemble → XAI) e na calibração do dataset para refletir o
risco relativo real reportado por região, não na acurácia em si.

## 6. Limitações (para deixar explícito na apresentação)

- O nível de rio/córrego **não vem de 6 estações reais independentes** — é a
  anomalia de uma única estação real da ANA (barragem no Rio Jaguari, dentro
  de SJC) escalada por um fator de exposição documentado por região (seção
  3). Não existe estação telemétrica pública por bairro em SJC.
- A API pública do INMET está indisponível na prática (endpoint de dados
  retorna vazio) — a precipitação real vem da Open-Meteo Archive, não do
  INMET diretamente, embora ambas usem reanálise/observação meteorológica.
- A geometria das regiões no mapa é esquemática, não um levantamento GIS
  oficial de limites de bairro.
- Não há ainda integração com pontos de alagamento oficiais da Defesa Civil
  de SJC (o portal da prefeitura descreve o *serviço* de vistoria, mas não
  publica uma lista/mapa de pontos críticos consultável via API).
- O modelo é avaliado contra um alvo derivado por regra de um subconjunto
  das próprias features de entrada — não há ainda validação contra eventos
  de enchente reais e documentados de forma independente.

## 7. Próximos passos

Ver `IMPLEMENTATION_PLAN.md` para o plano completo de fases. Destaques
diretamente relevantes para amadurecer este estudo de caso:

- Buscar registros históricos de pontos de alagamento junto à Defesa Civil
  do município para validar/recalibrar os limiares de risco contra eventos
  reais e documentados — e, idealmente, treinar contra esse alvo em vez do
  limiar por regra atual (ver seção 5).
- Reavaliar periodicamente se a API de dados do INMET voltou a funcionar
  (testada e indisponível em 18/08/2026), o que permitiria uma segunda fonte
  real de precipitação independente da Open-Meteo.
- Investigar se outras estações (não-telemétricas) da ANA dentro de SJC
  identificadas na pesquisa desta integração (ex.: réguas no Ribeirão dos
  Putins, Rio Buquira/Ferrão, Córrego do Vidoca) têm histórico consultável
  via HidroWeb, para diferenciar o nível de rio por região com mais de uma
  estação real.
- **Fase 6 (conceitual)**: a ideia de modelar a rede de drenagem como um
  grafo (ver seção 6.2 do `IMPLEMENTATION_PLAN.md`) ganharia mais sentido
  aqui — com sub-bacias reais de SJC como vértices — caso o projeto avance
  para essa direção.
