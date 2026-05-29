import os
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()
jira = JIRA(server=os.getenv('JIRA_SERVER'), basic_auth=(os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN')))

description = """
## US - Contagem Automática de Passageiros no Embarque

---

## 1. Persona e Valor de Negócio
**Como** Operador de Frota,
**Quero** contar automaticamente as pessoas que entram no veículo,
**Para** monitorar a ocupação e garantir que o limite de capacidade não seja excedido.

---

## 2. Critérios de Aceite
* O sistema deve detectar e contar cada indivíduo que cruza o portal de entrada do veículo.
* A contagem deve ser incrementada em tempo real.
* O dado deve ser persistido e associado ao ID do veículo e timestamp.

---

## 3. POV Técnico Crítico
* **Desafio de Fluxo:** Necessidade de diferenciar entradas de saídas para manter o saldo de lotação correto.
* **Hardware:** Requer posicionamento de câmera/sensor que cubra toda a largura da porta de entrada.
* **Conectividade:** O processamento deve ser local (Edge) para garantir resposta imediata caso o limite seja atingido.

---

## 4. Quality Report (Score: 35/100)
* **Pontos Fortes:** Intenção funcional direta.
* **Pontos Fracos:** Falta de detalhes sobre integração com sistema de bilhetagem ou sensores específicos.
"""

issue_dict = {
    'project': 'LAPDT',
    'summary': 'User Story: Contagem Automática de Passageiros no Embarque',
    'description': description,
    'issuetype': {'name': 'User Story'},
    'customfield_12600': 'LAPDT-938'
}

try:
    new_issue = jira.create_issue(fields=issue_dict)
    print(f"Sucesso: {new_issue.key}")
except Exception as e:
    print(f"Erro: {e}")
