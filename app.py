import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="INED Workspace", page_icon="⚙️", layout="wide")

st.title("⚙️ INED Workspace & Automation")
st.write("Panel central para gestión de módulos, mensajería y documentación.")

# Crear las pestañas
tab1, tab2, tab3 = st.tabs(["💬 Mensajería e Inyector", "📅 Calendario de Módulos", "📋 Checklist de Documentos"])

# --- PESTAÑA 1: MENSAJERÍA ---
with tab1:
    st.header("Inyector de Plantillas")
    st.write("Llena los datos del módulo actual. Las etiquetas en tu texto (ej. [FECHA_INICIO]) se reemplazarán solas.")
    
    col1, col2 = st.columns(2)
    with col1:
        curso = st.text_input("Nombre del Curso:", "Ej: Intensivo B1")
        f_inicio = st.text_input("Fecha de Inicio:", "Lunes 15 de Octubre")
        f_fin = st.text_input("Fecha de Fin:", "Viernes 9 de Noviembre")
    with col2:
        f_examen = st.text_input("Fecha de Exámenes:", "Jueves 8 de Noviembre")
        link_clases = st.text_input("Enlace de clases:", "https://drive...")
        link_examen = st.text_input("Enlace del examen:", "https://forms...")
        
    st.divider()
    
    plantilla = st.text_area(
        "Pega aquí tu documento o mensaje base:", 
        height=200,
        value="*Bienvenido al curso [CURSO]* 🚀\nIniciamos el [FECHA_INICIO] y terminamos el [FECHA_FIN].\n\nEl examen será el [FECHA_EXAMEN].\nEnlace a clases: [LINK_CLASES]\nEnlace a examen: [LINK_EXAMEN]"
    )
    
    if st.button("Procesar Mensajes"):
        resultado = plantilla.replace("[CURSO]", curso)
        resultado = resultado.replace("[FECHA_INICIO]", f_inicio)
        resultado = resultado.replace("[FECHA_FIN]", f_fin)
        resultado = resultado.replace("[FECHA_EXAMEN]", f_examen)
        resultado = resultado.replace("[LINK_CLASES]", link_clases)
        resultado = resultado.replace("[LINK_EXAMEN]", link_examen)
        
        st.success("¡Texto procesado! Listo para copiar y pegar.")
        st.text_area("Resultado final (puedes hacer retoques manuales):", value=resultado, height=200)

# --- PESTAÑA 2: CALENDARIO ---
with tab2:
    st.header("Calculadora de Periodos Académicos")
    st.write("Los módulos duran exactamente 4 semanas (lunes a viernes).")
    
    # Input para la fecha del último módulo
    fecha_referencia = st.date_input("Selecciona el LUNES de inicio del último módulo conocido:")
    
    if st.button("Calcular periodos anteriores"):
        st.write("### Proyección hacia atrás:")
        # Bucle para calcular los 5 módulos anteriores restando 28 días
        for i in range(1, 6):
            inicio_mod = fecha_referencia - timedelta(days=28 * i)
            fin_mod = inicio_mod + timedelta(days=25) # Suma 25 días para caer en el viernes de la 4ta semana
            
            st.info(f"**Módulo -{i}:** Inició el Lunes {inicio_mod.strftime('%d/%m/%Y')} y finalizó el Viernes {fin_mod.strftime('%d/%m/%Y')}")

# --- PESTAÑA 3: CHECKLIST Y NOTION ---
with tab3:
    st.header("Flujo de Documentación")
    st.write("Estados mapeados para sincronización futura con Notion.")
    
    estados = ["Iniciado", "En proceso", "En revisión", "2da revisión", "Terminado"]
    documentos = [
        "Statements", "Certificates", "Id1", "Id2", 
        "Carta de Ubicación", "Carta de Aprobación", 
        "Actas", "Data Base", "Notas", "Best Student (1)"
    ]
    
    # Generar selectores dinámicos para cada documento
    for doc in documentos:
        col_doc, col_estado = st.columns([3, 2])
        with col_doc:
            st.markdown(f"**{doc}**")
        with col_estado:
            st.selectbox("Estado", estados, key=doc, label_visibility="collapsed")
            
    st.divider()
    st.button("💾 Sincronizar con Notion (Próximamente)", disabled=True)
