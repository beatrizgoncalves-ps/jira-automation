import os
from dotenv import load_dotenv
from jira import JIRA

# Carrega as variáveis do arquivo .env
load_dotenv()

SERVER = os.getenv("JIRA_SERVER")
EMAIL = os.getenv("JIRA_EMAIL")
TOKEN = os.getenv("JIRA_API_TOKEN")

def connect_jira():
    return JIRA(server=SERVER, basic_auth=(EMAIL, TOKEN))

def main():
    try:
        jira = connect_jira()
        print("--- Verificador de Acesso a Projeto ---")
        
        # Pede o nome ou chave do projeto
        target_project = input("Informe a CHAVE do projeto (ex: PROJ) ou NOME: ").strip().upper()
        
        projects = jira.projects()
        
        # Busca o projeto na lista
        found_project = next((p for p in projects if p.key == target_project or p.name.upper() == target_project), None)
        
        if found_project:
            print(f"\n✅ Projeto encontrado!")
            print(f"Nome: {found_project.name}")
            print(f"Chave (Key): {found_project.key}")
            print(f"ID: {found_project.id}")
            
            # Opcional: Lista os tipos de tarefas disponíveis neste projeto
            # Isso é importante para sabermos se 'Epic' ou 'Story' existem com esses nomes exatos
            meta = jira.createmeta(projectKeys=found_project.key)
            issue_types = [it['name'] for it in meta['projects'][0]['issuetypes']]
            print(f"Tipos de itens disponíveis: {', '.join(issue_types)}")
            
        else:
            print(f"\n❌ Projeto '{target_project}' não encontrado ou você não tem permissão.")
            print("\nProjetos que você pode acessar:")
            for p in projects:
                print(f"- {p.key}: {p.name}")

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()
