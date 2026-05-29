import os
import google.generativeai as genai
from dotenv import load_dotenv
from jira import JIRA
import json
from PIL import Image
import mimetypes

# Carrega configurações
load_dotenv()

# Configuração Jira e Gemini
JIRA_SERVER = os.getenv("JIRA_SERVER")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_API_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

FIELD_EPIC_LINK = "customfield_12600"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

def connect_jira():
    return JIRA(server=JIRA_SERVER, basic_auth=(JIRA_EMAIL, JIRA_TOKEN))

def get_recent_epics(jira):
    epics = jira.search_issues('project = LAPDT AND issuetype = Epic ORDER BY created DESC', maxResults=15)
    return [{"key": e.key, "summary": e.fields.summary} for e in epics]

def process_multi_items_ai(user_input, epics_context, file_path=None):
    prompt = f"""
    Você é um Product Manager Sênior e Analista de Sistemas.
    Sua tarefa é analisar o input (texto ou arquivo) e identificar TODAS as User Stories ou Epics distintos contidos nele.
    
    INPUT: "{user_input if not file_path else 'Anexo enviado'}"
    CONTEXTO DE ÉPICOS: {json.dumps(epics_context, indent=2)}

    REGRAS:
    1. Se houver mais de uma funcionalidade, requisito ou tema, separe-os em itens individuais.
    2. Para cada item, gere: Título, Tipo (User Story/Epic), Descrição Enriquecida incluindo obrigatoriamente:
       - Persona e Valor de Negócio.
       - Critérios de Aceite detalhados.
       - **POV Técnico Crítico**: Analise como um desenvolvedor sênior. Não repita o óbvio. Foque em:
         - Gargalos de performance e escalabilidade.
         - Dependências técnicas e riscos de integração.
         - Segurança, permissões e conformidade de dados.
         - Perguntas "incômodas" sobre casos de borda extremos (ex: falhas de rede, dados inconsistentes, concorrência).
    3. Para User Stories, vincule à KEY de um Épico da lista de contexto se houver relação clara.
    4. Responda APENAS com um JSON contendo uma lista de objetos.

    FORMATO DE RETORNO:
    {{
        "items": [
            {{
                "type": "User Story",
                "title": "Título 1",
                "description": "Markdown Completo",
                "suggested_epic": "KEY"
            }},
            {{
                "type": "Epic",
                "title": "Título 2",
                "description": "Markdown Completo",
                "suggested_epic": null
            }}
        ]
    }}
    """
    
    content_list = [prompt]
    if file_path and os.path.exists(file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and mime_type.startswith('image'):
            content_list.append(Image.open(file_path))
        elif mime_type == 'application/pdf' or (mime_type and mime_type.startswith('audio')):
            print(f"📤 Uploading {mime_type} to Gemini...")
            doc_file = genai.upload_file(path=file_path)
            content_list.append(doc_file)
            
    response = model.generate_content(content_list)
    text = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(text)

def main():
    print("\n--- 🧠 Decompositor de Backlog Multimodal JIRA ---")
    user_input = input("Sua demanda ou caminho do arquivo: ").strip().strip('"')
    
    file_path = os.path.abspath(user_input) if os.path.exists(user_input) else None
    text_input = "" if file_path else user_input
    
    try:
        jira = connect_jira()
        print("🔍 Coletando contexto e analisando entrada...")
        epics = get_recent_epics(jira)
        
        result = process_multi_items_ai(text_input, epics, file_path=file_path)
        items = result.get("items", [])
        
        if not items:
            print("Nenhum item identificado pela IA.")
            return

        while True:
            # Gerar arquivo de revisão unificado
            md_content = f"# REVISÃO DE BACKLOG - {len(items)} ITENS IDENTIFICADOS\n\n"
            for i, item in enumerate(items, 1):
                md_content += f"## ITEM {i}: {item['title']} ({item['type']})\n"
                md_content += f"**ÉPICO:** {item.get('suggested_epic', 'N/A')}\n\n"
                md_content += f"{item['description']}\n"
                md_content += f"---\n\n"
            
            with open("REVISAO_JIRA.md", "w", encoding="utf-8") as f:
                f.write(md_content)
            
            print("\n" + "="*60)
            print(f"📋 SUMÁRIO DO BACKLOG IDENTIFICADO ({len(items)} itens)")
            print("="*60)
            for i, item in enumerate(items, 1):
                epic_info = f" [Épico: {item['suggested_epic']}]" if item.get('suggested_epic') else ""
                print(f"{i}. [{item['type']}] {item['title']}{epic_info}")
            
            print("\n" + "-"*60)
            print("📄 Detalhamento completo gerado em: 'REVISAO_JIRA.md'")
            print("-" * 60)
            print("[1] 🚀 CRIAR TODOS NO JIRA")
            print("[2] Pedir para IA refinar/mudar algo")
            print("[0] Cancelar")
            
            choice = input("\nEscolha: ")
            
            if choice == '1':
                break
            elif choice == '2':
                feedback = input("O que deseja ajustar em todos os itens? ")
                result = process_multi_items_ai(f"AJUSTE: {feedback}. Input anterior: {user_input}", epics, file_path=file_path)
                items = result.get("items", [])
            else:
                return

        print(f"🚀 Iniciando criação de {len(items)} itens...")
        for item in items:
            issue_dict = {
                'project': 'LAPDT',
                'summary': item['title'],
                'description': item['description'],
                'issuetype': {'name': item['type']},
            }
            if item['type'] == 'User Story' and item.get('suggested_epic'):
                issue_dict[FIELD_EPIC_LINK] = item['suggested_epic']
            
            new_issue = jira.create_issue(fields=issue_dict)
            print(f"✨ Criado: {item['title']} -> {new_issue.key}")
            
            if file_path:
                with open(file_path, 'rb') as f:
                    jira.add_attachment(issue=new_issue, attachment=f)

        print("\n🎉 Todos os itens foram processados e anexados!")
        os.remove("REVISAO_JIRA.md")

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()
