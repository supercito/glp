import streamlit as st

# Configuración de la página
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
        height: 192px; /* h-48 equivalente */
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
        background-color: #dc2626; /* red-600 */
        z-index: 10;
    }
    .max-level-line {
        position: absolute;
        width: 100%;
        height: 2px;
        border-top: 2px dashed #000; /* Linea punteada para el 85% */
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
FORMATS_C3 = {
    "Ambiental": 87.6,
    "Desinfectante": 69.5,
    "Selton": 93.6,
}

FORMATS_C2 = {
    "Jirafa": 100.7,
    "360g": 69.5,
}

TANK1_CAPACITY = 49170  # Capacidad geométrica base
TANK2_CAPACITY = 30694  # Capacidad geométrica base
TRUCK_CAPACITY_KG = 24000 # Carga del camión en Kg
SAFE_LIMIT_PERCENT = 85.0 # Límite de seguridad de llenado

# --- Función para dibujar el tanque ---
def draw_tank(name, percent, min_percent):
    is_low = percent <= min_percent
    is_overfilled = percent > SAFE_LIMIT_PERCENT
    
    # Colores: Rojo si está bajo, Naranja si excede el 85%, Verde si está normal
    if is_low:
        color = "#ef4444"
        alert_icon = "⚠️ B" # Bajo
    elif is_overfilled:
        color = "#f97316" # Orange-500
        alert_icon = "⚠️ A" # Alto
    else:
        color = "#22c55e"
        alert_icon = ""
    
    html = f"""
    <div class="tank-wrapper">
        <div class="tank-container">
            <div class="tank-level" style="height: {min(percent, 100)}%; background-color: {color};"></div>
            {'<div class="min-level-line" style="bottom: ' + str(min_percent) + '%;"></div>' if is_low else ''}
            <div class="max-level-line" style="bottom: {SAFE_LIMIT_PERCENT}%;" title="Límite 85%"></div>
        </div>
        <div class="tank-name">{name}</div>
        <div class="tank-value" style="color: {'inherit'}">
            {percent}% {alert_icon}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- Interfaz Principal ---
st.title("Calculadora de Disponibilidad de GLP")

with st.container(border=True):
    # Inputs numéricos
    col1, col2 = st.columns(2)
    
    with col1:
        tank1_percent = st.number_input("% Tanque Grande", value=75.0, min_value=0.0, max_value=100.0, step=0.1)
        min_percent = st.number_input("% Mínimo Requerido", value=5.0, min_value=0.0, max_value=100.0, step=0.1)
        
    with col2:
        tank2_percent = st.number_input("% Tanque Chico", value=75.0, min_value=0.0, max_value=100.0, step=0.1)
        speed = st.number_input("Velocidad C3 (env/min)", value=195, step=1)

    # Visualización de Tanques
    st.write("") 
    t_col1, t_col2 = st.columns([1, 1])
    with t_col1:
        draw_tank("Tanque Grande", tank1_percent, min_percent)
    with t_col2:
        draw_tank("Tanque Chico", tank2_percent, min_percent)
    
    st.caption(f"Línea punteada indica el límite de seguridad ({SAFE_LIMIT_PERCENT}%)")

    st.write("---")

    # Selección de Línea y Formatos
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

    # --- CÁLCULOS ---

    # 1. Disponibilidad Actual
    total_available_kg = ((TANK1_CAPACITY * (tank1_percent / 100)) + (TANK2_CAPACITY * (tank2_percent / 100))) * 0.54
    min_required_kg = ((TANK1_CAPACITY + TANK2_CAPACITY) * (min_percent / 100)) * 0.54
    usable_glp_kg = total_available_kg - min_required_kg

    # 2. Consumo
    total_consumption_per_minute = 0
    if line == "C3" and format_c3 is not None:
        total_consumption_per_minute = format_c3 * speed / 1000
    elif line == "C2" and format_c2 is not None:
        total_consumption_per_minute = format_c2 * 52 / 1000
    elif line == "C3 y C2" and format_c3 is not None and format_c2 is not None:
        total_consumption_per_minute = (format_c3 * speed + format_c2 * 52) / 1000

    minutes_available = usable_glp_kg / total_consumption_per_minute if (usable_glp_kg > 0 and total_consumption_per_minute > 0) else 0
    hours = int(minutes_available // 60)
    minutes = int(minutes_available % 60)

    # 3. Cálculo de Descarga de Camión (Considerando el límite del 85%)
    # Capacidad Total Física (100%)
    total_physical_capacity_kg = (TANK1_CAPACITY + TANK2_CAPACITY) * 0.54
    
    # Capacidad Segura Máxima (85%)
    max_safe_capacity_kg = total_physical_capacity_kg * (SAFE_LIMIT_PERCENT / 100.0)
    
    # Espacio libre hasta llegar al 85%
    # Si los tanques ya tienen más del 85%, el espacio libre es negativo
    space_available_for_truck_kg = max_safe_capacity_kg - total_available_kg
    
    can_offload = space_available_for_truck_kg >= TRUCK_CAPACITY_KG

    # --- RESULTADOS ---
    st.markdown("### Tiempo restante")
    st.markdown(f"<h2 style='text-align: center; color: #2563eb;'>{hours}h {minutes}min</h2>", unsafe_allow_html=True)
    
    # Alerta de Camión
    st.markdown("### Estado de Descarga")
    
    if can_offload:
        st.success(f"""
        ✅ **SE PUEDE DESCARGAR**
        
        El camión ({TRUCK_CAPACITY_KG:,.0f} kg) entra sin superar el {SAFE_LIMIT_PERCENT}%.
        \n(Espacio seguro disponible: {space_available_for_truck_kg:,.2f} kg)
        """)
    else:
        # Calculamos cuánto falta
        if space_available_for_truck_kg < 0:
            st.error(f"""
            ⛔ **PELIGRO: SOBRELLENADO**
            
            Los tanques actuales superan el límite de seguridad del {SAFE_LIMIT_PERCENT}%.
            """)
        else:
            missing = TRUCK_CAPACITY_KG - space_available_for_truck_kg
            st.error(f"""
            ⛔ **NO SE PUEDE DESCARGAR AÚN**
            
            Si descargas ahora, superarías el límite del {SAFE_LIMIT_PERCENT}%.
            \nFaltan consumir **{missing:,.2f} kg** para poder recibir el camión.
            """)

    with st.expander("Ver detalles técnicos"):
        st.write(f"Nivel actual (kg): **{total_available_kg:,.2f} kg**")
        st.write(f"Capacidad Máxima Segura ({SAFE_LIMIT_PERCENT}%): **{max_safe_capacity_kg:,.2f} kg**")
        st.write(f"Capacidad Física Total (100%): **{total_physical_capacity_kg:,.2f} kg**")
