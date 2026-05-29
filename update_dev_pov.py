import os
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()
jira = JIRA(server=os.getenv('JIRA_SERVER'), basic_auth=(os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN')))

def update_issue(key, section_text):
    issue = jira.issue(key)
    current_desc = issue.fields.description
    new_desc = current_desc + "\n\n" + section_text
    issue.update(description=new_desc)
    print(f"Atualizado: {key}")

dev_pov_1015 = """
---
## 🛠 POV Técnico & Perguntas Dev (Análise de Engenharia)
1. **Precedência de Ícones:** Se houver múltiplos status críticos simultâneos, o 'Uso Indevido' é o de maior prioridade visual?
2. **Implementação do Efeito:** O efeito de pulsação deve ser implementado via CSS (se for um Marker DOM) ou via renderização de camada no MapBox/GoogleMaps?
3. **Payload:** O status de uso indevido já vem mastigado pelo backend ou o front deve avaliar o array de alertas ativos?
4. **Asset:** Os ícones SVG serão fornecidos pelo Design ou devemos seguir uma biblioteca padrão?
"""

dev_pov_1016 = """
---
## 🛠 POV Técnico & Perguntas Dev (Análise de Engenharia)
1. **Hierarquia de Sensores:** Qual a regra de prioridade se o Odômetro CAN for nulo em parte do trajeto? (Ex: 1. CAN, 2. GPS Odometry, 3. Haversine).
2. **Momento do Cálculo:** O cálculo do Delta deve ocorrer de forma assíncrona no encerramento da Macro ou em tempo real a cada ping de posição?
3. **Precisão e Arredondamento:** Seguiremos o padrão de 1 casa decimal para o relatório? Como tratar valores menores que 100 metros?
4. **Consistência:** O que acontece se a Macro for encerrada manualmente pelo backoffice sem dados de GPS do final da viagem?
"""

update_issue('LAPDT-1015', dev_pov_1015)
update_issue('LAPDT-1016', dev_pov_1016)
