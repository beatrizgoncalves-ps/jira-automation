import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-flash-latest')

user_input = 'história para criar um ícone novo que represente uso indevido de veículos no mapa'
epics_context = [
    {'key': 'LAPDT-861', 'summary': 'Inteligência de Risco'},
    {'key': 'LAPDT-860', 'summary': 'Virtual Tower'},
    {'key': 'LAPDT-938', 'summary': 'Monitoramento de Atrasos Operacionais e Gestão de Performance de Frota'}
]

prompt = f"""
Você é um Product Manager Sênior. 
Gere uma User Story detalhada em Markdown para o input: "{user_input}"
Contexto de Épicos: {json.dumps(epics_context)}

Inclua:
1. Título claro.
2. Persona (Como um...).
3. Necessidade (Quero...).
4. Valor de Negócio (Para que...).
5. Critérios de Aceite (Gherkin ou lista).
6. Notas Técnicas (Sugestão de ícone, cores, comportamento no mapa).
7. Épico sugerido (escolha o mais adequado da lista).

Responda APENAS o Markdown.
"""

response = model.generate_content(prompt)
print(response.text)
