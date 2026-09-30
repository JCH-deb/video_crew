import streamlit as st
import requests
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN Y SECRETOS ---
# Recuerda que en st.secrets debes tener NOTION_TOKEN, DB_PLANTILLAS_ID y DB_CLASES_ID
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DB_PLANTILLAS_ID = st.secrets["DB_PLANTILLAS_ID"]
DB_CLASES_ID = st.secrets["DB_CLASES_ID"]

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# --- 2. FUNCIONES DE CONEXIÓN CON NOTION ---

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
                fragmentos_texto = props["Contenido"]["rich_text"]
                contenido = "".join([frag["text"]["content"] for frag in fragmentos_texto])
                plantillas[nombre] = contenido
            except (KeyError, IndexError):
                continue
    return plantillas

def guardar_plantilla_notion(nombre, contenido):
    url = "https://api.notion.com/v1/pages"
    fragmentos = [contenido[i:i+2000] for i in range(0, len(contenido), 2000)]
    arreglo_rich_text = [{"text": {"content": frag}} for frag in fragmentos]
    
    data = {
        "parent": {"database_id": DB_PLANTILLAS_ID},
        "properties": {
            "Nombre": {"title": [{"text": {"content": nombre}}]},
            "Contenido": {"rich_text": arreglo_rich_text}
        }
    }
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code != 200:
        st.error(f"Error al guardar plantilla en Notion: {response.text}")
    return response.status_code == 200

def calcular_periodos(fecha_inicio):
    # Calculamos 28 días (4 semanas exactas) por cada módulo
    modulos = {}
    fecha_actual = fecha_inicio
    for i in range(1, 6):
        fecha_fin = fecha_actual + timedelta(days=28)
        modulos[f"Módulo {i}"] = f"Del {fecha_actual.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}"
        fecha_actual = fecha_fin + timedelta(days=1)
    return modulos

def crear_clase_en_notion(nombre_clase, fecha_inicio, mensajes_procesados):
    url = "https://api.notion.com/v1/pages"
    periodos = calcular_periodos(fecha_inicio)
    
    data = {
        "parent": {"database_id": DB_CLASES_ID},
        "properties": {
            "Nombre": {"title": [{"text": {"content": nombre_clase}}]},
            "Módulo 1": {"rich_text": [{"text": {"content": periodos["Módulo 1"]}}]},
            "Módulo 2": {"rich_text": [{"text": {"content": periodos["Módulo 2"]}}]},
            "Módulo 3": {"rich_text": [{"text": {"content": periodos["Módulo 3"]}}]},
            "Módulo 4": {"rich_text": [{"text": {"content": periodos["Módulo 4"]}}]},
            "Módulo 5": {"rich_text": [{"text": {"content": periodos["Módulo 5"]}}]},
        },
        "children": []
    }
    
    # Inyectar los mensajes generados en el interior de la página
    for titulo, contenido in mensajes_procesados.items():
        data["children"].append({
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [{"text": {"content": f"Mensaje: {titulo}"}}]}
        })
        fragmentos = [contenido[i:i+2000] for i in range(0, len(contenido), 2000)]
        for frag in fragmentos:
            data["children"].append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": frag}}]}
            })
            
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code != 200:
        st.error(f"Error al crear la clase maestra: {response.text}")
    return response.status_code == 200

# --- 3. INTERFAZ VISUAL DE STREAMLIT ---

st.set_page_config(page_title="Gestor INED", layout="wide")
st.title("🎓 Sistema de Gestión Administrativa")

# Creamos 3 pestañas para organizar el trabajo
tab1, tab2, tab3 = st.tabs(["🚀 Crear Nueva Clase", "📚 Gestor de Plantillas", "📋 Mi Panel de Clases"])

with tab1:
    st.header("1. Datos Generales de la Clase")
    col1, col2 = st.columns(2)
    
    with col1:
        nombre_clase = st.text_input("Nombre de la Clase (Ej: CLASS 247)")
        docente = st.text_input("Nombre del Docente")
        horario = st.text_input("Horario de la Clase")
        link_clases = st.text_input("Enlace de las Clases (Zoom/Meet)")
        
    with col2:
        fecha_inicio = st.date_input("Fecha de Inicio (Arranque del Módulo 1)")
        fecha_test = st.date_input("Fecha del Test de Ubicación")
        horario_test = st.text_input("Horario del Test")
        link_test = st.text_input("Enlace del Test (Google Forms)")
        clave_test = st.text_input("Clave del Test")
        fecha_speaking = st.date_input("Fecha Límite para Speaking")

    st.divider()
    st.header("2. Seleccionar Mensajes a Generar")
    plantillas_disponibles = cargar_plantillas_notion()
    
    if not plantillas_disponibles:
        st.warning("No hay plantillas guardadas. Ve a la pestaña 'Gestor de Plantillas' para crear la primera.")
    else:
        # El usuario puede elegir varias plantillas a la vez
        plantillas_seleccionadas = st.multiselect(
            "Elige los mensajes que deseas preparar y guardar para esta clase:", 
            list(plantillas_disponibles.keys())
        )
        
        # Botón mágico para armar todo el paquete
        if st.button("✨ Procesar y Crear Clase Maestra en Notion", type="primary"):
            if not nombre_clase:
                st.error("⚠️ El nombre de la clase es obligatorio.")
            elif not plantillas_seleccionadas:
                st.error("⚠️ Selecciona al menos un mensaje para generar.")
            else:
                with st.spinner("Calculando periodos académicos y empaquetando clase..."):
                    mensajes_finales = {}
                    
                    for nombre_plantilla in plantillas_seleccionadas:
                        texto_base = plantillas_disponibles[nombre_plantilla]
                        
                        # Reemplazo de variables automáticas
                        texto_procesado = texto_base.replace("[CLASE]", nombre_clase)
                        texto_procesado = texto_procesado.replace("[DOCENTE]", docente)
                        texto_procesado = texto_procesado.replace("[HORARIO]", horario)
                        texto_procesado = texto_procesado.replace("[LINK_CLASES]", link_clases)
                        texto_procesado = texto_procesado.replace("[FECHA_TEST]", fecha_test.strftime('%d/%m/%Y'))
                        texto_procesado = texto_procesado.replace("[HORARIO_TEST]", horario_test)
                        texto_procesado = texto_procesado.replace("[LINK_TEST]", link_test)
                        texto_procesado = texto_procesado.replace("[CLAVE_TEST]", clave_test)
                        texto_procesado = texto_procesado.replace("[FECHA_SPEAKING]", fecha_speaking.strftime('%d/%m/%Y'))
                        
                        mensajes_finales[nombre_plantilla] = texto_procesado
                    
                    # Ejecutar la creación en la Base de Datos Maestra
                    exito = crear_clase_en_notion(nombre_clase, fecha_inicio, mensajes_finales)
                    
                    if exito:
                        st.success(f"¡Victoria! La {nombre_clase} ha sido creada en Notion con sus módulos calculados y mensajes almacenados.")
                        st.balloons()

with tab2:
    st.header("Administrar Biblioteca de Plantillas")
    st.markdown("Agrega nuevos modelos de mensajes usando las etiquetas oficiales (ej: `[CLASE]`, `[DOCENTE]`).")
    
    nueva_plantilla_nombre = st.text_input("Título descriptivo del mensaje:")
    nueva_plantilla_texto = st.text_area("Cuerpo del mensaje de WhatsApp:", height=250)
    
    if st.button("💾 Guardar Plantilla en Notion"):
        if nueva_plantilla_nombre and nueva_plantilla_texto:
            if guardar_plantilla_notion(nueva_plantilla_nombre, nueva_plantilla_texto):
                st.success(f"Plantilla '{nueva_plantilla_nombre}' lista para usarse.")
        else:
            st.warning("Completa ambos campos antes de guardar.")

with tab3:
    st.header("Lectura de Clases")
    st.info("🚧 Área en construcción. Aquí conectaremos la visualización para leer el Checklist y los mensajes directamente desde tu base maestra.")
