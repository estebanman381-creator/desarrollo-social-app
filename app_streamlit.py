import streamlit as st
from datetime import datetime
import pandas as pd
from supabase import create_client, Client

# --- CONFIGURACIÓN DE CONTRASEÑAS ---
CLAVE_TRABAJADORES = "trabajador123"
CLAVE_DIRECTIVOS = "direccion2026"

# Configuración de la página
st.set_page_config(page_title="Desarrollo Social", page_icon="📋", layout="wide")

# --- LOGO EN EL ENCABEZADO PRINCIPAL ---
# Ajusta 'width=350' si deseas que el logo se vea un poco más grande o más pequeño
st.image("logoloreto.jpeg", width=350)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    /* 1. Aumentar tamaño de letra en el Menú Lateral (Sidebar) */
    [data-testid="stSidebar"] label {
        font-size: 20px !important;
        font-weight: bold !important;
    }
    
    [data-testid="stSidebar"] p {
        font-size: 18px !important;
    }

    /* 2. Aumentar tamaño de letra de las etiquetas de contraseña/entradas de texto */
    div[data-baseweb="input"] label, 
    .stTextInput label {
        font-size: 19px !important;
        font-weight: 600 !important;
        color: #E0E0E0 !important;
    }

    /* 3. Aumentar tamaño del texto ingresado dentro del campo */
    input {
        font-size: 18px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📋 Sistema de Gestión - Desarrollo Social")

# --- CONEXIÓN A SUPABASE ---
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# Menú principal
opcion = st.sidebar.radio("Navegación", ["1. Cargar Ayuda", "2. Consultar por DNI"])

# ---------------------------------------------------------
# 1. MÓDULO: CARGA DE AYUDAS (ACCESO TRABAJADORES)
# ---------------------------------------------------------
if opcion == "1. Cargar Ayuda":
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
                    # Upsert persona (insertar o actualizar si ya existe DNI)
                    supabase.table("personas").upsert({
                        "dni": dni,
                        "nombre": nombre,
                        "apellido": apellido,
                        "direccion": direccion
                    }).execute()
                    
                    # Registrar entrega
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
elif opcion == "2. Consultar por DNI":
    st.subheader("🔒 Consulta de Historial (Exclusivo Directivos)")
    
    pass_consulta = st.text_input("Ingrese la contraseña de Directivo:", type="password", key="pass_consulta")
    
    if pass_consulta == CLAVE_DIRECTIVOS:
        st.success("Acceso concedido para consultas directivas")
        
        dni_buscar = st.text_input("Ingresa el DNI a buscar:").strip()
        
        if st.button("Buscar Historial") or dni_buscar:
            if dni_buscar:
                # Consultar datos de la persona
                resp_persona = supabase.table("personas").select("*").eq("dni", dni_buscar).execute()
                
                if resp_persona.data:
                    persona = resp_persona.data[0]
                    st.info(f"**Beneficiario:** {persona['apellido']}, {persona['nombre']} | **Domicilio:** {persona['direccion']}")
                    
                    # Consultar entregas
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
