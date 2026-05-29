import os
import google.generativeai as genai
from dotenv import load_dotenv
from jira import JIRA
import json
from PIL import Image
import mimetypes
import re

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

def get_epic_field(jira, project_key):
    """Detecta qual campo o projeto usa para vincular épicos."""
    try:
        # Tenta verificar se é um projeto Team-Managed (usa 'parent')
        proj = jira.project(project_key)
        if getattr(proj, 'style', '') == 'next-gen':
            return 'parent'
        
        # Para Company-Managed, busca o campo 'Epic Link'
        fields = jira.fields()
        epic_link_field = next((f['id'] for f in fields if f['name'] == 'Epic Link'), 'customfield_12600')
        return epic_link_field
    except:
        return 'customfield_12600'

def get_projects(jira):
    return {str(i+1): p for i, p in enumerate(jira.projects())}

def get_search_keywords_ai(text):
    prompt = f"Extraia 3 palavras-chave técnicas para busca no Jira da demanda: {text}. Retorne apenas as palavras separadas por vírgula."
    try:
        response = model.generate_content(prompt)
        return [k.strip() for k in response.text.split(',')]
    except:
        return re.findall(r'\w{4,}', text)[:3]

def search_potential_duplicates(jira, project_key, text):
    keywords = get_search_keywords_ai(text)
    if not keywords: return []
    query = f'project = "{project_key}" AND ("' + '" OR "'.join(keywords) + '") ORDER BY created DESC'
    try:
        results = jira.search_issues(query, maxResults=10)
        return [{"key": i.key, "summary": i.fields.summary, "description": i.fields.description or ""} for i in results]
    except:
        return []

def process_multi_items_ai(user_input, project_key, epics_context, similar_issues, file_path=None):
    prompt = f"""
    Você é um PM Sênior. Realize uma análise TRÍPLICE e INDEPENDENTE.
    Projeto Alvo: {project_key}

    --- CONTEXTO JIRA ---
    DUPLICATAS: {json.dumps(similar_issues)}
    ÉPICOS DISPONÍVEIS: {json.dumps(epics_context)}

    TAREFAS:
    1. QUALIDADE (0-100).
    2. DUPLICIDADE (Deep Analysis).
    3. MATURIDADE (Discovery vs Story).
    4. VÍNCULO DE ÉPICO: Escolha a KEY do épico mais relacionado na lista acima. Se não houver relação, use null.

    FORMATO JSON:
    {{
        "items": [
            {{
                "title": "...",
                "quality_score": 85,
                "quality_report": {{ "strengths": [], "weaknesses": [] }},
                "needs_discovery": true/false,
                "discovery_questions": [],
                "duplicate_analysis": {{ "is_duplicate": false, "matches": [] }},
                "suggested_epic": "KEY-DO-EPICO ou null",
                "type": "User Story ou Research Spike",
                "description": "Markdown"
            }}
        ]
    }}
    """
    content_list = [prompt]
    if not file_path: content_list.append(f"INPUT: {user_input}")
    if file_path and os.path.exists(file_path):
        img = Image.open(file_path)
        if img.width * img.height > 80000000: img.thumbnail((4000, 4000))
        content_list.append(img)
            
    response = model.generate_content(content_list)
    text = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(text)

def main():
    print("\n" + "="*60 + "\n🧠 JIRA BACKLOG GUARDIAN v3.3 (Epic Link Fixed)\n" + "="*60)
    
    try:
        jira = connect_jira()
        projects_map = get_projects(jira)
        
        print("\nEscolha o projeto alvo:")
        # Mostra apenas os 10 primeiros para brevidade ou deixa escolher por chave
        for idx, p in list(projects_map.items())[:20]:
            print(f"[{idx}] {p.key}: {p.name}")
        
        p_choice = input("\nDigite o número ou a Chave do Projeto: ").strip()
        selected_project = projects_map.get(p_choice) or next((p for p in projects_map.values() if p.key.upper() == p_choice.upper()), None)
        
        if not selected_project:
            print("❌ Projeto inválido."); return

        project_key = selected_project.key
        epic_field = get_epic_field(jira, project_key)
        print(f"✅ Projeto: {project_key} | Campo de Épico detectado: {epic_field}")

        user_input = input("\nSua demanda: ").strip().strip('"')
        
        print("🔍 Analisando...")
        potential_dups = search_potential_duplicates(jira, project_key, user_input)
        epics = [{"key": e.key, "summary": e.fields.summary} for e in jira.search_issues(f'project = "{project_key}" AND issuetype = Epic', maxResults=15)]
        
        result = process_multi_items_ai(user_input, project_key, epics, potential_dups)
        items = result.get("items", [])
        
        for i, item in enumerate(items, 1):
            print(f"\n{i}. RESULTADO DA ANÁLISE")
            print(f"   📌 Título: {item['title']}")
            print(f"   📂 Épico Vinculado: {item.get('suggested_epic') or 'Nenhum'}")
            print(f"   📊 Score: {item['quality_score']}/100")
            
            if item.get('duplicate_analysis', {}).get('is_duplicate'):
                print(f"   🚨 Duplicidade detectada!")
            
            if item.get('needs_discovery'):
                print(f"   🔍 Necessita Discovery: Sim")

        choice = input("\n[1] CRIAR | [0] CANCELAR: ")
        if choice == '1':
            issue_type = 'User Story'
            if any(item.get('needs_discovery') for item in items):
                t_choice = input("Criar como [1] User Story ou [2] Research Spike? ")
                if t_choice == '2': issue_type = 'Research Spike'

            for item in items:
                issue_dict = {
                    'project': project_key, 
                    'summary': item['title'], 
                    'description': item['description'], 
                    'issuetype': {'name': issue_type}
                }
                
                epic_key = item.get('suggested_epic')
                if epic_key:
                    if epic_field == 'parent':
                        issue_dict['parent'] = {'key': epic_key}
                    else:
                        issue_dict[epic_field] = epic_key
                
                new_issue = jira.create_issue(fields=issue_dict)
                print(f"✨ Criado: {new_issue.key} (Épico: {epic_key or 'N/A'})")
                
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()
