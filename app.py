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
    fragmentos = [contenido[i:i+1800] for i in range(0, len(contenido), 1800)]
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
        fragmentos = [contenido[i:i+1800] for i in range(0, len(contenido), 1800)]
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

def cargar_clases_notion():
    url = f"https://api.notion.com/v1/databases/{DB_CLASES_ID}/query"
    response = requests.post(url, headers=HEADERS)
    clases = {}
    if response.status_code == 200:
        resultados = response.json().get("results", [])
        for page in resultados:
            props = page["properties"]
            try:
                nombre = props["Nombre"]["title"][0]["text"]["content"]
                page_id = page["id"]
                
                modulos = {}
                for i in range(1, 6):
                    mod_name = f"Módulo {i}"
                    if mod_name in props and props[mod_name]["rich_text"]:
                        modulos[mod_name] = props[mod_name]["rich_text"][0]["text"]["content"]
                    else:
                        modulos[mod_name] = "Sin fecha"
                
                # Escáner ajustado para columnas tipo Selección (Select)
                checklist = {}
                # Excluimos "Categoría" por si existe en esta tabla, aunque es poco probable
                columnas_ignoradas = ["Categoría"] 
                
                for prop_name, prop_data in props.items():
                    if prop_data["type"] == "select" and prop_name not in columnas_ignoradas:
                        # Si está vacío (None), lo consideramos "No empezado" por defecto
                        if prop_data["select"] is None:
                            estado_actual = "No empezado"
                        else:
                            estado_actual = prop_data["select"]["name"]
                        checklist[prop_name] = estado_actual
                        
                clases[nombre] = {
                    "id": page_id,
                    "modulos": modulos,
                    "checklist": checklist
                }
            except (KeyError, IndexError):
                continue
    return clases

def actualizar_checklist_notion(page_id, nuevos_valores):
    propiedades = {}
    for nombre_columna, nuevo_estado in nuevos_valores.items():
        # Formato correcto para enviar a una propiedad tipo 'Select'
        propiedades[nombre_columna] = {"select": {"name": nuevo_estado}}
        
    url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {"properties": propiedades}
    response = requests.patch(url, headers=HEADERS, json=data)
    
    if response.status_code != 200:
        st.error(f"Error al actualizar estado: {response.text}")
    return response.status_code == 200

def obtener_contenido_clase(page_id):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.get(url, headers=HEADERS)
    contenido = []
    if response.status_code == 200:
        blocks = response.json().get("results", [])
        
        texto_acumulado = ""
        titulo_actual = ""
        
        for block in blocks:
            tipo = block["type"]
            if tipo in ["paragraph", "heading_3"]:
                try:
                    text_elements = block[tipo]["rich_text"]
                    text = "".join([t["text"]["content"] for t in text_elements])
                    
                    if tipo == "heading_3":
                        if titulo_actual:
                            contenido.append({"titulo": titulo_actual, "texto": texto_acumulado.strip()})
                        titulo_actual = text
                        texto_acumulado = ""
                    else:
                        texto_acumulado += text + "\n"
                except (KeyError, IndexError):
                    pass
                    
        if titulo_actual:
            contenido.append({"titulo": titulo_actual, "texto": texto_acumulado.strip()})
            
    return contenido

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
        nombre_clase = st.text_input("Nombre de la Clase", placeholder="Ej: Clase #245 - 5to nivel")
        horario = st.text_input("Horario de la Clase", placeholder="Ej: 7-9 p.m.")
        link_grabaciones = st.text_input("Enlace de Clases Grabadas", placeholder="Ej: https://drive.google.com/drive/folders/...")
        
    with col2:
        fecha_inicio = st.date_input("Fecha de Inicio (Módulo 1)")
        
        if tipo_clase == "Intensivo":
            docente = st.text_input("Nombre del Docente", placeholder="Ej: Jordy Chafuel")

    st.divider()
    st.header(f"3. Datos Específicos para {tipo_clase}")
    
    col3, col4 = st.columns(2)
    
    if tipo_clase == "Placement Test":
        with col3:
            fecha_test = st.text_input("Fecha del Test de Ubicación", placeholder="Ej: Sábado 01 de agosto, 2026")
            horario_test = st.text_input("Horario del Test", placeholder="Ej: 09:00 a.m. a 11:00 a.m.")
            clave_test = st.text_input("Clave del Test", placeholder="Ej: EXTES2026@T45")
        with col4:
            link_test = st.text_input("Enlace del Test", placeholder="Ej: https://forms.gle/SASU5kbDcccJwEtZ6")
            fecha_speaking = st.text_input("Fecha Límite Speaking", placeholder="Ej: MIÉRCOLES 26 DE AGOSTO 2026- 3PM")
            
    elif tipo_clase == "Intensivo":
        with col3:
            fecha_examen_escrito = st.text_input("Fecha Examen Escrito", placeholder="Ej: JUEVES 27 DE AGOSTO, 2026 - DE 7-9 PM")
            fecha_speaking = st.text_input("Fecha Límite Speaking", placeholder="Ej: MIÉRCOLES 26 DE AGOSTO 2026- 3PM")
            fecha_recordatorio_speaking = st.text_input("Fecha Recordatorio Speaking", placeholder="Ej: miércoles 26 de agosto a las 15:00 p.m")
            fecha_cartas_aprobacion = st.text_input("Fecha Cartas de Aprobación", placeholder="Ej: SÁBADO 29 DE AGOSTO, 2026")
            fecha_fin = st.text_input("Fecha Fin de Módulo", placeholder="Ej: 28 de agosto de 2026")
            fecha_resultados = st.text_input("Fecha de Resultados", placeholder="Ej: SÁBADO 29 DE AGOSTO, 2026")
            
        with col4:
            clave_examenes = st.text_input("Clave de los Exámenes", placeholder="Ej: TEX2026@45AG")
            link_listening = st.text_input("Enlace Listening", placeholder="Ej: https://forms.gle/roJLHkFabytkiGeaA")
            link_reading = st.text_input("Enlace Reading", placeholder="Ej: https://forms.gle/gBpatS6KdBXFxLuG9")
            link_writing = st.text_input("Enlace Writing", placeholder="Ej: https://forms.gle/mevqAwMfQoRQ1CDj9")

    st.divider()
    st.header("4. Generar y Enviar a Notion")
    
    if not plantillas_disponibles:
        st.warning("No hay plantillas. Crea una en el 'Gestor de Plantillas'.")
    else:
        nombres_filtrados = [
            nombre for nombre, datos in plantillas_disponibles.items() 
            if datos["categoria"] == tipo_clase
        ]
        
        if not nombres_filtrados:
            st.info(f"No hay plantillas con la categoría '{tipo_clase}'. Ve a la Pestaña 2 y actualiza la categoría de tus plantillas guardadas.")
        else:
            modo_seleccion = st.radio("Opciones de generación:", ["Seleccionar todos los mensajes automáticamente", "Elegir mensajes manualmente"])
            
            if modo_seleccion == "Seleccionar todos los mensajes automáticamente":
                plantillas_seleccionadas = nombres_filtrados
                st.success(f"Se generarán todos los {len(nombres_filtrados)} mensajes disponibles para {tipo_clase}.")
            else:
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
                            
                            texto_proc = texto_base.replace("[CLASE]", nombre_clase)
                            texto_proc = texto_proc.replace("[HORARIO]", horario)
                            texto_proc = texto_proc.replace("[LINK_GRABACIONES]", link_grabaciones)
                            
                            if tipo_clase == "Placement Test":
                                texto_proc = texto_proc.replace("[FECHA_TEST]", fecha_test)
                                texto_proc = texto_proc.replace("[HORARIO_TEST]", horario_test)
                                texto_proc = texto_proc.replace("[LINK_TEST]", link_test)
                                texto_proc = texto_proc.replace("[CLAVE_TEST]", clave_test)
                                texto_proc = texto_proc.replace("[FECHA_SPEAKING]", fecha_speaking)
                                
                            elif tipo_clase == "Intensivo":
                                texto_proc = texto_proc.replace("[DOCENTE]", docente)
                                texto_proc = texto_proc.replace("[FECHA_FIN]", fecha_fin)
                                texto_proc = texto_proc.replace("[FECHA_EXAMEN_ESCRITO]", fecha_examen_escrito)
                                texto_proc = texto_proc.replace("[FECHA_SPEAKING]", fecha_speaking)
                                texto_proc = texto_proc.replace("[FECHA_RECORDATORIO_SPEAKING]", fecha_recordatorio_speaking)
                                texto_proc = texto_proc.replace("[FECHA_CARTAS_APROBACION]", fecha_cartas_aprobacion)
                                texto_proc = texto_proc.replace("[FECHA_RESULTADOS]", fecha_resultados)
                                texto_proc = texto_proc.replace("[LINK_LISTENING]", link_listening)
                                texto_proc = texto_proc.replace("[LINK_READING]", link_reading)
                                texto_proc = texto_proc.replace("[LINK_WRITING]", link_writing)
                                texto_proc = texto_proc.replace("[CLAVE_EXAMENES]", clave_examenes)
                            
                            mensajes_finales[nombre_plantilla] = texto_proc
                        
                        if crear_clase_en_notion(nombre_clase, fecha_inicio, mensajes_finales):
                            st.success(f"¡{nombre_clase} guardada correctamente en Notion!")

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
    st.header("📋 Lectura y Panel de Clases")
    st.markdown("Selecciona una clase creada para ver sus módulos, actualizar su documentación y copiar sus mensajes.")
    
    clases_disponibles = cargar_clases_notion()
    
    if not clases_disponibles:
        st.info("Aún no hay clases registradas en tu Base de Datos. Ve a la Pestaña 1 para crear la primera.")
    else:
        clase_seleccionada = st.selectbox("Selecciona una clase para revisar:", list(clases_disponibles.keys()))
        
        if clase_seleccionada:
            datos_clase = clases_disponibles[clase_seleccionada]
            
            st.subheader("📅 Cronograma de Módulos")
            cols = st.columns(5)
            for i in range(1, 6):
                mod_name = f"Módulo {i}"
                cols[i-1].metric(label=mod_name, value="", delta=datos_clase["modulos"][mod_name], delta_color="off")
            
            st.divider()
            
            # --- SECCIÓN: CHECKLIST DE SELECCIÓN (SELECT) ---
            st.subheader("✅ Estado de Documentación")
            checklist_actual = datos_clase.get("checklist", {})
            
            if not checklist_actual:
                st.info("No se encontraron columnas de tipo 'Selección' (Select) en tu base de datos de Clases.")
            else:
                with st.form(key=f"form_checklist_{datos_clase['id']}"):
                    nuevos_valores = {}
                    cols_chk = st.columns(3)
                    
                    opciones_estado = ["No empezado", "En proceso", "Listo"]
                    
                    idx = 0
                    for nombre_item, estado_actual in checklist_actual.items():
                        with cols_chk[idx % 3]:
                            if estado_actual not in opciones_estado:
                                opciones_dinamicas = [estado_actual] + opciones_estado
                            else:
                                opciones_dinamicas = opciones_estado
                                
                            index_actual = opciones_dinamicas.index(estado_actual)
                            nuevos_valores[nombre_item] = st.selectbox(nombre_item, options=opciones_dinamicas, index=index_actual)
                        idx += 1
                        
                    if st.form_submit_button("💾 Guardar Cambios en Notion"):
                        if actualizar_checklist_notion(datos_clase["id"], nuevos_valores):
                            st.success("¡Estados actualizados correctamente! Recarga la pestaña para confirmar.")
                            
            st.divider()
            
            # --- SECCIÓN: MENSAJES ---
            st.subheader("💬 Mensajes Generados")
            
            with st.spinner("Descargando mensajes desde Notion..."):
                contenido_clase = obtener_contenido_clase(datos_clase["id"])
                
                if not contenido_clase:
                    st.warning("No se encontraron mensajes guardados dentro de esta clase.")
                else:
                    for bloque in contenido_clase:
                        st.markdown(f"**{bloque['titulo']}**")
                        st.code(bloque['texto'], language="text")
                        st.write("")
