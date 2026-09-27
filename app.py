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
# Si es la primera vez que abre la app en la sesión, cargamos las base
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
    
    st.subheader("1. Llena las variables del curso actual")
    col1, col2, col3 = st.columns(3)
    with col1:
        clase_id = st.text_input("ID de la Clase:", "CLASS 245 - 5to nivel")
        docente = st.text_input("Nombre del Docente:", "Jordy Chafuel")
        horario = st.text_input("Horario:", "7-9 p.m.")
    with col2:
        fecha_inicio = st.text_input("Fecha Inicio / Fecha Test:", "03 de agosto")
        fecha_fin = st.text_input("Fecha Fin:", "28 de agosto")
        fecha_speaking = st.text_input("Límite Speaking:", "Viernes 31 de julio, 09:00 a.m.")
    with col3:
        link_clases = st.text_input("Enlace Clases Grabadas:", "https://drive.google.com/...")
        horario_test = st.text_input("Hora Test / Límite:", "09:00 a.m.")

    st.divider()

    st.subheader("2. Editor y Gestor de Plantillas")
    
    # Selector de la plantilla actual
    nombres_plantillas = list(st.session_state['plantillas'].keys())
    if nombres_plantillas:
        seleccion = st.selectbox("Selecciona la plantilla a utilizar:", nombres_plantillas)
        texto_a_editar = st.text_area("Editor de Plantilla (Modifica aquí el texto):", value=st.session_state['plantillas'][seleccion], height=300)
        
        # Botones de Acción Rápida (Procesar vs Guardar)
        col_proc, col_act, col_del = st.columns([2, 2, 1])
        
        with col_proc:
            if st.button("🚀 Procesar Mensaje (Inyectar Variables)", type="primary"):
                resultado = texto_a_editar.replace("[CLASE]", clase_id)
                resultado = resultado.replace("[DOCENTE]", docente)
                resultado = resultado.replace("[HORARIO]", horario)
                resultado = resultado.replace("[FECHA_TEST]", fecha_inicio)
                resultado = resultado.replace("[FECHA_INICIO]", fecha_inicio)
                resultado = resultado.replace("[FECHA_FIN]", fecha_fin)
                resultado = resultado.replace("[FECHA_SPEAKING]", fecha_speaking)
                resultado = resultado.replace("[HORARIO_TEST]", horario_test)
                resultado = resultado.replace("[LINK_CLASES]", link_clases)
                
                st.success("¡Texto listo para enviar!")
                st.text_area("Copia este texto para WhatsApp:", value=resultado, height=300)
                
        with col_act:
            if st.button("💾 Guardar cambios en esta plantilla"):
                st.session_state['plantillas'][seleccion] = texto_a_editar
                st.success(f"Plantilla '{seleccion}' actualizada.")
                
        with col_del:
            if st.button("🗑️ Eliminar Plantilla"):
                del st.session_state['plantillas'][seleccion]
                st.rerun()
    else:
        st.warning("No hay plantillas guardadas. Crea una nueva abajo.")

    # --- AGREGAR NUEVA PLANTILLA ---
    st.divider()
    with st.expander("➕ Crear Nueva Plantilla"):
        nuevo_nombre = st.text_input("Nombre de la nueva plantilla (Ej: Intensivo - Recordatorio):")
        nuevo_texto = st.text_area("Escribe el texto base usando las variables en MAYÚSCULAS:", height=200)
        
        if st.button("Agregar a la Librería"):
            if nuevo_nombre and nuevo_texto:
                if nuevo_nombre in st.session_state['plantillas']:
                    st.error("Ya existe una plantilla con ese nombre.")
                else:
                    st.session_state['plantillas'][nuevo_nombre] = nuevo_texto
                    st.success("Plantilla agregada correctamente.")
                    st.rerun()
            else:
                st.warning("Debes ponerle un nombre y un texto para guardarla.")

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
