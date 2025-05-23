"""
Módulo responsável por buscar e processar dados históricos da Binance
"""

import ccxt
import pandas as pd
import streamlit as st
from datetime import datetime
import time


@st.cache_data(ttl=3600)
def buscar_dados_historicos(simbolo: str, data_inicio: datetime, data_fim: datetime) -> pd.DataFrame:
    """
    Busca dados históricos de OHLCV da Binance para o símbolo especificado
    
    Parâmetros:
        simbolo: Par de trading (ex: 'BTC/USDT')
        data_inicio: Data inicial para busca
        data_fim: Data final para busca
    
    Retorno:
        DataFrame com colunas: timestamp, open, high, low, close, volume
    """
    try:
        # Configurar exchange da Binance
        exchange = ccxt.binance({
            'sandbox': False,
            'enableRateLimit': True,
            'timeout': 30000,  # 30 segundos timeout
            'rateLimit': 1200,  # Rate limit mais conservador
        })
        
        # Converter datas para timestamp em milissegundos
        timestamp_inicio = int(data_inicio.timestamp() * 1000)
        timestamp_fim = int(data_fim.timestamp() * 1000)
        
        # Buscar dados com timeframe de 4 horas
        timeframe = '4h'
        dados_completos = []
        
        # Implementar paginação para períodos longos
        timestamp_atual = timestamp_inicio
        limite_por_request = 1000
        
        while timestamp_atual < timestamp_fim:
            try:
                dados_batch = exchange.fetch_ohlcv(
                    simbolo, 
                    timeframe, 
                    since=timestamp_atual,
                    limit=limite_por_request
                )
                
                if not dados_batch:
                    break
                
                dados_completos.extend(dados_batch)
                
                # Atualizar timestamp para próximo batch
                timestamp_atual = dados_batch[-1][0] + 1
                
                # Rate limiting
                time.sleep(0.1)
                
            except ccxt.NetworkError as e:
                st.warning(f"Tentando reconectar... Erro: {str(e)}")
                time.sleep(2)  # Aguardar antes de tentar novamente
                continue
                
            except ccxt.ExchangeError as e:
                st.warning(f"Erro da exchange, tentando continuar: {str(e)}")
                time.sleep(1)
                continue
        
        # Converter para DataFrame
        df = processar_dados_ohlcv(dados_completos)
        
        # Filtrar pelo período exato solicitado
        df = df[(df['timestamp'] >= data_inicio) & (df['timestamp'] <= data_fim)]
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao buscar dados históricos: {str(e)}")
        return pd.DataFrame()


def processar_dados_ohlcv(dados_brutos: list) -> pd.DataFrame:
    """
    Processa dados OHLCV brutos da API em DataFrame formatado
    
    Parâmetros:
        dados_brutos: Lista de listas com dados OHLCV da API
    
    Retorno:
        DataFrame formatado com colunas nomeadas
    """
    if not dados_brutos:
        return pd.DataFrame()
    
    # Criar DataFrame com colunas nomeadas
    df = pd.DataFrame(dados_brutos, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # Converter timestamp para datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Converter preços para float
    colunas_precos = ['open', 'high', 'low', 'close']
    for coluna in colunas_precos:
        df[coluna] = df[coluna].astype(float)
    
    df['volume'] = df['volume'].astype(float)
    
    # Ordenar por timestamp e remover duplicatas
    df = df.sort_values('timestamp').drop_duplicates(subset=['timestamp'])
    
    # Resetar índice
    df = df.reset_index(drop=True)
    
    return df


def validar_simbolo(simbolo: str) -> bool:
    """
    Valida se o símbolo existe na Binance
    
    Parâmetros:
        simbolo: Par de trading para validar
    
    Retorno:
        True se símbolo válido, False caso contrário
    """
    try:
        exchange = ccxt.binance()
        mercados = exchange.load_markets()
        return simbolo in mercados
    except:
        return False


def obter_preco_atual(simbolo: str) -> float:
    """
    Obtém o preço atual do símbolo
    
    Parâmetros:
        simbolo: Par de trading
    
    Retorno:
        Preço atual como float
    """
    try:
        exchange = ccxt.binance()
        ticker = exchange.fetch_ticker(simbolo)
        return float(ticker['last'])
    except:
        return 0.0