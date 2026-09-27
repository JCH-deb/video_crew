import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="INED Workspace", page_icon="🔐", layout="wide")

# --- CONFIGURACIÓN DE NOTION ---
# 1. Pega aquí tu Internal Integration Secret (empieza con secret_)
NOTION_TOKEN = "secret_PEGA_TU_TOKEN_AQUI"

# 2. Pega aquí el ID de la base de datos de PLANTILLAS (32 caracteres del enlace)
DB_PLANTILLAS_ID = "PEGA_AQUI_EL_ID_DE_PLANTILLAS"

# 3. Pega aquí el ID de la base de datos del CHECKLIST (32 caracteres del enlace)
DB_CHECKLIST_ID = "PEGA_AQUI_EL_ID_DEL_CHECKLIST"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# --- FUNCIONES DE NOTION ---
def cargar_plantillas_notion():
    url = f"https://api.notion.com/v1/databases/{DB_PLANTILLAS_ID}/query"
    response = requests.post(url, headers=HEADERS)
    plantillas = {}
    if response.status_code == 200:
        resultados = response.json().get("results", [])
        for page in resultados:
            props = page["properties"]
            try:
                nombre = props["Nombre"]["title"][0]["text"]["content"]
                contenido = props["Contenido"]["rich_text"][0]["text"]["content"]
                plantillas[nombre] = contenido
            except (KeyError, IndexError):
                continue
    return plantillas

def guardar_plantilla_notion(nombre, contenido):
    url = "https://api.notion.com/v1/pages"
    data = {
        "parent": {"database_id": DB_PLANTILLAS_ID},
        "properties": {
            "Nombre": {"title": [{"text": {"content": nombre}}]},
            "Contenido": {"rich_text": [{"text": {"content": contenido}}]}
        }
    }
    response = requests.post(url, headers=HEADERS, json=data)
    
    # Imprime el error exacto en Streamlit si falla la conexión a Notion
    if response.status_code != 200:
        st.error(f"Detalle del error de Notion: {response.text}") 
        
    return response.status_code == 200

# --- 1. SISTEMA DE AUTENTICACIÓN ---
if 'autenticado' not in st.session_state:
# ... (de aquí en adelante el código sigue igual) ...
