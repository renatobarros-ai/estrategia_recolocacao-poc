"""
Módulo contendo a lógica core da estratégia de recolocação de posição
"""

import pandas as pd
from typing import List, Dict, Any
from datetime import datetime


def executar_simulacao_estrategia(
    dados_historicos: pd.DataFrame,
    quantidade_inicial: float,
    percentual_desvalorizacao: float,
    percentual_valorizacao: float
) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Executa a simulação completa da estratégia de recolocação de posição
    
    Parâmetros:
        dados_historicos: DataFrame com dados OHLCV
        quantidade_inicial: Quantidade inicial de tokens
        percentual_desvalorizacao: Percentual para gatilho de venda (%)
        percentual_valorizacao: Percentual para gatilho de compra (%)
    
    Retorno:
        Tupla contendo lista de operações e métricas finais
    """
    if dados_historicos.empty:
        return [], {}
    
    # Inicializar variáveis da estratégia
    estado_atual = "COMPRADO"
    operacoes = []
    quantidade_tokens_atual = quantidade_inicial
    
    # Variáveis de controle para cálculos
    preco_minimo_apos_venda = float('inf')
    indice_venda = -1
    
    # Tamanho da janela deslizante (7 dias = 168 períodos de 4h)
    tamanho_janela = 42  # 7 dias * 6 períodos por dia (4h)
    
    # Processar cada período
    for i in range(len(dados_historicos)):
        periodo_atual = dados_historicos.iloc[i]
        preco_atual = periodo_atual['close']
        timestamp_atual = periodo_atual['timestamp']
        
        if estado_atual == "COMPRADO":
            # Calcular janela deslizante para preço máximo
            inicio_janela = max(0, i - tamanho_janela + 1)
            janela_dados = dados_historicos.iloc[inicio_janela:i+1]
            preco_maximo_janela = janela_dados['high'].max()
            
            # Calcular preço de gatilho para venda
            preco_venda = preco_maximo_janela * (1 - percentual_desvalorizacao / 100)
            
            # Verificar condição de venda
            if preco_atual <= preco_venda:
                # Executar venda
                operacao_venda = executar_operacao_venda(
                    timestamp_atual,
                    preco_atual,
                    quantidade_tokens_atual
                )
                operacoes.append(operacao_venda)
                
                # Atualizar estado
                estado_atual = "VENDIDO"
                preco_minimo_apos_venda = preco_atual
                indice_venda = i
        
        elif estado_atual == "VENDIDO":
            # Atualizar preço mínimo desde a venda
            preco_minimo_apos_venda = min(preco_minimo_apos_venda, preco_atual)
            
            # Calcular preço de gatilho para compra
            preco_compra = preco_minimo_apos_venda * (1 + percentual_valorizacao / 100)
            
            # Verificar condição de compra
            if preco_atual >= preco_compra:
                # Calcular nova quantidade de tokens
                valor_usd_disponivel = operacoes[-1]['valor_usd_posicao']
                nova_quantidade_tokens = valor_usd_disponivel / preco_atual
                
                # Executar compra
                operacao_compra = executar_operacao_compra(
                    timestamp_atual,
                    preco_atual,
                    nova_quantidade_tokens,
                    quantidade_tokens_atual
                )
                operacoes.append(operacao_compra)
                
                # Atualizar estado
                estado_atual = "COMPRADO"
                quantidade_tokens_atual = nova_quantidade_tokens
                preco_minimo_apos_venda = float('inf')
    
    # Calcular métricas finais
    metricas = calcular_metricas_performance(operacoes, quantidade_inicial)
    
    return operacoes, metricas


def executar_operacao_venda(
    timestamp: datetime,
    preco: float,
    quantidade_tokens: float
) -> Dict[str, Any]:
    """
    Executa uma operação de venda e registra os detalhes
    
    Parâmetros:
        timestamp: Momento da operação
        preco: Preço de venda
        quantidade_tokens: Quantidade de tokens vendidos
    
    Retorno:
        Dicionário com detalhes da operação
    """
    valor_usd_total = quantidade_tokens * preco
    
    return {
        'timestamp': timestamp,
        'tipo': 'VENDA',
        'preco': preco,
        'quantidade_tokens': quantidade_tokens,
        'total_tokens_apos_operacao': 0.0,  # Vendeu tudo
        'valor_usd_posicao': valor_usd_total,
        'lucro_operacao': 0.0,  # Será calculado na próxima compra
        'lucro_percentual': 0.0
    }


def executar_operacao_compra(
    timestamp: datetime,
    preco: float,
    quantidade_tokens: float,
    quantidade_tokens_anterior: float
) -> Dict[str, Any]:
    """
    Executa uma operação de compra e registra os detalhes
    
    Parâmetros:
        timestamp: Momento da operação
        preco: Preço de compra
        quantidade_tokens: Quantidade de tokens comprados
        quantidade_tokens_anterior: Quantidade anterior para cálculo de lucro
    
    Retorno:
        Dicionário com detalhes da operação
    """
    valor_usd_total = quantidade_tokens * preco
    lucro_tokens = quantidade_tokens - quantidade_tokens_anterior
    lucro_percentual = (lucro_tokens / quantidade_tokens_anterior) * 100 if quantidade_tokens_anterior > 0 else 0
    
    return {
        'timestamp': timestamp,
        'tipo': 'COMPRA',
        'preco': preco,
        'quantidade_tokens': quantidade_tokens,
        'total_tokens_apos_operacao': quantidade_tokens,
        'valor_usd_posicao': valor_usd_total,
        'lucro_operacao': lucro_tokens,
        'lucro_percentual': lucro_percentual
    }


def calcular_metricas_performance(
    operacoes: List[Dict[str, Any]], 
    quantidade_inicial: float
) -> Dict[str, Any]:
    """
    Calcula métricas consolidadas de performance da estratégia
    
    Parâmetros:
        operacoes: Lista de todas as operações executadas
        quantidade_inicial: Quantidade inicial de tokens
    
    Retorno:
        Dicionário com métricas calculadas
    """
    if not operacoes:
        return {
            'total_operacoes': 0,
            'operacoes_lucrativas': 0,
            'operacoes_prejuizo': 0,
            'tokens_inicial': quantidade_inicial,
            'tokens_final': quantidade_inicial,
            'lucro_total_tokens': 0.0,
            'lucro_percentual_total': 0.0
        }
    
    # Filtrar apenas operações de compra para calcular lucros
    compras = [op for op in operacoes if op['tipo'] == 'COMPRA']
    
    # Calcular estatísticas
    total_operacoes = len(operacoes)
    operacoes_lucrativas = len([op for op in compras if op['lucro_operacao'] > 0])
    operacoes_prejuizo = len([op for op in compras if op['lucro_operacao'] < 0])
    
    # Quantidade final de tokens
    if operacoes:
        ultima_operacao = operacoes[-1]
        if ultima_operacao['tipo'] == 'COMPRA':
            tokens_final = ultima_operacao['total_tokens_apos_operacao']
        else:
            # Se última operação foi venda, ainda tem o valor em USD
            # Para simplificar, consideramos que ainda temos os tokens da penúltima compra
            compras_executadas = [op for op in operacoes if op['tipo'] == 'COMPRA']
            tokens_final = compras_executadas[-1]['total_tokens_apos_operacao'] if compras_executadas else quantidade_inicial
    else:
        tokens_final = quantidade_inicial
    
    # Calcular lucro total
    lucro_total_tokens = tokens_final - quantidade_inicial
    lucro_percentual_total = (lucro_total_tokens / quantidade_inicial) * 100 if quantidade_inicial > 0 else 0
    
    return {
        'total_operacoes': total_operacoes,
        'operacoes_lucrativas': operacoes_lucrativas,
        'operacoes_prejuizo': operacoes_prejuizo,
        'tokens_inicial': quantidade_inicial,
        'tokens_final': tokens_final,
        'lucro_total_tokens': lucro_total_tokens,
        'lucro_percentual_total': lucro_percentual_total
    }


def validar_parametros_estrategia(
    percentual_desvalorizacao: float,
    percentual_valorizacao: float,
    quantidade_inicial: float
) -> tuple[bool, str]:
    """
    Valida os parâmetros de entrada da estratégia
    
    Parâmetros:
        percentual_desvalorizacao: Percentual para venda
        percentual_valorizacao: Percentual para compra
        quantidade_inicial: Quantidade inicial de tokens
    
    Retorno:
        Tupla com status de validação e mensagem de erro
    """
    if not (1 <= percentual_desvalorizacao <= 20):
        return False, "Percentual de desvalorização deve estar entre 1% e 20%"
    
    if not (1 <= percentual_valorizacao <= 20):
        return False, "Percentual de valorização deve estar entre 1% e 20%"
    
    if quantidade_inicial <= 0:
        return False, "Quantidade inicial deve ser maior que zero"
    
    return True, "Parâmetros válidos"