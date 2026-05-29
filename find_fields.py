import os
from jira import JIRA
from dotenv import load_dotenv

load_dotenv()

def find_fields():
    jira = JIRA(server=os.getenv('JIRA_SERVER'), basic_auth=(os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN')))
    
    # Busca metadados de criação para User Story no projeto LAPDT
    meta = jira.createmeta(projectKeys='LAPDT', issuetypeNames=['User Story'], expand='projects.issuetypes.fields')
    
    fields = meta['projects'][0]['issuetypes'][0]['fields']
    
    print("--- Campos Encontrados em LAPDT ---")
    for field_id, info in fields.items():
        name = info['name']
        if any(term in name.lower() for term in ['team', 'epic', 'parent']):
            print(f"ID: {field_id} | Nome: {name}")

if __name__ == "__main__":
    find_fields()
