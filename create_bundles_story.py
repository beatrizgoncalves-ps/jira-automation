import os
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()
jira = JIRA(server=os.getenv('JIRA_SERVER'), basic_auth=(os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN')))

description = """
# US - Melhoria da Experiência e Otimização da Tela de Bundles

### 📊 Score de Definição: 30/100 (Imaturo)

---

## 🔍 Roteiro de Discovery (Necessário antes de Dev)
* Qual é o principal motivador para a melhoria da tela de bundles? (Ex: novos produtos, atualização de design)?
* Quem é o responsável por fornecer os novos conteúdos, preços ou pacotes?
* Essa alteração será implementada via código ou via ferramentas dinâmicas (ex: Pendo)?
* Existe algum benchmark ou protótipo no Figma já desenhado?

---

## 🚨 Alerta de Duplicidade Semântica
* **LAPDT-976** (95% similar): Este item é altamente similar à LAPDT-976 ('Atualização da página de Bundles'). Recomenda-se validar se esta demanda não deve ser fundida com a anterior.

---

## 🛠 POV Técnico Inicial
* **Integração:** Verificar se as APIs de bundles suportam a exibição dinâmica de novos pacotes.
* **Performance:** Garantir que o carregamento da tela de bundles não degrade com a inclusão de novos elementos visuais ou trackings do Pendo.
"""

issue_dict = {
    'project': 'LAPDT', 
    'summary': 'User Story: Melhoria e Otimização da Experiência na Tela de Bundles', 
    'description': description, 
    'issuetype': {'name': 'User Story'}
}

try:
    new_issue = jira.create_issue(fields=issue_dict)
    print(f"Sucesso: {new_issue.key} (User Story)")
except Exception as e:
    print(f"Erro: {e}")
