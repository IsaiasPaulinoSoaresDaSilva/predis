# Guia de Execução e Testes

Este guia fornece as instruções para treinar o modelo de IA, iniciar os servidores de backend e frontend, e verificar se a aplicação está funcionando corretamente.

## Pré-requisitos

- Certifique-se de que você seguiu todos os passos do `INSTALL_GUIDE.md` e que todas as dependências foram instaladas.
- Para os comandos de backend, o ambiente virtual (`venv`) deve estar ativado.

## 1. Treinar o Modelo de Inteligência Artificial

Este passo só precisa ser executado uma vez (ou sempre que os dados em `historical_data.csv` forem atualizados).

O script `model.py` irá ler os dados históricos, treinar um modelo de classificação e salvá-lo como `disaster_model.joblib`.

**Comando (execute na raiz do projeto):**

```bash
python3 backend/model.py
```

**Verificação:**
- O terminal deve exibir uma mensagem como "Acurácia do modelo: X.XX" e "Modelo treinado e salvo com sucesso...".
- Um novo arquivo chamado `disaster_model.joblib` deve aparecer na pasta `backend`.

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
- Você pode abrir este endereço no seu navegador e verá a mensagem: `{"message":"Bem-vindo à API de Previsão de Desastres v2"}`.

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

Ao abrir a URL do frontend no navegador, você deve ver o "Painel de Monitoramento de Desastres".

**Verifique os seguintes pontos:**

1.  **Carregamento Inicial:** O gráfico de "Tendência de Chuvas" deve ser populado com os dados históricos.
2.  **Simulação em Tempo Real:** A cada 5 segundos:
    - O card "Probabilidade de Risco" deve atualizar seu valor percentual.
    - O círculo indicador de risco deve pulsar e, possivelmente, mudar de cor (verde, laranja, ou vermelho) dependendo da probabilidade.
    - Os gráficos de barra em "Fatores de Risco (XAI)" devem se ajustar, mostrando a contribuição da precipitação e do nível do rio para a previsão atual.
3.  **Ausência de Erros:** Verifique o console do navegador (pressione F12) e os terminais do backend e frontend para garantir que não há mensagens de erro sendo exibidas.
