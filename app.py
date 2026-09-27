import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="INED Workspace", page_icon="⚙️", layout="wide")

st.title("⚙️ INED Workspace & Automation")
st.write("Panel central para gestión de módulos, mensajería y documentación.")

tab1, tab2, tab3 = st.tabs(["💬 Mensajería de WhatsApp", "📅 Calendario de Módulos", "📋 Checklist de Documentos"])

# --- PESTAÑA 1: MENSAJERÍA ---
with tab1:
    st.header("Generador de Mensajes")
    
    # Selector de flujo
    flujo = st.radio("Selecciona el proceso:", ["Test de Ubicación", "Curso Intensivo"])
    
    st.subheader("Variables Generales")
    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        clase_id = st.text_input("ID de la Clase:", "CLASS 245 - 5to nivel")
    with col_g2:
        horario = st.text_input("Horario:", "7-9 p.m.")
    with col_g3:
        docente = st.text_input("Nombre del Docente:", "Jordy Chafuel")

    st.divider()

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
            
        if st.button("Generar Mensajes (Test)"):
            msg1 = f"""¡Bienvenidos al Curso de Preparación para el Test de Ubicación en Inglés! 🎉📚
{clase_id}

🧗🏻🫂 Nos alegra que estén aquí para dar este importante paso en el aprendizaje del idioma. Durante este proceso, revisaremos conceptos clave y estrategias que les ayudarán a sentirse más preparados y seguros al momento de rendir la prueba. Recordemos que el objetivo es alcanzar una nota alta y así puedan ubicarse en los últimos niveles; esto les otorga el beneficio de optimizar su tiempo y recursos.

✍🏻 Les recomendamos aprovechar al máximo cada sesión, practicar constantemente y hacer todas las preguntas que necesiten. ¡Estamos aquí para ayudarles a alcanzar su mejor nivel!

💡 Consejo: Mantengan una actitud positiva y confíen en su progreso. ¡Cada esfuerzo cuenta!

El horario será de {horario} y la plataforma de conexión es Google Meet
🧑🏻‍💻 Un link de conexión será enviado minutos antes del inicio.

💻 Clases grabadas estarán disponibles aquí: 
{link_clases}

🟢🙋‍♂️Puntajes (rúbrica) del test de ubicación: ined.ca/r

Todos ustedes han cumplido con los requisitos de admisión y están legalmente matriculados en INED. 

ESTE CURSO ES DE VITAL IMPORTANCIA para asegurar un avance eficiente y muy significativo en su proceso formativo y tener evidencias legales y académicas de justificación. 

Después de los resultados del test de ubicación, usted sabrá los niveles y el tiempo DE ESTUDIOS para completar los 5 niveles del programa académico y en base a esto, usted deberá realizar una pequeña inversión para cubrir todo lo correspondiente a su proceso académico de suficiencia B1. 

El docente {docente} los guiará en este proceso.
¡Mucho éxito en su preparación! 🚀✨"""

            msg2 = f"""🔴 Test de ubicación {fecha_test}
🙋🏻 Saludos a todos! 

Les enviamos instrucciones generales para el test.

🧑🏻‍💻 INFORMACIÓN TEST DE UBICACIÓN
✍🏻 Fecha: {fecha_test}
✍🏻 Horario: {horario_test}
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
✍🏻 EL LINK Y LA CLAVE DE LA PRUEBA serán enviados antes de las {horario_test.split(' ')[0]} por WhatsApp.
Se recomienda tener abierto WhatsApp web...
❌📱 NO haga el test desde su celular.
✅👩‍💻👨‍💻Use su computador por favor.
==============

🔴 Instrucciones para el examen de ubicación (Speaking) 🔴
✍🏻Ver la guía en pdf: https://drive.google.com/file/d/...
✍🏻Ver ejemplo de videos: https://drive.google.com/drive/folders/...

🚨 Fecha límite para enviar el video: {fecha_speaking}
📹Puede enviar su video por WhatsApp 0999102056, asegúrese de enviarlo en HD. 

🧗🏻🫂 Los resultados de su test se los enviamos en una carta formal la cual se enviará a su WhatsApp 1 o 2 días después del test. 
Mucha suerte a todos 🤝🤞🏻"""

            msg3 = f"""Buenos días a todos.

🔴Test de ubicación {fecha_test}.🔴

El link ya está habilitado, les recomiendo 100% hacer el test desde un computador ❌ NO desde un teléfono.
———————————————
LINK: {link_test}
CLAVE: {clave_test}
———————————————
Asegúrese de enviar el test a tiempo. 

Suerte!🍀

_________________________________________________________________
🔴 IMPORTANTE

🫂 Si usted ingresó al link, hizo el test, lo envió correctamente, envió su video a tiempo en el formato solicitado (vertical) y lo hizo aplicando los lineamientos de la guia. Usted ha finalizado su test de ubicación correctamente.
 
¿Qué precede ahora?
 1: INED calificará su test (video de speaking + el test digital) y aplicará la rubrica de ubicación para obtener su puntaje final /100
 2: 🧗🏻🫂 INED le enviará los resultados del test de ubicación en una carta formal la cual cada estudiante recibirá a su WhatsApp personal el mismo día del test.

🤝 También se adjuntará un mensaje con las sugerencias que usted debería seguir. Mientras le llegue el documento con los resultados, *espere con paciencia! 
Gracias."""

            st.success("Mensajes del Test de Ubicación generados.")
            st.text_area("Mensaje 1: Bienvenida e Info General", value=msg1, height=300)
            st.text_area("Mensaje 2: Instrucciones del Test", value=msg2, height=300)
            st.text_area("Mensaje 3: Día del Test y Cierre", value=msg3, height=300)

    elif flujo == "Curso Intensivo":
        st.subheader("Variables del Curso Intensivo")
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.text_input("Fecha Inicio:", "03 de agosto")
            fecha_fin = st.text_input("Fecha Fin:", "28 de agosto de 2026")
            fecha_escrito = st.text_input("Fecha Examen Escrito:", "JUEVES 27 DE AGOSTO, 2026 - DE 7-9 PM")
            fecha_speaking_int = st.text_input("Límite Speaking:", "MIÉRCOLES 26 DE AGOSTO 2026 - 3PM")
            fecha_resultados = st.text_input("Fecha Resultados:", "SÁBADO 29 DE AGOSTO, 2026")
        with col2:
            link_clases_int = st.text_input("Enlace Clases Grabadas:", "https://drive.google.com/...")
            link_listening = st.text_input("Link Listening:", "https://forms.gle/...")
            link_reading = st.text_input("Link Reading:", "https://forms.gle/...")
            link_writing = st.text_input("Link Writing:", "https://forms.gle/...")
            clave_general = st.text_input("Clave General Exámenes:", "TEX2026@45AG")

        if st.button("Generar Mensajes (Intensivo)"):
            # Aquí iría la misma lógica de f-strings aplicada a tus 4 textos del intensivo.
            # Por brevedad en este ejemplo, inserto un extracto del Mensaje 1 y 3 para que veas el funcionamiento.
            
            msg1_int = f"""🙋🏼‍♀️🙋🏻‍♂️ Estimados todos. 
Bienvenidos a este curso {clase_id}

✍🏻Nos complace darles la bienvenida a todos a nuestra institución educativa INED y desearles mucho éxito en este curso intensivo de Inglés que se llevará a cabo del {fecha_inicio} al {fecha_fin}, en modalidad online en el horario de {horario}.

🚨⤵️ Clases grabadas estarán aquí: 
{link_clases_int}

🟢 El docente {docente} los guiará en este proceso.
Cualquier duda, nos escriben."""

            msg3_int = f"""Estimados estudiantes, saludos a todos.

🔴 Les recordamos que la fecha límite de entrega del SPEAKING es el {fecha_speaking_int}. 
Por favor enviar a tiempo para evitar complicaciones.

Links para realizar el EXAMEN FINAL INED - TEFL B1
🛑 Se le recomienda abrir y hacer el examen en el siguiente orden:

1️⃣ Listening (hacer y enviar)  
LINK: {link_listening}
CLAVE: {clave_general}

2️⃣ Reading (hacer y enviar) 
LINK: {link_reading}
CLAVE: {clave_general}

3️⃣ Writing (hacer y enviar)  
LINK: {link_writing}
CLAVE: {clave_general}

4️⃣ Speaking: (YA FUE ENVIADO)"""

            st.success("Mensajes del Curso Intensivo generados.")
            st.text_area("Mensaje 1: Bienvenida", value=msg1_int, height=200)
            st.text_area("Mensaje 3: Exámenes y Enlaces", value=msg3_int, height=300)

# --- PESTAÑA 2: CALENDARIO ---
with tab2:
    st.header("Calculadora de Periodos Académicos")
    st.write("Los módulos duran exactamente 4 semanas (lunes a viernes).")
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
