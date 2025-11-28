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
TRUCK_CAPACITY_KG = 27000
SAFE_LIMIT_PERCENT = 85

# --- Función para dibujar el tanque ---
def draw_tank(name, percent, min_percent):
    is_low = percent <= min_percent
    is_overfilled = percent > SAFE_LIMIT_PERCENT
    
    if is_low:
        color = "#ef4444"
        alert_icon = "⚠️ B"
    elif is_overfilled:
        color = "#f97316"
        alert_icon = "⚠️ A"
    else:
        color = "#22c55e"
        alert_icon = ""
    
    min_line = f'<div class="min-level-line" style="bottom: {min_percent}%;"></div>' if is_low else ''

    # Construcción HTML segura sin indentación para evitar errores
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
st.title("Calculadora de Disponibilidad de GLP")

with st.container(border=True):
    # Inputs (AHORA SON ENTEROS GRACIAS A value=INT y step=1)
    col1, col2 = st.columns(2)
    with col1:
        # value=75 (int), step=1 -> Input de enteros
        tank1_percent = st.number_input("% Tanque Grande", value=75, min_value=0, max_value=100, step=1)
        min_percent = st.number_input("% Mínimo Requerido", value=5, min_value=0, max_value=100, step=1)
    with col2:
        tank2_percent = st.number_input("% Tanque Chico", value=75, min_value=0, max_value=100, step=1)
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

    # Selección
    line = st.selectbox("Línea de consumo", ["C3", "C2", "C3 y C2"])
    format_c3 = None
    format_c2 = None
    col_f1, col_f2 = st.columns(2)

    if line in ["C3", "C3 y C2"]:
        with col_f1:
            name_c3 = st.selectbox("Formato C3", list(FORMATS_C3.keys()), format_func=lambda x: f"{x} ({FORMATS_C3[x]} g)")
            format_c3 = FORMATS_C3[name_c3]
    if line in ["C2", "C3 y C2"]:
        with col_f2:
            name_c2 = st.selectbox("Formato C2", list(FORMATS_C2.keys()), format_func=lambda x: f"{x} ({FORMATS_C2[x]} g)")
            format_c2 = FORMATS_C2[name_c2]

    # Cálculos
    total_avail_kg = ((TANK1_CAPACITY * (tank1_percent/100)) + (TANK2_CAPACITY * (tank2_percent/100))) * 0.54
    min_req_kg = ((TANK1_CAPACITY + TANK2_CAPACITY) * (min_percent/100)) * 0.54
    usable_kg = total_avail_kg - min_req_kg

    cons_min = 0
    if line == "C3" and format_c3: cons_min = format_c3 * speed / 1000
    elif line == "C2" and format_c2: cons_min = format_c2 * 52 / 1000
    elif line == "C3 y C2" and format_c3 and format_c2: cons_min = (format_c3 * speed + format_c2 * 52) / 1000

    mins_avail = usable_kg / cons_min if (usable_kg > 0 and cons_min > 0) else 0
    
    # Camión
    total_phys_cap = (TANK1_CAPACITY + TANK2_CAPACITY) * 0.54
    max_safe_cap = total_phys_cap * (SAFE_LIMIT_PERCENT / 100.0)
    space_for_truck = max_safe_cap - total_avail_kg
    can_offload = space_for_truck >= TRUCK_CAPACITY_KG

    # Resultados
    st.markdown("### Tiempo restante")
    st.markdown(f"<h2 style='text-align:center; color:#2563eb;'>{int(mins_avail//60)}h {int(mins_avail%60)}min</h2>", unsafe_allow_html=True)
    
    st.markdown("### Estado de Descarga")
    if can_offload:
        st.success(f"✅ **SE PUEDE DESCARGAR**\n\nEl camión entra sin superar el {SAFE_LIMIT_PERCENT}%.\n(Espacio: {space_for_truck:,.2f} kg)")
    else:
        if space_for_truck < 0:
            st.error(f"⛔ **SOBRELLENADO**: Se supera el {SAFE_LIMIT_PERCENT}%.")
        else:
            st.error(f"⛔ **NO DESCARGAR**: Faltan consumir **{(TRUCK_CAPACITY_KG - space_for_truck):,.2f} kg**.")

    with st.expander("Ver detalles técnicos"):
        st.write(f"GLP actual: **{total_avail_kg:,.2f} kg**")
        st.write(f"Capacidad 85%: **{max_safe_cap:,.2f} kg**")
