"""
Módulo responsável por processar operações e gerar visualizações de resultados
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Any
import streamlit as st


def criar_grafico_principal(
    dados_historicos: pd.DataFrame,
    operacoes: List[Dict[str, Any]]
) -> go.Figure:
    """
    Cria o gráfico principal com preços e marcadores de operações
    
    Parâmetros:
        dados_historicos: DataFrame com dados OHLCV
        operacoes: Lista de operações executadas
    
    Retorno:
        Figura plotly com gráfico completo
    """
    fig = go.Figure()
    
    # Adicionar linha de preços
    fig.add_trace(go.Scatter(
        x=dados_historicos['timestamp'],
        y=dados_historicos['close'],
        mode='lines',
        name='Preço de Fechamento',
        line=dict(color='blue', width=2)
    ))
    
    if operacoes:
        # Separar operações por tipo
        compras = [op for op in operacoes if op['tipo'] == 'COMPRA']
        vendas = [op for op in operacoes if op['tipo'] == 'VENDA']
        
        # Adicionar marcadores de compra
        if compras:
            fig.add_trace(go.Scatter(
                x=[op['timestamp'] for op in compras],
                y=[op['preco'] for op in compras],
                mode='markers',
                name='Compras',
                marker=dict(
                    color='green',
                    size=12,
                    symbol='triangle-up',
                    line=dict(width=2, color='darkgreen')
                )
            ))
        
        # Adicionar marcadores de venda
        if vendas:
            fig.add_trace(go.Scatter(
                x=[op['timestamp'] for op in vendas],
                y=[op['preco'] for op in vendas],
                mode='markers',
                name='Vendas',
                marker=dict(
                    color='red',
                    size=12,
                    symbol='triangle-down',
                    line=dict(width=2, color='darkred')
                )
            ))
    
    # Configurar layout
    fig.update_layout(
        title='Estratégia de Recolocação de Posição - Histórico de Preços e Operações',
        xaxis_title='Data/Hora',
        yaxis_title='Preço (USD)',
        hovermode='x unified',
        showlegend=True,
        height=600,
        template='plotly_white'
    )
    
    # Formatação do eixo Y para valores monetários
    fig.update_layout(yaxis=dict(tickformat='$,.2f'))
    
    return fig


def processar_tabela_operacoes(operacoes: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Processa lista de operações em DataFrame formatado para exibição
    
    Parâmetros:
        operacoes: Lista de operações executadas
    
    Retorno:
        DataFrame formatado para exibição na interface
    """
    if not operacoes:
        return pd.DataFrame()
    
    # Converter para DataFrame
    df_operacoes = pd.DataFrame(operacoes)
    
    # Formatar colunas para exibição
    df_formatado = pd.DataFrame()
    df_formatado['Data/Hora'] = df_operacoes['timestamp'].dt.strftime('%d/%m/%Y %H:%M')
    df_formatado['Tipo'] = df_operacoes['tipo']
    df_formatado['Preço'] = df_operacoes['preco'].apply(lambda x: f'${x:,.2f}')
    df_formatado['Quantidade'] = df_operacoes['quantidade_tokens'].apply(lambda x: f'{x:.6f}')
    df_formatado['Total Tokens'] = df_operacoes['total_tokens_apos_operacao'].apply(lambda x: f'{x:.6f}')
    df_formatado['Lucro Operação'] = df_operacoes['lucro_operacao'].apply(lambda x: f'{x:+.6f}')
    df_formatado['Lucro %'] = df_operacoes['lucro_percentual'].apply(lambda x: f'{x:+.1f}%')
    
    return df_formatado


def criar_metricas_resumidas(metricas: Dict[str, Any]) -> Dict[str, tuple]:
    """
    Organiza métricas para exibição com st.metric
    
    Parâmetros:
        metricas: Dicionário com métricas calculadas
    
    Retorno:
        Dicionário com métricas formatadas para st.metric
    """
    if not metricas:
        return {}
    
    # Organizar métricas com valores e deltas
    metricas_formatadas = {
        'Total de Operações': (
            metricas['total_operacoes'],
            None
        ),
        'Operações Lucrativas': (
            metricas['operacoes_lucrativas'],
            f"+{metricas['operacoes_lucrativas']}" if metricas['operacoes_lucrativas'] > 0 else None
        ),
        'Operações com Prejuízo': (
            metricas['operacoes_prejuizo'],
            f"+{metricas['operacoes_prejuizo']}" if metricas['operacoes_prejuizo'] > 0 else None
        ),
        'Tokens Inicial': (
            f"{metricas['tokens_inicial']:.6f}",
            None
        ),
        'Tokens Final': (
            f"{metricas['tokens_final']:.6f}",
            f"{metricas['lucro_total_tokens']:+.6f}"
        ),
        'Lucro Total (%)': (
            f"{metricas['lucro_percentual_total']:.2f}%",
            f"{metricas['lucro_percentual_total']:+.2f}%" if metricas['lucro_percentual_total'] != 0 else None
        )
    }
    
    return metricas_formatadas


def gerar_relatorio_resumo(
    operacoes: List[Dict[str, Any]], 
    metricas: Dict[str, Any],
    simbolo: str,
    periodo_analise: str
) -> str:
    """
    Gera relatório textual resumido dos resultados
    
    Parâmetros:
        operacoes: Lista de operações executadas
        metricas: Métricas calculadas
        simbolo: Símbolo analisado
        periodo_analise: Período da análise
    
    Retorno:
        String com relatório formatado
    """
    if not operacoes or not metricas:
        return "Nenhuma operação foi executada durante o período analisado."
    
    # Calcular taxa de sucesso
    total_compras = len([op for op in operacoes if op['tipo'] == 'COMPRA'])
    taxa_sucesso = (metricas['operacoes_lucrativas'] / total_compras * 100) if total_compras > 0 else 0
    
    relatorio = f"""
## Relatório Resumido - {simbolo}

**Período de Análise:** {periodo_analise}

**Resultados Gerais:**
- Total de operações executadas: {metricas['total_operacoes']}
- Operações lucrativas: {metricas['operacoes_lucrativas']} ({taxa_sucesso:.1f}%)
- Operações com prejuízo: {metricas['operacoes_prejuizo']}

**Performance Financeira:**
- Tokens inicial: {metricas['tokens_inicial']:.6f}
- Tokens final: {metricas['tokens_final']:.6f}
- Lucro total: {metricas['lucro_total_tokens']:+.6f} tokens ({metricas['lucro_percentual_total']:+.2f}%)

**🎯 Conclusão:**  
> A estratégia {"foi lucrativa" if metricas['lucro_percentual_total'] > 0 else "teve prejuízo"} no período analisado, 
> {"aumentando" if metricas['lucro_total_tokens'] > 0 else "diminuindo"} a quantidade de tokens em 
> {abs(metricas['lucro_percentual_total']):.2f}%.
    """
    
    return relatorio


def validar_dados_para_analise(
    dados_historicos: pd.DataFrame,
    operacoes: List[Dict[str, Any]]
) -> tuple[bool, str]:
    """
    Valida se os dados estão adequados para análise
    
    Parâmetros:
        dados_historicos: DataFrame com dados históricos
        operacoes: Lista de operações
    
    Retorno:
        Tupla com status de validação e mensagem
    """
    if dados_historicos.empty:
        return False, "Dados históricos não foram carregados corretamente"
    
    if len(dados_historicos) < 168:  # Menos que 7 dias de dados 4h
        return False, "Dados históricos insuficientes (mínimo 7 dias necessários)"
    
    # Verificar se há preços válidos
    if dados_historicos['close'].isna().any() or (dados_historicos['close'] <= 0).any():
        return False, "Dados históricos contêm preços inválidos"
    
    return True, "Dados válidos para análise"


def exportar_operacoes_csv(operacoes: List[Dict[str, Any]]) -> bytes:
    """
    Exporta operações para formato CSV
    
    Parâmetros:
        operacoes: Lista de operações
    
    Retorno:
        Bytes do arquivo CSV
    """
    if not operacoes:
        return b""
    
    df = pd.DataFrame(operacoes)
    return df.to_csv(index=False).encode('utf-8')