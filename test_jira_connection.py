import os
from dotenv import load_dotenv
from jira import JIRA

# Carrega as variáveis do arquivo .env
load_dotenv()

SERVER = os.getenv("JIRA_SERVER")
EMAIL = os.getenv("JIRA_EMAIL")
TOKEN = os.getenv("JIRA_API_TOKEN")

def test_connection():
    try:
        if not all([SERVER, EMAIL, TOKEN]):
            print("Erro: Verifique se JIRA_SERVER, JIRA_EMAIL e JIRA_API_TOKEN estão configurados no arquivo .env")
            return

        print(f"Tentando conectar ao Jira em: {SERVER}...")
        
        # Inicializa a conexão
        # Nota: O JIRA Cloud usa basic_auth com (email, api_token)
        jira = JIRA(server=SERVER, basic_auth=(EMAIL, TOKEN))
        
        # Tenta buscar as informações do usuário atual para validar a sessão
        user = jira.myself()
        print(f"Sucesso! Conectado como: {user['displayName']} ({user['emailAddress']})")
        
        # Lista os projetos para confirmar que temos permissão de leitura
        projects = jira.projects()
        print("\nProjetos encontrados:")
        if projects:
            for project in projects[:5]:
                print(f"- {project.key}: {project.name}")
        else:
            print("Nenhum projeto encontrado. Verifique suas permissões no Jira.")
            
    except Exception as e:
        print(f"\nErro ao conectar: {e}")
        print("\n--- CHECKLIST DE SOLUÇÃO ---")
        print("1. O JIRA_SERVER no .env começa com https:// e termina em .atlassian.net?")
        print("2. O JIRA_EMAIL é exatamente o que você usa para logar?")
        print("3. Você criou o 'API Token' (e não uma senha comum)?")
        print("4. O arquivo foi renomeado de .env.example para .env?")

if __name__ == "__main__":
    test_connection()
