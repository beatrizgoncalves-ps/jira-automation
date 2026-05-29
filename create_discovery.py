import os
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()
jira = JIRA(server=os.getenv('JIRA_SERVER'), basic_auth=(os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN')))

description = """
## Discovery: Mapeamento, Inventário e Viabilidade de Migração de Sistemas Internos

### 📊 Score de Definição: 35/100

---

## 🔍 Roteiro de Discovery (Perguntas Críticas)
* Quais são os sistemas, planilhas ou portais internos específicos que hoje operam fora do padrão corporativo?
* Quem são os stakeholders, mantenedores atuais e áreas de negócio dependentes dessas ferramentas?
* Qual é a tecnologia/infraestrutura atual desses sistemas e qual é a arquitetura de destino idealizada?
* Quais dados/funcionalidades são críticos e não podem sofrer perda de disponibilidade durante a migração?
* Existe alguma dependência direta de APIs ou parceiros externos que inviabilize uma migração de curto prazo?

---

## 🛠 POV Técnico Crítico
* **Mapeamento de Stack:** Identificar linguagens, versões de SO e bancos de dados para prever incompatibilidades com o novo ambiente.
* **Integridade de Dados:** Validar se os dados atuais possuem backups confiáveis para processos de ETL.
* **Segurança:** Avaliar se os projetos paralelos possuem vulnerabilidades que podem ser herdadas pelo novo ambiente.

---

## 🚨 Alerta de Duplicidade
* **LAPDT-925**: Item com objetivo similar (Avaliação painéis Julio para migração). Este discovery deve considerar o trabalho já iniciado naquele item.
"""

issue_dict = {
    'project': 'LAPDT', 
    'summary': 'Discovery: Mapeamento e Viabilidade de Migração de Sistemas Internos', 
    'description': description, 
    'issuetype': {'name': 'Research Spike'}
}

try:
    new_issue = jira.create_issue(fields=issue_dict)
    print(f"Sucesso: {new_issue.key}")
except Exception as e:
    print(f"Erro: {e}")
