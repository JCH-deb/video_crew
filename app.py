import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="INED Workspace", page_icon="🔐", layout="wide")

# --- 1. SISTEMA DE AUTENTICACIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acceso Restringido - INED")
    st.write("Por favor, ingresa tu credencial para acceder al panel administrativo.")
    
    pwd = st.text_input("Contraseña:", type="password")
    if st.button("Entrar"):
        if pwd == "ined2026":  
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Credencial incorrecta.")
    st.stop()

# --- 2. BASE DE DATOS DE PLANTILLAS EN MEMORIA ---
if 'plantillas' not in st.session_state:
    st.session_state['plantillas'] = {
        "Test Ubicación - Msj 1 (Bienvenida)": "¡Bienvenidos al Curso de Preparación!\n[CLASE]\n\nEl horario será de [HORARIO] con el docente [DOCENTE].\nEnlace: [LINK_CLASES]",
        "Test Ubicación - Msj 2 (Instrucciones)": "🔴 Test de ubicación [FECHA_TEST]\nHorario: [HORARIO_TEST]\n\nRecuerda enviar el speaking hasta: [FECHA_SPEAKING]",
        "Intensivo - Msj 1 (Bienvenida)": "Bienvenidos al curso intensivo [CLASE].\nIniciamos el [FECHA_INICIO] y finalizamos el [FECHA_FIN].\nEnlace: [LINK_CLASES]"
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
    
    # --- VARIABLES GENERALES ---
    st.subheader("1. Variables Generales")
    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        clase_id = st.text_input("ID de la Clase:", "CLASS 245 - 5to nivel")
    with col_g2:
        docente = st.text_input("Nombre del Docente:", "Jordy Chafuel")
    with col_g3:
        horario = st.text_input("Horario:", "7-9 p.m.")

    # Diccionario maestro que guardará todas las variables a inyectar
    reemplazos = {
        "[CLASE]": clase_id,
        "[DOCENTE]": docente,
        "[HORARIO]": horario
    }

    st.divider()

    # --- SELECTOR DE FLUJO ---
    flujo = st.radio("Selecciona el proceso para cargar las variables específicas:", ["Test de Ubicación", "Curso Intensivo"], horizontal=True)

    if flujo == "Test de Ubicación":
        st.subheader("Variables del Test de Ubicación")
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
            "[FECHA_TEST]": fecha_test,
            "[HORARIO_TEST]": horario_test,
            "[FECHA_SPEAKING]": fecha_speaking,
            "[LINK_CLASES]": link_clases,
            "[LINK_TEST]": link_test,
            "[CLAVE_TEST]": clave_test
        })

    else:
        st.subheader("Variables del Curso Intensivo")
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.text_input("Fecha Inicio:", "03 de agosto")
            fecha_fin = st.text_input("Fecha Fin:", "28 de agosto")
            fecha_escrito = st.text_input("Fecha Examen Escrito:", "JUEVES 27 DE AGOSTO, 2026 - DE 7-9 PM")
            fecha_speaking_int = st.text_input("Límite Speaking:", "MIÉRCOLES 26 DE AGOSTO 2026 - 3PM")
            fecha_resultados = st.text_input("Fecha Resultados:", "SÁBADO 29 DE AGOSTO, 2026")
        with col2:
            link_clases_int = st.text_input("Enlace Clases Grabadas (Intensivo):", "https://drive.google.com/...")
            link_listening = st.text_input("Link Listening:", "https://forms.gle/...")
            link_reading = st.text_input("Link Reading:", "https://forms.gle/...")
            link_writing = st.text_input("Link Writing:", "https://forms.gle/...")
            clave_general = st.text_input("Clave General Exámenes:", "TEX2026@45AG")
            
        reemplazos.update({
            "[FECHA_INICIO]": fecha_inicio,
            "[FECHA_FIN]": fecha_fin,
            "[FECHA_ESCRITO]": fecha_escrito,
            "[FECHA_SPEAKING]": fecha_speaking_int,
            "[FECHA_RESULTADOS]": fecha_resultados,
            "[LINK_CLASES]": link_clases_int,
            "[LINK_LISTENING]": link_listening,
            "[LINK_READING]": link_reading,
            "[LINK_WRITING]": link_writing,
            "[CLAVE_GENERAL]": clave_general
        })

    st.divider()

    # --- EDITOR Y GESTOR ---
    st.subheader("2. Editor y Gestor de Plantillas")
    
    nombres_plantillas = list(st.session_state['plantillas'].keys())
    if nombres_plantillas:
        seleccion = st.selectbox("Selecciona la plantilla a utilizar:", nombres_plantillas)
        texto_a_editar = st.text_area("Editor de Plantilla (Modifica aquí el texto):", value=st.session_state['plantillas'][seleccion], height=300)
        
        col_proc, col_act, col_del = st.columns([2, 2, 1])
        
        with col_proc:
            if st.button("🚀 Procesar Mensaje", type="primary"):
                resultado = texto_a_editar
                # Reemplaza dinámicamente usando el diccionario
                for etiqueta, valor in reemplazos.items():
                    resultado = resultado.replace(etiqueta, valor)
                
                st.success("¡Texto listo para enviar!")
                st.text_area("Copia este texto para WhatsApp:", value=resultado, height=300)
                
        with col_act:
            if st.button("💾 Guardar cambios"):
                st.session_state['plantillas'][seleccion] = texto_a_editar
                st.success(f"Plantilla '{seleccion}' actualizada.")
                
        with col_del:
            if st.button("🗑️ Eliminar"):
                del st.session_state['plantillas'][seleccion]
                st.rerun()
    else:
        st.warning("No hay plantillas guardadas.")

    st.divider()
    with st.expander("➕ Crear Nueva Plantilla"):
        nuevo_nombre = st.text_input("Nombre de la nueva plantilla (Ej: Intensivo - Recordatorio):")
        nuevo_texto = st.text_area("Escribe el texto base usando las etiquetas permitidas:", height=200)
        
        if st.button("Agregar a la Librería"):
            if nuevo_nombre and nuevo_texto:
                if nuevo_nombre in st.session_state['plantillas']:
                    st.error("Ya existe una plantilla con ese nombre.")
                else:
                    st.session_state['plantillas'][nuevo_nombre] = nuevo_texto
                    st.success("Plantilla agregada correctamente.")
                    st.rerun()
            else:
                st.warning("Debes ponerle un nombre y un texto.")

# --- PESTAÑA 2: CALENDARIO ---
with tab2:
    st.header("Calculadora de Periodos Académicos")
    fecha_referencia = st.date_input("Selecciona el LUNES de inicio del último módulo conocido:")
    if st.button("Calcular periodos anteriores"):
        for i in range(1, 6):
            inicio_mod = fecha_referencia - timedelta(days=28 * i)
            fin_mod = inicio_mod + timedelta(days=25)
            st.info(f"**Módulo -{i}:** Inició el Lunes {inicio_mod.strftime('%d/%m/%Y')} y finalizó el Viernes {fin_mod.strftime('%d/%m/%Y')}")

# --- PESTAÑA 3: CHECKLIST Y NOTION ---
with tab3:
    st.header("Flujo de Documentación")
    estados = ["Iniciado", "En proceso", "En revisión", "2da revisión", "Terminado"]
    documentos = ["Statements", "Certificates", "Id1", "Id2", "Carta de Ubicación", "Carta de Aprobación", "Actas", "Data Base", "Notas", "Best Student (1)"]
    for doc in documentos:
        col_doc, col_estado = st.columns([3, 2])
        with col_doc:
            st.markdown(f"**{doc}**")
        with col_estado:
            st.selectbox("Estado", estados, key=doc, label_visibility="collapsed")
