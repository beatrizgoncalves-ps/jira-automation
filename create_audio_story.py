import os
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()

SERVER = os.getenv("JIRA_SERVER")
EMAIL = os.getenv("JIRA_EMAIL")
TOKEN = os.getenv("JIRA_API_TOKEN")

def create_audio_story():
    jira = JIRA(server=SERVER, basic_auth=(EMAIL, TOKEN))

    description = """
# User Story: Cálculo de Distância Percorrida por Intervalo de Macro

### 1. Persona e Valor de Negócio
**Como** Gestor de Frota / Analista de Operações,
**Quero** visualizar a distância exata percorrida por um veículo durante o período em que uma macro específica esteve ativa,
**Para que** eu possa auditar a produtividade das viagens, entender o deslocamento real em atividades operacionais e identificar desperdícios ou desvios.

---

### 2. Critérios de Aceite
1. **Detecção de Ciclo de Macro**: Identificar par de eventos: ativação (início) e desativação (fim) de uma macro.
2. **Cálculo de Distância**: Diferença do odômetro (CAN-bus) ou, na ausência, soma geodésica (Haversine) dos pontos de GPS no intervalo.
3. **Tratamento de Deslocamento Zero**: Se não houver movimento real, o valor registrado deve ser `0 km`.
4. **Apresentação no Relatório**: Exibir Nome da Macro, Veículo, Início, Fim e Distância (em km, 2 casas decimais).

---

### 3. POV Técnico Crítico (Análise de Arquitetura e Engenharia)
- **Performance**: O cálculo 'on-the-fly' para grandes volumes causará timeout. **Recomendação**: Processamento assíncrono via consumer de eventos (Kafka/RabbitMQ) e persistência em Read Model otimizado.
- **Resiliência de Dados**: Tratar mensagens fora de ordem (Out-of-order events) reordenando por timestamp de geração no hardware.
- **GPS Drift**: Implementar threshold mínimo de velocidade ou validação cruzada com odômetro para evitar 'distância fantasma' em veículos parados.
- **Conformidade (LGPD)**: Garantir controle de acesso (RBAC) sobre o histórico de trajetos vinculados a motoristas.

---

### 4. Perguntas Incômodas / Casos de Borda
1. Como processar retroativamente dados que ficaram retidos em 'zona de sombra' de sinal e chegaram horas depois?
2. Como o sistema deve se comportar se a macro for encerrada manualmente pelo backoffice sem dados de GPS do hardware?
"""

    issue_dict = {
        'project': 'LAPDT',
        'summary': 'User Story: Cálculo de Distância Percorrida por Intervalo de Macro (via Áudio)',
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
    create_audio_story()
