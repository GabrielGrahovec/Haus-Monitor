"""
Módulo: upload_handler.py
Responsável: Carregar e validar arquivos Excel
"""

import pandas as pd
import streamlit as st
from typing import Optional

def carregar_excel(arquivo) -> pd.DataFrame:
    """
    Carrega arquivo Excel com emissores.
    
    Esperado:
    - Colunas: Nome, Rating, Setor
    - Cada linha = um emissor
    
    Args:
        arquivo: UploadedFile do Streamlit
        
    Returns:
        DataFrame com emissores validados
        
    Raises:
        ValueError: Se colunas obrigatórias faltarem
    """
    try:
        df = pd.read_excel(arquivo)
        
        # Validar colunas obrigatórias
        colunas_obrigatorias = ["Nome", "Rating", "Setor"]
        colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
        
        if colunas_faltantes:
            raise ValueError(
                f"❌ Colunas obrigatórias faltando: {', '.join(colunas_faltantes)}\n"
                f"Colunas encontradas: {', '.join(df.columns)}"
            )
        
        # Limpar espaços em branco
        df = df.astype(str).apply(lambda x: x.str.strip())
        
        # Remover linhas vazias
        df = df.dropna(subset=["Nome"])
        
        # Validar que não há duplicatas
        duplicatas = df[df.duplicated(subset=["Nome"], keep=False)]
        if not duplicatas.empty:
            st.warning(f"⚠️ Encontradas duplicatas (mantendo primeira ocorrência):")
            st.dataframe(duplicatas)
            df = df.drop_duplicates(subset=["Nome"], keep="first")
        
        return df
    
    except Exception as e:
        raise ValueError(f"Erro ao processar arquivo: {str(e)}")


def validar_emissor(nome_emissor: str, df: pd.DataFrame) -> Optional[dict]:
    """
    Valida se emissor existe na planilha.
    
    Args:
        nome_emissor: Nome do emissor a validar
        df: DataFrame de emissores
        
    Returns:
        Dict com dados do emissor ou None
    """
    resultado = df[df["Nome"].str.lower() == nome_emissor.lower()]
    
    if resultado.empty:
        return None
    
    return resultado.iloc[0].to_dict()