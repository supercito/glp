import streamlit as st
import time

st.set_page_config(page_title="Control de Tanques", layout="centered")

st.title("📦 Control de Tanques - Versión Streamlit")

st.markdown("---")

# Valores iniciales
default_tanque_grande = 85
default_tanque_chico = 85
velocidad_c2 = 52

# Estilos
st.markdown(
    """
    <style>
    .nivel {
        height: 300px;
        width: 80px;
        border-radius: 15px;
        background-color: #ddd;
        display: flex;
        align-items: flex-end;
        justify-content: center;
        margin: auto;
    }
    .barra {
        width: 100%;
        border-radius: 15px;
    }
    .etiqueta{
        text-align: center;
        font-size: 20px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Contenedor principal
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("🛢️ Tanque Grande")
    nivel1 = st.number_input("Nivel %", 0, 100, default_tanque_grande)

    color1 = "red" if nivel1 <= 5 else "green"

    st.markdown(f"""
        <div class="etiqueta">{nivel1}%</div>
        <div class="nivel">
            <div class="barra" style="height:{nivel1}%; background:{color1};"></div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.subheader("🛢️ Tanque Chico")
    nivel2 = st.number_input("Nivel %  ", 0, 100, default_tanque_chico)

    color2 = "red" if nivel2 <= 5 else "green"

    st.markdown(f"""
        <div class="etiqueta">{nivel2}%</div>
        <div class="nivel">
            <div class="barra" style="height:{nivel2}%; background:{color2};"></div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.subheader("⚙️ Información de Proceso")
st.write(f"**Velocidad C2:** {velocidad_c2} env/min")

st.markdown("💡 *Esta es una versión completamente funcional y lista para subir a Streamlit Cloud.*")
