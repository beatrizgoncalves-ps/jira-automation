import os
import google.generativeai as genai
from dotenv import load_dotenv
from jira import JIRA
import json

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-flash-latest')

user_input = "solução que conta a quantidade de pessoas saindo de um veículo"
epics_context = [
    {'key': 'LAPDT-860', 'summary': 'Virtual Tower'},
    {'key': 'LAPDT-861', 'summary': 'Inteligência de Risco'},
    {'key': 'LAPDT-938', 'summary': 'Monitoramento de Atrasos Operacionais e Performance'}
]

prompt = f"""
Você é um Product Manager Sênior e Analista de Sistemas Sênior.
Gere uma User Story detalhada com diagramação limpa para o Jira.

INPUT: "{user_input}"
CONTEXTO DE ÉPICOS: {json.dumps(epics_context)}

REGRAS DE FORMATAÇÃO JIRA:
- Use ## para títulos de seção.
- Use **negrito** para termos chave.
- Use --- para separar seções.
- Use listas com * para critérios de aceite.

ESTRUTURA OBRIGATÓRIA:
1. Persona e Valor de Negócio.
2. Critérios de Aceite (detalhados e testáveis).
3. POV Técnico Crítico (Foque em: precisão de sensores, processamento edge vs cloud, condições de luz/clima, concorrência de saída).
4. Perguntas Incômodas (Edge cases extremos).

Responda APENAS o Markdown.
"""

response = model.generate_content(prompt)
print(response.text)
