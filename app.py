import streamlit as st
import requests
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN Y SECRETOS ---
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
                page_id = page["id"]
                
                fragmentos_texto = props["Contenido"]["rich_text"]
                contenido = "".join([frag["text"]["content"] for frag in fragmentos_texto])
                
                categoria = "Sin categoría"
                if "Categoría" in props and props["Categoría"].get("select"):
                    categoria = props["Categoría"]["select"]["name"]
                    
                plantillas[nombre] = {
                    "id": page_id,
                    "contenido": contenido,
                    "categoria": categoria
                }
            except (KeyError, IndexError):
                continue
    return plantillas

def guardar_o_actualizar_plantilla(nombre, contenido, categoria, page_id=None):
    fragmentos = [contenido[i:i+2000] for i in range(0, len(contenido), 2000)]
    arreglo_rich_text = [{"text": {"content": frag}} for frag in fragmentos]
    
    propiedades = {
        "Nombre": {"title": [{"text": {"content": nombre}}]},
        "Contenido": {"rich_text": arreglo_rich_text},
        "Categoría": {"select": {"name": categoria}}
    }

    if page_id:
        url = f"https://api.notion.com/v1/pages/{page_id}"
        data = {"properties": propiedades}
        response = requests.patch(url, headers=HEADERS, json=data)
    else:
        url = "https://api.notion.com/v1/pages"
        data = {
            "parent": {"database_id": DB_PLANTILLAS_ID},
            "properties": propiedades
        }
        response = requests.post(url, headers=HEADERS, json=data)
        
    if response.status_code != 200:
        st.error(f"Error de Notion: {response.text}")
    return response.status_code == 200

def calcular_periodos(fecha_inicio):
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
        st.error(f"Error al crear la clase: {response.text}")
    return response.status_code == 200

# --- 3. INTERFAZ VISUAL DE STREAMLIT ---

st.set_page_config(page_title="Gestor INED", layout="wide")
st.title("🎓 Sistema de Gestión Administrativa")

plantillas_disponibles = cargar_plantillas_notion()

tab1, tab2, tab3 = st.tabs(["🚀 Crear Nueva Clase", "📚 Gestor de Plantillas", "📋 Mi Panel de Clases"])

with tab1:
    st.header("1. Tipo de Proceso")
    tipo_clase = st.radio("¿Qué tipo de mensajes vas a preparar?", ["Placement Test", "Intensivo"], horizontal=True)
    
    st.divider()
    st.header("2. Llenar Datos Generales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nombre_clase = st.text_input("Nombre de la Clase", placeholder="Ej: CLASS 247")
        horario = st.text_input("Horario de la Clase", placeholder="Ej: 19:00 a 21:00")
        link_grabaciones = st.text_input("Enlace de Clases Grabadas", placeholder="Ej: https://drive.google.com/...")
        
    with col2:
        fecha_inicio = st.date_input("Fecha de Inicio (Módulo 1)")
        # El Docente solo se pide en Intensivo
        if tipo_clase == "Intensivo":
            docente = st.text_input("Nombre del Docente", placeholder="Ej: Teacher Jordy Chafuel")

    st.divider()
    st.header(f"3. Datos Específicos para {tipo_clase}")
    
    col3, col4 = st.columns(2)
    
    if tipo_clase == "Placement Test":
        with col3:
            fecha_test = st.date_input("Fecha del Test de Ubicación")
            horario_test = st.text_input("Horario del Test", placeholder="Ej: 09:00 a.m. a 11:00 a.m.")
            clave_test = st.text_input("Clave del Test", placeholder="Ej: INED2026")
        with col4:
            link_test = st.text_input("Enlace del Test (Google Forms)", placeholder="Ej: https://forms.gle/abc123xyz")
            fecha_speaking = st.text_input("Fecha Límite Speaking", placeholder="Ej: VIERNES 23 DE OCTUBRE")
            
    elif tipo_clase == "Intensivo":
        with col3:
            fecha_examen_escrito = st.text_input("Fecha Examen Escrito", placeholder="Ej: JUEVES 22 DE OCTUBRE")
            fecha_speaking = st.text_input("Fecha Límite Speaking", placeholder="Ej: VIERNES 23 DE OCTUBRE")
            fecha_recordatorio_speaking = st.text_input("Fecha Recordatorio Speaking", placeholder="Ej: MIÉRCOLES 21 DE OCTUBRE")
            fecha_cartas_aprobacion = st.text_input("Fecha Cartas de Aprobación", placeholder="Ej: LUNES 26 DE OCTUBRE")
            fecha_resultados = st.date_input("Fecha de Resultados")
            fecha_fin = st.date_input("Fecha Fin de Módulo")
            
        with col4:
            clave_examenes = st.text_input("Clave de los Exámenes", placeholder="Ej: INED-B2")
            link_listening = st.text_input("Enlace Listening", placeholder="Ej: https://forms.gle/...")
            link_reading = st.text_input("Enlace Reading", placeholder="Ej: https://forms.gle/...")
            link_writing = st.text_input("Enlace Writing", placeholder="Ej: https://forms.gle/...")

    st.divider()
    st.header("4. Generar y Enviar a Notion")
    
    if not plantillas_disponibles:
        st.warning("No hay plantillas. Crea una en el 'Gestor de Plantillas'.")
    else:
        nombres_filtrados = [
            nombre for nombre, datos in plantillas_disponibles.items() 
            if datos["categoria"] == tipo_clase
        ]
        
        plantillas_seleccionadas = st.multiselect(
            f"Mensajes de {tipo_clase} disponibles:", 
            nombres_filtrados
        )
        
        if st.button("✨ Procesar y Crear Clase en Notion", type="primary"):
            if not nombre_clase:
                st.error("El nombre de la clase es obligatorio.")
            elif not plantillas_seleccionadas:
                st.error("Selecciona al menos un mensaje.")
            else:
                with st.spinner("Calculando periodos académicos y empaquetando clase..."):
                    mensajes_finales = {}
                    for nombre_plantilla in plantillas_seleccionadas:
                        texto_base = plantillas_disponibles[nombre_plantilla]["contenido"]
                        
                        # Reemplazo de variables GENERALES (Ambos casos)
                        texto_proc = texto_base.replace("[CLASE]", nombre_clase)
                        texto_proc = texto_proc.replace("[HORARIO]", horario)
                        texto_proc = texto_proc.replace("[LINK_GRABACIONES]", link_grabaciones)
                        
                        # Reemplazo para PLACEMENT TEST
                        if tipo_clase == "Placement Test":
                            texto_proc = texto_proc.replace("[FECHA_TEST]", fecha_test.strftime('%d/%m/%Y'))
                            texto_proc = texto_proc.replace("[HORARIO_TEST]", horario_test)
                            texto_proc = texto_proc.replace("[LINK_TEST]", link_test)
                            texto_proc = texto_proc.replace("[CLAVE_TEST]", clave_test)
                            texto_proc = texto_proc.replace("[FECHA_SPEAKING]", fecha_speaking)
                            
                        # Reemplazo para INTENSIVO
                        elif tipo_clase == "Intensivo":
                            texto_proc = texto_proc.replace("[DOCENTE]", docente)
                            texto_proc = texto_proc.replace("[FECHA_FIN]", fecha_fin.strftime('%d/%m/%Y'))
                            texto_proc = texto_proc.replace("[FECHA_EXAMEN_ESCRITO]", fecha_examen_escrito)
                            texto_proc = texto_proc.replace("[FECHA_SPEAKING]", fecha_speaking)
                            texto_proc = texto_proc.replace("[FECHA_RECORDATORIO_SPEAKING]", fecha_recordatorio_speaking)
                            texto_proc = texto_proc.replace("[FECHA_CARTAS_APROBACION]", fecha_cartas_aprobacion)
                            texto_proc = texto_proc.replace("[FECHA_RESULTADOS]", fecha_resultados.strftime('%d/%m/%Y'))
                            texto_proc = texto_proc.replace("[LINK_LISTENING]", link_listening)
                            texto_proc = texto_proc.replace("[LINK_READING]", link_reading)
                            texto_proc = texto_proc.replace("[LINK_WRITING]", link_writing)
                            texto_proc = texto_proc.replace("[CLAVE_EXAMENES]", clave_examenes)
                        
                        mensajes_finales[nombre_plantilla] = texto_proc
                    
                    if crear_clase_en_notion(nombre_clase, fecha_inicio, mensajes_finales):
                        st.success(f"¡{nombre_clase} creada exitosamente en Notion con todos sus módulos calculados!")
                        st.balloons()

with tab2:
    st.header("Biblioteca de Plantillas")
    
    total = len(plantillas_disponibles)
    total_test = sum(1 for p in plantillas_disponibles.values() if p["categoria"] == "Placement Test")
    total_intensivo = sum(1 for p in plantillas_disponibles.values() if p["categoria"] == "Intensivo")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Plantillas", total)
    col2.metric("Placement Test", total_test)
    col3.metric("Intensivo", total_intensivo)
    
    st.divider()
    
    opciones_edicion = ["➕ Crear nueva plantilla"] + list(plantillas_disponibles.keys())
    seleccion = st.selectbox("Selecciona una plantilla para editar o crea una nueva:", opciones_edicion)
    
    if seleccion == "➕ Crear nueva plantilla":
        st.subheader("Nueva Plantilla")
        nombre_actual = ""
        texto_actual = ""
        categoria_actual = "Placement Test"
        id_actual = None
    else:
        st.subheader(f"Editando: {seleccion}")
        nombre_actual = seleccion
        texto_actual = plantillas_disponibles[seleccion]["contenido"]
        categoria_actual = plantillas_disponibles[seleccion]["categoria"]
        id_actual = plantillas_disponibles[seleccion]["id"]

    nuevo_nombre = st.text_input("Nombre de la plantilla:", value=nombre_actual)
    lista_categorias = ["Placement Test", "Intensivo", "Sin categoría"]
    indice_categoria = lista_categorias.index(categoria_actual) if categoria_actual in lista_categorias else 0
    nueva_categoria = st.selectbox("Categoría:", lista_categorias, index=indice_categoria)
    nuevo_texto = st.text_area("Cuerpo del mensaje:", value=texto_actual, height=300)
    
    if st.button("💾 Guardar / Actualizar Plantilla"):
        if nuevo_nombre and nuevo_texto:
            if guardar_o_actualizar_plantilla(nuevo_nombre, nuevo_texto, nueva_categoria, id_actual):
                st.success("Cambios guardados correctamente. Recarga la página para ver la actualización.")
        else:
            st.warning("Completa el nombre y el contenido.")

with tab3:
    st.header("Lectura de Clases")
    st.info("🚧 Área en construcción. Aquí conectaremos la visualización del Checklist y los mensajes de tus clases creadas.")
