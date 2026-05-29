import os
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()

SERVER = os.getenv("JIRA_SERVER")
EMAIL = os.getenv("JIRA_EMAIL")
TOKEN = os.getenv("JIRA_API_TOKEN")

def create_story():
    jira = JIRA(server=SERVER, basic_auth=(EMAIL, TOKEN))

    description = """
## 1. Título
Sinalização Visual de Uso Indevido de Veículos no Mapa de Monitoramento

---

## 2. Descrição da Persona
**Como um** Operador de Monitoramento de Risco e Segurança
**Quero** visualizar um ícone exclusivo e destacado no mapa para veículos que apresentem comportamento classificado como 'uso indevido'
**Para que** eu possa identificar anomalias críticas instantaneamente, priorizar o plano de acionamento e mitigar riscos de sinistros, roubos ou avarias na frota.

---

## 3. Valor de Negócio
Atualmente, o operador precisa analisar alertas textuais ou múltiplos menus para identificar quando um veículo está sendo utilizado de forma indevida (ex: condução agressiva extrema, uso fora do horário permitido, violação de cerca geográfica de segurança). A centralização dessa informação em um ícone intuitivo e de alto contraste diretamente no mapa de monitoramento reduz o tempo médio de reação (MTTR - *Mean Time to Respond*) da equipe de segurança, reduzindo custos operacionais com sinistros e melhorando a acurácia da Inteligência de Risco.

---

## 4. Critérios de Aceite

### Cenário 1: Exibição do novo ícone de uso indevido no mapa
* **Dado que** um veículo da frota gerou um evento de 'Uso Indevido' ativo (ex: desvio crítico de rota, uso fora do horário ou velocidade excessiva recorrente)
* **Quando** o operador acessar o mapa de monitoramento em tempo real
* **Então** o ícone do veículo em questão deve ser substituído pelo novo ícone de 'Uso Indevido'
* **E** o ícone deve ter a cor vermelha de alerta de risco para se destacar dos demais veículos em operação normal.

### Cenário 2: Interação com o ícone (Hover/Tooltip)
* **Dado que** o operador está visualizando o ícone de uso indevido no mapa
* **Quando** ele passar o ponteiro do mouse (*hover*) sobre o ícone
* **Então** o sistema deve exibir um *tooltip* com as informações rápidas:
  * Placa do Veículo
  * Nome do Motorista
  * Tipo de Uso Indevido (ex: 'Saída de Cerca Não Autorizada')
  * Tempo de duração do alerta ativo.

### Cenário 3: Resolução do Alerta / Retorno ao Estado Normal
* **Dado que** o alerta de uso indevido foi tratado pelo operador ou cessado pelo sistema
* **Quando** o status do veículo retornar para 'Normal' ou 'Em Viagem Regular'
* **Então** o mapa deve atualizar dinamicamente, removendo o ícone de uso indevido e voltando a exibir o ícone padrão de tráfego do veículo.

---

## 5. Notas Técnicas e Comportamento

### Sugestão de Design do Ícone
* **Ícone sugerido:** Silhueta de um carro de perfil ou vista superior, sobreposto por um símbolo de exclamação de alerta (!) ou um triângulo de advertência.
* **Formatos necessários:** SVG e PNG.

### Cores (Paleta de Risco)
* **Cor do Ícone Ativo:** Vermelho Alerta (#D32F2F)
* **Cor de Fundo/Borda (Halo):** Efeito de pulsação em vermelho translúcido.

---

## 6. Épico Sugerido
* **LAPDT-861: Inteligência de Risco**
"""

    issue_dict = {
        'project': 'LAPDT',
        'summary': 'US - Novo Ícone de Mapa para Sinalização de Uso Indevido de Veículos',
        'description': description,
        'issuetype': {'name': 'User Story'},
        'customfield_12600': 'LAPDT-861' # Epic Link
    }

    try:
        new_issue = jira.create_issue(fields=issue_dict)
        print(f"Sucesso: {new_issue.key}")
    except Exception as e:
        print(f"Erro ao criar: {e}")

if __name__ == "__main__":
    create_story()
