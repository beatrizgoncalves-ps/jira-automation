import json
import mimetypes
import os
import tempfile
from typing import Any, Dict, List, Optional

import google.generativeai as genai
import streamlit as st
from jira import JIRA
from PIL import Image

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def get_config(name: str, default: Optional[str] = None) -> Optional[str]:
    """Read config from Streamlit secrets first, then environment variables."""
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name, default)


def validate_config() -> List[str]:
    required = ["JIRA_SERVER", "JIRA_EMAIL", "JIRA_API_TOKEN", "GEMINI_API_KEY"]
    return [key for key in required if not get_config(key)]


@st.cache_resource(show_spinner=False)
def connect_jira(server: str, email: str, token: str) -> JIRA:
    return JIRA(server=server, basic_auth=(email, token))


@st.cache_data(ttl=600, show_spinner=False)
def get_recent_epics(server: str, email: str, token: str, project_key: str) -> List[Dict[str, str]]:
    jira = connect_jira(server, email, token)
    issues = jira.search_issues(
        f'project = {project_key} AND issuetype = Epic ORDER BY created DESC',
        maxResults=25,
    )
    return [{"key": issue.key, "summary": issue.fields.summary} for issue in issues]


def get_gemini_model(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-flash-latest")


def parse_gemini_json(text: str) -> Dict[str, Any]:
    clean = text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


def save_uploaded_file(uploaded_file) -> Optional[str]:
    if not uploaded_file:
        return None
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        return tmp.name


def process_multi_items_ai(
    user_input: str,
    epics_context: List[Dict[str, str]],
    gemini_api_key: str,
    file_path: Optional[str] = None,
) -> Dict[str, Any]:
    model = get_gemini_model(gemini_api_key)
    project_key = get_config("JIRA_PROJECT_KEY", "LAPDT")

    prompt = f"""
Você é um Product Manager Sênior e Analista de Sistemas.
Sua tarefa é analisar o input abaixo e identificar TODAS as User Stories ou Epics distintos contidos nele.

PROJETO JIRA: {project_key}
INPUT: "{user_input if not file_path else 'Anexo enviado'}"
CONTEXTO DE ÉPICOS: {json.dumps(epics_context, ensure_ascii=False, indent=2)}

REGRAS:
1. Se houver mais de uma funcionalidade, requisito ou tema, separe-os em itens individuais.
2. Para cada item, gere: Título, Tipo (User Story/Epic), Descrição Enriquecida incluindo obrigatoriamente:
   - Persona e Valor de Negócio.
   - Critérios de Aceite detalhados.
   - POV Técnico Crítico: gargalos, dependências, riscos, segurança, permissões, dados e casos de borda.
3. Para User Stories, vincule à KEY de um Épico da lista de contexto se houver relação clara.
4. Escreva em português do Brasil.
5. Responda APENAS com JSON válido contendo uma lista de objetos.

FORMATO DE RETORNO:
{{
  "items": [
    {{
      "type": "User Story",
      "title": "Título 1",
      "description": "Markdown completo",
      "suggested_epic": "KEY ou null"
    }}
  ]
}}
"""

    content_list: List[Any] = [prompt]
    if file_path and os.path.exists(file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and mime_type.startswith("image"):
            content_list.append(Image.open(file_path))
        elif mime_type == "application/pdf" or (mime_type and mime_type.startswith("audio")):
            uploaded_doc = genai.upload_file(path=file_path)
            content_list.append(uploaded_doc)
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content_list.append(f.read())

    response = model.generate_content(content_list)
    return parse_gemini_json(response.text)


def build_review_markdown(items: List[Dict[str, Any]]) -> str:
    content = f"# REVISÃO DE BACKLOG - {len(items)} ITENS IDENTIFICADOS\n\n"
    for index, item in enumerate(items, 1):
        content += f"## ITEM {index}: {item.get('title', 'Sem título')} ({item.get('type', 'User Story')})\n"
        content += f"**ÉPICO:** {item.get('suggested_epic') or 'N/A'}\n\n"
        content += f"{item.get('description', '')}\n\n---\n\n"
    return content


def create_items_in_jira(
    items: List[Dict[str, Any]],
    attachment_path: Optional[str] = None,
) -> List[str]:
    server = get_config("JIRA_SERVER")
    email = get_config("JIRA_EMAIL")
    token = get_config("JIRA_API_TOKEN")
    project_key = get_config("JIRA_PROJECT_KEY", "LAPDT")
    epic_link_field = get_config("JIRA_EPIC_LINK_FIELD", "customfield_12600")

    jira = connect_jira(server, email, token)
    created_keys: List[str] = []

    for item in items:
        issue_type = item.get("type") or "User Story"
        fields = {
            "project": project_key,
            "summary": item.get("title", "Item criado via Streamlit"),
            "description": item.get("description", ""),
            "issuetype": {"name": issue_type},
        }
        if issue_type == "User Story" and item.get("suggested_epic"):
            fields[epic_link_field] = item["suggested_epic"]

        issue = jira.create_issue(fields=fields)
        created_keys.append(issue.key)

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as file_obj:
                jira.add_attachment(issue=issue, attachment=file_obj)

    return created_keys


st.set_page_config(page_title="Jira Backlog Automation", page_icon="🧠", layout="wide")
st.title("🧠 Jira Backlog Automation")
st.caption("Transforme texto, áudio, PDF ou imagem em Epics e User Stories prontas para revisar e criar no Jira.")

missing = validate_config()
if missing:
    st.error("Configuração incompleta. Adicione estas variáveis nos Secrets do Streamlit: " + ", ".join(missing))
    st.stop()

server = get_config("JIRA_SERVER")
email = get_config("JIRA_EMAIL")
token = get_config("JIRA_API_TOKEN")
gemini_key = get_config("GEMINI_API_KEY")
project_key = get_config("JIRA_PROJECT_KEY", "LAPDT")

with st.sidebar:
    st.header("Configuração")
    st.write(f"Projeto Jira: `{project_key}`")
    st.write(f"Jira: `{server}`")
    st.divider()
    if st.button("Testar conexão com Jira"):
        try:
            jira = connect_jira(server, email, token)
            user = jira.myself()
            st.success(f"Conectado como {user.get('displayName', 'usuário')}")
        except Exception as exc:
            st.error(f"Falha na conexão: {exc}")

input_text = st.text_area(
    "Descreva a demanda",
    height=160,
    placeholder="Ex: Precisamos criar uma funcionalidade para calcular a distância percorrida durante uma macro...",
)

uploaded_file = st.file_uploader(
    "Ou envie um arquivo de apoio",
    type=["pdf", "png", "jpg", "jpeg", "m4a", "mp3", "wav", "txt", "md"],
)

col1, col2 = st.columns([1, 1])
with col1:
    analyze = st.button("Gerar revisão", type="primary", use_container_width=True)
with col2:
    clear = st.button("Limpar resultado", use_container_width=True)

if clear:
    st.session_state.pop("items", None)
    st.session_state.pop("attachment_path", None)

if analyze:
    if not input_text and not uploaded_file:
        st.warning("Digite uma demanda ou envie um arquivo.")
    else:
        attachment_path = save_uploaded_file(uploaded_file)
        st.session_state["attachment_path"] = attachment_path
        try:
            with st.spinner("Coletando épicos recentes e gerando revisão com IA..."):
                epics = get_recent_epics(server, email, token, project_key)
                result = process_multi_items_ai(input_text, epics, gemini_key, attachment_path)
                st.session_state["items"] = result.get("items", [])
            st.success(f"Revisão gerada com {len(st.session_state['items'])} item(ns).")
        except Exception as exc:
            st.error(f"Erro ao gerar revisão: {exc}")

items = st.session_state.get("items", [])
if items:
    st.subheader("Revisão antes de criar no Jira")
    review_md = build_review_markdown(items)
    st.download_button(
        "Baixar revisão em Markdown",
        data=review_md,
        file_name="REVISAO_JIRA.md",
        mime="text/markdown",
    )

    edited_json = st.text_area(
        "Edite o JSON antes de criar, se necessário",
        value=json.dumps({"items": items}, ensure_ascii=False, indent=2),
        height=360,
    )

    with st.expander("Preview em Markdown", expanded=True):
        st.markdown(review_md)

    if st.button("Criar itens no Jira", type="primary"):
        try:
            parsed = json.loads(edited_json)
            final_items = parsed.get("items", [])
            with st.spinner("Criando itens no Jira..."):
                keys = create_items_in_jira(final_items, st.session_state.get("attachment_path"))
            st.success("Itens criados: " + ", ".join(keys))
        except Exception as exc:
            st.error(f"Erro ao criar itens no Jira: {exc}")
