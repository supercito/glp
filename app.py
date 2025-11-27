import streamlit as st

st.set_page_config(page_title="Control de Tanques GLP", layout="wide")

# --- FUNCIONES ---
def calcular(capacidad, nivel):
    espacio = capacidad - nivel
    capacidad_trabajo = nivel
    puede_cargar = espacio >= 8000  # define tu mínima carga de camión aquí (ej: 8.000 L)
    return capacidad_trabajo, espacio, puede_cargar

# --- DIBUJO DEL ZEPPELIN ---
def tanque_zeppelin(label, nivel, capacidad):
    porcentaje = int((nivel / capacidad) * 100)

    tanque_html = f"""
    <div style='text-align:center; margin-bottom:10px;'>
        <div style="
            width: 280px;
            height: 80px;
            background: #d9d9d9;
            border-radius: 40px;
            position: relative;
            overflow: hidden;
            border: 2px solid #444;">
            
            <div style="
                width:{porcentaje}%;
                height:100%;
                background:#6cb1ff;">
            </div>
        </div>
        <b>{label}</b><br>
        Nivel: {nivel} / {capacidad} L
    </div>
    """
    st.markdown(tanque_html, unsafe_allow_html=True)

# --- INTERFAZ ---
st.title("🚛 Control de Carga – Tanques GLP")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Tanque Grande")
    capacidad1 = st.number_input("Capacidad tanque grande (L)", value=30000, step=500)
    nivel1 = st.number_input("Nivel actual tanque grande (L)", value=12000, step=500)

with col2:
    st.subheader("Tanque Chico")
    capacidad2 = st.number_input("Capacidad tanque chico (L)", value=15000, step=500)
    nivel2 = st.number_input("Nivel actual tanque chico (L)", value=6000, step=500)

st.markdown("---")

# --- ZEPPELINS ARRIBA DE TODO EN HORIZONTAL ---
cZ1, cZ2 = st.columns(2)

with cZ1:
    tanque_zeppelin("Tanque Grande", nivel1, capacidad1)

with cZ2:
    tanque_zeppelin("Tanque Chico", nivel2, capacidad2)

st.markdown("---")

# --- CÁLCULOS ---
cap1, espacio1, cargar1 = calcular(capacidad1, nivel1)
cap2, espacio2, cargar2 = calcular(capacidad2, nivel2)

st.subheader("📊 Resultados")

colA, colB = st.columns(2)

with colA:
    st.markdown("### Tanque Grande")
    st.write(f"**Capacidad de trabajo:** {cap1} L")
    st.write(f"**Espacio disponible:** {espacio1} L")
    st.write("**¿Puede cargar el camión?** " +
             ("🟢 Sí" if cargar1 else "🔴 No"))

with colB:
    st.markdown("### Tanque Chico")
    st.write(f"**Capacidad de trabajo:** {cap2} L")
    st.write(f"**Espacio disponible:** {espacio2} L")
    st.write("**¿Puede cargar el camión?** " +
             ("🟢 Sí" if cargar2 else "🔴 No"))
