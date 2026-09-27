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
    
    if response.status_code != 200:
        # Esto imprimirá el error real en Streamlit
        st.error(f"Detalle del error de Notion: {response.text}") 
        
    return response.status_code == 200

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
    return response.status_code == 200

# --- 1. SISTEMA DE AUTENTICACIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acceso Restringido - INED")
    pwd = st.text_input("Contraseña:", type="password")
    if st.button("Entrar"):
        if pwd == "ined2026":  
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Credencial incorrecta.")
    st.stop()

# --- 2. CARGA DE BASE DE DATOS EN MEMORIA ---
if 'plantillas' not in st.session_state:
    # Intenta cargar desde Notion; si falla, pone unas de ejemplo
    plantillas_notion = cargar_plantillas_notion()
    if plantillas_notion:
        st.session_state['plantillas'] = plantillas_notion
    else:
        st.session_state['plantillas'] = {
            "Plantilla de Ejemplo": "Conecta Notion para ver tus plantillas reales. [CLASE]"
        }

# --- 3. INTERFAZ PRINCIPAL ---
st.title("⚙️ INED Workspace & Automation")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state['autenticado'] = False
    st.rerun()

tab1, tab2, tab3 = st.tabs(["💬 Mensajería Editable", "📅 Calendario de Módulos", "📋 Checklist de Documentos"])

# --- PESTAÑA 1: MENSAJERÍA ---
with tab1:
    st.header("Librería de Plantillas y Generador")
    st.subheader("1. Variables Generales")
    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        clase_id = st.text_input("ID de la Clase:", "CLASS 245 - 5to nivel")
    with col_g2:
        docente = st.text_input("Nombre del Docente:", "Jordy Chafuel")
    with col_g3:
        horario = st.text_input("Horario:", "7-9 p.m.")

    reemplazos = {"[CLASE]": clase_id, "[DOCENTE]": docente, "[HORARIO]": horario}
    st.divider()

    flujo = st.radio("Selecciona el proceso para cargar las variables específicas:", ["Test de Ubicación", "Curso Intensivo"], horizontal=True)

    if flujo == "Test de Ubicación":
        col1, col2 = st.columns(2)
        with col1:
            fecha_test = st.text_input("Fecha del Test:", "Sábado 01 de agosto, 2026")
            horario_test = st.text_input("Horario del Test:", "09:00 a.m. a 11:00 a.m.")
            fecha_speaking = st.text_input("Fecha Límite Speaking:", "Viernes 31 de julio 2026, 09:00 a.m.")
        with col2:
            link_clases = st.text_input("Enlace Clases Grabadas:", "https://drive.google.com/...")
            link_test = st.text_input("Enlace del Test:", "https://forms.gle/...")
            clave_test = st.text_input("Clave del Test:", "EXTES2026@T45")
            
        reemplazos.update({
            "[FECHA_TEST]": fecha_test, "[HORARIO_TEST]": horario_test, "[FECHA_SPEAKING]": fecha_speaking,
            "[LINK_CLASES]": link_clases, "[LINK_TEST]": link_test, "[CLAVE_TEST]": clave_test
        })
    else:
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.text_input("Fecha Inicio:", "03 de agosto")
            fecha_fin = st.text_input("Fecha Fin:", "28 de agosto")
            fecha_escrito = st.text_input("Fecha Examen Escrito:", "JUEVES 27 DE AGOSTO, 2026 - DE 7-9 PM")
            fecha_speaking_int = st.text_input("Límite Speaking:", "MIÉRCOLES 26 DE AGOSTO 2026 - 3PM")
            fecha_resultados = st.text_input("Fecha Resultados:", "SÁBADO 29 DE AGOSTO, 2026")
        with col2:
            link_clases_int = st.text_input("Enlace Clases Grabadas:", "https://drive.google.com/...")
            link_listening = st.text_input("Link Listening:", "https://forms.gle/...")
            link_reading = st.text_input("Link Reading:", "https://forms.gle/...")
            link_writing = st.text_input("Link Writing:", "https://forms.gle/...")
            clave_general = st.text_input("Clave General Exámenes:", "TEX2026@45AG")
            
        reemplazos.update({
            "[FECHA_INICIO]": fecha_inicio, "[FECHA_FIN]": fecha_fin, "[FECHA_ESCRITO]": fecha_escrito,
            "[FECHA_SPEAKING]": fecha_speaking_int, "[FECHA_RESULTADOS]": fecha_resultados,
            "[LINK_CLASES]": link_clases_int, "[LINK_LISTENING]": link_listening,
            "[LINK_READING]": link_reading, "[LINK_WRITING]": link_writing, "[CLAVE_GENERAL]": clave_general
        })

    st.divider()

    st.subheader("2. Editor y Gestor de Plantillas")
    nombres_plantillas = list(st.session_state['plantillas'].keys())
    if nombres_plantillas:
        seleccion = st.selectbox("Selecciona la plantilla a utilizar:", nombres_plantillas)
        texto_a_editar = st.text_area("Editor de Plantilla:", value=st.session_state['plantillas'][seleccion], height=300)
        
        col_proc, col_act = st.columns(2)
        with col_proc:
            if st.button("🚀 Procesar Mensaje", type="primary"):
                resultado = texto_a_editar
                for etiqueta, valor in reemplazos.items():
                    resultado = resultado.replace(etiqueta, valor)
                st.success("¡Texto listo para enviar!")
                st.text_area("Copia este texto para WhatsApp:", value=resultado, height=300)
                
        with col_act:
            if st.button("💾 Guardar cambios en Notion"):
                if guardar_plantilla_notion(seleccion, texto_a_editar):
                    st.session_state['plantillas'][seleccion] = texto_a_editar
                    st.success(f"Plantilla '{seleccion}' actualizada en Notion.")
                else:
                    st.error("Error al conectar con Notion. Verifica tu Token y el ID.")
    else:
        st.warning("No hay plantillas. Crea una abajo o revisa tu conexión a Notion.")

    st.divider()
    with st.expander("➕ Crear Nueva Plantilla"):
        nuevo_nombre = st.text_input("Nombre de la nueva plantilla (Ej: Recordatorio B1):")
        nuevo_texto = st.text_area("Escribe el texto base con etiquetas:", height=200)
        
        if st.button("Guardar en Notion y Librería"):
            if nuevo_nombre and nuevo_texto:
                if guardar_plantilla_notion(nuevo_nombre, nuevo_texto):
                    st.session_state['plantillas'][nuevo_nombre] = nuevo_texto
                    st.success("Plantilla guardada permanentemente.")
                    st.rerun()
                else:
                    st.error("Error al guardar en Notion.")

# --- PESTAÑA 2: CALENDARIO ---
with tab2:
    st.header("Calculadora de Periodos Académicos")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        fecha_inicio_ultimo = st.date_input("Fecha de Inicio (Último periodo):", value=datetime(2026, 10, 5).date())
    with col_c2:
        fecha_fin_calculada = fecha_inicio_ultimo + timedelta(days=25)
        st.date_input("Fecha de Finalización (Calculada):", value=fecha_fin_calculada, disabled=True)
        
    if st.button("Generar Tabla de Periodos"):
        periodos = []
        inicio_nivel_1 = fecha_inicio_ultimo - timedelta(days=28 * 4)
        for i in range(1, 6):
            inicio_mod = inicio_nivel_1 + timedelta(days=28 * (i - 1))
            fin_mod = inicio_mod + timedelta(days=25)
            
            inicio_str = inicio_mod.strftime("%B %d, %Y").replace(" 0", " ")
            fin_str = fin_mod.strftime("%B %d, %Y").replace(" 0", " ")
            periodos.append({"Periodo": f"{i}.", "Fecha de Inicio": inicio_str, "Fecha de Finalización": fin_str})
        st.table(periodos)

# --- PESTAÑA 3: CHECKLIST Y NOTION ---
with tab3:
    st.header("Flujo de Documentación")
    st.write("Sincronización con tablero Kanban en construcción (Requiere configurar base de datos Checklist).")
    estados = ["Iniciado", "En proceso", "En revisión", "2da revisión", "Terminado"]
    documentos = ["Statements", "Certificates", "Id1", "Id2", "Carta de Ubicación", "Carta de Aprobación", "Actas", "Data Base", "Notas", "Best Student (1)"]
    for doc in documentos:
        col_doc, col_estado = st.columns([3, 2])
        with col_doc:
            st.markdown(f"**{doc}**")
        with col_estado:
            st.selectbox("Estado", estados, key=doc, label_visibility="collapsed")
