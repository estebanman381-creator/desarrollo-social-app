import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Desarrollo Social", page_icon="📋", layout="wide")

st.title("📋 Sistema de Gestión - Desarrollo Social")

# Conexión a Base de Datos
def conectar_bd():
    conn = sqlite3.connect("desarrollo_social.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personas (
            dni TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            direccion TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entregas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dni_persona TEXT NOT NULL,
            fecha TEXT NOT NULL,
            tipo_ayuda TEXT NOT NULL,
            descripcion TEXT,
            FOREIGN KEY (dni_persona) REFERENCES personas (dni)
        )
    """)
    conn.commit()
    return conn

conn = conectar_bd()

# Menú principal
opcion = st.sidebar.radio("Navegación", ["1. Cargar Ayuda", "2. Consultar por DNI"])

# ---------------------------------------------------------
# 1. CARGA DE AYUDAS
# ---------------------------------------------------------
if opcion == "1. Cargar Ayuda":
    st.subheader("✍️ Registro de Beneficiario y Entrega")
    
    with st.form("form_carga", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            dni = st.text_input("DNI *").strip()
            nombre = st.text_input("Nombre *").strip()
        with col2:
            apellido = st.text_input("Apellido *").strip()
            direccion = st.text_input("Dirección").strip()
            
        # Lista de ayudas actualizada
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
                cursor = conn.cursor()
                # Insertar o actualizar persona
                cursor.execute("""
                    INSERT INTO personas (dni, nombre, apellido, direccion)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(dni) DO UPDATE SET
                        nombre=excluded.nombre,
                        apellido=excluded.apellido,
                        direccion=excluded.direccion
                """, (dni, nombre, apellido, direccion))
                
                # Registrar entrega
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                cursor.execute("""
                    INSERT INTO entregas (dni_persona, fecha, tipo_ayuda, descripcion)
                    VALUES (?, ?, ?, ?)
                """, (dni, fecha_actual, tipo_ayuda, descripcion))
                
                conn.commit()
                st.success(f"¡Registro guardado correctamente para el DNI {dni}!")

# ---------------------------------------------------------
# 2. CONSULTA POR DNI
# ---------------------------------------------------------
elif opcion == "2. Consultar por DNI":
    st.subheader("🔍 Consulta de Historial de Ayudas")
    
    dni_buscar = st.text_input("Ingresa el DNI a buscar:").strip()
    
    if st.button("Buscar Historial") or dni_buscar:
        if dni_buscar:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre, apellido, direccion FROM personas WHERE dni = ?", (dni_buscar,))
            persona = cursor.fetchone()
            
            if persona:
                st.info(f"**Beneficiario:** {persona[1]}, {persona[0]} | **Domicilio:** {persona[2]}")
                
                # Consultar historial
                query = "SELECT fecha as 'Fecha y Hora', tipo_ayuda as 'Tipo de Ayuda', descripcion as 'Descripción' FROM entregas WHERE dni_persona = ? ORDER BY id DESC"
                df = pd.read_sql_query(query, conn, params=(dni_buscar,))
                
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("El beneficiario existe pero no tiene entregas registradas.")
            else:
                st.error("No se encontró ningún beneficiario con ese DNI.")