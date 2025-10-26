# Guia de Configuração do n8n

Este guia detalha como importar e configurar os workflows do n8n que servem como interface para o sistema de apostas. Siga estes passos após ter o [backend Python rodando](#) na sua máquina local.

## Pré-requisitos

-   Acesso a uma instância do n8n (Cloud ou Self-hosted).
-   A API Python deve estar em execução em `http://localhost:5000`.

## Workflows Incluídos

O projeto vem com dois workflows essenciais:

1.  **`betting_prediction.json`**: Um workflow acionado por webhook que recebe uma solicitação de predição, chama a API Python e retorna o resultado. É a principal forma de interagir com o sistema.
2.  **`data_update.json`**: Um workflow agendado que executa automaticamente (por padrão, uma vez por dia) para chamar o endpoint `/update` da API Python, mantendo o banco de dados de estatísticas sempre atualizado.

## Passo 1: Importar os Workflows

Primeiro, você precisa importar os dois arquivos JSON para a sua instância do n8n.

1.  Abra seu painel do n8n.
2.  No menu lateral, clique em **Workflows**.
3.  Clique no botão **Import from File**.
4.  Selecione o arquivo `betting_prediction.json` localizado no diretório `n8n_workflows/` do projeto.
5.  Clique em **Import Workflow**.
6.  Repita os passos 3 a 5 para o arquivo `data_update.json`.

Após a importação, você verá os dois novos workflows na sua lista.

## Passo 2: Configurar e Ativar o Workflow de Predição

O workflow `Sports Betting Prediction` é o mais importante para o uso diário.

1.  Abra o workflow `Sports Betting Prediction`.
2.  **Verifique o nó `Call Python API`**: Por padrão, a URL está configurada como `http://localhost:5000/predict`. Se você estiver rodando a API Python em uma porta ou endereço diferente, atualize a URL neste nó.
    -   Se você estiver usando o n8n Desktop, `localhost` funcionará diretamente.
    -   Se estiver usando n8n Cloud, você precisará expor sua API Python local para a internet usando uma ferramenta como o **ngrok**. A URL no nó `HTTP Request` deverá ser a URL pública fornecida pelo ngrok.

3.  **Ative o Workflow**: No canto superior direito da tela, alterne o botão de **Inactive** para **Active**. Isso ativará o webhook.

4.  **Obtenha a URL do Webhook**: Com o workflow ativo, o n8n gerará uma URL de webhook. Clique no nó `Webhook` e, na aba **Webhook URLs**, você encontrará as URLs de teste e de produção. A URL de teste é ideal para o desenvolvimento, enquanto a de produção é para uso contínuo.

    -   **URL de Teste**: `https://seu-n8n.com/webhook-test/predict-bet`
    -   **URL de Produção**: `https://seu-n8n.com/webhook/predict-bet`

Guarde esta URL, pois é através dela que você solicitará as predições.

## Passo 3: Configurar e Ativar o Workflow de Atualização

O workflow `Sports Data Auto Update` garante que seus dados estejam sempre frescos.

1.  Abra o workflow `Sports Data Auto Update`.
2.  **Verifique o nó `Schedule Trigger`**: Por padrão, ele está configurado para rodar todos os dias às 2h da manhã (`0 0 2 * * *`). Você pode ajustar essa frequência conforme sua necessidade. Por exemplo, para rodar a cada 12 horas, você pode usar a expressão cron `0 */12 * * *`.

3.  **Verifique o nó `Update League Data`**: Assim como no outro workflow, verifique se a URL `http://localhost:5000/update` está correta.

4.  **Ative o Workflow**: Alterne o botão de **Inactive** para **Active**.

Uma vez ativo, este workflow executará silenciosamente no horário agendado, mantendo seu banco de dados atualizado sem qualquer intervenção manual.

## Solução de Problemas (Troubleshooting)

-   **Erro `Connection Refused` no n8n**: Este erro geralmente significa que o n8n não conseguiu se conectar à sua API Python.
    -   Verifique se a API Python está rodando.
    -   Confirme se a URL no nó `HTTP Request` está correta (`http://localhost:5000/...`).
    -   Se estiver usando n8n Cloud, certifique-se de que sua API local está exposta corretamente (ex: via ngrok) e que você está usando a URL pública.

-   **Workflow não é acionado**: 
    -   Verifique se o workflow está **ativo**.
    -   Confirme se você está usando a URL correta do webhook (teste vs. produção).
    -   Verifique se você está fazendo a requisição com o método correto (`POST`).

-   **Erros de `Timeout`**: Se o nó `Call Python API` resultar em timeout, pode ser que a API esteja levando muito tempo para processar. Você pode aumentar o valor do timeout nas configurações do nó `HTTP Request` > **Options** > **Timeout**.

Com os workflows configurados, você está pronto para começar a usar o sistema. Consulte o **[USER_GUIDE.md](./USER_GUIDE.md)** para aprender a fazer suas primeiras predições.

