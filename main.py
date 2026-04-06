import streamlit as st
import pandas as pd
from modules.upload_handler import carregar_excel
from modules.search_handler import buscar_noticias
from modules.analysis_handler import analisar_emissor
from modules.ui_handler import exibir_analise, configurar_tema

st.set_page_config(
    page_title="Haus Monitor",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

configurar_tema()

if "emissores_df" not in st.session_state:
    st.session_state.emissores_df = None

if "analise_cache" not in st.session_state:
    st.session_state.analise_cache = {}

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("# 🏦 HausMonitor")
    st.markdown("*Análise de Risco de Crédito - Haus Invest*")
with col2:
    st.markdown("#### v1.0 MVP")

st.divider()

with st.sidebar:
    st.markdown("## 📤 Upload de Dados")
    
    arquivo = st.file_uploader(
        "Selecione arquivo Excel com emissores",
        type=["xlsx", "xls"],
        help="Arquivo deve ter colunas: Nome, Rating, Setor"
    )
    
    if arquivo:
        try:
            st.session_state.emissores_df = carregar_excel(arquivo)
            st.success("✅ Arquivo carregado com sucesso!")
            st.markdown(f"**Total de emissores:** {len(st.session_state.emissores_df)}")
        except Exception as e:
            st.error(f"❌ Erro ao carregar arquivo: {str(e)}")
    
    st.divider()
    st.markdown("## ℹ️ Sobre")
    st.markdown("""
    **HausMonitor** é uma plataforma de análise de risco de crédito que combina:
    - 📰 Notícias recentes (web search)
    - 🤖 Análise de IA (Claude API)
    - 📊 Parecer de risco automatizado
    
    **Versão:** 1.0 (MVP)
    """)

if st.session_state.emissores_df is None:
    st.info("👈 **Comece fazendo upload de um arquivo Excel** com os emissores para análise.")
    st.markdown("""
    ### Formato esperado do arquivo:
    | Nome | Rating | Setor |
    |------|--------|-------|
    | Raizen | BB | Energia |
    | BRF | BBB | Alimentos |
    | Madero | B | Alimentos |
    """)
else:
    st.markdown("## 🔍 Selecione um Emissor")
    
    nomes_emissores = st.session_state.emissores_df["Nome"].unique().tolist()
    emissor_selecionado = st.selectbox(
        "Digite ou selecione o emissor:",
        nomes_emissores,
        label_visibility="collapsed"
    )
    
    st.divider()
    
    emissor_info = st.session_state.emissores_df[
        st.session_state.emissores_df["Nome"] == emissor_selecionado
    ].iloc[0]
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        btn_analisar = st.button(
            "🔄 Analisar Agora",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        btn_limpar = st.button(
            "🗑️ Limpar",
            use_container_width=True
        )
    
    if btn_limpar:
        st.session_state.analise_cache = {}
        st.rerun()
    
    st.divider()
    
    if btn_analisar:
        with st.spinner(f"🔍 Buscando notícias sobre {emissor_selecionado}..."):
            try:
                noticias = buscar_noticias(emissor_selecionado)
                
                if not noticias:
                    st.warning(f"⚠️ Nenhuma notícia recente encontrada para {emissor_selecionado}.")
                    noticias = []
                else:
                    st.success(f"✅ {len(noticias)} notícia(s) encontrada(s)")
            except Exception as e:
                st.error(f"❌ Erro ao buscar notícias: {str(e)}")
                noticias = []
        
        with st.spinner("🤖 Analisando com Claude API..."):
            try:
                analise = analisar_emissor(
                    nome_emissor=emissor_selecionado,
                    rating=emissor_info["Rating"],
                    setor=emissor_info["Setor"],
                    noticias=noticias
                )
                
                st.session_state.analise_cache[emissor_selecionado] = {
                    "noticias": noticias,
                    "analise": analise,
                    "info": emissor_info.to_dict()
                }
                
                st.success("✅ Análise concluída!")
            except Exception as e:
                st.error(f"❌ Erro na análise: {str(e)}")
    
    if emissor_selecionado in st.session_state.analise_cache:
        resultado = st.session_state.analise_cache[emissor_selecionado]
        exibir_analise(resultado)
    
    st.divider()
    
    with st.expander("📋 Ver todos os emissores carregados"):
        st.dataframe(
            st.session_state.emissores_df,
            use_container_width=True,
            hide_index=True
        )

st.divider()
st.markdown("**HausMonitor v1.0** | Desenvolvido para Haus Invest | 🏦")