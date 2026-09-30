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
                
                # Cargar el texto
                fragmentos_texto = props["Contenido"]["rich_text"]
                contenido = "".join([frag["text"]["content"] for frag in fragmentos_texto])
                
                # Cargar la categoría (si existe)
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
        # Actualizar plantilla existente
        url = f"https://api.notion.com/v1/pages/{page_id}"
        data = {"properties": propiedades}
        response = requests.patch(url, headers=HEADERS, json=data)
    else:
        # Crear plantilla nueva
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
    # Este selector controla qué campos adicionales se muestran
    tipo_clase = st.radio("¿Qué tipo de mensajes vas a preparar?", ["Placement Test", "Intensivo"], horizontal=True)
    
    st.divider()
    st.header("2. Llenar Datos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Los placeholders guían visualmente a cualquier usuario del sistema
        nombre_clase = st.text_input("Nombre de la Clase", placeholder="Ej: CLASS 247")
        docente = st.text_input("Nombre del Docente", placeholder="Ej: Teacher Jordy Chafuel")
        horario = st.text_input("Horario de la Clase", placeholder="Ej: 19:00 a 21:00")
        
    with col2:
        fecha_inicio = st.date_input("Fecha de Inicio (Módulo 1)")
        
        # Lógica dinámica: Los campos del test SOLO aparecen si se elige 'Placement Test'
        if tipo_clase == "Placement Test":
            fecha_test = st.date_input("Fecha del Test de Ubicación")
            horario_test = st.text_input("Horario del Test", placeholder="Ej: 09:00 a.m. a 11:00 a.m.")
            link_test = st.text_input("Enlace del Test (Google Forms)", placeholder="Ej: https://forms.gle/abc123xyz")
            clave_test = st.text_input("Clave del Test", placeholder="Ej: INED2026")
            fecha_speaking = st.date_input("Fecha Límite Speaking")

    st.divider()
    st.header("3. Generar y Enviar a Notion")
    
    if not plantillas_disponibles:
        st.warning("No hay plantillas. Crea una en el 'Gestor de Plantillas'.")
    else:
        # Filtramos automáticamente las plantillas según el tipo de proceso elegido arriba
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
                        
                        # Reemplazo de variables generales (Siempre presentes)
                        texto_proc = texto_base.replace("[CLASE]", nombre_clase)
                        texto_proc = texto_proc.replace("[DOCENTE]", docente)
                        texto_proc = texto_proc.replace("[HORARIO]", horario)
                        
                        # Reemplazo de variables específicas (Solo si es Placement Test)
                        if tipo_clase == "Placement Test":
                            texto_proc = texto_proc.replace("[FECHA_TEST]", fecha_test.strftime('%d/%m/%Y'))
                            texto_proc = texto_proc.replace("[HORARIO_TEST]", horario_test)
                            texto_proc = texto_proc.replace("[LINK_TEST]", link_test)
                            texto_proc = texto_proc.replace("[CLAVE_TEST]", clave_test)
                            texto_proc = texto_proc.replace("[FECHA_SPEAKING]", fecha_speaking.strftime('%d/%m/%Y'))
                        
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
