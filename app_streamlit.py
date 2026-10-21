import streamlit as st
from datetime import datetime
import pandas as pd
from supabase import create_client, Client
from fpdf import FPDF
import io

# --- CONFIGURACIÓN DE CONTRASEÑAS ---
CLAVE_TRABAJADORES = "trabajador123"
CLAVE_DIRECTIVOS = "direccion2026"

st.set_page_config(page_title="Desarrollo Social - Loreto", page_icon="📋", layout="wide")

# --- CONEXIÓN A SUPABASE ---
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# --- FUNCIÓN PARA GENERAR COMPROBANTE PDF ---
def generar_pdf(nombre, apellido, dni, direccion, tipo_ayuda, descripcion, fecha, operador):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Encabezado
    pdf.cell(0, 10, "MUNICIPALIDAD DE LORETO", ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Secretaría de Desarrollo Social", ln=True, align='C')
    pdf.cell(0, 8, "COMPROBANTE DE ENTREGA DE ASISTENCIA", ln=True, align='C')
    pdf.ln(10)
    
    # Datos de la entrega
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 7, f"Fecha y Hora: {fecha}", ln=True)
    pdf.cell(0, 7, f"Operador Responsable: {operador}", ln=True)
    pdf.cell(0, 7, f"Beneficiario: {apellido}, {nombre}", ln=True)
    pdf.cell(0, 7, f"DNI: {dni}", ln=True)
    pdf.cell(0, 7, f"Domicilio: {direccion}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 7, f"Tipo de Ayuda: {tipo_ayuda}", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, f"Detalle/Descripción: {descripcion}")
    pdf.ln(25)
    
    # Área de firma
    pdf.cell(0, 7, "______________________________", ln=True, align='C')
    pdf.cell(0, 7, "Firma del Beneficiario", ln=True, align='C')
    
    # Retornar como bytes en memoria
    return bytes(pdf.output())

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    [data-testid="stToolbar"] {display: none;}
    div[class^="viewerBadge"] {display: none;}
    .stAppDeployButton {display: none;}

    [data-testid="stSidebar"] {
        background-color: #1E232A !important;
        border-right: 1px solid #2D3748;
    }

    .sidebar-header {
        font-size: 13px !important;
        font-weight: 700 !important;
        color: #A0AEC0 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    [data-testid="stSidebar"] .stRadio label {
        font-size: 17px !important;
        font-weight: 500 !important;
        color: #E2E8F0 !important;
        padding: 8px 12px;
        border-radius: 6px;
    }

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

# --- LOGO Y TÍTULO ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logoloreto.jpeg", use_container_width=True)

st.title("📋 Sistema de Gestión - Desarrollo Social")

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown('<p class="sidebar-header">MENÚ DE NAVEGACIÓN</p>', unsafe_allow_html=True)
    
    opcion = st.radio(
        label="",
        options=[
            "✍️ Cargar Ayuda Directa", 
            "🔍 Consultar Historial (DNI)",
            "📊 Dashboard & Estadísticas"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown("""
        <div class="sidebar-footer">
            <strong>Municipalidad de Loreto</strong><br>
            Secretaría de Desarrollo Social<br><br>
            🟢 <strong>Base de datos:</strong> Conectada<br>
            🔒 <strong>Acceso:</strong> Seguro (Encriptado)
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. CARGA DE AYUDAS + REGISTRO DE OPERADOR + PDF
# ---------------------------------------------------------
if opcion == "✍️ Cargar Ayuda Directa":
    st.subheader("✍️ Registro de Beneficiario y Entrega")
    
    pass_carga = st.text_input("Ingrese la contraseña de Operador/Trabajador:", type="password", key="pass_carga")
    
    if pass_carga == CLAVE_TRABAJADORES:
        st.success("Acceso concedido para carga de datos")
        
        with st.form("form_carga", clear_on_submit=False):
            col_op1, col_op2 = st.columns(2)
            with col_op1:
                operador = st.text_input("Nombre/Legajo del Operador Responsable *").strip()
            
            st.markdown("---")
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
                if not dni or not nombre or not apellido or not operador:
                    st.error("Por favor completa los campos obligatorios: Operador, DNI, Nombre y Apellido.")
                else:
                    # Guardar Persona
                    supabase.table("personas").upsert({
                        "dni": dni,
                        "nombre": nombre,
                        "apellido": apellido,
                        "direccion": direccion
                    }).execute()
                    
                    # Registrar Entrega con Operador
                    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                    supabase.table("entregas").insert({
                        "dni_persona": dni,
                        "fecha": fecha_actual,
                        "tipo_ayuda": tipo_ayuda,
                        "descripcion": descripcion,
                        "operador": operador
                    }).execute()
                    
                    st.success(f"¡Registro guardado correctamente para el DNI {dni}!")
                    
                    # Generar PDF para descarga inmediata
                    pdf_bytes = generar_pdf(nombre, apellido, dni, direccion, tipo_ayuda, descripcion, fecha_actual, operador)
                    st.download_button(
                        label="📄 Descargar Comprobante PDF",
                        data=pdf_bytes,
                        file_name=f"comprobante_{dni}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf"
                    )
                    
    elif pass_carga != "":
        st.error("Contraseña incorrecta.")

# ---------------------------------------------------------
# 2. CONSULTA HISTORIAL POR DNI
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
                    
                    resp_entregas = supabase.table("entregas").select("fecha, tipo_ayuda, descripcion, operador").eq("dni_persona", dni_buscar).order("id", desc=True).execute()
                    
                    if resp_entregas.data:
                        df = pd.DataFrame(resp_entregas.data)
                        df.rename(columns={
                            'fecha': 'Fecha y Hora',
                            'tipo_ayuda': 'Tipo de Ayuda',
                            'descripcion': 'Descripción',
                            'operador': 'Operador Carga'
                        }, inplace=True)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.warning("El beneficiario existe pero no tiene entregas registradas.")
                else:
                    st.error("No se encontró ningún beneficiario con ese DNI.")
                    
    elif pass_consulta != "":
        st.error("Contraseña incorrecta.")

# ---------------------------------------------------------
# 3. DASHBOARD Y ESTADÍSTICAS MENSUALES/ANUALES
# ---------------------------------------------------------
elif opcion == "📊 Dashboard & Estadísticas":
    st.subheader("📊 Panel de Métricas de Asistencia")
    
    pass_dash = st.text_input("Ingrese la contraseña de Directivo:", type="password", key="pass_dash")
    
    if pass_dash == CLAVE_DIRECTIVOS:
        st.success("Acceso concedido a Métricas")
        
        # Cargar todas las entregas
        resp = supabase.table("entregas").select("*").execute()
        
        if resp.data:
            df = pd.DataFrame(resp.data)
            df['fecha_dt'] = pd.to_datetime(df['fecha'], errors='coerce')
            df['Año'] = df['fecha_dt'].dt.year
            df['Mes_Num'] = df['fecha_dt'].dt.month
            df['Año_Mes'] = df['fecha_dt'].dt.strftime('%Y-%m')
            
            # Filtros superiores
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                anios_disponibles = sorted(df['Año'].dropna().unique().astype(int).tolist(), reverse=True)
                anio_sel = st.selectbox("Seleccionar Año:", anios_disponibles)
            
            # Métricas rápidas
            df_filtrado_anio = df[df['Año'] == anio_sel]
            
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric(f"Total Ayudas ({anio_sel})", len(df_filtrado_anio))
            m2.metric("Beneficiarios Únicos", df_filtrado_anio['dni_persona'].nunique())
            m3.metric("Tipos de Ayuda Distintos", df_filtrado_anio['tipo_ayuda'].nunique())
            st.markdown("---")
            
            # Tabla mensual
            st.write(f"### Total de Ayudas Entregadas por Mes en {anio_sel}")
            resumen_mensual = df_filtrado_anio.groupby('Año_Mes').size().reset_index(name='Cantidad de Entregas')
            resumen_mensual.rename(columns={'Año_Mes': 'Mes (Año-Mes)'}, inplace=True)
            st.bar_chart(resumen_mensual.set_index('Mes (Año-Mes)'))
            st.dataframe(resumen_mensual, use_container_width=True)
            
            # Desglose por tipo de ayuda
            st.write("### Desglose por Tipo de Ayuda")
            resumen_tipo = df_filtrado_anio.groupby('tipo_ayuda').size().reset_index(name='Total Entregado')
            st.dataframe(resumen_tipo, use_container_width=True)
            
        else:
            st.info("Aún no hay registros de entregas para mostrar estadísticas.")
            
    elif pass_dash != "":
        st.error("Contraseña incorrecta.")
