"""
Aplicativo Streamlit - POC Estratégia de Recolocação de Posição
Interface web principal para simulação e análise da estratégia de trading
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

# Importar módulos locais
from buscador_dados import buscar_dados_historicos, validar_simbolo
from simulador_estrategia import (
    executar_simulacao_estrategia, 
    validar_parametros_estrategia
)
from analisador_resultados import (
    criar_grafico_principal,
    processar_tabela_operacoes,
    criar_metricas_resumidas,
    gerar_relatorio_resumo,
    validar_dados_para_analise,
    exportar_operacoes_csv
)


def configurar_pagina():
    """Configura a página inicial do Streamlit"""
    st.set_page_config(
        page_title="POC - Estratégia de Recolocação de Posição",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📈 POC - Estratégia de Recolocação de Posição")
    st.markdown("---")


def criar_sidebar_configuracao():
    """
    Cria a sidebar com configurações da simulação
    
    Retorno:
        Dicionário com parâmetros configurados
    """
    st.sidebar.header("⚙️ Configurações da Simulação")
    
    # Seleção do par de trading
    simbolo = st.sidebar.selectbox(
        "Par de Trading",
        options=["BTC/USDT", "ETH/USDT", "BNB/USDT"],
        index=0,
        help="Selecione o par de criptomoedas para análise"
    )
    
    # Parâmetros da estratégia
    st.sidebar.subheader("Parâmetros da Estratégia")
    
    percentual_desvalorizacao = st.sidebar.slider(
        "Percentual Desvalorização para Venda (%)",
        min_value=3.0,
        max_value=10.0,
        value=5.0,
        step=0.5,
        help="Percentual de queda do preço máximo para disparar venda"
    )
    
    percentual_valorizacao = st.sidebar.slider(
        "Percentual Valorização para Compra (%)",
        min_value=3.0,
        max_value=10.0,
        value=5.0,
        step=0.5,
        help="Percentual de alta do preço mínimo para disparar compra"
    )
    
    quantidade_inicial = st.sidebar.number_input(
        "Quantidade Inicial de Tokens",
        min_value=0.001,
        max_value=100.0,
        value=1.0,
        step=0.001,
        format="%.6f",
        help="Quantidade inicial de tokens para iniciar a estratégia"
    )
    
    # Período de análise
    st.sidebar.subheader("Período de Análise")
    
    # Data padrão: últimos 6 meses
    data_fim_padrao = datetime.now().date()
    data_inicio_padrao = data_fim_padrao - timedelta(days=180)
    
    data_inicio = st.sidebar.date_input(
        "Data de Início",
        value=data_inicio_padrao,
        max_value=data_fim_padrao,
        help="Data inicial para análise histórica"
    )
    
    data_fim = st.sidebar.date_input(
        "Data de Fim",
        value=data_fim_padrao,
        min_value=data_inicio,
        max_value=data_fim_padrao,
        help="Data final para análise histórica"
    )
    
    return {
        'simbolo': simbolo,
        'percentual_desvalorizacao': percentual_desvalorizacao,
        'percentual_valorizacao': percentual_valorizacao,
        'quantidade_inicial': quantidade_inicial,
        'data_inicio': datetime.combine(data_inicio, datetime.min.time()),
        'data_fim': datetime.combine(data_fim, datetime.max.time())
    }


def validar_configuracoes(config: dict) -> tuple[bool, str]:
    """
    Valida todas as configurações antes da execução
    
    Parâmetros:
        config: Dicionário com configurações
    
    Retorno:
        Tupla com status de validação e mensagem
    """
    # Validar datas
    if config['data_fim'] <= config['data_inicio']:
        return False, "Data de fim deve ser posterior à data de início"
    
    # Validar período mínimo
    diferenca_dias = (config['data_fim'] - config['data_inicio']).days
    if diferenca_dias < 7:
        return False, "Período mínimo de análise é 7 dias"
    
    # Validar parâmetros da estratégia
    is_valid, msg = validar_parametros_estrategia(
        config['percentual_desvalorizacao'],
        config['percentual_valorizacao'],
        config['quantidade_inicial']
    )
    
    if not is_valid:
        return False, msg
    
    return True, "Configurações válidas"


def executar_simulacao_completa(config: dict):
    """
    Executa a simulação completa com feedback visual
    
    Parâmetros:
        config: Dicionário com configurações da simulação
    """
    # Container para mensagens de status
    status_container = st.empty()
    progress_bar = st.progress(0)
    
    try:
        # Etapa 1: Buscar dados históricos
        status_container.info("🔄 Buscando dados históricos da Binance...")
        progress_bar.progress(20)
        
        dados_historicos = buscar_dados_historicos(
            config['simbolo'],
            config['data_inicio'],
            config['data_fim']
        )
        
        # Validar dados obtidos
        is_valid, msg = validar_dados_para_analise(dados_historicos, [])
        if not is_valid:
            st.error(f"❌ Erro nos dados históricos: {msg}")
            return
        
        progress_bar.progress(40)
        status_container.info(f"✅ Dados carregados: {len(dados_historicos)} períodos")
        
        # Etapa 2: Executar simulação da estratégia
        status_container.info("🧮 Executando simulação da estratégia...")
        progress_bar.progress(60)
        
        operacoes, metricas = executar_simulacao_estrategia(
            dados_historicos,
            config['quantidade_inicial'],
            config['percentual_desvalorizacao'],
            config['percentual_valorizacao']
        )
        
        progress_bar.progress(80)
        status_container.info(f"✅ Simulação concluída: {len(operacoes)} operações executadas")
        
        # Etapa 3: Processar e exibir resultados
        status_container.info("📊 Processando resultados...")
        progress_bar.progress(100)
        
        time.sleep(0.5)  # Pequena pausa para feedback visual
        status_container.success("🎉 Simulação concluída com sucesso!")
        
        # Exibir resultados
        exibir_resultados(dados_historicos, operacoes, metricas, config)
        
    except Exception as e:
        status_container.error(f"❌ Erro durante a simulação: {str(e)}")
        st.error(f"Detalhes do erro: {str(e)}")
        st.info("💡 Dica: Tente reduzir o período de análise ou verificar sua conexão com a internet.")


def exibir_resultados(dados_historicos: pd.DataFrame, operacoes: list, metricas: dict, config: dict):
    """
    Exibe os resultados da simulação na interface
    
    Parâmetros:
        dados_historicos: DataFrame com dados históricos
        operacoes: Lista de operações executadas
        metricas: Métricas calculadas
        config: Configurações da simulação
    """
    st.markdown("---")
    st.header("📊 Resultados da Simulação")
    
    if not operacoes:
        st.warning("⚠️ Nenhuma operação foi executada no período analisado. Tente ajustar os parâmetros da estratégia.")
        return
    
    # Seção 1: Gráfico Principal
    st.subheader("📈 Gráfico de Preços e Operações")
    
    grafico = criar_grafico_principal(dados_historicos, operacoes)
    st.plotly_chart(grafico, use_container_width=True)
    
    # Seção 2: Métricas Resumidas
    st.subheader("📋 Métricas de Performance")
    
    metricas_formatadas = criar_metricas_resumidas(metricas)
    
    # Organizar métricas em colunas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        for i, (nome, (valor, delta)) in enumerate(list(metricas_formatadas.items())[:2]):
            st.metric(nome, valor, delta)
    
    with col2:
        for i, (nome, (valor, delta)) in enumerate(list(metricas_formatadas.items())[2:4]):
            st.metric(nome, valor, delta)
    
    with col3:
        for i, (nome, (valor, delta)) in enumerate(list(metricas_formatadas.items())[4:]):
            st.metric(nome, valor, delta)
    
    # Seção 3: Tabela de Operações
    st.subheader("📝 Histórico de Operações")
    
    tabela_operacoes = processar_tabela_operacoes(operacoes)
    st.dataframe(
        tabela_operacoes,
        use_container_width=True,
        hide_index=True
    )
    
    # Botão para download das operações
    if operacoes:
        csv_data = exportar_operacoes_csv(operacoes)
        st.download_button(
            label="📥 Baixar Operações (CSV)",
            data=csv_data,
            file_name=f"operacoes_{config['simbolo'].replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Seção 4: Relatório Resumo
    st.subheader("📄 Relatório Resumo")
    
    periodo_str = f"{config['data_inicio'].strftime('%d/%m/%Y')} a {config['data_fim'].strftime('%d/%m/%Y')}"
    relatorio = gerar_relatorio_resumo(operacoes, metricas, config['simbolo'], periodo_str)
    st.markdown(relatorio)


def main():
    """Função principal da aplicação"""
    # Configurar página
    configurar_pagina()
    
    # Criar sidebar com configurações
    config = criar_sidebar_configuracao()
    
    # Seção de execução
    st.header("🚀 Execução da Simulação")
    
    # Validar configurações
    is_valid, validation_msg = validar_configuracoes(config)
    
    if not is_valid:
        st.error(f"❌ {validation_msg}")
        return
    
    # Exibir resumo das configurações
    with st.expander("📋 Resumo das Configurações", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Par de Trading:** {config['simbolo']}")
            st.write(f"**Quantidade Inicial:** {config['quantidade_inicial']:.6f} tokens")
            st.write(f"**Período:** {config['data_inicio'].strftime('%d/%m/%Y')} a {config['data_fim'].strftime('%d/%m/%Y')}")
        
        with col2:
            st.write(f"**Desvalorização para Venda:** {config['percentual_desvalorizacao']:.1f}%")
            st.write(f"**Valorização para Compra:** {config['percentual_valorizacao']:.1f}%")
            dias_analise = (config['data_fim'] - config['data_inicio']).days
            st.write(f"**Dias de Análise:** {dias_analise}")
    
    # Botão de execução
    if st.button("🚀 Executar Simulação", type="primary", use_container_width=True):
        executar_simulacao_completa(config)
    
    # Informações adicionais
    with st.expander("ℹ️ Sobre a Estratégia", expanded=False):
        st.markdown("""
        ### Estratégia de Recolocação de Posição
        
        Esta estratégia opera em ciclos de compra e venda baseados em:
        
        1. **Estado COMPRADO:** Monitora preço máximo em janela de 7 dias
        2. **Gatilho de Venda:** Quando preço cai X% do máximo
        3. **Estado VENDIDO:** Monitora preço mínimo após venda
        4. **Gatilho de Compra:** Quando preço sobe Y% do mínimo
        
        **Objetivo:** Aumentar quantidade de tokens através de ciclos repetidos
        
        **Timeframe:** Dados de 4 horas da Binance
        """)


if __name__ == "__main__":
    main()