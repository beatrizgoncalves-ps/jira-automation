import os
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()

SERVER = os.getenv("JIRA_SERVER")
EMAIL = os.getenv("JIRA_EMAIL")
TOKEN = os.getenv("JIRA_API_TOKEN")

def create_macro_story():
    jira = JIRA(server=SERVER, basic_auth=(EMAIL, TOKEN))

    description = """
# User Story: Macros - Informação de Distância Percorrida

**Status:** Refined / Ready for Engineering
**Persona:** Gerente de Frota / Analista de Operações
**Prioridade:** Alta

---

## 1. Contexto de Negócio
Atualmente, as operações rodoviárias carecem de uma forma automatizada de auditar a distância exata percorrida durante a execução de uma "Macro" específica (ex: Viagem de Entrega, Coleta, Desvio de Rota). Ter essa informação consolidada no Relatório de Produtividade elimina processos manuais de cálculo e aumenta a precisão na análise de custo e eficiência por atividade.

## 2. Descrição (User Story)
**Como** um Gerente de Frota,
**Eu quero** visualizar a distância total percorrida entre a ativação e a finalização de uma Macro no Relatório de Produtividade do Vfleets,
**Para que** eu possa auditar o deslocamento real de cada atividade e validar a produtividade da frota de forma precisa.

---

## 3. Critérios de Aceite (Conditions of Satisfaction)

### Cenário 1: Cálculo de distância em uma Macro concluída
**Dado** que um veículo ativou uma Macro (ex: "Início de Viagem") às 08:00;
**E** finalizou a mesma Macro às 10:00;
**Quando** o Relatório de Produtividade for gerado para este período;
**Então** o sistema deve calcular o delta do odômetro/GPS e exibir a distância total percorrida (ex: "120.5 KM").

### Cenário 2: Veículo estacionário durante a Macro
**Dado** que uma Macro foi ativada e finalizada;
**Mas** o veículo não registrou deslocamento físico durante o intervalo;
**Quando** eu visualizar o Relatório de Produtividade;
**Então** o campo de distância percorrida deve exibir obrigatoriamente "0KM".

### Cenário 3: Formatação e Unidade de Medida
**Dado** que a informação de distância está disponível no relatório;
**Quando** eu realizar a leitura do campo;
**Então** a informação deve estar acompanhada da unidade de medida "KM" e deve ser exibida de forma clara em uma coluna dedicada (ex: "Distância da Macro").

---

## 4. Regras de Negócio e Requisitos Técnicos
1. **Fonte de Dados:** A distância deve ser baseada na telemetria do veículo (Odômetro de barramento ou GPS, seguindo a hierarquia de confiabilidade do sistema).
2. **Precisão:** O valor deve suportar ao menos uma casa decimal (ex: 10.5 KM).
3. **Persistência:** O cálculo deve ser realizado no momento da finalização da Macro e persistido para consulta histórica.
4. **Relatório:** O campo deve ser incluído como uma nova coluna opcional ou padrão no "Relatório de Produtividade" do Vfleets.

---

## 5. Definição de Pronto (DoD)
- [ ] Lógica de cálculo implementada e validada com dados de GPS/Odômetro.
- [ ] Coluna adicionada ao Relatório de Produtividade no Vfleets.
- [ ] Testes unitários cobrindo cenários de deslocamento zero e deslocamento positivo.
- [ ] UI/UX validada para garantir que a unidade "KM" está visível e legível.
"""

    issue_dict = {
        'project': 'LAPDT',
        'summary': 'User Story: Macros - Informação de Distância Percorrida',
        'description': description,
        'issuetype': {'name': 'User Story'},
        'customfield_12600': 'LAPDT-938' # Epic: Monitoramento de Atrasos e Performance
    }

    try:
        new_issue = jira.create_issue(fields=issue_dict)
        print(f"Sucesso: {new_issue.key}")
    except Exception as e:
        print(f"Erro ao criar: {e}")

if __name__ == "__main__":
    create_macro_story()
