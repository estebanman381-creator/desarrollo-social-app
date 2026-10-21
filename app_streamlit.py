import streamlit as st
from datetime import datetime
import pandas as pd
from supabase import create_client, Client

# --- CONFIGURACIÓN DE CONTRASEÑAS ---
CLAVE_TRABAJADORES = "trabajador123"
CLAVE_DIRECTIVOS = "direccion2026"

# Configuración de la página
st.set_page_config(page_title="Desarrollo Social - Loreto", page_icon="📋", layout="wide")

# --- CONEXIÓN A SUPABASE ---
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    /* 1. Ocultar menús de desarrollo y gestión de Streamlit (Share, GitHub, Manage App, etc.) */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    [data-testid="stToolbar"] {display: none;}
    div[class^="viewerBadge"] {display: none;}
    .stAppDeployButton {display: none;}

    /* 2. Estilo para el panel lateral completo */
    [data-testid="stSidebar"] {
        background-color: #1E232A !important;
        border-right: 1px solid #2D3748;
    }

    /* 3. Formato del título de sección en el menú */
    .sidebar-header {
        font-size: 13px !important;
        font-weight: 700 !important;
        color: #A0AEC0 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    /* 4. Aumentar tamaño y espacio de las opciones del menú */
    [data-testid="stSidebar"] .stRadio label {
        font-size: 17px !important;
        font-weight: 500 !important;
        color: #E2E8F0 !important;
        padding: 8px 12px;
        border-radius: 6px;
        transition: all 0.2s ease;
    }

    /* 5. Tarjeta de información institucional en la barra lateral */
    .sidebar-footer {
        background-color: #14171D;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #2D3748;
        font-size: 12px;
        color: #A0AEC0;
        margin-top: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# --- LOGO CENTRADO EN ENCABEZADO PRINCIPAL ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logoloreto.jpeg", use_container_width=True)

st.title("📋 Sistema de Gestión - Desarrollo Social")

# --- BARRA LATERAL PROFESIONAL ---
with st.sidebar:
    st.markdown('<p class="sidebar-header">MENÚ DE NAVEGACIÓN</p>', unsafe_allow_html=True)
    
    opcion = st.radio(
        label="",
        options=[
            "✍️ Cargar Ayuda Directa", 
            "🔍 Consultar Historial (DNI)"
        ],
        index=0
    )
    
    st.markdown("---")
    
    # Tarjeta informativa fija
    st.markdown("""
        <div class="sidebar-footer">
            <strong>Municipalidad de Loreto</strong><br>
            Secretaría de Desarrollo Social<br><br>
            🟢 <strong>Base de datos:</strong> Conectada<br>
            🔒 <strong>Acceso:</strong> Seguro (Encriptado)
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. MÓDULO: CARGA DE AYUDAS (ACCESO TRABAJADORES)
# ---------------------------------------------------------
if opcion == "✍️ Cargar Ayuda Directa":
    st.subheader("✍️ Registro de Beneficiario y Entrega")
    
    pass_carga = st.text_input("Ingrese la contraseña de Operador/Trabajador:", type="password", key="pass_carga")
    
    if pass_carga == CLAVE_TRABAJADORES:
        st.success("Acceso concedido para carga de datos")
        
        with st.form("form_carga", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                dni = st.text_input("DNI *").strip()
                nombre = st.text_input("Nombre *").strip()
            with col2:
                apellido = st.text_input("Apellido *").strip()
                direccion = st.text_input("Dirección").strip()
                
            tipo_ayuda = st.selectbox("Tipo de Ayuda", [
                "Materiales de Construcción", 
                "Módulo Alimentario", 
                "Subsidio Económico", 
                "Medicamentos", 
                "Asistencia Directa", 
                "Trámites", 
                "Otros"
            ])
            
            descripcion = st.text_input("Descripción / Detalle", placeholder="Ej: 10 chapas de zinc, receta de farmacia, etc.")
            
            guardar = st.form_submit_button("Guardar Registro")
            
            if guardar:
                if not dni or not nombre or not apellido:
                    st.error("Por favor completa al menos DNI, Nombre y Apellido.")
                else:
                    supabase.table("personas").upsert({
                        "dni": dni,
                        "nombre": nombre,
                        "apellido": apellido,
                        "direccion": direccion
                    }).execute()
                    
                    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                    supabase.table("entregas").insert({
                        "dni_persona": dni,
                        "fecha": fecha_actual,
                        "tipo_ayuda": tipo_ayuda,
                        "descripcion": descripcion
                    }).execute()
                    
                    st.success(f"¡Registro guardado correctamente para el DNI {dni}!")
                    
    elif pass_carga != "":
        st.error("Contraseña incorrecta. Solo el personal autorizado puede cargar datos.")

# ---------------------------------------------------------
# 2. MÓDULO: CONSULTA POR DNI (ACCESO DIRECTIVOS)
# ---------------------------------------------------------
elif opcion == "🔍 Consultar Historial (DNI)":
    st.subheader("🔒 Consulta de Historial (Exclusivo Directivos)")
    
    pass_consulta = st.text_input("Ingrese la contraseña de Directivo:", type="password", key="pass_consulta")
    
    if pass_consulta == CLAVE_DIRECTIVOS:
        st.success("Acceso concedido para consultas directivas")
        
        dni_buscar = st.text_input("Ingresa el DNI a buscar:").strip()
        
        if st.button("Buscar Historial") or dni_buscar:
            if dni_buscar:
                resp_persona = supabase.table("personas").select("*").eq("dni", dni_buscar).execute()
                
                if resp_persona.data:
                    persona = resp_persona.data[0]
                    st.info(f"**Beneficiario:** {persona['apellido']}, {persona['nombre']} | **Domicilio:** {persona['direccion']}")
                    
                    resp_entregas = supabase.table("entregas").select("fecha, tipo_ayuda, descripcion").eq("dni_persona", dni_buscar).order("id", desc=True).execute()
                    
                    if resp_entregas.data:
                        df = pd.DataFrame(resp_entregas.data)
                        df.rename(columns={
                            'fecha': 'Fecha y Hora',
                            'tipo_ayuda': 'Tipo de Ayuda',
                            'descripcion': 'Descripción'
                        }, inplace=True)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.warning("El beneficiario existe pero no tiene entregas registradas.")
                else:
                    st.error("No se encontró ningún beneficiario con ese DNI.")
                    
    elif pass_consulta != "":
        st.error("Contraseña incorrecta. Solo la dirección puede consultar los datos.")
