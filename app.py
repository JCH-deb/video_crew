import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# --- 1. CONFIGURACIÓN Y SECRETOS ---
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DB_PLANTILLAS_ID = st.secrets["DB_PLANTILLAS_ID"]
DB_CLASES_ID = st.secrets["DB_CLASES_ID"]
DB_ESTUDIANTES_ID = st.secrets["DB_ESTUDIANTES_ID"] 

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# --- 2. FUNCIONES DE CONEXIÓN CON NOTION (CLASES Y PLANTILLAS) ---

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
                plantillas[nombre] = {"id": page_id, "contenido": contenido, "categoria": categoria}
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
        response = requests.patch(url, headers=HEADERS, json={"properties": propiedades})
    else:
        url = "https://api.notion.com/v1/pages"
        data = {"parent": {"database_id": DB_PLANTILLAS_ID}, "properties": propiedades}
        response = requests.post(url, headers=HEADERS, json=data)
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
            "object": "block", "type": "heading_3",
            "heading_3": {"rich_text": [{"text": {"content": f"Mensaje: {titulo}"}}]}
        })
        fragmentos = [contenido[i:i+1800] for i in range(0, len(contenido), 1800)]
        for frag in fragmentos:
            data["children"].append({
                "object": "block", "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": frag}}]}
            })
    response = requests.post(url, headers=HEADERS, json=data)
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
                    modulos[mod_name] = props[mod_name]["rich_text"][0]["text"]["content"] if props.get(mod_name, {}).get("rich_text") else "Sin fecha"
                
                checklist = {}
                columnas_ignoradas = ["Categoría", "Estudiantes", "Alumnos"] 
                for prop_name, prop_data in props.items():
                    if prop_data["type"] == "select" and prop_name not in columnas_ignoradas:
                        checklist[prop_name] = prop_data["select"]["name"] if prop_data["select"] else "No empezado"
                        
                clases[nombre] = {"id": page_id, "modulos": modulos, "checklist": checklist}
            except (KeyError, IndexError):
                continue
    return clases

def actualizar_checklist_notion(page_id, nuevos_valores):
    propiedades = {k: {"select": {"name": v}} for k, v in nuevos_valores.items()}
    url = f"https://api.notion.com/v1/pages/{page_id}"
    response = requests.patch(url, headers=HEADERS, json={"properties": propiedades})
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

def agregar_o_reemplazar_mensajes_notion(page_id, mensajes_procesados):
    # 1. Obtener todos los bloques actuales de la clase
    url_get = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.get(url_get, headers=HEADERS)
    if response.status_code == 200:
        blocks = response.json().get("results", [])
        
        bloques_a_eliminar = []
        eliminando = False
        titulos_a_reemplazar = [f"Mensaje: {titulo}" for titulo in mensajes_procesados.keys()]
        
        for block in blocks:
            if block["type"] == "heading_3":
                try:
                    texto_heading = "".join([t["text"]["content"] for t in block["heading_3"]["rich_text"]])
                    if texto_heading in titulos_a_reemplazar:
                        eliminando = True  # Encontramos un mensaje viejo, marcamos para borrar
                        bloques_a_eliminar.append(block["id"])
                    else:
                        eliminando = False
                except:
                    pass
            elif eliminando:
                bloques_a_eliminar.append(block["id"])
        
        # 2. Eliminar los bloques viejos
        for block_id in bloques_a_eliminar:
            requests.delete(f"https://api.notion.com/v1/blocks/{block_id}", headers=HEADERS)
            time.sleep(0.1)
            
    # 3. Agregar los bloques actualizados/nuevos al final
    url_append = f"https://api.notion.com/v1/blocks/{page_id}/children"
    children = []
    for titulo, contenido in mensajes_procesados.items():
        children.append({
            "object": "block", "type": "heading_3",
            "heading_3": {"rich_text": [{"text": {"content": f"Mensaje: {titulo}"}}]}
        })
        fragmentos = [contenido[i:i+1800] for i in range(0, len(contenido), 1800)]
        for frag in fragmentos:
            children.append({
                "object": "block", "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": frag}}]}
            })
    
    if children:
        res_append = requests.patch(url_append, headers=HEADERS, json={"children": children})
        return res_append.status_code == 200
    return True

# --- 2.1 FUNCIONES DE CONEXIÓN CON NOTION (ESTUDIANTES) ---

def agregar_estudiante_notion(nombre, id_alumno, id_clase, orden_lista):
    url = "https://api.notion.com/v1/pages"
    data = {
        "parent": {"database_id": DB_ESTUDIANTES_ID},
        "properties": {
            "Nombre y Apellido": {"title": [{"text": {"content": nombre}}]},
            "Clase Asignada": {"relation": [{"id": id_clase}]},
            "Orden": {"number": orden_lista}  
        }
    }
    if id_alumno and str(id_alumno).strip() != "":
        data["properties"]["ID's"] = {"rich_text": [{"text": {"content": str(id_alumno)}}]}
        
    response = requests.post(url, headers=HEADERS, json=data)
    
    if response.status_code != 200:
        st.error(f"Error al guardar a {nombre}: {response.text}")
        
    return response.status_code == 200

def cargar_estudiantes_por_clase(id_clase):
    url = f"https://api.notion.com/v1/databases/{DB_ESTUDIANTES_ID}/query"
    
    # FORZAR ORDENAMIENTO POR LA COLUMNA 'Orden'
    payload = {
        "filter": {
            "property": "Clase Asignada",
            "relation": {"contains": id_clase}
        },
        "sorts": [
            {
                "property": "Orden",
                "direction": "ascending"
            }
        ]
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    estudiantes = []
    if response.status_code == 200:
        resultados = response.json().get("results", [])
        for page in resultados:
            props = page["properties"]
            try:
                nombre = props["Nombre y Apellido"]["title"][0]["text"]["content"]
                
                def get_number(prop_name):
                    return props.get(prop_name, {}).get("number", 0) or 0
                
                def get_formula_number(prop_name):
                    return props.get(prop_name, {}).get("formula", {}).get("number", 0) or 0
                
                def get_select(prop_name):
                    select_data = props.get(prop_name, {}).get("select")
                    return select_data["name"] if select_data else None
                    
                def get_rich_text(prop_name):
                    rt = props.get(prop_name, {}).get("rich_text", [])
                    return "".join([t["text"]["content"] for t in rt]) if rt else ""

                estudiante = {
                    "page_id": page["id"],
                    "Nombre y Apellido": nombre,
                    "PT - Writing /80": get_number("PT - Writing /80"),
                    "PT - Speaking /20": get_number("PT - Speaking /20"),
                    "PT - Total /100": get_formula_number("PT - Total /100"), 
                    "Nivel de ubicación": get_select("Nivel de ubicación"),
                    "INT - Reading /25": get_number("INT - Reading /25"),
                    "INT - Writing /25": get_number("INT - Writing /25"),
                    "INT - Listening /25": get_number("INT - Listening /25"),
                    "INT - Speaking /25": get_number("INT - Speaking /25"),
                    "INT - Final Average /100": get_formula_number("INT - Final Average /100"),
                    "CEFR Level": get_select("CEFR Level"),
                    "Observaciones": get_rich_text("Observaciones")
                }
                estudiantes.append(estudiante)
            except Exception as e:
                continue
    return estudiantes

def actualizar_notas_notion(page_id, propiedades_actualizar):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    propiedades = {}
    
    for key, value in propiedades_actualizar.items():
        if "Nivel" in key or "CEFR" in key:
            if value and str(value).strip() != "":
                propiedades[key] = {"select": {"name": str(value)}}
        elif key == "Observaciones":
            texto_obs = "" if pd.isna(value) or value is None else str(value)
            propiedades[key] = {"rich_text": [{"text": {"content": texto_obs}}]}
        else:
            try:
                num_val = 0 if pd.isna(value) or value == "" or value is None else float(value)
                propiedades[key] = {"number": num_val}
            except ValueError:
                propiedades[key] = {"number": 0}

    response = requests.patch(url, headers=HEADERS, json={"properties": propiedades})
    return response.status_code == 200

# --- 3. INTERFAZ VISUAL Y AUTENTICACIÓN ---

st.set_page_config(page_title="Gestor INED", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.title("🔒 Acceso Restringido")
    st.markdown("Por favor, ingresa la credencial administrativa de INED para acceder al sistema.")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        clave_ingresada = st.text_input("Contraseña:", type="password")
        if st.button("Ingresar", type="primary", use_container_width=True):
            if clave_ingresada == st.secrets["APP_PASSWORD"]:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    st.stop()

col_titulo, col_boton = st.columns([4, 1])
with col_titulo:
    st.title("🎓 Sistema de Gestión Administrativa")
with col_boton:
    st.write("") 
    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state["autenticado"] = False
        st.rerun()

plantillas_disponibles = cargar_plantillas_notion()
clases_disponibles = cargar_clases_notion()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚀 Crear Nueva Clase", 
    "📚 Gestor Plantillas", 
    "📋 Panel de Clases", 
    "👥 Registro de Estudiantes", 
    "📝 Libro de Calificaciones"
])

# --- PESTAÑA 1: CREAR / ACTUALIZAR CLASE ---
with tab1:
    st.header("1. Tipo de Proceso")
    tipo_clase = st.radio("¿Qué tipo de mensajes vas a preparar?", ["Placement Test", "Intensivo"], horizontal=True)
    
    st.divider()
    st.header("2. Llenar Datos Generales")
    
    col1, col2 = st.columns(2)
    with col1:
        nombre_clase = st.text_input("Nombre de la Clase", placeholder="Ej: Clase #245 - 5to nivel")
        horario = st.text_input("Horario de la Clase", placeholder="Ej: 7-9 p.m. (Lunes a Viernes)")
        link_grabaciones = st.text_input("Enlace de Clases Grabadas", placeholder="Ej: https://drive.google.com/drive/folders/...")
        
    with col2:
        fecha_inicio = st.date_input("Fecha de Inicio (Para Notion)")
        fecha_inicio_texto = st.text_input("Fecha de Inicio (Para Mensajes)", placeholder="Ej: 03 de agosto, 2026")
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
            fecha_pago_1 = st.text_input("Fecha de abono #1", placeholder="Ej: 05 DE AGOSTO, 2026")
            fecha_pago_2 = st.text_input("Fecha de abono #2", placeholder="Ej: 25 DE AGOSTO, 2026")
            fecha_confirmacion = st.text_input("Fecha límite de confirmación", placeholder="Ej: domingo 02 de agosto, 2026 11h00 am")

    st.divider()
    st.header("4. Generar y Enviar a Notion")
    
    if plantillas_disponibles:
        nombres_filtrados = [n for n, d in plantillas_disponibles.items() if d["categoria"] == tipo_clase]
        if nombres_filtrados:
            modo_seleccion = st.radio("Opciones de generación:", ["Seleccionar todos automáticamente", "Elegir manualmente"])
            plantillas_seleccionadas = nombres_filtrados if modo_seleccion == "Seleccionar todos automáticamente" else st.multiselect("Mensajes disponibles:", nombres_filtrados)
            
            if plantillas_seleccionadas:
                st.markdown("---")
                col_n1, col_n2 = st.columns(2)
                
                with col_n1:
                    st.markdown("**Opción A: Clase Nueva**")
                    st.caption("Crea una página desde cero en Notion.")
                    btn_nueva = st.button("✨ Procesar y Crear NUEVA Clase", type="primary", use_container_width=True)
                
                with col_n2:
                    st.markdown("**Opción B: Actualizar Existente**")
                    if clases_disponibles:
                        clase_a_actualizar = st.selectbox("Selecciona la clase a modificar:", list(clases_disponibles.keys()), label_visibility="collapsed")
                        btn_actualizar = st.button("🔄 Reemplazar/Agregar a esta Clase", type="secondary", use_container_width=True)
                    else:
                        st.info("No hay clases creadas para actualizar.")
                        btn_actualizar = False

                if btn_nueva or btn_actualizar:
                    if btn_nueva and not nombre_clase:
                        st.error("Falta el 'Nombre de la Clase' para poder crearla.")
                    elif btn_actualizar and not clases_disponibles:
                        st.error("No hay clases disponibles para actualizar.")
                    else:
                        with st.spinner("Procesando y conectando con Notion..."):
                            mensajes_finales = {}
                            nombre_final_clase = nombre_clase if btn_nueva else clase_a_actualizar
                            
                            for np in plantillas_seleccionadas:
                                texto = plantillas_disponibles[np]["contenido"]
                                
                                texto = texto.replace("[CLASE]", nombre_final_clase).replace("[HORARIO]", horario).replace("[LINK_GRABACIONES]", link_grabaciones).replace("[FECHA_INICIO]", fecha_inicio_texto)
                                
                                if tipo_clase == "Placement Test":
                                    texto = texto.replace("[FECHA_TEST]", fecha_test).replace("[HORARIO_TEST]", horario_test).replace("[LINK_TEST]", link_test).replace("[CLAVE_TEST]", clave_test).replace("[FECHA_SPEAKING]", fecha_speaking)
                                elif tipo_clase == "Intensivo":
                                    texto = texto.replace("[DOCENTE]", docente).replace("[FECHA_FIN]", fecha_fin).replace("[FECHA_EXAMEN_ESCRITO]", fecha_examen_escrito).replace("[FECHA_SPEAKING]", fecha_speaking).replace("[FECHA_RECORDATORIO_SPEAKING]", fecha_recordatorio_speaking).replace("[FECHA_CARTAS_APROBACION]", fecha_cartas_aprobacion).replace("[FECHA_RESULTADOS]", fecha_resultados).replace("[LINK_LISTENING]", link_listening).replace("[LINK_READING]", link_reading).replace("[LINK_WRITING]", link_writing).replace("[CLAVE_EXAMENES]", clave_examenes).replace("[FECHA_PAGO_1]", fecha_pago_1).replace("[FECHA_PAGO_2]", fecha_pago_2).replace("[FECHA_CONFIRMACION]", fecha_confirmacion)
                                
                                mensajes_finales[np] = texto
                            
                            if btn_nueva:
                                if crear_clase_en_notion(nombre_final_clase, fecha_inicio, mensajes_finales):
                                    st.success(f"¡Clase '{nombre_final_clase}' creada correctamente!")
                                else:
                                    st.error("Hubo un error al crear la clase.")
                            elif btn_actualizar:
                                id_de_la_clase = clases_disponibles[clase_a_actualizar]["id"]
                                if agregar_o_reemplazar_mensajes_notion(id_de_la_clase, mensajes_finales):
                                    st.success(f"¡Textos actualizados exitosamente en '{clase_a_actualizar}'!")
                                else:
                                    st.error("Hubo un error al actualizar la clase en Notion.")

# --- PESTAÑA 2: GESTOR PLANTILLAS ---
with tab2:
    st.header("Biblioteca de Plantillas")
    opciones = ["➕ Crear nueva plantilla"] + list(plantillas_disponibles.keys())
    seleccion = st.selectbox("Selecciona:", opciones)
    
    if seleccion == "➕ Crear nueva plantilla":
        nuevo_nombre, texto_actual, nueva_categoria, id_actual = "", "", "Placement Test", None
    else:
        nuevo_nombre = seleccion
        texto_actual = plantillas_disponibles[seleccion]["contenido"]
        nueva_categoria = plantillas_disponibles[seleccion]["categoria"]
        id_actual = plantillas_disponibles[seleccion]["id"]

    nuevo_nombre = st.text_input("Nombre:", value=nuevo_nombre)
    lista_cat = ["Placement Test", "Intensivo", "Sin categoría"]
    nueva_categoria = st.selectbox("Categoría:", lista_cat, index=lista_cat.index(nueva_categoria) if nueva_categoria in lista_cat else 0)
    nuevo_texto = st.text_area("Contenido:", value=texto_actual, height=300)
    
    if st.button("💾 Guardar Plantilla"):
        if nuevo_nombre and nuevo_texto:
            if guardar_o_actualizar_plantilla(nuevo_nombre, nuevo_texto, nueva_categoria, id_actual):
                st.success("¡Guardado!")

# --- PESTAÑA 3: PANEL DE CLASES ---
with tab3:
    st.header("📋 Panel de Clases")
    if clases_disponibles:
        clase_sel = st.selectbox("Revisar clase:", list(clases_disponibles.keys()))
        if clase_sel:
            datos = clases_disponibles[clase_sel]
            cols = st.columns(5)
            for i in range(1, 6):
                cols[i-1].metric(f"Módulo {i}", "", delta=datos["modulos"][f"Módulo {i}"], delta_color="off")
            st.divider()
            st.subheader("✅ Estado de Documentación")
            check = datos.get("checklist", {})
            if check:
                with st.form(key=f"form_{datos['id']}"):
                    nuevos = {}
                    cols_chk = st.columns(3)
                    ops = ["No empezado", "En proceso", "Listo"]
                    for idx, (item, estado) in enumerate(check.items()):
                        with cols_chk[idx % 3]:
                            ops_dyn = [estado] + ops if estado not in ops else ops
                            nuevos[item] = st.selectbox(item, ops_dyn, index=ops_dyn.index(estado))
                    if st.form_submit_button("💾 Guardar Estados"):
                        if actualizar_checklist_notion(datos["id"], nuevos):
                            st.success("¡Actualizado!")
            st.divider()
            st.subheader("💬 Mensajes Generados")
            for bloque in obtener_contenido_clase(datos["id"]):
                st.markdown(f"**{bloque['titulo']}**")
                st.code(bloque['texto'], language="text")

# --- PESTAÑA 4: REGISTRO MASIVO ---
with tab4:
    st.header("👥 Registro Masivo de Estudiantes")
    st.markdown("Selecciona una clase, pega la lista de nombres desde Excel y digita sus ID's directamente en la web.")
    
    if not clases_disponibles:
        st.warning("No hay clases creadas. Ve a la Pestaña 1 primero.")
    else:
        clase_destino = st.selectbox("1. ¿A qué clase se van a matricular?", list(clases_disponibles.keys()), key="sel_clase_reg")
        id_de_la_clase = clases_disponibles[clase_destino]["id"]
        
        st.markdown("---")
        lista_nombres = st.text_area("2. Pega aquí los nombres (un alumno por línea):", height=150, placeholder="Juan Pérez\nMaría López\nCarlos Santana...")
        
        if lista_nombres:
            nombres_limpios = [n.strip() for n in lista_nombres.split('\n') if n.strip()]
            df_inscripcion = pd.DataFrame({
                "Nombre y Apellido": nombres_limpios,
                "ID's": [""] * len(nombres_limpios)
            })
            
            st.markdown("**3. Ingresa las cédulas (Puedes moverte con las flechas del teclado):**")
            df_editado = st.data_editor(
                df_inscripcion, 
                use_container_width=True,
                column_config={
                    "Nombre y Apellido": st.column_config.TextColumn(disabled=True) 
                }
            )
            
            if st.button("💾 Matricular a todos en Notion", type="primary"):
                barra_progreso = st.progress(0)
                total_alumnos = len(df_editado)
                errores = 0
                
                for idx, fila in df_editado.iterrows():
                    exito = agregar_estudiante_notion(fila["Nombre y Apellido"], fila["ID's"], id_de_la_clase, idx + 1)
                    if not exito:
                        errores += 1
                    barra_progreso.progress((idx + 1) / total_alumnos)
                    time.sleep(0.1) 
                
                if errores == 0:
                    st.success(f"¡Se han matriculado {total_alumnos} estudiantes exitosamente a {clase_destino}!")
                else:
                    st.warning(f"Se matricularon los alumnos, pero hubo {errores} errores. Revisa tu Notion.")

# --- PESTAÑA 5: NOTAS ---
with tab5:
    st.header("📝 Libro de Calificaciones")
    
    if not clases_disponibles:
        st.info("No hay clases disponibles.")
    else:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            clase_a_calificar = st.selectbox("Selecciona la Clase a calificar:", list(clases_disponibles.keys()), key="sel_clase_cal")
        with col_c2:
            tipo_evaluacion = st.radio("Tipo de Evaluación:", ["Placement Test", "Intensivo"], horizontal=True)
            
        id_clase_calificar = clases_disponibles[clase_a_calificar]["id"]
        
        with st.spinner("Cargando lista de estudiantes desde Notion..."):
            lista_estudiantes = cargar_estudiantes_por_clase(id_clase_calificar)
            
        if not lista_estudiantes:
            st.warning(f"No hay estudiantes matriculados en {clase_a_calificar}. Ve a la Pestaña 4 para inscribirlos.")
        else:
            df_notas = pd.DataFrame(lista_estudiantes)
            
            if tipo_evaluacion == "Placement Test":
                columnas_vista = ["Nombre y Apellido", "PT - Writing /80", "PT - Speaking /20", "PT - Total /100", "Nivel de ubicación", "Observaciones"]
            else:
                columnas_vista = ["Nombre y Apellido", "INT - Reading /25", "INT - Writing /25", "INT - Listening /25", "INT - Speaking /25", "INT - Final Average /100", "CEFR Level", "Observaciones"]
            
            df_mostrar = df_notas[["page_id"] + columnas_vista]
            
            st.markdown("---")
            st.markdown("**Digita las calificaciones a continuación:**")
            
            with st.form("form_notas"):
                df_notas_editadas = st.data_editor(
                    df_mostrar,
                    use_container_width=True,
                    column_config={
                        "page_id": None, 
                        "Nombre y Apellido": st.column_config.TextColumn(disabled=True),
                        "PT - Total /100": st.column_config.NumberColumn(disabled=True), 
                        "INT - Final Average /100": st.column_config.NumberColumn(disabled=True),
                        "Observaciones": st.column_config.TextColumn() 
                    }
                )
                
                submit_notas = st.form_submit_button("💾 Sincronizar Calificaciones con Notion", type="primary")
                
                if submit_notas:
                    barra_progreso_notas = st.progress(0)
                    total_estudiantes = len(df_notas_editadas)
                    
                    columnas_formula = ["PT - Total /100", "INT - Final Average /100"]
                    
                    for idx, fila_editada in df_notas_editadas.iterrows():
                        page_id = fila_editada["page_id"]
                        datos_a_actualizar = {}
                        
                        for col in columnas_vista:
                            if col != "Nombre y Apellido" and col not in columnas_formula:
                                datos_a_actualizar[col] = fila_editada[col]
                                
                        actualizar_notas_notion(page_id, datos_a_actualizar)
                        barra_progreso_notas.progress((idx + 1) / total_estudiantes)
                        
                    st.success("¡Calificaciones guardadas! Recargando para mostrar los nuevos totales...")
                    time.sleep(1.5) 
                    st.rerun()
