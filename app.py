import streamlit as st
import os
from crewai import Agent, Task, Crew, Process, LLM

st.set_page_config(page_title="Videos Crew", page_icon="🎬", layout="wide")

st.title("Videos Crew")
st.write("Define tu concepto y deja que el equipo de agentes redacte la guía de producción.")

# Panel lateral para la clave
st.sidebar.header("Configuración")
api_key = st.sidebar.text_input("Ingresa tu Gemini API Key:", type="password")

# Interfaz principal
col1, col2 = st.columns(2)
with col1:
    cancion = st.text_input("Canción:", "Boulevard of Broken Dreams")
    tempo = st.text_input("Tempo y Energía:", "Lento y melancólico, guitarra acústica")
with col2:
    estilo = st.text_input("Estilo Visual:", "Neon Noir, alto contraste, sombras oscuras")
    letra = st.text_area("Letra clave:", "I walk a lonely road, the only one that I have ever known")

if st.button("Generar Guion de Producción"):
    if not api_key:
        st.error("Por favor, ingresa tu API Key en el menú lateral izquierdo.")
    else:
        with st.spinner("El equipo está trabajando. Esto tomará 1 o 2 minutos..."):
            os.environ["GEMINI_API_KEY"] = api_key
            gemini_llm = LLM(model="gemini/gemini-3.5-flash")

            # Agentes
            director = Agent(
                role="Director de Escena",
                goal="Diseñar la narrativa visual, cámara y luz.",
                backstory="Cineasta experto en trasladar emociones a movimientos de cámara.",
                llm=gemini_llm
            )
            tipografo = Agent(
                role="Diseñador de Tipografía",
                goal="Integrar la letra de la canción en el entorno.",
                backstory="Diseñador gráfico. Integras letras en luces, reflejos o humo.",
                llm=gemini_llm
            )
            colorista = Agent(
                role="Colorista",
                goal="Establecer paleta de colores y contraste.",
                backstory="Especialista en etalonaje que traduce moods a colores precisos.",
                llm=gemini_llm
            )

            # Tareas
            t_escenas = Task(description=f"Diseña la escena de apertura para '{cancion}' ({tempo}) estilo '{estilo}'.", expected_output="Descripción de escena y cámara.", agent=director)
            t_letras = Task(description=f"Integra esta letra orgánicamente en la escena: '{letra}'.", expected_output="Propuesta tipográfica.", agent=tipografo)
            t_color = Task(description=f"Define la teoría de color para la escena con estética '{estilo}'.", expected_output="Guía de etalonaje.", agent=colorista)

            # Orquestación (Síncrono normal, ya que no estamos en Colab)
            equipo = Crew(agents=[director, tipografo, colorista], tasks=[t_escenas, t_letras, t_color], process=Process.sequential)
            
            resultado = equipo.kickoff()

            st.success("¡Producción Finalizada!")
            st.markdown(resultado.raw)
