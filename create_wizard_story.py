import os
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()

SERVER = os.getenv("JIRA_SERVER")
EMAIL = os.getenv("JIRA_EMAIL")
TOKEN = os.getenv("JIRA_API_TOKEN")

def create_wizard_story():
    jira = JIRA(server=SERVER, basic_auth=(EMAIL, TOKEN))

    description = """
# US - Implementação do Assistente de Configuração de Situações Críticas (Virtual Tower)

### 📊 Score de Qualidade: 88/100

---

### 1. Persona e Valor de Negócio
**Como** Gestor de Frota / Operador da Virtual Tower,
**Quero** um assistente (wizard) intuitivo para configurar regras de situações críticas,
**Para que** eu possa parametrizar alertas personalizados de velocidade e comportamento de direção, agilizando a resposta a incidentes operacionais.

---

### 2. Fluxo de Configuração (Wizard - 4 Passos)

#### **Passo 1: Identificação da Regra**
* **Campos:** Nome da regra, Grupo de veículos, Canal de aplicação.
* **Validação:** Botão 'Próximo' só habilita com campos preenchidos.

#### **Passo 2: Parametrização Crítica**
* **Gatilhos:** Seleção de evento (ex: Excesso de Velocidade).
* **Configuração:** Limites numéricos, mensagens customizadas e **escolha de som de alerta** (com player de teste).

#### **Passo 3: Notificações**
* **Destinatários:** Gestão de contatos (E-mail, SMS, Push).
* **Configuração:** Seleção multicanal de envio de alertas.

#### **Passo 4: Revisão e Ativação**
* Resumo completo da regra antes do salvamento final e ativação do monitoramento.

---

### 3. Critérios de Aceite
* **CA01:** O sistema deve persistir as regras no banco de dados e iniciar o monitoramento imediato após a ativação.
* **CA02:** Validação de campos obrigatórios em tempo real em cada etapa do wizard.
* **CA03:** O som de alerta selecionado deve ser reproduzível no navegador durante a configuração para validação do usuário.

---

### 4. POV Técnico Crítico (Engenharia)
* **Persistência do Estado:** Como o wizard possui 4 passos, o estado deve ser mantido localmente (Local Storage ou State Management) para evitar perda de dados em caso de refresh acidental antes da conclusão.
* **Latência de Alerta:** A regra criada deve ser propagada para o motor de eventos em tempo real para garantir que o monitoramento comece imediatamente.
* **Segurança de API:** Validar limites de caracteres e sanitização nos inputs de mensagens customizadas para evitar ataques de injeção no canal de comunicação.

---

### 5. Perguntas Incômodas / Edge Cases
1. O que acontece se dois operadores tentarem editar a mesma regra crítica simultaneamente? (Locking de regra).
2. Como o sistema lida com regras conflitantes (ex: uma regra de 80km/h e outra de 100km/h para o mesmo veículo)?
"""

    issue_dict = {
        'project': 'LAPDT',
        'summary': 'US - Implementação do Assistente de Configuração de Situações Críticas - Virtual Tower',
        'description': description,
        'issuetype': {'name': 'User Story'},
        'customfield_12600': 'LAPDT-860' # Épico: Virtual Tower
    }

    try:
        new_issue = jira.create_issue(fields=issue_dict)
        print(f"Sucesso: {new_issue.key}")
        
        # Anexando a imagem original
        image_path = "rule_creation_steps.png"
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                jira.add_attachment(issue=new_issue, attachment=f)
            print("✨ Imagem anexada com sucesso!")
            
    except Exception as e:
        print(f"Erro ao criar: {e}")

if __name__ == "__main__":
    create_wizard_story()
