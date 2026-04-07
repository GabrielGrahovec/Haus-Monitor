"""
Módulo: analysis_handler.py
Responsável: Analisar risco de crédito usando Claude API
"""

import anthropic
import streamlit as st
from typing import Dict, List
import json

def analisar_emissor(
    nome_emissor: str,
    rating: str,
    setor: str,
    noticias: List[Dict]
) -> Dict:
    """
    Analisa risco de crédito do emissor usando Claude API.
    Foco em análise ESPECÍFICA e não-genérica.
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
        
        # Construir contexto de notícias - DETALHADO
        contexto_noticias = ""
        if noticias and len(noticias) > 0:
            contexto_noticias = "NOTÍCIAS ESPECÍFICAS ENCONTRADAS:\n"
            for i, n in enumerate(noticias[:15], 1):
                contexto_noticias += f"\n{i}. [{n.get('tipo_evento', 'Evento')}] {n.get('titulo', 'Sem título')}\n"
                contexto_noticias += f"   Data: {n.get('data', 'N/A')}\n"
                contexto_noticias += f"   Resumo: {n.get('resumo', 'Sem resumo')}\n"
                contexto_noticias += f"   Relevância: {n.get('relevancia', 'N/A')}\n"
        else:
            contexto_noticias = "⚠️ AVISO: Poucas ou nenhuma notícia recente encontrada. Análise baseará em dados limitados."
        
        # Prompt ESPECÍFICO - Não genérico
        prompt = f"""
Você é um analista de crédito sênior de uma gestora de investimentos. Faça uma análise ESPECÍFICA e DETALHADA.

DADOS DO EMISSOR:
- Empresa: {nome_emissor}
- Rating: {rating}
- Setor: {setor}

{contexto_noticias}

ANÁLISE REQUERIDA:
1. Se houver notícia de recuperação/extrajudicial → Isto é CRÍTICO
2. Se houver default → Isto é CRÍTICO
3. Se houver downgrade → Menione qual foi
4. Relacione o rating atual ({rating}) com os eventos encontrados
5. Se poucas notícias → Menione isto como limitação
6. Seja ESPECÍFICO: cite números, datas, tipos de eventos
7. Evite análises genéricas: seja concreto

Retorne JSON estruturado:

{{
  "parecer": "Baixo/Médio/Alto",
  "justificativa": "Análise ESPECÍFICA (5-7 frases). Cite eventos reais encontrados, números, datas. Explique por que este é o parecer.",
  "principais_riscos": [
    "Risco 1 específico (ex: Recuperação judicial em andamento)",
    "Risco 2 específico (ex: Alavancagem estimada em 3.5x)",
    "Risco 3 específico"
  ],
  "principais_positivos": [
    "Ponto positivo 1 se houver (ex: Receitas operacionais estáveis)",
    "Ponto positivo 2 se houver"
  ],
  "score_risco": número 0-100 (baseado em eventos reais),
  "eventos_criticos_resumo": "Resumo dos eventos críticos encontrados ou 'Nenhum evento crítico identificado'",
  "limitacoes_analise": "Se poucas notícias encontradas, menione isto. Caso contrário, coloque 'Análise com dados suficientes'",
  "recomendacao": "COMPRAR/MANTER/VENDER com justificativa concisa baseada em eventos específicos"
}}

REGRAS CRÍTICAS:
- Se recuperação judicial → parecer SEMPRE "Alto" e score >= 75
- Se default → parecer SEMPRE "Alto" e score >= 85
- Se downgrade recente → parecer >= "Médio"
- Se poucas notícias → mencione isto como limitação da análise
- NUNCA seja genérico: cite fatos específicos
- Relate rating atual com situação

IMPORTANTE: A análise deve ser diferente para cada empresa, não genérica!
"""
        
        # Chamar Claude
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Extrair e parsear resposta
        analise = {}
        for block in response.content:
            if hasattr(block, "text"):
                try:
                    text = block.text
                    # Limpar markdown
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0]
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0]
                    
                    analise = json.loads(text.strip())
                except (json.JSONDecodeError, IndexError):
                    analise = {
                        "parecer": "Médio",
                        "justificativa": text[:400] if hasattr(block, "text") else "Erro no parsing",
                        "principais_riscos": ["Análise parcial"],
                        "principais_positivos": [],
                        "score_risco": 50,
                        "eventos_criticos_resumo": "Não identificados",
                        "limitacoes_analise": "Erro no processamento",
                        "recomendacao": "Aguardar re-análise"
                    }
        
        # Garantir campos obrigatórios
        if not analise:
            analise = {
                "parecer": "Médio",
                "justificativa": "Análise não concluída",
                "principais_riscos": [],
                "principais_positivos": [],
                "score_risco": 50,
                "eventos_criticos_resumo": "N/A",
                "limitacoes_analise": "Sem dados",
                "recomendacao": "Tente novamente"
            }
        
        return analise
    
    except ValueError as e:
        st.error(str(e))
        return {
            "parecer": "Erro",
            "justificativa": "API não configurada.",
            "principais_riscos": ["Configuração pendente"],
            "principais_positivos": [],
            "score_risco": 0,
            "eventos_criticos_resumo": "N/A",
            "limitacoes_analise": "API key faltando",
            "recomendacao": "Configure ANTHROPIC_API_KEY"
        }
    except Exception as e:
        st.error(f"❌ Erro na análise: {str(e)}")
        return {
            "parecer": "Erro",
            "justificativa": f"Erro: {str(e)}",
            "principais_riscos": ["Erro na API"],
            "principais_positivos": [],
            "score_risco": 0,
            "eventos_criticos_resumo": "N/A",
            "limitacoes_analise": "Erro técnico",
            "recomendacao": "Tente novamente"
        }


def classificar_risco_cor(parecer: str) -> str:
    """
    Retorna emoji baseado no parecer de risco.
    """
    mapa = {
        "Baixo": "🟢",
        "Médio": "🟡",
        "Alto": "🔴",
        "Erro": "⚫"
    }
    return mapa.get(parecer, "⚫")
