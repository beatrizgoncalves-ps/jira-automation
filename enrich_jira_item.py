import os
import google.generativeai as genai
from dotenv import load_dotenv
from jira import JIRA
import json

# Carrega configurações
load_dotenv()

# Configuração Jira e Gemini
JIRA_SERVER = os.getenv("JIRA_SERVER")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_API_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

def connect_jira():
    return JIRA(server=JIRA_SERVER, basic_auth=(JIRA_EMAIL, JIRA_TOKEN))

def enrich_with_ai(current_description, new_input):
    prompt = f"""
    Você é um Product Manager Sênior brasileiro especialista em refinamento técnico.
    Sua tarefa é ENRIQUECER um ticket do JIRA existente com novas REGRAS DE NEGÓCIO e detalhes.

    CONTEÚDO ATUAL DO TICKET:
    "{current_description}"

    NOVAS INFORMAÇÕES/REGRAS PARA ADICIONAR:
    "{new_input}"

    REGRAS DE OURO:
    1. Não apague informações importantes já existentes, a menos que as novas informações as contradigam.
    2. Escreva exclusivamente em PORTUGUÊS DO BRASIL.
    3. Mantenha e expanda as seções:
       - **PADRÃO USER STORY** (se aplicável)
       - **DESCRIÇÃO** (mais detalhada agora)
       - **REGRAS DE NEGÓCIO** (Seção nova ou expandida com detalhes técnicos/operacionais)
       - **OBJETIVO ESPERADO**
       - **BENEFÍCIOS**
       - **ENTREGÁVEIS**
       - **DEPENDÊNCIAS E RISCOS**
       - **LISTA DE DEFINIÇÕES/PERGUNTAS**

    FORMATO DE RETORNO (Responda APENAS com este JSON):
    {{
        "title": "Título atualizado (se necessário)",
        "description": "Texto completo enriquecido em Markdown"
    }}
    """
    response = model.generate_content(prompt)
    text = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(text)

def main():
    print("--- 🚀 Enriquecedor de Tickets JIRA LAPDT ---")
    ticket_key = input("Informe a CHAVE do ticket (ex: LAPDT-938): ").strip().upper()
    new_details = input("Quais novos detalhes ou regras de negócio deseja adicionar? ")

    try:
        jira = connect_jira()
        print(f"🔍 Buscando ticket {ticket_key}...")
        issue = jira.issue(ticket_key)
        
        current_description = issue.fields.description or ""
        
        print("🤖 Inteligência Artificial refinando o conteúdo...")
        enriched_data = enrich_with_ai(current_description, new_details)
        
        print("📝 Atualizando no Jira...")
        issue.update(
            summary=enriched_data['title'],
            description=enriched_data['description']
        )
        
        print(f"\n✨ SUCESSO! O ticket {ticket_key} foi enriquecido e atualizado.")
        print(f"🔗 Link: {issue.permalink()}")

    except Exception as e:
        print(f"Erro ao enriquecer: {e}")

if __name__ == "__main__":
    main()
