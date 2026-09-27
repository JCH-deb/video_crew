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
        if pwd == "ined2026":  # Cambia esta contraseña por la que prefieras
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Credencial incorrecta.")
    
    st.stop()  # Detiene la ejecución del resto del código si no hay login

# --- 2. BASE DE DATOS DE PLANTILLAS ---
PLANTILLAS = {
    "Test Ubicación - Msj 1 (Bienvenida)": """¡Bienvenidos al Curso de Preparación para el Test de Ubicación en Inglés! 🎉📚
[CLASE]

🧗🏻🫂 Nos alegra que estén aquí para dar este importante paso en el aprendizaje del idioma. Durante este proceso, revisaremos conceptos clave y estrategias que les ayudarán a sentirse más preparados y seguros al momento de rendir la prueba. Recordemos que el objetivo es alcanzar una nota alta y así puedan ubicarse en los últimos niveles; esto les otorga el beneficio de optimizar su tiempo y recursos.

✍🏻 Les recomendamos aprovechar al máximo cada sesión, practicar constantemente y hacer todas las preguntas que necesiten. ¡Estamos aquí para ayudarles a alcanzar su mejor nivel!

💡 Consejo: Mantengan una actitud positiva y confíen en su progreso. ¡Cada esfuerzo cuenta!

El horario será de [HORARIO] y la plataforma de conexión es Google Meet
🧑🏻‍💻 Un link de conexión será enviado minutos antes.

💻 Clases grabadas estarán disponibles aquí: 
[LINK_CLASES]

🟢🙋‍♂️Puntajes (rúbrica) del test de ubicación: ined.ca/r

Todos ustedes han cumplido con los requisitos de admisión y están legalmente matriculados en INED. 
ESTE CURSO ES DE VITAL IMPORTANCIA para asegurar un avance eficiente y muy significativo en su proceso formativo y tener evidencias legales y académicas de justificación. 

Después de los resultados del test de ubicación, usted sabrá los niveles y el tiempo DE ESTUDIOS para completar los 5 niveles del programa académico y en base a esto, usted deberá realizar una pequeña inversión para cubrir todo lo correspondiente a su proceso académico de suficiencia B1. 

El docente [DOCENTE] los guiará en este proceso.
¡Mucho éxito en su preparación! 🚀✨""",
    
    "Test Ubicación - Msj 2 (Instrucciones)": """🔴 Test de ubicación [FECHA_TEST]
🙋🏻 Saludos a todos! 
Les enviamos instrucciones generales para el test.

🧑🏻‍💻 INFORMACIÓN TEST DE UBICACIÓN
✍🏻 Fecha: [FECHA_TEST]
✍🏻 Horario: [HORARIO_TEST]
✍🏻 Modalidad: Online

🎯 Objetivo: Alcanzar el mejor puntaje posible sobre /100 puntos...

✅ El test tiene 80 preguntas de opción múltiple, normalmente les tomaría una hora con 20 minutos, pero el test estará habilitado 2 horas.

==============
🔴 Instrucciones para el test de ubicación de Listening🔴
🧏🏻 CUANDO USTED ABRE LA PRUEBA, LAS PRIMERAS 3 PREGUNTAS SON DEL LISTENING #1 
El link del audio está en la misma plataforma (puede repetirlo 2/3 veces) 

🧏🏻 LAS PREGUNTAS DE LAS 4-6 SON DEL LISTENING #2
El link del audio está en la misma plataforma (puede repetirlo 2/3 veces) 
==============
🫂 Luego de completar las 6 preguntas de listening, ustedes deben seguir completando el resto del test hasta llegar a la pregunta 80.
==============
✍🏻 EL LINK Y LA CLAVE DE LA PRUEBA serán enviados antes de las [HORARIO_TEST] por WhatsApp.
Se recomienda tener abierto WhatsApp web.
❌📱 NO haga el test desde su celular.
✅👩‍💻👨‍💻Use su computador por favor.
==============

🔴 Instrucciones para el examen de ubicación (Speaking) 🔴
✍🏻Ver la guía en pdf: [link_guia_pdf]
✍🏻Ver ejemplo de videos: [link_ejemplos]

🚨 Fecha límite para enviar el video: [FECHA_SPEAKING]
📹Puede enviar su video por WhatsApp, asegúrese de enviarlo en HD. 

🧗🏻🫂 Los resultados de su test se los enviamos en una carta formal la cual se enviará a su WhatsApp 1 o 2 días después del test. 
Mucha suerte a todos 🤝🤞🏻""",

    "Intensivo - Msj 1 (Bienvenida)": """🙋🏼‍♀️🙋🏻‍♂️ Estimados todos. 
Bienvenidos a este curso [CLASE]

✍🏻Nos complace darles la bienvenida a todos a nuestra institución educativa INED y desearles mucho éxito en este curso intensivo de Inglés que se llevará a cabo del [FECHA_INICIO] al [FECHA_FIN], en modalidad online en el horario de [HORARIO].

🎯 Estamos seguros que este programa intensivo será una experiencia enriquecedora y efectiva para todos ustedes.

✍🏻Durante este curso intensivo, tendrán la oportunidad de mejorar sus habilidades en las áreas claves del inglés. 
🎯Nuestro objetivo es proporcionarles las herramientas necesarias para que logren obtener bases sólidas en inglés, nosotros no llenamos libros, llenamos cerebros, las clases serán 100% prácticas. 

🟢 Les enviamos material de apoyo (Softwares Interactivos, Prepare Presentation Plus de Cambridge). 
Guarden estos links por favor
💻 Presentation Plus Softwares: [LINK_SOFTWARES]
🟢 Ver tutorial de como instalar: [LINK_TUTORIAL]

🚨⤵️ Clases grabadas estarán aquí: 
[LINK_CLASES]

🟢 El docente [DOCENTE] los guiará en este proceso.
Cualquier duda, nos escriben."""
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
    
    # Variables Universales
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

    # Selector y Editor
    st.subheader("2. Elige, edita y genera el mensaje")
    seleccion = st.selectbox("Selecciona la plantilla a utilizar:", list(PLANTILLAS.keys()))
    
    st.write("Modifica el texto libremente antes de procesar (las etiquetas en MAYÚSCULAS se llenarán solas):")
    texto_a_editar = st.text_area("Editor de Plantilla:", value=PLANTILLAS[seleccion], height=350)
    
    if st.button("Procesar Mensaje Final"):
        # Reemplazo de variables
        resultado = texto_a_editar.replace("[CLASE]", clase_id)
        resultado = resultado.replace("[DOCENTE]", docente)
        resultado = resultado.replace("[HORARIO]", horario)
        resultado = resultado.replace("[FECHA_TEST]", fecha_inicio)
        resultado = resultado.replace("[FECHA_INICIO]", fecha_inicio)
        resultado = resultado.replace("[FECHA_FIN]", fecha_fin)
        resultado = resultado.replace("[FECHA_SPEAKING]", fecha_speaking)
        resultado = resultado.replace("[HORARIO_TEST]", horario_test)
        resultado = resultado.replace("[LINK_CLASES]", link_clases)
        
        st.success("¡Texto procesado y listo para WhatsApp!")
        st.text_area("Copia este texto:", value=resultado, height=350)

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
