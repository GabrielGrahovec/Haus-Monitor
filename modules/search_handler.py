"""
Módulo: search_handler.py
Responsável: Buscar notícias sobre emissores usando Anthropic Web Search
"""

import anthropic
import streamlit as st
from typing import List, Dict
import json

def buscar_noticias(nome_emissor: str) -> List[Dict]:
    """
    Busca notícias recentes sobre um emissor usando Anthropic Web Search.
    Busca agressiva com múltiplas estratégias para encontrar eventos críticos.
    """
    try:
        # Obter API key
        api_key = st.secrets.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "❌ ANTHROPIC_API_KEY não configurada. "
                "Configure em: Settings > Secrets"
            )
        
        # Inicializar cliente
        client = anthropic.Anthropic(api_key=api_key)
        
        # Prompt AGRESSIVO - Busca específica por eventos críticos
        prompt = f"""
BUSCA URGENTE DE NOTÍCIAS CRÍTICAS SOBRE: {nome_emissor}

Você é um pesquisador financeiro. Procure TODAS as notícias sobre {nome_emissor} nos últimos 24 meses.

PROCURE ESPECIALMENTE POR:
1. Recuperação judicial / extrajudicial de {nome_emissor}
2. Default ou inadimplência de {nome_emissor}
3. Downgrade de rating de {nome_emissor}
4. Reestruturação de dívida de {nome_emissor}
5. Problemas financeiros de {nome_emissor}
6. Venda de ativos de {nome_emissor}
7. Processos regulatórios de {nome_emissor}
8. Demissões em massa de {nome_emissor}
9. Fechamento de filiais de {nome_emissor}
10. Investigações de {nome_emissor}

TERMOS DE BUSCA QUE DEVEM SER USADOS:
- "{nome_emissor} recuperação judicial"
- "{nome_emissor} extrajudicial"
- "{nome_emissor} RJ 2024"
- "{nome_emissor} RJ 2025"
- "{nome_emissor} default"
- "{nome_emissor} dívida"
- "{nome_emissor} falência"
- "{nome_emissor} crise"
- "{nome_emissor} problemas"

RETORNE UM JSON COM TODAS AS NOTÍCIAS ENCONTRADAS:

[
  {{
    "titulo": "Título completo e exato da notícia",
    "resumo": "Resumo detalhado (3-4 frases) - inclua números, datas e impacto específico",
    "data": "Data aproximada",
    "relevancia": "Alta" ou "Média",
    "tipo_evento": "Tipo específico (ex: Recuperação Judicial, Default, Downgrade)",
    "fonte": "Fonte da notícia se disponível"
  }}
]

SE NÃO ENCONTRAR NOTÍCIAS, RETORNE: []

IMPORTANTE:
- Seja AGRESSIVO na busca
- Inclua notícias de 2024 e 2025
- Priorize eventos críticos (RJ, default, downgrade)
- Se encontrar múltiplas notícias sobre o MESMO evento, inclua TODAS
- Inclua datas específicas
"""
        
        # Primeira busca - AGRESSIVA
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=300,
            tools=[
                {
                    "type": "web_search_20260209",
                    "name": "web_search"
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Extrair resposta
        noticias = []
        for block in response.content:
            if hasattr(block, "text"):
                try:
                    text = block.text
                    # Limpar markdown se existir
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0]
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0]
                    
                    noticias_encontradas = json.loads(text.strip())
                    
                    # Validar estrutura
                    if isinstance(noticias_encontradas, list):
                        noticias = [
                            n for n in noticias_encontradas 
                            if isinstance(n, dict) and "titulo" in n
                        ]
                except (json.JSONDecodeError, IndexError):
                    noticias = []
        
        # Se não encontrou notícias, tentar busca alternativa
        if not noticias:
            prompt_alternativo = f"""
Segunda tentativa de busca. Procure por notícias sobre {nome_emissor} com termos alternativos:
- Notícias financeiras sobre {nome_emissor}
- Situação econômica de {nome_emissor}
- Resultados recentes de {nome_emissor}
- Rating de {nome_emissor}
- Análise de crédito de {nome_emissor}

Retorne em JSON com mesma estrutura anterior.
"""
            
            response2 = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=300,
                tools=[
                    {
                        "type": "web_search_20260209",
                        "name": "web_search"
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": prompt_alternativo
                    }
                ]
            )
            
            for block in response2.content:
                if hasattr(block, "text"):
                    try:
                        text = block.text
                        if "```json" in text:
                            text = text.split("```json")[1].split("```")[0]
                        elif "```" in text:
                            text = text.split("```")[1].split("```")[0]
                        
                        noticias = json.loads(text.strip())
                        
                        if isinstance(noticias, list):
                            noticias = [
                                n for n in noticias 
                                if isinstance(n, dict) and "titulo" in n
                            ]
                    except (json.JSONDecodeError, IndexError):
                        pass
        
        return noticias
    
    except ValueError as e:
        st.error(str(e))
        return []
    except Exception as e:
        st.error(f"❌ Erro ao buscar notícias: {str(e)}")
        return []


def filtrar_noticias_relevantes(noticias: List[Dict]) -> List[Dict]:
    """
    Filtra notícias por relevância.
    """
    if not noticias:
        return []
    
    return [
        n for n in noticias 
        if n.get("relevancia", "Média").lower() in ["alta", "média"]
    ]
