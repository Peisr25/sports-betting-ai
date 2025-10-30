# Comparação Detalhada - Lite vs Pro

## 📊 Visão Geral

| Aspecto | Lite | Pro |
|---------|------|-----|
| **Preço** | Gratuito | Gratuito |
| **Nível** | Iniciante | Avançado |
| **API** | football-data.org | football-data.org |
| **Banco de Dados** | ❌ Memória | ✅ SQLite |

## 🤖 Modelos de Predição

| Modelo | Lite | Pro |
|--------|------|-----|
| Poisson Distribution | ✅ | ✅ |
| XGBoost (ML) | ❌ | ✅ |
| Sistema Ensemble | ❌ | ✅ |
| Treinamento Customizado | ❌ | ✅ |

## 🎯 Mercados de Apostas

| Mercado | Lite | Pro |
|---------|------|-----|
| Resultado (1X2) | ✅ | ✅ |
| Total de Gols (Over/Under) | ✅ (5 linhas) | ✅ (5 linhas) |
| Ambos Marcam (BTTS) | ✅ | ✅ |
| Escanteios | ✅ Estimado | ✅ Estimado |
| Cartões | ✅ Estimado | ✅ Estimado |
| Placar Exato | ✅ | ✅ |
| Handicap Asiático | ❌ | ✅ |

## 📈 Análises Avançadas

| Recurso | Lite | Pro |
|---------|------|-----|
| Valor Esperado (EV) | ❌ | ✅ |
| Critério de Kelly | ❌ | ✅ |
| Backtesting | ❌ | ✅ |
| Análise de Forma | Básica | Avançada |
| Confrontos Diretos | ❌ | ✅ |
| Análise Multi-Mercado | ❌ | ✅ |

## 💾 Dados e Armazenamento

| Recurso | Lite | Pro |
|---------|------|-----|
| Cache de Dados | Memória (5min) | SQLite Persistente |
| Histórico de Partidas | ❌ | ✅ |
| Histórico de Predições | ❌ | ✅ |
| Resultados de Apostas | ❌ | ✅ |
| Exportação de Dados | ❌ | ✅ CSV/JSON |

## 🔧 Recursos Técnicos

| Recurso | Lite | Pro |
|---------|------|-----|
| API REST | ✅ FastAPI | ✅ FastAPI |
| Documentação OpenAPI | ✅ | ✅ |
| Scripts de Exemplo | ✅ 4 scripts | ✅ 7+ scripts |
| Workflows n8n | ❌ | ✅ |
| Notificações | ❌ | ✅ (Telegram/Discord) |

## 📚 Documentação

| Item | Lite | Pro |
|------|------|-----|
| README | ✅ | ✅ Detalhado |
| API Documentation | ✅ | ✅ Completa |
| User Guide | ✅ | ✅ Avançado |
| N8N Setup | ❌ | ✅ |
| Advanced Features | ❌ | ✅ |

## 🏆 Competições Suportadas

| Competição | Lite | Pro |
|------------|------|-----|
| Premier League | ✅ | ✅ |
| La Liga | ✅ | ✅ |
| Bundesliga | ✅ | ✅ |
| Serie A | ✅ | ✅ |
| Ligue 1 | ✅ | ✅ |
| Brasileirão | ✅ | ✅ |
| Champions League | ✅ | ✅ |
| Primeira Liga | ✅ | ✅ |
| Eredivisie | ✅ | ✅ |
| Outras Ligas | ❌ | ✅ Fácil Adicionar |

## 💰 Custos

### API football-data.org

**Tier Gratuito** (Recomendado para Lite):
- 10 requisições/minuto
- 100 requisições/dia
- Dados básicos

**Tier Pago** (Recomendado para Pro):
- A partir de €19/mês
- 3000+ requisições/dia
- Dados avançados
- Sem rate limit

## 🎓 Curva de Aprendizado

### Lite
- ⭐ Fácil
- Ideal para iniciantes
- Configuração em 5 minutos
- Resultados imediatos

### Pro
- ⭐⭐⭐ Moderado
- Requer conhecimento em ML
- Configuração em 15-30 minutos
- Treinamento de modelos opcional
- Gestão de banco de dados

## 🚀 Performance

| Métrica | Lite | Pro |
|---------|------|-----|
| Tempo de Resposta | <200ms | <500ms |
| Predições/Segundo | ~50 | ~20 |
| Uso de Memória | ~100MB | ~500MB |
| Uso de Disco | Mínimo | 100MB+ |

## 📊 Precisão Estimada

| Mercado | Lite (Poisson) | Pro (Ensemble) |
|---------|----------------|----------------|
| Resultado (1X2) | 50-55% | 55-60% |
| Over/Under 2.5 | 55-60% | 60-65% |
| BTTS | 55-60% | 60-65% |

*Precisão varia por liga e qualidade dos dados*

## 🤔 Qual Escolher?

### Escolha **Lite** se você:
- ✅ Está começando em análise esportiva
- ✅ Quer testar o sistema gratuitamente
- ✅ Não precisa de histórico de dados
- ✅ Faz poucas predições por dia
- ✅ Prefere simplicidade

### Escolha **Pro** se você:
- ✅ Já tem experiência em apostas
- ✅ Quer máxima precisão
- ✅ Precisa análise de valor (EV)
- ✅ Quer gestão de banca (Kelly)
- ✅ Faz muitas predições diariamente
- ✅ Quer backtesting
- ✅ Planeja uso profissional

## 🆙 Migração

Migrar de Lite para Pro é simples:

1. Copie seu `.env`
2. Instale dependências da Pro
3. Seus scripts continuam funcionando
4. Recursos extras disponíveis gradualmente

## 📞 Suporte

Ambas as versões incluem:
- ✅ Documentação completa
- ✅ Exemplos funcionais
- ✅ API interativa
- ✅ Community support

---

**Recomendação**: Comece com **Lite**, depois faça upgrade para **Pro** quando precisar de recursos avançados.
