import streamlit as st

# --- Configuración de la página ---
st.set_page_config(page_title="Calculadora GLP", page_icon="🔥")

# --- Estilos CSS personalizados para los tanques ---
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
        height: 192px; /* Altura del tanque */
        background-color: #f3f4f6;
        border: 2px solid #9ca3af;
        border-radius: 9999px; /* Bordes redondeados */
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
        background-color: #dc2626; /* Rojo */
        z-index: 10;
    }
    .max-level-line {
        position: absolute;
        width: 100%;
        height: 2px;
        border-top: 2px dashed #000; /* Línea punteada negra */
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

# --- Constantes y Datos ---
FORMATS_C3 = {
    "Ambiental": 87.6,
    "Desinfectante": 69.5,
    "Selton": 93.6,
}

FORMATS_C2 = {
    "Jirafa": 100.7,
    "360g": 69.5,
}

TANK1_CAPACITY = 49170  # Capacidad m3 Tanque Grande
TANK2_CAPACITY = 30694  # Capacidad m3 Tanque Chico
TRUCK_CAPACITY_KG = 24000 # Carga del camión
SAFE_LIMIT_PERCENT = 85.0 # Límite de seguridad

# --- Función para dibujar el tanque ---
def draw_tank(name, percent, min_percent):
    is_low = percent <= min_percent
    is_overfilled = percent > SAFE_LIMIT_PERCENT
    
    # Definir colores según estado
    if is_low:
        color = "#ef4444" # Rojo
        alert_icon = "⚠️ B"
    elif is_overfilled:
        color = "#f97316" # Naranja (alerta alto)
        alert_icon = "⚠️ A"
    else:
        color = "#22c55e" # Verde
        alert_icon = ""
    
    # Generar línea de mínimo solo si es necesario
    min_line_html = f'<div class="min-level-line" style="bottom: {min_percent}%;"></div>' if is_low else ''

    # HTML sin identación al inicio para evitar errores de renderizado en Streamlit
    html = f"""
<div class="tank-wrapper">
    <div class="tank-container">
        <div class="tank-level" style="height: {min(percent, 100)}%; background-color: {color};"></div>
        {min_line_html}
        <div class="max-level-line" style="bottom: {SAFE_LIMIT_PERCENT}%;" title="Límite 85%"></div>
    </div>
    <div class="tank-name">{name}</div>
    <div class="tank-value" style="color: inherit">
        {percent}% {alert_icon}
    </div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)

# --- Interfaz de Usuario ---
st.title("Calculadora de Disponibilidad de GLP")

with st.container(border=True):
    # 1. Entradas numéricas
    col1, col2 = st.columns(2)
    
    with col1:
        tank1_percent = st.number_input("% Tanque Grande", value=75.0, min_value=0.0, max_value=100.0, step=0.1)
        min_percent = st.number_input("% Mínimo Requerido", value=5.0, min_value=0.0, max_value=100.0, step=0.1)
        
    with col2:
        tank2_percent = st.number_input("% Tanque Chico", value=75.0, min_value=0.0, max_value=100.0, step=0.1)
        speed = st.number_input("Velocidad C3 (env/min)", value=195, step=1)

    # 2. Visualización de Tanques
    st.write("") 
    t_col1, t_col2 = st.columns([1, 1])
    with t_col1:
        draw_tank("Tanque Grande", tank1_percent, min_percent)
    with t_col2:
        draw_tank("Tanque Chico", tank2_percent, min_percent)
    
    st.caption(f"La línea punteada indica el límite de seguridad del {SAFE_LIMIT_PERCENT}%")

    st.divider()

    # 3. Configuración de Línea
    line = st.selectbox("Línea de consumo", ["C3", "C2", "C3 y C2"])
    
    format_c3 = None
    format_c2 = None

    col_f1, col_f2 = st.columns(2)

    if line in ["C3", "C3 y C2"]:
        with col_f1:
            format_c3_name = st.selectbox(
                "Formato C3", 
                options=list(FORMATS_C3.keys()),
                format_func=lambda x: f"{x} ({FORMATS_C3[x]} g/env)"
            )
            format_c3 = FORMATS_C3[format_c3_name]

    if line in ["C2", "C3 y C2"]:
        with col_f2:
            format_c2_name = st.selectbox(
                "Formato C2", 
                options=list(FORMATS_C2.keys()),
                format_func=lambda x: f"{x} ({FORMATS_C2[x]} g/env)"
            )
            format_c2 = FORMATS_C2[format_c2_name]

    # --- LÓGICA DE CÁLCULO ---

    # A. Cálculo de masa disponible (Densidad 0.54)
    total_available_kg = ((TANK1_CAPACITY * (tank1_percent / 100)) + (TANK2_CAPACITY * (tank2_percent / 100))) * 0.54
    min_required_kg = ((TANK1_CAPACITY + TANK2_CAPACITY) * (min_percent / 100)) * 0.54
    usable_glp_kg = total_available_kg - min_required_kg

    # B. Cálculo de consumo por minuto
    total_consumption_per_minute = 0
    if line == "C3" and format_c3 is not None:
        total_consumption_per_minute = format_c3 * speed / 1000
    elif line == "C2" and format_c2 is not None:
        total_consumption_per_minute = format_c2 * 52 / 1000 # Vel fija C2
    elif line == "C3 y C2" and format_c3 is not None and format_c2 is not None:
        total_consumption_per_minute = (format_c3 * speed + format_c2 * 52) / 1000

    # C. Tiempo restante
    if usable_glp_kg > 0 and total_consumption_per_minute > 0:
        minutes_available = usable_glp_kg / total_consumption_per_minute
    else:
        minutes_available = 0
        
    hours = int(minutes_available // 60)
    minutes = int(minutes_available % 60)

    # D. Lógica de Descarga de Camión (Considerando el 85%)
    total_physical_capacity_kg = (TANK1_CAPACITY + TANK2_CAPACITY) * 0.54
    max_safe_capacity_kg = total_physical_capacity_kg * (SAFE_LIMIT_PERCENT / 100.0)
    space_available_for_truck_kg = max_safe_capacity_kg - total_available_kg
    
    can_offload = space_available_for_truck_kg >= TRUCK_CAPACITY_KG

    # --- RESULTADOS ---
    st.markdown("### Tiempo restante")
    st.markdown(f"<h2 style='text-align: center; color: #2563eb;'>{hours}h {minutes}min</h2>", unsafe_allow_html=True)
    
    st.markdown("### Estado de Descarga")
    
    if can_offload:
        st.success(f"""
        ✅ **SE PUEDE DESCARGAR**
        
        El camión de **{TRUCK_CAPACITY_KG:,.0f} kg** entra sin superar el límite del {SAFE_LIMIT_PERCENT}%.
        \n(Espacio seguro disponible: {space_available_for_truck_kg:,.2f} kg)
        """)
    else:
        if space_available_for_truck_kg < 0:
            st.error(f"""
            ⛔ **PELIGRO: SOBRELLENADO**
            
            Los tanques actuales ya superan el límite de seguridad del {SAFE_LIMIT_PERCENT}%.
            """)
        else:
            missing = TRUCK_CAPACITY_KG - space_available_for_truck_kg
            st.error(f"""
            ⛔ **NO SE PUEDE DESCARGAR AÚN**
            
            Si descargas ahora, superarías el límite de seguridad.
            \nFaltan consumir **{missing:,.2f} kg** para poder recibir el camión.
            """)

    with st.expander("Ver detalles técnicos"):
        st.write(f"GLP actual en tanques: **{total_available_kg:,.2f} kg**")
        st.write(f"Capacidad Máxima al 85%: **{max_safe_capacity_kg:,.2f} kg**")
        st.write(f"Capacidad Física al 100%: **{total_physical_capacity_kg:,.2f} kg**")
        st.write(f"Consumo actual: **{total_consumption_per_minute*60:,.2f} kg/hora**")
