# POC - Estratégia de Recolocação de Posição

Sistema de simulação para estratégia de trading de criptomoedas baseada em recolocação de posição com análise de dados históricos da Binance.

## 📋 Funcionalidades

- Simulação de estratégia de recolocação de posição
- Interface web interativa com Streamlit
- Análise de dados históricos da Binance (timeframe 4h)
- Visualização gráfica de preços e operações
- Métricas detalhadas de performance
- Exportação de relatórios em CSV

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd poc-v3
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Execute a aplicação

```bash
streamlit run aplicativo.py
```

A aplicação será aberta automaticamente no navegador em `http://localhost:8501`

## 📊 Como Usar

### 1. Configurações Básicas

Na barra lateral, configure:

- **Par de Trading**: Escolha entre BTC/USDT, ETH/USDT ou BNB/USDT
- **Quantidade Inicial**: Quantidade de tokens para iniciar a estratégia
- **Período de Análise**: Defina as datas de início e fim

### 2. Parâmetros da Estratégia

- **Percentual Desvalorização para Venda**: Quando o preço cair X% do máximo em 7 dias, dispara venda
- **Percentual Valorização para Compra**: Quando o preço subir Y% do mínimo após venda, dispara compra

### 3. Execução

1. Clique em "🚀 Executar Simulação"
2. Aguarde o processamento dos dados
3. Analise os resultados apresentados

### 4. Resultados

A aplicação apresenta:

- **Gráfico Principal**: Preços históricos com pontos de compra/venda
- **Métricas de Performance**: Resumo quantitativo dos resultados
- **Histórico de Operações**: Tabela detalhada de todas as transações
- **Relatório Resumo**: Análise textual dos resultados

## 🎯 Como Funciona a Estratégia

### Estados da Estratégia

1. **COMPRADO**: Monitora preço máximo em janela de 7 dias
2. **VENDIDO**: Monitora preço mínimo desde a venda

### Lógica de Operação

1. **Gatilho de Venda**: Quando preço atual ≤ (preço_máximo_7dias × (1 - percentual_desvalorização/100))
2. **Gatilho de Compra**: Quando preço atual ≥ (preço_mínimo_pós_venda × (1 + percentual_valorização/100))

### Objetivo

Aumentar a quantidade de tokens através de ciclos repetidos de compra/venda, aproveitando volatilidade do mercado.

## 📁 Estrutura do Projeto

```
poc-v3/
├── aplicativo.py           # Interface principal Streamlit
├── buscador_dados.py       # Módulo para buscar dados da Binance
├── simulador_estrategia.py # Lógica core da estratégia
├── analisador_resultados.py # Processamento e visualização de resultados
├── requirements.txt        # Dependências do projeto
└── README.md              # Este arquivo
```

## 🔧 Dependências

- `streamlit==1.45.1`: Framework para interface web
- `pandas==2.2.3`: Manipulação de dados
- `ccxt==4.4.85`: Biblioteca para APIs de exchanges
- `plotly==6.1.1`: Criação de gráficos interativos

## ⚠️ Limitações

- Dados limitados à Binance (exchange pública)
- Timeframe fixo de 4 horas
- Não executa operações reais (apenas simulação)
- Não considera taxas de transação
- Requer conexão com internet para buscar dados

## 📈 Dicas de Uso

1. **Período de Análise**: Use pelo menos 30 dias para resultados significativos
2. **Parâmetros**: Comece com valores moderados (5% para ambos os percentuais)
3. **Mercado Volátil**: A estratégia funciona melhor em mercados com alta volatilidade
4. **Backtesting**: Teste diferentes períodos e parâmetros antes de aplicar em real

## 🐛 Solução de Problemas

### Erro de Conexão com Binance
- Verifique sua conexão com internet
- Tente reduzir o período de análise
- Aguarde alguns minutos e tente novamente

### Nenhuma Operação Executada
- Ajuste os percentuais da estratégia (valores menores)
- Verifique se o período escolhido teve volatilidade suficiente
- Teste com períodos mais longos

### Performance Lenta
- Reduza o período de análise
- Use períodos mais recentes
- Verifique recursos do sistema

## 📚 Guia Detalhado de Uso

### Interface do Usuário

#### Barra Lateral (Configurações)

**Seleção do Par de Trading**
- **Opções disponíveis**: BTC/USDT, ETH/USDT, BNB/USDT
- **Recomendação**: BTC/USDT para maior liquidez e dados consistentes

**Parâmetros da Estratégia**

- **Percentual Desvalorização para Venda (3% - 10%)**
  - Define quando vender baseado na queda do preço máximo
  - Valores menores = mais operações, maior sensibilidade
  - Valores maiores = menos operações, maior tolerância

- **Percentual Valorização para Compra (3% - 10%)**
  - Define quando comprar baseado na alta do preço mínimo
  - Valores menores = recompra mais rápida
  - Valores maiores = aguarda maior confirmação de alta

- **Quantidade Inicial de Tokens**
  - Valor de referência para calcular lucros
  - Use 1.0 para facilitar cálculos

**Período de Análise**
- Período mínimo: 7 dias
- Recomendado: 30-180 dias para resultados significativos

#### Área Principal (Resultados)

**Gráfico de Preços e Operações**
- **Linha azul**: Preço histórico do par
- **Pontos vermelhos**: Operações de venda
- **Pontos verdes**: Operações de compra
- **Interativo**: Zoom, pan, hover para detalhes

**Métricas de Performance**
- **Total de Operações**: Quantidade total de compras + vendas
- **Operações Lucrativas**: Compras que resultaram em ganho de tokens
- **Tokens Final vs Inicial**: Comparação quantitativa
- **Lucro Percentual**: Performance geral da estratégia

### Interpretando os Resultados

#### Métricas Importantes

**Taxa de Sucesso**
- Calculada como: (Operações Lucrativas / Total de Compras) × 100
- Acima de 50% = estratégia positiva
- Acima de 70% = estratégia muito boa

**Lucro Total em Tokens**
- Quantidade adicional de tokens obtida
- Valor positivo = estratégia lucrativa

**Lucro Percentual**
- Performance relativa ao investimento inicial
- Compare com buy-and-hold do período

#### Cenários de Análise

**Resultado Positivo**
- Mais tokens no final do que no início
- Múltiplas operações bem-sucedidas
- Aproveitou bem a volatilidade do mercado

**Resultado Negativo**
- Menos tokens no final
- Pode indicar parâmetros inadequados
- Mercado pode ter sido muito lateral ou em forte tendência

**Nenhuma Operação**
- Parâmetros muito conservadores
- Período com pouca volatilidade
- Ajustar percentuais para valores menores

### Casos de Uso Recomendados

1. **Backtesting de Parâmetros**: Teste diferentes combinações de percentuais
2. **Análise de Mercado**: Observe comportamento em diferentes condições
3. **Educação em Trading**: Compreenda mecânicas de estratégias automatizadas
4. **Validação de Conceitos**: Teste hipóteses sobre comportamento de preços

### Considerações Importantes

#### Limitações da Simulação

- **Não considera taxas**: Exchanges cobram taxas de transação (0.1-0.25%)
- **Slippage não modelado**: Diferença entre preço esperado e executado
- **Dados históricos**: Performance passada não garante resultados futuros

#### Boas Práticas

- Teste em diferentes períodos (alta, baixa, lateral)
- Use múltiplos pares de trading
- Compare com estratégia buy-and-hold
- Nunca invista mais do que pode perder

## 📞 Suporte

Para reportar problemas ou sugerir melhorias, abra uma issue no repositório do projeto.

---

## ⚖️ Direitos Autorais e Aviso Legal

**© 2025 - Todos os direitos reservados.**

Esta versão do sistema tem **única e exclusivamente finalidade de prova de conceito (POC)**. 

### Importante:
- Este software é fornecido apenas para fins educacionais e de demonstração
- Não constitui aconselhamento financeiro ou de investimento
- O uso em operações reais de trading é de inteira responsabilidade do usuário
- Os desenvolvedores não se responsabilizam por perdas financeiras
- Sempre consulte profissionais qualificados antes de investir
- Investimentos em criptomoedas envolvem riscos significativos