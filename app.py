import streamlit as st

# --- Configuración de la página ---
st.set_page_config(page_title="Calculadora GLP", page_icon="🔥")

# --- Estilos CSS personalizados ---
st.markdown("""
<style>
    .tank-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 10px;
    }
    .tank-container {
        position: relative;
        width: 64px;
        height: 192px;
        background-color: #f3f4f6;
        border: 2px solid #9ca3af;
        border-radius: 9999px;
        overflow: hidden;
    }
    .tank-level {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        transition: height 0.5s ease;
    }
    .min-level-line {
        position: absolute;
        width: 100%;
        height: 2px;
        background-color: #dc2626;
        z-index: 10;
    }
    .max-level-line {
        position: absolute;
        width: 100%;
        height: 2px;
        border-top: 2px dashed #000;
        z-index: 5;
        opacity: 0.5;
    }
    .tank-name {
        font-size: 12px;
        font-weight: 600;
        margin-top: 4px;
    }
    .tank-value {
        font-size: 14px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 4px;
    }
</style>
""", unsafe_allow_html=True)

# --- Constantes ---
FORMATS_C3 = {"Ambiental": 87.6, "Desinfectante": 69.5, "Selton": 93.6}
FORMATS_C2 = {"Jirafa": 100.7, "360g": 69.5}

TANK1_CAPACITY = 49170
TANK2_CAPACITY = 30694
SAFE_LIMIT_PERCENT = 85

# --- Función para dibujar el tanque ---
def draw_tank(name, percent, min_percent):
    is_low = percent <= min_percent
    is_overfilled = percent > SAFE_LIMIT_PERCENT
    
    if is_low:
        color = "#ef4444"
        alert_icon = "⚠️"
    elif is_overfilled:
        color = "#f97316"
        alert_icon = "⚠️"
    else:
        color = "#22c55e"
        alert_icon = ""
    
    min_line = f'<div class="min-level-line" style="bottom: {min_percent}%;"></div>' if is_low else ''

    html_content = (
        f'<div class="tank-wrapper">'
        f'  <div class="tank-container">'
        f'    <div class="tank-level" style="height: {min(percent, 100)}%; background-color: {color};"></div>'
        f'    {min_line}'
        f'    <div class="max-level-line" style="bottom: {SAFE_LIMIT_PERCENT}%;" title="Límite 85%"></div>'
        f'  </div>'
        f'  <div class="tank-name">{name}</div>'
        f'  <div class="tank-value" style="color: inherit">{percent}% {alert_icon}</div>'
        f'</div>'
    )
    st.markdown(html_content, unsafe_allow_html=True)

# --- Interfaz de Usuario ---
st.title("Calculadora GLP")

with st.container(border=True):
    # Inputs (Enteros)
    col1, col2 = st.columns(2)
    with col1:
        tank1_percent = st.number_input("% Tanque Grande", value=85, min_value=0, max_value=100, step=1)
        min_percent = st.number_input("% Mínimo Requerido", value=5, min_value=0, max_value=100, step=1)
        # INPUT DE DENSIDAD
        density = st.number_input("Densidad (según ficha)", value=0.567, min_value=0.500, max_value=0.600, step=0.001, format="%.3f")
        
    with col2:
        tank2_percent = st.number_input("% Tanque Chico", value=85, min_value=0, max_value=100, step=1)
        speed = st.number_input("Velocidad C3 (env/min)", value=195, step=1)
        
    # Visualización
    st.write("") 
    t_col1, t_col2 = st.columns([1, 1])
    with t_col1:
        draw_tank("Tanque Grande", tank1_percent, min_percent)
    with t_col2:
        draw_tank("Tanque Chico", tank2_percent, min_percent)
    
    st.caption(f"Línea punteada indica límite de seguridad {SAFE_LIMIT_PERCENT}%")
    st.divider()

    # Selección de Línea
    line = st.selectbox("Línea de consumo", ["C3", "C2", "C3 y C2"])
    
    format_c3 = None
    format_c2 = None
    eff_c3_input = 80 # default

    col_f1, col_f2 = st.columns(2)

    # Selectores dinámicos
    if line in ["C3", "C3 y C2"]:
        with col_f1:
            na
