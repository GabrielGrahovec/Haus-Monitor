"""
Módulo: ui_handler.py
Responsável: Renderizar interface e resultados
"""

import streamlit as st
from typing import Dict, List
from .analysis_handler import classificar_risco_cor


def configurar_tema():
    """
    Configura tema dark mode com cores institucionais Haus Invest.
    """
    tema_css = """
    <style>
    :root {
        --primary-color: #1f4788;
        --secondary-color: #2d5aa6;
        --accent-color: #4a90e2;
        --success-color: #2ecc71;
        --warning-color: #f39c12;
        --danger-color: #e74c3c;
        --dark-bg: #0f1419;
        --text-light: #e8eaed;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: var(--dark-bg);
    }
    
    [data-testid="stHeader"] {
        background-color: var(--primary-color);
        color: var(--text-light);
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--primary-color);
        color: var(--text-light);
    }
    
    .stButton > button {
        background-color: var(--accent-color);
        color: white;
        border-radius: 6px;
        font-weight: 600;
        border: none;
    }
    
    .stButton > button:hover {
        background-color: var(--secondary-color);
    }
    
    h1, h2, h3 {
        color: var(--text-light);
    }
    
    p, span {
        color: var(--text-light);
    }
    </style>
    """
    st.markdown(tema_css, unsafe_allow_html=True)


def exibir_analise(resultado: Dict):
    """
    Exibe análise completa de um emissor de forma formatada.
    """
    noticias = resultado.get("noticias", [])
    analise = resultado.get("analise", {})
    info = resultado.get("info", {})
    
    # SEÇÃO 1: DADOS BÁSICOS
    st.markdown("## 📊 Resultado da Análise")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Emissor", info.get("Nome", "N/A"))
    
    with col2:
        st.metric("Rating", info.get("Rating", "N/A"))
    
    with col3:
        st.metric("Setor", info.get("Setor", "N/A"))
    
    with col4:
        parecer = analise.get("parecer", "N/A")
        emoji = classificar_risco_cor(parecer)
        st.metric("Risco", f"{emoji} {parecer}")
    
    st.divider()
    
    # SEÇÃO 2: PARECER PRINCIPAL
    st.markdown("### ⚠️ Parecer de Risco")
    
    parecer = analise.get("parecer", "N/A")
    emoji_risco = classificar_risco_cor(parecer)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown(f"## {emoji_risco}")
        st.markdown(f"**{parecer}**")
    
    with col2:
        st.info(analise.get("justificativa", "Sem justificativa"))
    
    st.divider()
    
    # SEÇÃO 3: EVENTOS CRÍTICOS (NOVA)
    st.markdown("### 🚨 Eventos Críticos")
    eventos = analise.get("eventos_criticos_resumo", "Nenhum evento crítico identificado")
    if eventos and eventos.lower() != "nenhum":
        st.error(f"**⚠️ {eventos}**")
    else:
        st.success("✅ Nenhum evento crítico identificado")
    
    st.divider()
    
    # SEÇÃO 4: SCORE NUMÉRICO
    st.markdown("### 📈 Score de Risco (0-100)")
    
    score = analise.get("score_risco", 50)
    
    if score <= 33:
        cor = "🟢"
    elif score <= 66:
        cor = "🟡"
    else:
        cor = "🔴"
    
    st.progress(score / 100)
    st.markdown(f"{cor} **Score: {score}/100** - {'Baixo' if score <= 33 else 'Médio' if score <= 66 else 'Alto'}")
    
    st.divider()
    
    # SEÇÃO 5: RISCOS E POSITIVOS
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⛔ Principais Riscos")
        riscos = analise.get("principais_riscos", [])
        if riscos:
            for risco in riscos:
                st.markdown(f"- {risco}")
        else:
            st.markdown("Nenhum risco identificado")
    
    with col2:
        st.markdown("### ✅ Principais Positivos")
        positivos = analise.get("principais_positivos", [])
        if positivos:
            for positivo in positivos:
                st.markdown(f"- {positivo}")
        else:
            st.markdown("Nenhum ponto positivo identificado")
    
    st.divider()
    
    # SEÇÃO 6: LIMITAÇÕES DE ANÁLISE (NOVA)
    st.markdown("### 📝 Limitações da Análise")
    limitacoes = analise.get("limitacoes_analise", "N/A")
    if "limitado" in limitacoes.lower() or "poucas" in limitacoes.lower():
        st.warning(f"⚠️ {limitacoes}")
    else:
        st.info(f"✅ {limitacoes}")
    
    st.divider()
    
    # SEÇÃO 7: RECOMENDAÇÃO
    st.markdown("### 💡 Recomendação")
    
    recomendacao = analise.get("recomendacao", "Sem recomendação")
    st.success(f"**{recomendacao}**")
    
    st.divider()
    
    # SEÇÃO 8: NOTÍCIAS
    st.markdown("### 📰 Notícias Encontradas")
    
    if noticias:
        st.markdown(f"**Total de notícias encontradas: {len(noticias)}**")
        for i, noticia in enumerate(noticias[:10], 1):
            with st.expander(f"{i}. {noticia.get('titulo', 'Sem título')}"):
                st.markdown(f"**Tipo:** {noticia.get('tipo_evento', 'N/A')}")
                st.markdown(f"**Data:** {noticia.get('data', 'Desconhecida')}")
                st.markdown(f"**Relevância:** {noticia.get('relevancia', 'N/A')}")
                st.markdown(f"**Resumo:** {noticia.get('resumo', 'Sem resumo')}")
                if noticia.get('fonte'):
                    st.markdown(f"**Fonte:** {noticia.get('fonte')}")
    else:
        st.warning("⚠️ Nenhuma notícia recente encontrada. Análise baseada em dados limitados.")
    
    st.divider()
    
    # SEÇÃO 9: RESUMO EXECUTIVO
    st.markdown("### 📋 Resumo Executivo")
    
    resumo = f"""
**Empresa:** {info.get('Nome')}
**Rating:** {info.get('Rating')} | **Setor:** {info.get('Setor')}
**Parecer:** {parecer} | **Score de Risco:** {score}/100

**Eventos Críticos:** {analise.get('eventos_criticos_resumo', 'N/A')}
**Limitações:** {analise.get('limitacoes_analise', 'N/A')}
**Recomendação:** {recomendacao}
"""
    
    st.text(resumo)


def exibir_erro(titulo: str, mensagem: str):
    """
    Exibe mensagem de erro formatada.
    """
    st.error(f"**{titulo}**\n\n{mensagem}")


def exibir_sucesso(mensagem: str):
    """
    Exibe mensagem de sucesso.
    """
    st.success(mensagem)


def exibir_aviso(mensagem: str):
    """
    Exibe mensagem de aviso.
    """
    st.warning(mensagem)