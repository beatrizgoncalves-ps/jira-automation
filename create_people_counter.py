import os
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()

SERVER = os.getenv("JIRA_SERVER")
EMAIL = os.getenv("JIRA_EMAIL")
TOKEN = os.getenv("JIRA_API_TOKEN")

def create_people_counter_story():
    jira = JIRA(server=SERVER, basic_auth=(EMAIL, TOKEN))

    description = """
## US - Contagem Automática de Desembarque de Passageiros e Tripulação

---

## 1. Persona e Valor de Negócio

**Como** Coordenador de Operações de Solo e Analista de Performance da Torre Virtual,
**Quero** monitorar e contar automaticamente a quantidade de pessoas que saem de um veículo de transporte ao chegar na posição de parada,
**Para** medir com precisão o tempo de desembarque (Deboarding TAT), identificar gargalos operacionais e garantir a segurança operacional.

**Épico Relacionado:**
* **LAPDT-938**: Performance de Frota
* **LAPDT-860**: Virtual Tower

---

## 2. Critérios de Aceite

* **CA 01 - Detecção de Início do Evento:** O sistema deve iniciar o monitoramento apenas quando o veículo estiver em **Geofencing** e a porta for aberta.
* **CA 02 - Precisão Mínima de Contagem:** Acurácia mínima de **97%** em condições normais e **93%** em adversas (chuva/noite).
* **CA 03 - Direcionalidade do Fluxo:** Contar estritamente as pessoas que estão **saindo**.
* **CA 04 - Latência de Atualização:** Dado consolidado no dashboard em até **5 segundos** após o fechamento da porta.
* **CA 05 - Registro de Auditoria:** Log com ID Veículo, Timestamp e clip de vídeo curto (10s) para auditoria.

---

## 3. POV Técnico Crítico

* **Arquitetura Edge Computing:** O processamento (YOLOv8/DeepSORT) deve rodar no **Edge**. Enviar stream de vídeo contínuo para nuvem via 4G/5G é economicamente inviável.
* **Oclusão e Ângulo:** Necessidade de câmera em ângulo zenital oblíquo (45°-60°) para evitar que uma pessoa cubra a outra.
* **Condições Ambientais:** Câmeras com **WDR** e infravermelho são mandatórias para mitigar contraluz e operação noturna.
* **Tracking de ID Único:** O algoritmo deve persistir o ID mesmo em sobreposição parcial (overlap) para evitar contagem dupla ou perda de rastro.

---

## 4. Perguntas Incômodas (Edge Cases Extremos)

* **O efeito 'Vai e Volta':** Se um passageiro sai, volta para pegar algo e sai de novo, o tracking de ID consegue evitar a contagem duplicada?
* **Oclusão por Malas/Carrinhos:** Malas volumosas serão classificadas como indivíduos extras ou causarão falha na detecção do corpo humano?
* **Agente de Solo Estático:** Um funcionário parado na porta ajudando passageiros causará ruído na contagem ou bloqueará o rastro dos outros?
* **Resiliência Offline:** Qual o tamanho do buffer local se o gateway perder conexão com a nuvem durante um desembarque de grande porte?
"""

    issue_dict = {
        'project': 'LAPDT',
        'summary': 'User Story: Solução de Contagem Automática de Desembarque de Passageiros (Computer Vision)',
        'description': description,
        'issuetype': {'name': 'User Story'},
        'customfield_12600': 'LAPDT-938'
    }

    try:
        new_issue = jira.create_issue(fields=issue_dict)
        print(f"Sucesso: {new_issue.key}")
    except Exception as e:
        print(f"Erro ao criar: {e}")

if __name__ == "__main__":
    create_people_counter_story()
